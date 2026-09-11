#!/usr/bin/env python3
"""
exp005 -- Bone-surface segmentation in REAL human lumbar ultrasound, with
subject-level evaluation and a handheld/robotic cross-domain matrix.

Data: KU Leuven / Balgrist, doi:10.48804/3XPCAE (CC-BY-4.0). 9 annotated
subjects, 18 scans, 6,182 expert-annotated frames.

WHAT IS BEING SEGMENTED: expert-annotated VISIBLE BONE SURFACE. Not a puncture
target, entry point or trajectory.

EVALUATION DESIGN
-----------------
* Splits are SUBJECT-DISJOINT, never random over frames. Frames within a sweep
  are near-duplicates; a random split would be meaningless.
* 3-fold grouped cross-validation over the 9 subjects. Folds are arranged so
  each test fold holds 2 subjects with handheld data (only 7 of 9 have any) plus
  one robotic-only subject.
* Per fold, three training regimes -- HUS-only, RUS-only, HUS+RUS -- each
  evaluated separately on held-out HUS and held-out RUS. That yields the full
  cross-acquisition matrix with subject-level rigour.
* Statistics are aggregated PER SUBJECT first, then across subjects. Frame
  counts are reported but never treated as independent samples.
* Dice is reported alongside a tolerance-band F1, because the target is a
  1-2 px contour where strict Dice punishes a one-pixel offset as total failure.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import platform
import random
import subprocess
import sys
import time

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))
from lumbar_markany.lumbar_data import (  # noqa: E402
    LumbarBoneSeg, load_index, dice_iou, tolerance_f1)
from lumbar_markany.unet import UNet  # noqa: E402

# Each test fold: 2 subjects with handheld data + 1 robotic-only subject.
FOLDS = [
    ["URS08", "URS16", "URS31"],
    ["URS26", "URS36", "URS51"],
    ["URS40", "URS45", "URS54"],
]
REGIMES = {"HUS": ["HUS"], "RUS": ["RUS"], "BOTH": ["HUS", "RUS"]}


def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)


class DiceBCE(nn.Module):
    """Dice + positively-weighted BCE.

    The positive class is ~0.1-0.6% of pixels, so unweighted BCE collapses to
    predicting all-background. pos_weight counteracts that; the Dice term keeps
    the overlap objective aligned with the reported metric.
    """
    def __init__(self, pos_weight=25.0, w_dice=0.6):
        super().__init__()
        self.bce = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(pos_weight))
        self.w = w_dice

    def forward(self, logits, target):
        b = self.bce(logits, target)
        p = torch.sigmoid(logits)
        inter = (p * target).sum((1, 2, 3))
        denom = p.sum((1, 2, 3)) + target.sum((1, 2, 3))
        d = 1 - ((2 * inter + 1.0) / (denom + 1.0)).mean()
        return (1 - self.w) * b + self.w * d


@torch.no_grad()
def evaluate(model, rows, root, size, dev, batch=16, thr=0.5, tol=2):
    ds = LumbarBoneSeg(rows, root=root, size=size)
    dl = DataLoader(ds, batch_size=batch, shuffle=False, num_workers=4, pin_memory=True)
    byuid = {r["uid"]: r for r in rows}
    per = []
    model.eval()
    for x, y, uids in dl:
        x = x.to(dev, non_blocking=True)
        with torch.autocast("cuda", enabled=(dev.type == "cuda")):
            logit = model(x)
        pred = (torch.sigmoid(logit.float()) > thr).cpu().numpy()[:, 0]
        targ = y.numpy()[:, 0] > 0.5
        for k, uid in enumerate(uids):
            d, j = dice_iou(pred[k], targ[k])
            f = tolerance_f1(pred[k], targ[k], tol)
            r = byuid[uid]
            per.append(dict(uid=uid, subject=r["subject"], scan=r["scan"],
                            modality=r["modality"], dice=d, iou=j, tol_f1=f,
                            gt_px=int(targ[k].sum()), pred_px=int(pred[k].sum()),
                            empty_label=bool(r["empty_label"])))
    return per


def summarise(per, tag):
    """Per-subject means first, then across subjects. Frames are not independent."""
    ann = [p for p in per if not p["empty_label"]]
    subs = sorted({p["subject"] for p in ann})
    rows = []
    for s in subs:
        sp = [p for p in ann if p["subject"] == s]
        rows.append(dict(subject=s, n_frames=len(sp),
                         dice=float(np.nanmean([p["dice"] for p in sp])),
                         iou=float(np.nanmean([p["iou"] for p in sp])),
                         tol_f1=float(np.nanmean([p["tol_f1"] for p in sp]))))
    emp = [p for p in per if p["empty_label"]]
    out = {
        "tag": tag,
        "n_subjects": len(subs), "n_frames_annotated": len(ann),
        "n_frames_empty_label": len(emp),
        "per_subject": rows,
        "subject_mean_dice": float(np.mean([r["dice"] for r in rows])) if rows else None,
        "subject_sd_dice": float(np.std([r["dice"] for r in rows])) if rows else None,
        "subject_median_dice": float(np.median([r["dice"] for r in rows])) if rows else None,
        "subject_min_dice": float(np.min([r["dice"] for r in rows])) if rows else None,
        "subject_max_dice": float(np.max([r["dice"] for r in rows])) if rows else None,
        "subject_mean_iou": float(np.mean([r["iou"] for r in rows])) if rows else None,
        "subject_mean_tol_f1": float(np.mean([r["tol_f1"] for r in rows])) if rows else None,
        "frame_mean_dice": float(np.nanmean([p["dice"] for p in ann])) if ann else None,
        # On frames the expert left empty, a perfect model predicts nothing.
        "empty_label_false_positive_rate": (
            float(np.mean([p["pred_px"] > 0 for p in emp])) if emp else None),
    }
    return out


def train_one(train_rows, size, dev, epochs, lr, batch, base, seed, log):
    set_seed(seed)
    ds = LumbarBoneSeg(train_rows, size=size, augment=True)
    dl = DataLoader(ds, batch_size=batch, shuffle=True, num_workers=4,
                    pin_memory=True, drop_last=True)
    model = UNet(1, 1, base=base).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    scaler = torch.amp.GradScaler("cuda", enabled=(dev.type == "cuda"))
    lossf = DiceBCE().to(dev)
    hist = []
    for ep in range(1, epochs + 1):
        model.train(); tot = nb = 0; t0 = time.time()
        for x, y, _ in dl:
            x, y = x.to(dev, non_blocking=True), y.to(dev, non_blocking=True)
            opt.zero_grad(set_to_none=True)
            with torch.autocast("cuda", enabled=(dev.type == "cuda")):
                loss = lossf(model(x), y)
            scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
            tot += float(loss); nb += 1
        sched.step()
        hist.append(dict(epoch=ep, loss=tot / max(nb, 1), sec=round(time.time() - t0, 1)))
        print(f"      ep {ep:2d}/{epochs} loss {tot/max(nb,1):.4f} ({time.time()-t0:.0f}s)",
              flush=True, file=log)
    return model, hist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/processed/kuleuven_lumbar")
    ap.add_argument("--out", default="experiments/exp005_lumbar_bone_seg")
    ap.add_argument("--epochs", type=int, default=14)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--base", type=int, default=32)
    ap.add_argument("--height", type=int, default=384)
    ap.add_argument("--width", type=int, default=192)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--folds", default="0,1,2")
    ap.add_argument("--regimes", default="HUS,RUS,BOTH")
    a = ap.parse_args()

    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "checkpoints").mkdir(exist_ok=True)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    size = (a.height, a.width)
    index = load_index(a.root)
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                             text=True).stdout.strip()
    except Exception:
        sha = "unknown"

    cfg = dict(vars(a), device=str(dev),
               gpu=torch.cuda.get_device_name(0) if dev.type == "cuda" else None,
               torch=torch.__version__, python=platform.python_version(),
               git_sha=sha, folds=FOLDS, n_index=len(index),
               dataset_doi="doi:10.48804/3XPCAE", licence="CC-BY-4.0",
               task="binary expert bone-surface segmentation (NOT a puncture target)")
    (out / "config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    want_folds = [int(x) for x in a.folds.split(",")]
    want_reg = [r.strip() for r in a.regimes.split(",")]
    results = []
    log = sys.stdout
    t0 = time.time()

    for fi in want_folds:
        test_subj = FOLDS[fi]
        train_subj = [s for s in sorted({r["subject"] for r in index}) if s not in test_subj]
        print(f"\n=== fold {fi}: test={test_subj}  train={train_subj} ===", flush=True)
        for reg in want_reg:
            mods = REGIMES[reg]
            tr = [r for r in index if r["subject"] in train_subj and r["modality"] in mods]
            print(f"   regime {reg:4s}: {len(tr)} training frames "
                  f"from {len({r['subject'] for r in tr})} subjects", flush=True)
            model, hist = train_one(tr, size, dev, a.epochs, a.lr, a.batch, a.base, a.seed, log)
            torch.save({"model": model.state_dict(), "fold": fi, "regime": reg, "config": cfg},
                       out / "checkpoints" / f"fold{fi}_{reg}.pt")
            for test_mod in ("HUS", "RUS"):
                te = [r for r in index if r["subject"] in test_subj and r["modality"] == test_mod]
                if not te:
                    continue
                per = evaluate(model, te, a.root, size, dev, batch=a.batch)
                s = summarise(per, f"fold{fi}_train{reg}_test{test_mod}")
                s.update(fold=fi, train_regime=reg, test_modality=test_mod,
                         train_subjects=train_subj, test_subjects=test_subj,
                         n_train_frames=len(tr), train_history=hist[-1])
                results.append(s)
                np.savez_compressed(out / f"per_frame_fold{fi}_{reg}_{test_mod}.npz",
                                    **{k: np.array([p[k] for p in per]) for k in
                                       ("uid", "subject", "modality", "dice", "iou",
                                        "tol_f1", "gt_px", "pred_px", "empty_label")})
                print(f"      -> test {test_mod}: subject-mean Dice {s['subject_mean_dice']:.4f} "
                      f"tolF1 {s['subject_mean_tol_f1']:.4f} "
                      f"(n_subj={s['n_subjects']}, n_frames={s['n_frames_annotated']})", flush=True)
            (out / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    (out / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\ntotal runtime {time.time()-t0:.0f}s -> {out}")


if __name__ == "__main__":
    main()
