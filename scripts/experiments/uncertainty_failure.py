#!/usr/bin/env python3
"""
uncertainty_failure.py -- exp004: can the trained model tell when it is wrong?

Two questions, both clinically motivated:

  Q1  Does a cheap uncertainty signal correlate with actual error?
      If it does not, an "AI confidence" display is decoration and would be
      actively dangerous in a guidance system.

  Q2  What do the worst cases have in common?
      A failure taxonomy computed from image statistics, not from eyeballing.

Method
------
Monte-Carlo dropout: the U-Net keeps its bottleneck Dropout2d active at test
time, so T stochastic forward passes give a predictive distribution per pixel.
We summarise it two ways -- mean predictive entropy, and mean disagreement
between passes -- and correlate each against the per-image Dice that the same
image actually achieved.

The headline number is Spearman rho between uncertainty and error. A useful
abstention signal needs a clearly negative rho (more uncertainty -> lower Dice).
We report it whatever it is.

Everything here runs on porcine intraoperative spinal-cord data. It validates
the MECHANISM, not any clinical claim.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import sys

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))
from lumbar_markany.data_jhu import JHUSpinalSeg, CLASSES, N_CLASSES  # noqa: E402
from lumbar_markany.unet import UNet  # noqa: E402


def enable_dropout(model: nn.Module) -> int:
    """Put ONLY dropout layers back into train mode; BatchNorm stays in eval."""
    n = 0
    for m in model.modules():
        if isinstance(m, (nn.Dropout, nn.Dropout2d)):
            m.train()
            n += 1
    return n


def dice_per_image(pred, targ, n_cls=N_CLASSES):
    d = np.full(n_cls, np.nan)
    for c in range(n_cls):
        p, t = pred == c, targ == c
        ps, ts = p.sum(), t.sum()
        if ps == 0 and ts == 0:
            continue
        d[c] = 2.0 * np.logical_and(p, t).sum() / (ps + ts)
    return np.nanmean(d)


def spearman(a, b):
    """Rank correlation without a SciPy dependency."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = ~(np.isnan(a) | np.isnan(b))
    a, b = a[ok], b[ok]
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    den = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / den) if den else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/extracted/jhu_segmentation/SegmentationDataset")
    ap.add_argument("--ckpt", default="experiments/exp003_unet_baseline/best.pt")
    ap.add_argument("--out", default="experiments/exp004_uncertainty_failure")
    ap.add_argument("--passes", type=int, default=10)
    ap.add_argument("--batch", type=int, default=8)
    a = ap.parse_args()

    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ck = torch.load(a.ckpt, map_location=dev, weights_only=False)
    cfg = ck["config"]
    size = (cfg["height"], cfg["width"])

    model = UNet(1, N_CLASSES, base=cfg["base"]).to(dev)
    model.load_state_dict(ck["model"])
    model.eval()
    ndrop = enable_dropout(model)
    print(f"device={dev} checkpoint_epoch={ck['epoch']} dropout_layers_active={ndrop}", flush=True)

    te = JHUSpinalSeg(a.root, "test", size=size)
    loader = DataLoader(te, batch_size=a.batch, shuffle=False, num_workers=2)

    names, dices, entropies, disagreements = [], [], [], []
    img_mean, img_std = [], []

    with torch.no_grad():
        for x, y, nm in loader:
            x = x.to(dev)
            probs = []
            for _ in range(a.passes):
                with torch.autocast("cuda", enabled=(dev.type == "cuda")):
                    probs.append(torch.softmax(model(x).float(), 1))
            P = torch.stack(probs)                    # (T, B, C, H, W)
            mean_p = P.mean(0)                        # (B, C, H, W)
            ent = -(mean_p.clamp_min(1e-8) * mean_p.clamp_min(1e-8).log()).sum(1)  # (B,H,W)
            # fraction of passes disagreeing with the modal prediction
            hard = P.argmax(2)                        # (T, B, H, W)
            modal = mean_p.argmax(1, keepdim=True)    # (B,1,H,W)
            dis = (hard != modal.squeeze(1)).float().mean(0)   # (B,H,W)

            pred = modal.squeeze(1).cpu().numpy()
            targ = y.numpy()
            xc = x.cpu().numpy()[:, 0]
            for k in range(pred.shape[0]):
                names.append(nm[k])
                dices.append(dice_per_image(pred[k], targ[k]))
                entropies.append(float(ent[k].mean()))
                disagreements.append(float(dis[k].mean()))
                img_mean.append(float(xc[k].mean()))
                img_std.append(float(xc[k].std()))

    dices = np.array(dices)
    ent = np.array(entropies)
    dis = np.array(disagreements)

    rho_ent = spearman(ent, dices)
    rho_dis = spearman(dis, dices)

    # --- abstention analysis: if we decline the most uncertain X%, how much
    #     does Dice improve on what remains?
    abstain = {}
    order = np.argsort(-ent)                      # most uncertain first
    for frac in (0.05, 0.10, 0.20, 0.30):
        k = int(len(dices) * frac)
        keep = np.ones(len(dices), bool)
        keep[order[:k]] = False
        abstain[f"{int(frac*100)}%"] = {
            "n_declined": int(k),
            "dice_on_retained": float(np.nanmean(dices[keep])),
            "dice_on_declined": float(np.nanmean(dices[~keep])),
            "improvement": float(np.nanmean(dices[keep]) - np.nanmean(dices)),
        }

    # --- failure taxonomy over the worst decile, from image statistics
    worst = np.argsort(dices)[:max(1, len(dices) // 10)]
    best = np.argsort(dices)[-max(1, len(dices) // 10):]
    tax = {
        "worst_decile_n": int(len(worst)),
        "worst_decile_mean_dice": float(np.nanmean(dices[worst])),
        "best_decile_mean_dice": float(np.nanmean(dices[best])),
        "worst_decile_mean_image_intensity": float(np.mean(np.array(img_mean)[worst])),
        "best_decile_mean_image_intensity": float(np.mean(np.array(img_mean)[best])),
        "worst_decile_mean_image_contrast_sd": float(np.mean(np.array(img_std)[worst])),
        "best_decile_mean_image_contrast_sd": float(np.mean(np.array(img_std)[best])),
        "worst_decile_mean_entropy": float(np.mean(ent[worst])),
        "best_decile_mean_entropy": float(np.mean(ent[best])),
        "spearman_dice_vs_image_contrast": spearman(np.array(img_std), dices),
        "spearman_dice_vs_image_intensity": spearman(np.array(img_mean), dices),
    }

    res = {
        "checkpoint_epoch": int(ck["epoch"]),
        "mc_passes": a.passes,
        "n_test_images": int(len(dices)),
        "mean_dice_mc": float(np.nanmean(dices)),
        "spearman_entropy_vs_dice": rho_ent,
        "spearman_disagreement_vs_dice": rho_dis,
        "abstention": abstain,
        "failure_taxonomy": tax,
        "interpretation": (
            "A clearly negative Spearman rho means the uncertainty signal tracks real "
            "error and could support abstention. A rho near zero would mean the signal "
            "is decorative and must not be displayed as confidence."),
        "caveat": ("Porcine, intraoperative, post-laminectomy data. This validates the "
                   "uncertainty MECHANISM only. It is not a clinical safety claim and "
                   "the model is not safety-certified."),
    }
    (out / "metrics.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    np.savez_compressed(out / "per_image.npz", names=np.array(names), dice=dices,
                        entropy=ent, disagreement=dis,
                        img_mean=np.array(img_mean), img_std=np.array(img_std))

    print(json.dumps({k: res[k] for k in
                      ("n_test_images", "mean_dice_mc", "spearman_entropy_vs_dice",
                       "spearman_disagreement_vs_dice")}, indent=1))
    print("\nabstention:", json.dumps(abstain, indent=1))
    print("\nfailure taxonomy:", json.dumps(tax, indent=1))
    print(f"\nwrote {out/'metrics.json'}")


if __name__ == "__main__":
    main()
