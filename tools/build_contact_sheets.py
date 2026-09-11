#!/usr/bin/env python3
"""
build_contact_sheets.py -- Dense grids for rapid visual inspection of the REAL
human lumbar ultrasound set.

Contact sheets exist so a reviewer can judge the data in one screen rather than
clicking through 6,182 frames, and so cherry-picking is visible: each sheet
states its selection rule in the header.
"""
from __future__ import annotations
import argparse
import csv
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROC = pathlib.Path("data/processed/kuleuven_lumbar")
OUT = pathlib.Path("visuals/ultrasound/real_human_lumbar/contact_sheets")
RED = (255, 45, 45)


def dil(m, k=1):
    out = m.copy()
    for _ in range(k):
        p = np.pad(out, 1, constant_values=False)
        out = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:] | out)
    return out


def tile(uid, w=150, overlay=True):
    img = np.array(Image.open(PROC / "images" / f"{uid}.png"))
    rgb = np.stack([img] * 3, -1)
    if overlay:
        m = np.array(Image.open(PROC / "masks" / f"{uid}.png")) > 127
        rgb = rgb.copy(); rgb[dil(m, 2)] = RED
    im = Image.fromarray(rgb)
    h = int(im.height * w / im.width)
    return im.resize((w, h), Image.LANCZOS)


def sheet(uids, labels, title, subtitle, cols=10, tw=150, path=None):
    tiles = [tile(u) for u in uids]
    if not tiles:
        return
    th = max(t.height for t in tiles)
    pad, head, cap = 4, 54, 15
    rows = (len(tiles) + cols - 1) // cols
    W = cols * (tw + pad) + pad
    H = head + rows * (th + cap + pad) + pad
    canvas = Image.new("RGB", (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    try:
        ft = ImageFont.truetype("DejaVuSans.ttf", 17)
        fs = ImageFont.truetype("DejaVuSans.ttf", 12)
        fc = ImageFont.truetype("DejaVuSans.ttf", 10)
    except Exception:
        ft = fs = fc = ImageFont.load_default()
    d.text((pad + 2, 8), title, fill=(245, 245, 245), font=ft)
    d.text((pad + 2, 32), subtitle, fill=(165, 165, 165), font=fs)
    for i, (t, lb) in enumerate(zip(tiles, labels)):
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad)
        y = head + r * (th + cap + pad)
        canvas.paste(t, (x, y))
        d.text((x + 1, y + th + 1), lb, fill=(190, 190, 190), font=fc)
    canvas.save(path)
    print(f"  {path.name}: {len(tiles)} tiles ({rows}x{cols})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cols", type=int, default=10)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(PROC / "index.csv", encoding="utf-8")))
    for r in rows:
        r["bone_px"] = int(r["bone_px"])
        r["empty_label"] = r["empty_label"] == "True"

    def pick(sel, n):
        sel = sorted(sel, key=lambda r: (r["subject"], r["scan"], r["frame_index"]))
        if len(sel) <= n:
            return sel
        idx = np.linspace(0, len(sel) - 1, n).astype(int)
        return [sel[i] for i in idx]

    lab = lambda r: f"{r['subject']}/{r['scan']} f{r['frame_index']}"

    hus = pick([r for r in rows if r["modality"] == "HUS" and not r["empty_label"]], 40)
    sheet([r["uid"] for r in hus], [lab(r) for r in hus],
          "HANDHELD lumbar ultrasound (HUS) with expert bone-surface annotation",
          "Real human in-vivo data, KU Leuven/Balgrist doi:10.48804/3XPCAE (CC-BY-4.0). "
          "Selection: evenly spaced across all annotated HUS frames, not curated for appearance.",
          a.cols, path=OUT / "CONTACT_SHEET_HUS_GT.png")

    rus = pick([r for r in rows if r["modality"] == "RUS" and not r["empty_label"]], 40)
    sheet([r["uid"] for r in rus], [lab(r) for r in rus],
          "ROBOT-ASSISTED lumbar ultrasound (RUS) with expert bone-surface annotation",
          "Same source and licence. Selection: evenly spaced across all annotated RUS frames.",
          a.cols, path=OUT / "CONTACT_SHEET_RUS_GT.png")

    hard = sorted([r for r in rows if not r["empty_label"]], key=lambda r: r["bone_px"])[:20]
    empty = [r for r in rows if r["empty_label"]][:20]
    diff = hard + empty
    sheet([r["uid"] for r in diff],
          [f"{lab(r)} {'EMPTY' if r['empty_label'] else str(r['bone_px'])+'px'}" for r in diff],
          "DIFFICULT cases: smallest expert annotations, and frames the expert left EMPTY",
          "Left block: the 20 frames with the least annotated bone surface. Right block: 20 of the "
          "184 frames (3.0%) where the expert identified no bone surface at all.",
          a.cols, path=OUT / "CONTACT_SHEET_DIFFICULT.png")

    paired = []
    for s in sorted({r["subject"] for r in rows}):
        h = [r for r in rows if r["subject"] == s and r["modality"] == "HUS" and not r["empty_label"]]
        u = [r for r in rows if r["subject"] == s and r["modality"] == "RUS" and not r["empty_label"]]
        if h and u:
            paired += [h[len(h) // 2], h[len(h) // 3], u[len(u) // 2], u[len(u) // 3]]
    sheet([r["uid"] for r in paired],
          [f"{r['subject']} {r['modality']}" for r in paired],
          "PAIRED handheld vs robot-assisted, same subject",
          "Each subject contributes 2 HUS then 2 RUS frames (7 of 9 subjects have both). "
          "Same anatomy, different acquisition.",
          4, path=OUT / "CONTACT_SHEET_PAIRED_HUS_RUS.png")


if __name__ == "__main__":
    main()
