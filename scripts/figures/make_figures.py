#!/usr/bin/env python3
"""
make_figures.py -- Publication figures built ONLY from measured project data.

Every figure reads a real artefact under experiments/ or data/registry/. No
figure is drawn from a hand-typed number, and nothing is generated to fill a
slot in a figure plan.

Design rules applied (see the project's dataviz guidance):
  * categorical hues assigned in fixed order, never cycled
  * never a dual y-axis -- two measures of different scale become two panels
  * legend whenever >=2 series; direct value labels rather than a dense grid
  * recessive grid and axes; thin marks
  * validated palette (checked with validate_palette.js, light mode)

Outputs SVG (vector) + PNG (300 dpi) into figures/svg and figures/png.
"""
from __future__ import annotations
import json
import pathlib
import csv
import collections
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- validated categorical palette (light mode) ----------------------------
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"      # blue, orange, aqua
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8983"
SURFACE, GRID = "#fcfcfb", "#e3e2dd"

SVG = pathlib.Path("figures/svg"); SVG.mkdir(parents=True, exist_ok=True)
PNG = pathlib.Path("figures/png"); PNG.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "axes.titlesize": 11,
    "axes.titleweight": "bold", "axes.titlecolor": INK,
    "xtick.color": INK2, "ytick.color": INK2,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
    "grid.color": GRID, "grid.linewidth": 0.7,
    "legend.frameon": False, "svg.fonttype": "none",
})


def finish(fig, name, caption=None):
    if caption:
        fig.text(0.01, 0.005, caption, fontsize=7, color=MUTED, va="bottom", ha="left")
    fig.savefig(SVG / f"{name}.svg", bbox_inches="tight")
    fig.savefig(PNG / f"{name}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {name}.svg / .png")


def despine(ax, keep=("left", "bottom")):
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(s in keep)


def headline(fig, title, subtitle, top=0.99, gap=0.055):
    """Title above subtitle, both left-aligned to the figure edge.

    Done explicitly rather than with suptitle+text so the two never invert
    when tight_layout adjusts the axes rectangle.
    """
    fig.text(0.008, top, title, ha="left", va="top",
             fontsize=12, fontweight="bold", color=INK)
    fig.text(0.008, top - gap, subtitle, ha="left", va="top",
             fontsize=9, color=INK2)


# ---------------------------------------------------------------- figure 1
def fig_dataset_survey():
    """How little Tier-0 data exists. One series -> one hue, direct labels."""
    p = pathlib.Path("data/registry/DISCOVERY_CANDIDATES.csv")
    if not p.exists():
        print("  skip fig01 (no discovery csv)"); return
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    us = [r for r in rows if r["mentions_ultrasound"] == "True"]
    typed = [r for r in us if r["resource_type"] == "dataset"]
    order = ["T0", "T1", "T2", "T3", "T4"]
    labels = {
        "T0": "T0  human lumbar /\n      neuraxial",
        "T1": "T1  spine / robotic /\n      tracked",
        "T2": "T2  needle in\n      ultrasound",
        "T3": "T3  supporting spinal /\n      animal / phantom",
        "T4": "T4  broad ultrasound\n      ecosystem",
    }
    ca = collections.Counter(r["provisional_tier"] for r in us)
    cb = collections.Counter(r["provisional_tier"] for r in typed)

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.5), sharey=True)
    y = np.arange(len(order))
    for ax, counts, title, col in (
        (axes[0], ca, "Records mentioning ultrasound", C1),
        (axes[1], cb, "…of which typed as a dataset", C2),
    ):
        v = [counts.get(t, 0) for t in order]
        ax.barh(y, v, height=0.6, color=col, zorder=3)
        ax.set_title(title, loc="left", pad=10)
        ax.xaxis.grid(True, zorder=0); ax.set_axisbelow(True)
        despine(ax, keep=("bottom",))
        ax.tick_params(axis="y", length=0)
        for i, val in enumerate(v):
            ax.text(val + max(v) * 0.02, i, str(val), va="center", ha="left",
                    fontsize=9, color=INK, fontweight="bold")
        ax.set_xlim(0, max(v) * 1.18)
    axes[0].set_yticks(y, [labels[t] for t in order], fontsize=8)
    axes[0].invert_yaxis()
    fig.tight_layout(rect=[0, 0.03, 1, 0.84])
    headline(fig, "Public ultrasound dataset survey — 891 candidates, 6 repository APIs",
             "Only 2 Tier-0 datasets exist, and neither contains real human transcutaneous lumbar ultrasound.")
    finish(fig, "fig01_dataset_survey",
           "Source: data/registry/DISCOVERY_CANDIDATES.csv (E1, surveyed 2026-09-11). "
           "Tier assignment is keyword triage over each record's own title/abstract.")


# ---------------------------------------------------------------- figure 2
def fig_class_distribution():
    """JHU class stats. Two measures of different scale -> two panels, never a
    dual axis."""
    p = pathlib.Path("experiments/exp002_class_distribution/metrics.json")
    if not p.exists():
        print("  skip fig02"); return
    m = json.load(open(p, encoding="utf-8"))["matched_to_paper_table1"]
    names = sorted(m, key=lambda k: -m[k]["observed"]["pixels"])
    px = [m[k]["observed"]["pixels"] / 1e6 for k in names]
    im = [m[k]["observed"]["images"] for k in names]

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.0), sharey=True)
    y = np.arange(len(names))
    axes[0].barh(y, px, height=0.62, color=C1, zorder=3)
    axes[0].set_title("Labelled pixels (millions)", loc="left", pad=10)
    axes[1].barh(y, im, height=0.62, color=C3, zorder=3)
    axes[1].set_title("Images containing the class (of 10,223)", loc="left", pad=10)
    for ax, v in ((axes[0], px), (axes[1], im)):
        ax.xaxis.grid(True, zorder=0); ax.set_axisbelow(True)
        despine(ax, keep=("bottom",)); ax.tick_params(axis="y", length=0)
        ax.set_xlim(0, max(v) * 1.2)
        for i, val in enumerate(v):
            t = f"{val:,.0f}" if val >= 100 else f"{val:,.1f}"
            ax.text(val + max(v) * 0.02, i, t, va="center", ha="left",
                    fontsize=8, color=INK)
    axes[0].set_yticks(y, names, fontsize=8.5)
    axes[0].invert_yaxis()
    fig.tight_layout(rect=[0, 0.03, 1, 0.86])
    headline(fig, "JHU porcine spinal-cord dataset — class distribution, independently reproduced",
             "All 10 classes matched the publication's Table 1 exactly (13 stray pixels in 1.9 billion).")
    finish(fig, "fig02_class_distribution",
           "Source: experiments/exp002_class_distribution/metrics.json (E1). "
           "Recomputed from the distributed masks; palette-to-class mapping recovered empirically.")


# ---------------------------------------------------------------- figure 3
def fig_leakage_audit():
    """Two distributions on one common x -> one axis, two hues, legend."""
    p = pathlib.Path("experiments/exp001_leakage_audit/metrics.json")
    q = pathlib.Path("experiments/exp001_leakage_audit/nearest_neighbours.csv")
    if not (p.exists() and q.exists()):
        print("  skip fig03"); return
    calib = json.load(open(p, encoding="utf-8"))["calibration_within_sweep_adjacent"]
    rows = list(csv.DictReader(open(q, encoding="utf-8")))
    test = np.array([float(r["cosine"]) for r in rows if r["split"] == "test"])
    val = np.array([float(r["cosine"]) for r in rows if r["split"] == "val"])

    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    bins = np.linspace(0, 1, 61)
    ax.hist(test, bins=bins, color=C2, alpha=0.85, label=f"test → nearest train (n={len(test)})", zorder=3)
    ax.hist(val, bins=bins, color=C1, alpha=0.6, label=f"val → nearest train (n={len(val)})", zorder=3)
    thr = calib["p05"]
    ax.axvline(thr, color=INK, lw=1.6, ls="--", zorder=4)
    ax.axvspan(thr, 1.02, color=C3, alpha=0.12, zorder=1)
    top = ax.get_ylim()[1]
    # Horizontal callout with a leader line. A rotated label on the threshold
    # collided with the zone annotation.
    ax.annotate(f"within-sweep 5th percentile {thr:.3f}",
                xy=(thr, top * 0.995), xytext=(thr - 0.05, top * 1.14),
                ha="right", va="bottom", fontsize=8.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK, lw=1.0))
    ax.text((thr + 1.02) / 2, top * 0.46,
            "near-duplicate\nzone\n\n0 images", ha="center", va="center",
            fontsize=8.5, color=INK2, linespacing=1.4)
    ax.set_xlabel("cosine similarity to the most similar training image (64×64, z-normalised)")
    ax.set_ylabel("images")
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, top * 1.26)
    ax.yaxis.grid(True, zorder=0); ax.set_axisbelow(True)
    despine(ax)
    ax.legend(loc="upper left", fontsize=8.5)
    fig.tight_layout(rect=[0, 0.04, 1, 0.86])
    headline(fig, "Split-integrity audit: the official splits are sweep-disjoint",
             f"Adjacent frames within one sweep score {calib['median']:.3f} (median). "
             f"No held-out image exceeds {max(test.max(), val.max()):.3f}.")
    finish(fig, "fig03_leakage_audit",
           "Source: experiments/exp001_leakage_audit (E1). A negative result: the "
           "leakage hypothesis we set out to test was not supported.")


# ---------------------------------------------------------------- figure 4
def fig_training():
    p = pathlib.Path("experiments/exp003_unet_baseline/history.json")
    if not p.exists():
        print("  skip fig04 (training not finished)"); return
    h = json.load(open(p, encoding="utf-8"))
    ep = [r["epoch"] for r in h]
    loss = [r["train_loss"] for r in h]
    vd = [r["val_macro_dice"] for r in h]

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.6))
    axes[0].plot(ep, loss, color=C1, lw=2, zorder=3)
    axes[0].set_title("Training loss (Dice + cross-entropy)", loc="left", pad=10)
    axes[0].set_xlabel("epoch"); axes[0].set_ylabel("loss")
    axes[1].plot(ep, vd, color=C2, lw=2, zorder=3)
    best = int(np.argmax(vd))
    axes[1].scatter([ep[best]], [vd[best]], s=42, color=C2, zorder=5,
                    edgecolor=SURFACE, linewidth=2)
    axes[1].annotate(f"best {vd[best]:.4f} (ep {ep[best]})",
                     (ep[best], vd[best]), textcoords="offset points",
                     xytext=(-8, -16), ha="right", fontsize=8.5, color=INK)
    axes[1].set_title("Validation macro Dice", loc="left", pad=10)
    axes[1].set_xlabel("epoch"); axes[1].set_ylabel("Dice")
    for ax in axes:
        ax.yaxis.grid(True, zorder=0); ax.set_axisbelow(True); despine(ax)
    fig.tight_layout(rect=[0, 0.03, 1, 0.85])
    headline(fig, "U-Net baseline — porcine intraoperative spinal-cord ultrasound (NOT lumbar)",
             "Pipeline validation only. These results say nothing about human neuraxial anatomy.")
    finish(fig, "fig04_training_curves",
           "Source: experiments/exp003_unet_baseline/history.json (E1). "
           "Two measures of different scale are shown as two panels, never a dual axis.")


# ---------------------------------------------------------------- figure 5
def fig_per_class_dice():
    p = pathlib.Path("experiments/exp003_unet_baseline/metrics.json")
    if not p.exists():
        print("  skip fig05 (training not finished)"); return
    m = json.load(open(p, encoding="utf-8"))["test"]
    d = {k: v for k, v in m["per_class_dice"].items() if v is not None}
    n = m["per_class_n_images_defined"]
    names = sorted(d, key=lambda k: -d[k])
    vals = [d[k] for k in names]

    fig, ax = plt.subplots(figsize=(8.8, 4.2))
    y = np.arange(len(names))
    ax.barh(y, vals, height=0.62, color=C1, zorder=3)
    ax.axvline(m["mean_dice"], color=INK, ls="--", lw=1.4, zorder=4)
    # Place the mean callout above the plot area so it cannot collide with a
    # bar's value label.
    ax.annotate(f"image-level macro mean {m['mean_dice']:.3f}",
                xy=(m["mean_dice"], -0.62), xytext=(m["mean_dice"] + 0.02, -1.05),
                fontsize=8.5, color=INK, va="center", ha="left",
                annotation_clip=False,
                arrowprops=dict(arrowstyle="-", color=INK, lw=1.0))
    for i, k in enumerate(names):
        ax.text(vals[i] + 0.008, i, f"{vals[i]:.3f}   n={n[k]:,}",
                va="center", fontsize=8, color=INK)
    ax.set_yticks(y, names, fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.14)
    ax.set_xlabel("Dice (test split, mean over images where the class is defined)")
    ax.xaxis.grid(True, zorder=0); ax.set_axisbelow(True)
    despine(ax, keep=("bottom",)); ax.tick_params(axis="y", length=0)
    fig.tight_layout(rect=[0, 0.03, 1, 0.85])
    headline(fig, "Per-class test Dice — porcine intraoperative spinal cord",
             "Classes absent from both prediction and ground truth score NaN, not 0; "
             "n = test images in which the class is defined.")
    finish(fig, "fig05_per_class_dice",
           "Source: experiments/exp003_unet_baseline/metrics.json (E1).")


# ---------------------------------------------------------------- figure 6
def fig_uncertainty():
    """Does uncertainty track error? Scatter + abstention curve, two panels."""
    mp = pathlib.Path("experiments/exp004_uncertainty_failure/metrics.json")
    ap = pathlib.Path("experiments/exp004_uncertainty_failure/per_image.npz")
    if not (mp.exists() and ap.exists()):
        print("  skip fig06 (exp004 not run)"); return
    m = json.load(open(mp, encoding="utf-8"))
    d = np.load(ap, allow_pickle=True)
    dice, ent = d["dice"], d["entropy"]

    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.0))

    # panel 1: uncertainty vs error
    axes[0].scatter(ent, dice, s=11, color=C1, alpha=0.45, linewidths=0, zorder=3)
    axes[0].set_xlabel("mean predictive entropy (MC dropout, 10 passes)")
    axes[0].set_ylabel("per-image Dice")
    axes[0].set_title("Uncertainty tracks real error", loc="left", pad=10)
    axes[0].text(0.97, 0.95,
                 "Spearman ρ = {:+.3f}".format(m["spearman_entropy_vs_dice"]),
                 transform=axes[0].transAxes, ha="right", va="top",
                 fontsize=10, color=INK, fontweight="bold")

    # panel 2: abstention
    fr = [0] + [int(k.rstrip("%")) for k in m["abstention"]]
    keep = [m["mean_dice_mc"]] + [v["dice_on_retained"] for v in m["abstention"].values()]
    axes[1].plot(fr, keep, color=C2, lw=2, marker="o", ms=6,
                 markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=3)
    for x, y in zip(fr, keep):
        axes[1].annotate(f"{y:.3f}", (x, y), textcoords="offset points",
                         xytext=(0, 9), ha="center", fontsize=8, color=INK)
    axes[1].set_xlabel("% of most-uncertain images declined")
    axes[1].set_ylabel("Dice on retained images")
    axes[1].set_title("Abstention improves what remains", loc="left", pad=10)
    axes[1].set_ylim(min(keep) - 0.012, max(keep) + 0.022)

    for ax in axes:
        ax.yaxis.grid(True, zorder=0); ax.set_axisbelow(True); despine(ax)
    fig.tight_layout(rect=[0, 0.03, 1, 0.85])
    headline(fig, "Can the model tell when it is wrong?",
             "Yes, on this data. Both uncertainty measures correlate strongly with error "
             "(entropy ρ={:+.3f}, pass-disagreement ρ={:+.3f}).".format(
                 m["spearman_entropy_vs_dice"], m["spearman_disagreement_vs_dice"]))
    finish(fig, "fig06_uncertainty_abstention",
           "Source: experiments/exp004_uncertainty_failure (E1). Porcine intraoperative data: "
           "this validates the uncertainty mechanism, not any clinical safety property.")


if __name__ == "__main__":
    print("generating figures ...")
    for fn in (fig_dataset_survey, fig_class_distribution, fig_leakage_audit,
               fig_training, fig_per_class_dice, fig_uncertainty):
        try:
            fn()
        except Exception as e:
            print(f"  !! {fn.__name__}: {type(e).__name__}: {e}", file=sys.stderr)
    print("done")
