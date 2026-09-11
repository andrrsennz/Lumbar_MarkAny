#!/usr/bin/env python3
"""
build_visual_library.py -- Curate REAL human lumbar ultrasound visuals from the
KU Leuven / Balgrist expert-annotated frames.

Source: doi:10.48804/3XPCAE, CC-BY-4.0. Every pixel here is genuine dataset
content or a direct rendering of it. Nothing is generated, painted, simulated
or stylised.

The labels are EXPERT-ANNOTATED VISIBLE BONE SURFACE. They are not puncture
targets, entry points or trajectories, and no caption produced here says
otherwise.

Selection is deliberately NOT "the prettiest frames": each scan contributes a
spread across the annotation-area distribution, plus the hardest frames, plus
frames the expert left empty.
"""
from __future__ import annotations
import argparse
import csv
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path("data/processed/kuleuven_lumbar")
OUT = pathlib.Path("visuals/ultrasound/real_human_lumbar")
SUBDIRS = ["raw", "expert_labels", "expert_overlays", "contours", "side_by_side",
           "hus", "rus", "paired_hus_rus", "difficult_cases", "contact_sheets",
           "publication_candidates"]

RED = (255, 45, 45)
CYAN = (0, 220, 255)


def load(uid):
    img = np.array(Image.open(ROOT / "images" / f"{uid}.png"))
    msk = np.array(Image.open(ROOT / "masks" / f"{uid}.png")) > 127
    return img, msk


def to_rgb(img):
    if img.ndim == 2:
        return np.stack([img] * 3, -1)
    return img


def overlay(img, msk, colour=RED, alpha=1.0):
    rgb = to_rgb(img).astype(np.float32).copy()
    if alpha >= 1.0:
        rgb[msk] = colour
    else:
        rgb[msk] = (1 - alpha) * rgb[msk] + alpha * np.array(colour, np.float32)
    return rgb.astype(np.uint8)


def dilate(m, k=2):
    out = m.copy()
    for _ in range(k):
        p = np.pad(out, 1, constant_values=False)
        out = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:] | out)
    return out


def contour(m):
    """Outline of the mask (mask minus its erosion)."""
    p = np.pad(m, 1, constant_values=False)
    er = (p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:] & m)
    return m & ~er


def label_bar(w, text, h=26, bg=(18, 18, 18), fg=(240, 240, 240)):
    im = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("DejaVuSans.ttf", 13)
    except Exception:
        f = ImageFont.load_default()
    d.text((6, 5), text, fill=fg, font=f)
    return np.array(im)


def stack_h(panels, gap=6, bg=30):
    h = max(p.shape[0] for p in panels)
    outs = []
    for p in panels:
        if p.shape[0] < h:
            p = np.pad(p, ((0, h - p.shape[0]), (0, 0), (0, 0)), constant_values=bg)
        outs.append(p)
        outs.append(np.full((h, gap, 3), bg, np.uint8))
    return np.hstack(outs[:-1])


def stack_v(panels, gap=6, bg=30):
    w = max(p.shape[1] for p in panels)
    outs = []
    for p in panels:
        if p.shape[1] < w:
            p = np.pad(p, ((0, 0), (0, w - p.shape[1]), (0, 0)), constant_values=bg)
        outs.append(p)
        outs.append(np.full((gap, w, 3), bg, np.uint8))
    return np.vstack(outs[:-1])


def select(index, per_scan=4):
    """Spread across the annotation-area distribution, never only easy frames."""
    by_scan = {}
    for r in index:
        by_scan.setdefault((r["subject"], r["scan"]), []).append(r)
    chosen = []
    for key, rows in sorted(by_scan.items()):
        ann = sorted([r for r in rows if not r["empty_label"]], key=lambda r: r["bone_px"])
        if not ann:
            continue
        # quantiles of annotated area: hardest (smallest) .. richest (largest)
        qs = np.linspace(0, len(ann) - 1, per_scan).astype(int)
        for q in qs:
            chosen.append(dict(ann[q], pick="quantile"))
        chosen.append(dict(ann[0], pick="hardest"))
        empty = [r for r in rows if r["empty_label"]]
        if empty:
            chosen.append(dict(empty[len(empty) // 2], pick="expert_left_empty"))
    seen, uniq = set(), []
    for c in chosen:
        if c["uid"] not in seen:
            seen.add(c["uid"]); uniq.append(c)
    return uniq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-scan", type=int, default=4)
    a = ap.parse_args()
    for d in SUBDIRS:
        (OUT / d).mkdir(parents=True, exist_ok=True)

    index = list(csv.DictReader(open(ROOT / "index.csv", encoding="utf-8")))
    for r in index:
        r["bone_px"] = int(r["bone_px"])
        r["empty_label"] = r["empty_label"] == "True"

    picks = select(index, a.per_scan)
    print(f"selected {len(picks)} frames from {len(index)} for the visual library")

    prov = []
    for r in picks:
        uid = r["uid"]
        img, msk = load(uid)
        rgb = to_rgb(img)
        ov = overlay(img, dilate(msk, 1))
        ct = overlay(img, contour(dilate(msk, 2)), CYAN)
        lab = np.stack([(msk * 255).astype(np.uint8)] * 3, -1)

        tag = f"{r['subject']} {r['scan']} ({r['modality']}) frame {r['frame_index']}  bone px={r['bone_px']}"
        Image.fromarray(rgb).save(OUT / "raw" / f"{uid}.png")
        Image.fromarray(lab).save(OUT / "expert_labels" / f"{uid}.png")
        Image.fromarray(ov).save(OUT / "expert_overlays" / f"{uid}.png")
        Image.fromarray(ct).save(OUT / "contours" / f"{uid}.png")

        sbs = stack_h([
            stack_v([label_bar(rgb.shape[1], "raw ultrasound"), rgb]),
            stack_v([label_bar(lab.shape[1], "expert bone-surface label"), lab]),
            stack_v([label_bar(ov.shape[1], "overlay"), ov]),
        ])
        sbs = stack_v([label_bar(sbs.shape[1], tag, h=28), sbs])
        Image.fromarray(sbs).save(OUT / "side_by_side" / f"{uid}.png")

        mod_dir = "hus" if r["modality"] == "HUS" else "rus"
        Image.fromarray(ov).save(OUT / mod_dir / f"{uid}.png")
        if r["pick"] in ("hardest", "expert_left_empty"):
            Image.fromarray(ov).save(OUT / "difficult_cases" / f"{uid}_{r['pick']}.png")

        prov.append(dict(
            asset_id=uid, subject=r["subject"], scan=r["scan"], modality=r["modality"],
            protocol=r["protocol"], frame_index=r["frame_index"],
            bone_px=r["bone_px"], empty_label=r["empty_label"], selection_reason=r["pick"],
            original_path=r["original_path"], source_archive=r["source_archive"],
        ))

    with open(OUT / "SELECTION.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(prov[0].keys()))
        w.writeheader(); w.writerows(prov)
    print(f"wrote visual library -> {OUT}")


if __name__ == "__main__":
    main()
