"""Dataset for REAL human lumbar ultrasound bone-surface segmentation.

Source: KU Leuven / Balgrist, doi:10.48804/3XPCAE (CC-BY-4.0), built by
tools/build_lumbar_dataset.py from the `US/US_labels` archives.

TASK
----
Binary segmentation of EXPERT-ANNOTATED VISIBLE BONE SURFACE. This is anatomy
perception. It is not a puncture target, an entry point, or a trajectory, and
nothing downstream may describe it as one.

TWO PROPERTIES THAT SHAPE EVERY DESIGN CHOICE HERE
--------------------------------------------------
1. The positive class is a THIN CONTOUR occupying ~0.1-0.6% of sector pixels.
   Aggressive downsampling destroys it, and plain Dice is a harsh, high-variance
   metric on structures one or two pixels wide. Both are handled explicitly:
   masks are resized with MAX-pooling so a thin line survives, and evaluation
   reports a tolerance-band F1 alongside Dice.
2. ~3% of frames carry an EMPTY expert label: the annotator identified no bone
   surface. Those are kept for training (they teach "nothing visible here") but
   Dice is undefined on them and they are excluded from Dice averaging rather
   than silently scored 0 or 1.
"""
from __future__ import annotations

import csv
import pathlib

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset


def load_index(root="data/processed/kuleuven_lumbar"):
    rows = list(csv.DictReader(open(pathlib.Path(root) / "index.csv", encoding="utf-8")))
    for r in rows:
        r["bone_px"] = int(r["bone_px"])
        r["frame_index"] = int(r["frame_index"])
        r["empty_label"] = r["empty_label"] == "True"
        r["label_px_outside_sector"] = int(r.get("label_px_outside_sector", 0) or 0)
    return rows


def subjects_of(rows):
    return sorted({r["subject"] for r in rows})


def resize_mask_max(m: np.ndarray, size_hw) -> np.ndarray:
    """Downsample a binary mask by MAX over each block.

    PIL NEAREST would drop a 1-2 px contour almost entirely; max-pooling keeps
    the structure connected, which is what the task actually needs.

    Implemented with `np.maximum.reduceat` rather than a Python loop: this runs
    for every sample of every epoch, and the naive version was the single
    biggest throughput bottleneck in training.
    """
    H, W = size_hw
    h, w = m.shape
    if (h, w) == (H, W):
        return m.astype(bool)
    ys = np.minimum((np.arange(H) * h) // H, h - 1)
    xs = np.minimum((np.arange(W) * w) // W, w - 1)
    a = m.astype(np.uint8)
    a = np.maximum.reduceat(a, ys, axis=0)
    a = np.maximum.reduceat(a, xs, axis=1)
    return a.astype(bool)


class LumbarBoneSeg(Dataset):
    def __init__(self, rows, root="data/processed/kuleuven_lumbar",
                 size=(384, 192), augment=False, drop_empty=False):
        self.root = pathlib.Path(root)
        self.rows = [r for r in rows if not (drop_empty and r["empty_label"])]
        self.size = size
        self.augment = augment

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        r = self.rows[i]
        H, W = self.size
        img = Image.open(self.root / "images" / f"{r['uid']}.png").convert("L")
        x = np.asarray(img.resize((W, H), Image.BILINEAR), dtype=np.float32) / 255.0
        m = np.asarray(Image.open(self.root / "masks" / f"{r['uid']}.png")) > 127
        y = resize_mask_max(m, (H, W))

        if self.augment:
            rng = np.random
            if rng.rand() < 0.5:                       # left-right flip
                x = x[:, ::-1].copy(); y = y[:, ::-1].copy()
            if rng.rand() < 0.5:                       # gain / brightness
                x = np.clip(x * rng.uniform(0.82, 1.18) + rng.uniform(-0.08, 0.08), 0, 1)
            if rng.rand() < 0.3:                       # speckle-ish noise
                x = np.clip(x + rng.normal(0, 0.02, x.shape).astype(np.float32), 0, 1)

        return (torch.from_numpy(x.astype(np.float32))[None],
                torch.from_numpy(y.astype(np.float32))[None],
                r["uid"])


def dice_iou(pred: np.ndarray, targ: np.ndarray):
    """Binary Dice/IoU for one frame. NaN when the frame has no ground truth
    AND no prediction -- undefined, not zero."""
    ps, ts = pred.sum(), targ.sum()
    if ps == 0 and ts == 0:
        return np.nan, np.nan
    inter = np.logical_and(pred, targ).sum()
    return (2.0 * inter / (ps + ts), inter / np.logical_or(pred, targ).sum())


def tolerance_f1(pred: np.ndarray, targ: np.ndarray, tol: int = 2):
    """F1 where a predicted pixel counts as correct if any ground-truth pixel
    lies within `tol` pixels, and vice versa.

    For a 1-2 px contour this is far more informative than strict Dice: a
    prediction that traces the right surface one pixel off scores ~0 on Dice
    but is clinically indistinguishable from a hit.
    """
    if pred.sum() == 0 and targ.sum() == 0:
        return np.nan
    if pred.sum() == 0 or targ.sum() == 0:
        return 0.0

    def dil(m, k):
        out = m.copy()
        for _ in range(k):
            p = np.pad(out, 1, constant_values=False)
            out = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:] | out)
        return out

    tp_p = np.logical_and(pred, dil(targ, tol)).sum()      # predictions near GT
    tp_t = np.logical_and(targ, dil(pred, tol)).sum()      # GT covered by prediction
    prec = tp_p / pred.sum()
    rec = tp_t / targ.sum()
    return 0.0 if (prec + rec) == 0 else float(2 * prec * rec / (prec + rec))
