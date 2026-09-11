#!/usr/bin/env python3
"""
exp006 -- Can the model tell when it is wrong, on REAL HUMAN LUMBAR ultrasound?

V1 answered this on porcine intraoperative data (exp004). That result cannot
carry a human lumbar claim, so the question is asked again here on the real
thing, using the exp005 checkpoints and strictly held-out subjects.

The clinically meaningful form of the question:
    can the system detect that its lumbar interpretation is unreliable, and ask
    for repositioning or clinician review, instead of silently emitting a bad
    result?

Method: Monte-Carlo dropout (bottleneck Dropout2d re-enabled, BatchNorm kept in
eval). Two uncertainty summaries -- mean predictive entropy and mean inter-pass
standard deviation -- are correlated against the Dice each frame actually
achieved. Reported per fold, per modality, and per subject.

Also reported: the coverage-vs-performance curve (abstain on the most uncertain
X% and measure what remains), and behaviour on the 3% of frames where the
expert annotated NOTHING -- there, a good model should predict nothing.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import sys

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))
from lumbar_markany.lumbar_data import (  # noqa: E402
    LumbarBoneSeg, load_index, dice_iou, tolerance_f1)
from lumbar_markany.unet import UNet  # noqa: E402

FOLDS = [["URS08", "URS16", "URS31"], ["URS26", "URS36", "URS51"], ["URS40", "URS45", "URS54"]]


def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = ~(np.isnan(a) | np.isnan(b))
    a, b = a[ok], b[ok]
    if a.size < 3:
        return float("nan")
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    den = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / den) if den else float("nan")


def enable_dropout(model):
    n = 0
    for m in model.modules():
        if isinstance(m, (torch.nn.Dropout, torch.nn.Dropout2d)):
            m.train(); n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/processed/kuleuven_lumbar")
    ap.add_argument("--exp5", default="experiments/exp005_lumbar_bone_seg")
    ap.add_argument("--out", default="experiments/exp006_lumbar_uncertainty")
    ap.add_argument("--regime", default="BOTH")
    ap.add_argument("--passes", type=int, default=10)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--height", type=int, default=384)
    ap.add_argument("--width", type=int, default=192)
    a = ap.parse_args()

    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    size = (a.height, a.width)
    index = load_index(a.root)
    allrec = []

    for fi, test_subj in enumerate(FOLDS):
        ck = pathlib.Path(a.exp5) / "checkpoints" / f"fold{fi}_{a.regime}.pt"
        if not ck.exists():
            print(f"skip fold {fi}: no checkpoint at {ck}"); continue
        st = torch.load(ck, map_location=dev, weights_only=False)
        model = UNet(1, 1, base=st["config"]["base"]).to(dev)
        model.load_state_dict(st["model"]); model.eval()
        nd = enable_dropout(model)

        rows = [r for r in index if r["subject"] in test_subj]
        ds = LumbarBoneSeg(rows, root=a.root, size=size)
        dl = DataLoader(ds, batch_size=a.batch, shuffle=False, num_workers=4)
        byuid = {r["uid"]: r for r in rows}
        print(f"fold {fi}: {len(rows)} held-out frames from {test_subj} "
              f"(dropout layers active: {nd})", flush=True)

        with torch.no_grad():
            for x, y, uids in dl:
                x = x.to(dev)
                ps = []
                for _ in range(a.passes):
                    with torch.autocast("cuda", enabled=(dev.type == "cuda")):
                        ps.append(torch.sigmoid(model(x).float()))
                P = torch.stack(ps)                       # (T,B,1,H,W)
                mean_p = P.mean(0)
                ent = -(mean_p.clamp(1e-6, 1 - 1e-6).log() * mean_p
                        + (1 - mean_p).clamp(1e-6, 1 - 1e-6).log() * (1 - mean_p))
                sd = P.std(0)
                pred = (mean_p > 0.5).cpu().numpy()[:, 0]
                targ = y.numpy()[:, 0] > 0.5
                e = ent.cpu().numpy()[:, 0]
                s = sd.cpu().numpy()[:, 0]
                for k, uid in enumerate(uids):
                    d, j = dice_iou(pred[k], targ[k])
                    r = byuid[uid]
                    allrec.append(dict(
                        uid=uid, fold=fi, subject=r["subject"], scan=r["scan"],
                        modality=r["modality"], empty_label=bool(r["empty_label"]),
                        dice=float(d) if d == d else float("nan"),
                        tol_f1=float(tolerance_f1(pred[k], targ[k], 2)),
                        entropy=float(e[k].mean()), pass_sd=float(s[k].mean()),
                        gt_px=int(targ[k].sum()), pred_px=int(pred[k].sum())))

    if not allrec:
        sys.exit("no checkpoints found -- run exp005 first")

    ann = [r for r in allrec if not r["empty_label"] and r["dice"] == r["dice"]]
    emp = [r for r in allrec if r["empty_label"]]
    dice = np.array([r["dice"] for r in ann])
    ent = np.array([r["entropy"] for r in ann])
    psd = np.array([r["pass_sd"] for r in ann])

    # abstention: decline the most uncertain X%, measure what remains
    order = np.argsort(-ent)
    abst = {}
    for frac in (0.05, 0.10, 0.20, 0.30):
        k = int(len(dice) * frac)
        keep = np.ones(len(dice), bool); keep[order[:k]] = False
        abst[f"{int(frac*100)}%"] = dict(
            n_declined=int(k),
            dice_on_retained=float(dice[keep].mean()),
            dice_on_declined=float(dice[~keep].mean()) if k else None,
            improvement=float(dice[keep].mean() - dice.mean()))

    per_sub, per_mod = {}, {}
    for s in sorted({r["subject"] for r in ann}):
        sub = [r for r in ann if r["subject"] == s]
        per_sub[s] = dict(n=len(sub),
                          spearman_entropy_vs_dice=spearman([r["entropy"] for r in sub],
                                                            [r["dice"] for r in sub]),
                          mean_dice=float(np.mean([r["dice"] for r in sub])))
    for m in ("HUS", "RUS"):
        sub = [r for r in ann if r["modality"] == m]
        if sub:
            per_mod[m] = dict(n=len(sub),
                              spearman_entropy_vs_dice=spearman([r["entropy"] for r in sub],
                                                                [r["dice"] for r in sub]),
                              mean_dice=float(np.mean([r["dice"] for r in sub])),
                              mean_entropy=float(np.mean([r["entropy"] for r in sub])))

    res = dict(
        regime=a.regime, mc_passes=a.passes,
        n_frames_scored=len(allrec), n_annotated=len(ann), n_empty_label=len(emp),
        spearman_entropy_vs_dice=spearman(ent, dice),
        spearman_pass_sd_vs_dice=spearman(psd, dice),
        mean_dice=float(dice.mean()),
        abstention=abst, per_subject=per_sub, per_modality=per_mod,
        empty_label_behaviour=dict(
            n=len(emp),
            frac_predicting_something=float(np.mean([r["pred_px"] > 0 for r in emp])) if emp else None,
            mean_entropy=float(np.mean([r["entropy"] for r in emp])) if emp else None,
            mean_entropy_on_annotated=float(ent.mean())),
        caveat=("Real human transcutaneous lumbar ultrasound, subject-held-out. Validates that "
                "uncertainty tracks error for BONE-SURFACE perception. It is not a safety claim, "
                "the model is not calibrated for clinical use, and it says nothing about "
                "puncture targeting."))
    (out / "metrics.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    np.savez_compressed(out / "per_frame.npz",
                        **{k: np.array([r[k] for r in allrec]) for k in
                           ("uid", "subject", "modality", "fold", "dice", "tol_f1",
                            "entropy", "pass_sd", "gt_px", "pred_px", "empty_label")})

    print(json.dumps({k: res[k] for k in
                      ("n_annotated", "mean_dice", "spearman_entropy_vs_dice",
                       "spearman_pass_sd_vs_dice")}, indent=1))
    print("abstention:", json.dumps(abst, indent=1))
    print("per modality:", json.dumps(per_mod, indent=1))
    print(f"wrote {out/'metrics.json'}")


if __name__ == "__main__":
    main()
