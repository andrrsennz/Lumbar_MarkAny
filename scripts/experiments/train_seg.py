#!/usr/bin/env python3
"""
train_seg.py -- Baseline 10-class semantic segmentation on the JHU porcine
spinal-cord ultrasound dataset, using the OFFICIAL train/val/test split.

The official split was verified sweep-disjoint in experiments/exp001_leakage_audit
(no held-out image has a training neighbour at within-sweep similarity), so the
held-out metrics here are not inflated by near-duplicate frames. Animal-level
disjointness remains unverifiable from the public release, because no animal
identifier is distributed; that is reported as a limitation rather than
silently assumed.

Every artefact needed to reproduce a run is written into the experiment
directory: config.json, history.json, metrics.json, best.pt, per-image metrics.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import platform
import random
import sys
import time

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))
from lumbar_markany.data_jhu import JHUSpinalSeg, CLASSES, N_CLASSES  # noqa: E402
from lumbar_markany.unet import UNet  # noqa: E402


def set_seed(s):
    random.seed(s)
    np.random.seed(s)
    torch.manual_seed(s)
    torch.cuda.manual_seed_all(s)


def dice_iou(pred, targ, n_cls=N_CLASSES):
    """Per-class Dice/IoU for one image.

    Returns NaN for a class that is absent from BOTH prediction and ground
    truth: that case is undefined, and scoring it as 0 (or as 1) would bias the
    macro average. Rare classes are therefore averaged only over the images in
    which they are actually defined.
    """
    d = np.full(n_cls, np.nan, np.float64)
    j = np.full(n_cls, np.nan, np.float64)
    for c in range(n_cls):
        p, t = (pred == c), (targ == c)
        ps, ts = p.sum(), t.sum()
        if ps == 0 and ts == 0:
            continue
        inter = np.logical_and(p, t).sum()
        d[c] = 2.0 * inter / (ps + ts)
        j[c] = inter / np.logical_or(p, t).sum()
    return d, j


class DiceCE(nn.Module):
    def __init__(self, n_cls=N_CLASSES, w=0.5):
        super().__init__()
        self.ce = nn.CrossEntropyLoss()
        self.n = n_cls
        self.w = w

    def forward(self, logits, target):
        ce = self.ce(logits, target)
        p = torch.softmax(logits, 1)
        t = torch.nn.functional.one_hot(target, self.n).permute(0, 3, 1, 2).float()
        dims = (0, 2, 3)
        inter = (p * t).sum(dims)
        denom = p.sum(dims) + t.sum(dims)
        dice = 1 - ((2 * inter + 1.0) / (denom + 1.0)).mean()
        return (1 - self.w) * ce + self.w * dice


def evaluate(model, loader, dev, n_cls=N_CLASSES):
    model.eval()
    D, J, names = [], [], []
    with torch.no_grad():
        for x, y, nm in loader:
            x = x.to(dev, non_blocking=True)
            with torch.autocast("cuda", enabled=(dev.type == "cuda")):
                logit = model(x)
            pred = logit.float().argmax(1).cpu().numpy()
            targ = y.numpy()
            for k in range(pred.shape[0]):
                d, j = dice_iou(pred[k], targ[k], n_cls)
                D.append(d)
                J.append(j)
                names.append(nm[k])
    return np.array(D), np.array(J), names


def summarise(D, J):
    """Image-level macro Dice, then dataset-level statistics with bootstrap CI."""
    per_img = np.nanmean(D, axis=1)
    per_img_iou = np.nanmean(J, axis=1)
    rng = np.random.default_rng(0)
    boot = [np.nanmean(rng.choice(per_img, size=len(per_img), replace=True)) for _ in range(2000)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {
        "n_images": int(len(per_img)),
        "mean_dice": float(np.nanmean(per_img)),
        "sd_dice": float(np.nanstd(per_img)),
        "median_dice": float(np.nanmedian(per_img)),
        "iqr_dice": [float(np.nanpercentile(per_img, 25)), float(np.nanpercentile(per_img, 75))],
        "ci95_mean_dice_bootstrap": [float(lo), float(hi)],
        "mean_iou": float(np.nanmean(per_img_iou)),
        "per_class_dice": {
            CLASSES[c]: (None if np.all(np.isnan(D[:, c])) else float(np.nanmean(D[:, c])))
            for c in range(D.shape[1])
        },
        "per_class_iou": {
            CLASSES[c]: (None if np.all(np.isnan(J[:, c])) else float(np.nanmean(J[:, c])))
            for c in range(J.shape[1])
        },
        "per_class_n_images_defined": {
            CLASSES[c]: int((~np.isnan(D[:, c])).sum()) for c in range(D.shape[1])
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/extracted/jhu_segmentation/SegmentationDataset")
    ap.add_argument("--out", default="experiments/exp003_unet_baseline")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--base", type=int, default=32)
    ap.add_argument("--height", type=int, default=144)
    ap.add_argument("--width", type=int, default=352)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "predictions").mkdir(exist_ok=True)
    set_seed(a.seed)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    size = (a.height, a.width)
    tr = JHUSpinalSeg(a.root, "train", size=size, augment=True)
    va = JHUSpinalSeg(a.root, "val", size=size)
    te = JHUSpinalSeg(a.root, "test", size=size)
    ltr = DataLoader(tr, batch_size=a.batch, shuffle=True, num_workers=a.workers,
                     pin_memory=True, drop_last=True)
    lva = DataLoader(va, batch_size=a.batch, shuffle=False, num_workers=a.workers, pin_memory=True)
    lte = DataLoader(te, batch_size=a.batch, shuffle=False, num_workers=a.workers, pin_memory=True)

    model = UNet(1, N_CLASSES, base=a.base).to(dev)
    nparam = sum(p.numel() for p in model.parameters())
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=a.epochs)
    scaler = torch.amp.GradScaler("cuda", enabled=(dev.type == "cuda"))
    lossf = DiceCE()

    cfg = dict(vars(a), n_params=nparam, device=str(dev),
               gpu=(torch.cuda.get_device_name(0) if dev.type == "cuda" else None),
               torch=torch.__version__, python=platform.python_version(),
               n_train=len(tr), n_val=len(va), n_test=len(te), classes=CLASSES)
    (out / "config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    print(json.dumps({k: cfg[k] for k in ("device", "gpu", "n_params", "n_train", "n_val", "n_test")},
                     indent=1), flush=True)

    hist, best, t0 = [], -1.0, time.time()
    for ep in range(1, a.epochs + 1):
        model.train()
        tot, nb, te0 = 0.0, 0, time.time()
        for x, y, _ in ltr:
            x, y = x.to(dev, non_blocking=True), y.to(dev, non_blocking=True)
            opt.zero_grad(set_to_none=True)
            with torch.autocast("cuda", enabled=(dev.type == "cuda")):
                loss = lossf(model(x), y)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            tot += float(loss)
            nb += 1
        sched.step()
        Dv, Jv, _ = evaluate(model, lva, dev)
        vdice = float(np.nanmean(np.nanmean(Dv, axis=1)))
        hist.append({"epoch": ep, "train_loss": tot / max(nb, 1), "val_macro_dice": vdice,
                     "lr": sched.get_last_lr()[0], "sec": round(time.time() - te0, 1)})
        print(f"ep {ep:3d}/{a.epochs}  loss {tot/max(nb,1):.4f}  "
              f"val_dice {vdice:.4f}  ({time.time()-te0:.0f}s)", flush=True)
        if vdice > best:
            best = vdice
            torch.save({"model": model.state_dict(), "epoch": ep, "val_dice": vdice, "config": cfg},
                       out / "best.pt")
    (out / "history.json").write_text(json.dumps(hist, indent=1), encoding="utf-8")

    ck = torch.load(out / "best.pt", map_location=dev, weights_only=False)
    model.load_state_dict(ck["model"])
    Dt, Jt, nt = evaluate(model, lte, dev)
    Dv, Jv, nv = evaluate(model, lva, dev)
    np.savez_compressed(out / "predictions" / "per_image_metrics.npz",
                        test_dice=Dt, test_iou=Jt, test_names=np.array(nt),
                        val_dice=Dv, val_iou=Jv, val_names=np.array(nv))
    metrics = {"best_epoch": ck["epoch"], "best_val_macro_dice": ck["val_dice"],
               "total_train_seconds": round(time.time() - t0, 1),
               "val": summarise(Dv, Jv), "test": summarise(Dt, Jt)}
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("\n=== TEST ===")
    print(json.dumps(metrics["test"], indent=1))


if __name__ == "__main__":
    main()
