#!/usr/bin/env python3
"""
build_prediction_figures.py -- Render REAL model predictions on REAL human
lumbar ultrasound, including failures and uncertainty.

Uses the exp005 checkpoints. Every frame rendered is from a subject that was
HELD OUT of the model that predicts on it, so no figure shows a model scoring
its own training data.

Panels produced per frame:
    raw | expert bone-surface label | our prediction | error (TP/FP/FN) | uncertainty

Colour convention, used consistently everywhere:
    RED    expert annotation (ground truth)
    GREEN  our prediction
    white  true positive        red  false negative (missed)
    blue   false positive (spurious)
"""
from __future__ import annotations
import argparse
import csv
import json
import pathlib
import sys

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from lumbar_markany.lumbar_data import (  # noqa: E402
    LumbarBoneSeg, load_index, dice_iou, tolerance_f1, resize_mask_max)
from lumbar_markany.unet import UNet  # noqa: E402

VIS = pathlib.Path("visuals/ultrasound/real_human_lumbar")
EXP = pathlib.Path("experiments/exp005_lumbar_bone_seg")
FOLDS = [["URS08", "URS16", "URS31"], ["URS26", "URS36", "URS51"], ["URS40", "URS45", "URS54"]]

GT_C = (255, 45, 45)
PR_C = (40, 230, 90)
TP_C = (250, 250, 250)
FN_C = (255, 60, 60)
FP_C = (60, 140, 255)


def dil(m, k=1):
    out = m.copy()
    for _ in range(k):
        p = np.pad(out, 1, constant_values=False)
        out = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:] | out)
    return out


def to_rgb(g):
    return np.stack([g] * 3, -1)


def paint(gray, mask, colour):
    rgb = to_rgb(gray).copy()
    rgb[mask] = colour
    return rgb


def bar(w, text, h=24, bg=(20, 20, 20), fg=(238, 238, 238), size=13):
    im = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        f = ImageFont.load_default()
    d.text((6, (h - size) // 2 - 1), text, fill=fg, font=f)
    return np.array(im)


def hcat(ps, gap=5, bg=28):
    h = max(p.shape[0] for p in ps)
    o = []
    for p in ps:
        if p.shape[0] < h:
            p = np.pad(p, ((0, h - p.shape[0]), (0, 0), (0, 0)), constant_values=bg)
        o += [p, np.full((h, gap, 3), bg, np.uint8)]
    return np.hstack(o[:-1])


def vcat(ps, gap=5, bg=28):
    w = max(p.shape[1] for p in ps)
    o = []
    for p in ps:
        if p.shape[1] < w:
            p = np.pad(p, ((0, 0), (0, w - p.shape[1]), (0, 0)), constant_values=bg)
        o += [p, np.full((gap, w, 3), bg, np.uint8)]
    return np.vstack(o[:-1])


def heat(u):
    """Simple perceptually-ordered heat ramp for the uncertainty map."""
    u = np.clip((u - u.min()) / max(1e-6, u.max() - u.min()), 0, 1)
    r = np.clip(1.5 * u, 0, 1)
    g = np.clip(1.5 * u - 0.4, 0, 1)
    b = np.clip(2.0 * (0.5 - np.abs(u - 0.25)), 0, 1)
    return (np.stack([r, g, b], -1) * 255).astype(np.uint8)


@torch.no_grad()
def predict(model, uid, root, size, dev, mc=10):
    ds = LumbarBoneSeg([{"uid": uid, "empty_label": False}], root=root, size=size)
    x, _, _ = ds[0]
    xb = x[None].to(dev)
    model.eval()
    logit = model(xb)
    prob = torch.sigmoid(logit.float())[0, 0].cpu().numpy()
    # MC-dropout uncertainty: dropout back on, BatchNorm left in eval
    for m in model.modules():
        if isinstance(m, (torch.nn.Dropout, torch.nn.Dropout2d)):
            m.train()
    ps = []
    for _ in range(mc):
        ps.append(torch.sigmoid(model(xb).float())[0, 0].cpu().numpy())
    model.eval()
    P = np.stack(ps)
    return prob, P.std(0), x.numpy()[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/processed/kuleuven_lumbar")
    ap.add_argument("--regime", default="BOTH")
    ap.add_argument("--per-fold", type=int, default=8)
    ap.add_argument("--height", type=int, default=384)
    ap.add_argument("--width", type=int, default=192)
    a = ap.parse_args()

    for d in ("predictions", "prediction_overlays", "failures", "uncertainty",
              "publication_candidates"):
        (VIS / d).mkdir(parents=True, exist_ok=True)

    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    size = (a.height, a.width)
    index = load_index(a.root)
    rows = []

    for fi, test_subj in enumerate(FOLDS):
        ck = EXP / "checkpoints" / f"fold{fi}_{a.regime}.pt"
        if not ck.exists():
            print(f"  skip fold {fi}: no checkpoint"); continue
        st = torch.load(ck, map_location=dev, weights_only=False)
        model = UNet(1, 1, base=st["config"]["base"]).to(dev)
        model.load_state_dict(st["model"]); model.eval()

        cand = [r for r in index if r["subject"] in test_subj and not r["empty_label"]]
        # score every held-out frame, then sample across the quality range
        scored = []
        for r in cand[::7]:                       # stride for speed
            prob, unc, img = predict(model, r["uid"], a.root, size, dev, mc=0 if False else 6)
            gt = resize_mask_max(
                np.asarray(Image.open(pathlib.Path(a.root) / "masks" / f"{r['uid']}.png")) > 127,
                size)
            pr = prob > 0.5
            d, _ = dice_iou(pr, gt)
            scored.append((r, float(d if d == d else 0.0), prob, unc, img, gt, pr))
        if not scored:
            continue
        scored.sort(key=lambda t: t[1])
        n = len(scored)
        picks = ([("failure", scored[i]) for i in range(min(3, n))] +
                 [("typical", scored[n // 2]), ("typical", scored[int(n * 0.65)])] +
                 [("best", scored[-1]), ("best", scored[-2])])

        for kind, (r, d, prob, unc, img, gt, pr) in picks[:a.per_fold]:
            uid = r["uid"]
            gray = (img * 255).astype(np.uint8)
            tp, fn, fp = (pr & gt), (~pr & gt), (pr & ~gt)
            err = to_rgb(gray).copy()
            err[dil(fp)] = FP_C; err[dil(fn)] = FN_C; err[dil(tp)] = TP_C
            tf = tolerance_f1(pr, gt, 2)
            tag = (f"{r['subject']} {r['scan']} ({r['modality']}) frame {r['frame_index']}  "
                   f"Dice {d:.3f}  tolF1 {tf:.3f}  [held out of fold {fi}]")

            panels = [
                vcat([bar(gray.shape[1], "raw human lumbar US"), to_rgb(gray)]),
                vcat([bar(gray.shape[1], "expert bone surface"), paint(gray, dil(gt), GT_C)]),
                vcat([bar(gray.shape[1], "our prediction"), paint(gray, dil(pr), PR_C)]),
                vcat([bar(gray.shape[1], "error  TP/FN/FP"), err]),
                vcat([bar(gray.shape[1], "MC-dropout uncertainty"), heat(unc)]),
            ]
            fig = vcat([bar(sum(p.shape[1] for p in panels) + 20, tag, h=26), hcat(panels)])
            Image.fromarray(fig).save(VIS / "prediction_overlays" / f"{uid}.png")
            Image.fromarray(paint(gray, dil(pr), PR_C)).save(VIS / "predictions" / f"{uid}.png")
            Image.fromarray(heat(unc)).save(VIS / "uncertainty" / f"{uid}.png")
            if kind == "failure":
                Image.fromarray(fig).save(VIS / "failures" / f"{uid}_dice{d:.3f}.png")
            rows.append(dict(uid=uid, subject=r["subject"], scan=r["scan"],
                             modality=r["modality"], fold=fi, regime=a.regime,
                             kind=kind, dice=round(d, 4), tol_f1=round(tf, 4),
                             gt_px=int(gt.sum()), pred_px=int(pr.sum()),
                             mean_uncertainty=round(float(unc.mean()), 6)))
        print(f"  fold {fi}: rendered {len(picks[:a.per_fold])} frames from {test_subj}", flush=True)

    if rows:
        with open(VIS / "PREDICTION_SELECTION.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
    print(f"wrote {len(rows)} prediction figures -> {VIS}")


if __name__ == "__main__":
    main()
