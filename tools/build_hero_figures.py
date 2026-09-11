#!/usr/bin/env python3
"""
build_hero_figures.py -- Assemble the two candidate paper figures.

FIGURE_1_REAL_LUMBAR_EVIDENCE_PIPELINE
    (a) real handheld human lumbar ultrasound
    (b) the same frame with the PUBLIC EXPERT bone-surface annotation
    (c) our prediction on a HELD-OUT subject, with its error
    (d) real robot-assisted ultrasound with expert overlay
    (e) uncertainty / failure example
    (f) the proposed clinician-in-the-loop system -- clearly marked as NOT
        clinically validated

FIGURE_2_HUMAN_LUMBAR_AI_RESULTS
    rows: strong HUS | difficult HUS | RUS | failures
    cols: raw | expert | prediction | error

Design rule for both: **ultrasound must dominate**. V1's figures were charts;
a reader should understand this technology from the images in five seconds.
Panel (f) is the only non-photographic panel in Figure 1 and is bounded,
labelled and small.
"""
from __future__ import annotations
import argparse
import csv
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

VIS = pathlib.Path("visuals/ultrasound/real_human_lumbar")
PROC = pathlib.Path("data/processed/kuleuven_lumbar")
OUT = pathlib.Path("deliverables/paper_v2_assets")

INK = (242, 242, 242)
MUTED = (158, 158, 158)
BG = (16, 16, 16)
PANEL = (26, 26, 26)
GT_C = (255, 45, 45)
PR_C = (40, 230, 90)
WARN = (255, 196, 60)


def font(sz, bold=False):
    for name in (("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),):
        try:
            return ImageFont.truetype(name, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def outline(m, k=2):
    """Boundary of a mask, so it can be drawn ON TOP of a filled overlay and
    remain visible where the two agree."""
    d = dil(m, k)
    e = m.copy()
    for _ in range(1):
        p = np.pad(e, 1, constant_values=False)
        e = (p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:] & e)
    return d & ~e


def dil(m, k=1):
    out = m.copy()
    for _ in range(k):
        p = np.pad(out, 1, constant_values=False)
        out = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:] | out)
    return out


def load(uid):
    img = np.array(Image.open(PROC / "images" / f"{uid}.png"))
    msk = np.array(Image.open(PROC / "masks" / f"{uid}.png")) > 127
    return img, msk


def focus_crop(gray, masks, pad_top=170, pad_bot=210):
    """Crop to the informative band around the annotation.

    The sector runs to ~7 cm depth and the lower third is usually anechoic, so
    a full-height panel wastes most of a figure on black. This is a PRESENTATION
    crop only: it never touches the arrays used for metrics, and it is stated in
    the figure caption. The window is derived from the annotation so no
    annotated pixel is ever cut.
    """
    ref = None
    for m in masks:
        if m is not None and m.any():
            ref = m if ref is None else (ref | m)
    if ref is None or not ref.any():
        r0, r1 = 0, int(gray.shape[0] * 0.62)
    else:
        ys = np.nonzero(ref.any(1))[0]
        r0 = max(0, int(ys.min()) - pad_top)
        r1 = min(gray.shape[0], int(ys.max()) + pad_bot)
    return r0, r1


def panel(gray, overlays, title, sub="", w=270, title_c=INK, crop=None):
    """One labelled image panel. overlays = [(mask, colour), ...]"""
    rgb = np.stack([gray] * 3, -1).copy()
    for m, c in overlays:
        rgb[m] = c
    if crop is not None:
        rgb = rgb[crop[0]:crop[1]]
    im = Image.fromarray(rgb)
    h = int(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    head = 34 if sub else 22
    out = Image.new("RGB", (w, h + head), PANEL)
    d = ImageDraw.Draw(out)
    d.text((5, 3), title, fill=title_c, font=font(12, True))
    if sub:
        d.text((5, 18), sub, fill=MUTED, font=font(10))
    out.paste(im, (0, head))
    return np.array(out)


def hcat(ps, gap=7):
    h = max(p.shape[0] for p in ps)
    o = []
    for p in ps:
        if p.shape[0] < h:
            p = np.pad(p, ((0, h - p.shape[0]), (0, 0), (0, 0)), constant_values=BG[0])
        o += [p, np.full((h, gap, 3), BG[0], np.uint8)]
    return np.hstack(o[:-1])


def vcat(ps, gap=7):
    w = max(p.shape[1] for p in ps)
    o = []
    for p in ps:
        if p.shape[1] < w:
            p = np.pad(p, ((0, 0), (0, w - p.shape[1]), (0, 0)), constant_values=BG[0])
        o += [p, np.full((gap, w, 3), BG[0], np.uint8)]
    return np.vstack(o[:-1])


def concept_panel(w, h):
    """Panel (f): the proposed system. Deliberately schematic, bounded and
    unmistakably marked as not validated."""
    im = Image.new("RGB", (w, h), (30, 26, 20))
    d = ImageDraw.Draw(im)
    d.rectangle([1, 1, w - 2, h - 2], outline=WARN, width=2)
    d.text((10, 10), "(f) PROPOSED SYSTEM", fill=WARN, font=font(13, True))
    d.text((10, 28), "NOT CLINICALLY VALIDATED", fill=WARN, font=font(11, True))
    steps = ["robot-held probe, force-limited",
             "AI anatomy + quality assessment",
             "candidate window + uncertainty",
             "-> CLINICIAN CONFIRMS <-",
             "guide aligned to confirmed plan",
             "CLINICIAN performs the puncture"]
    y = 54
    for i, s in enumerate(steps):
        c = WARN if "CLINICIAN CONFIRMS" in s else INK
        d.text((14, y), ("* " if "CLINICIAN" in s else "- ") + s,
               fill=c, font=font(10, "CLINICIAN" in s))
        y += 17
    d.text((10, h - 46), "No hardware exists. No safety case exists.",
           fill=MUTED, font=font(9))
    d.text((10, h - 33), "Any target or trajectory shown would be a",
           fill=MUTED, font=font(9))
    d.text((10, h - 21), "CONCEPT requiring clinician annotation.",
           fill=MUTED, font=font(9))
    return np.array(im)


def header(w, title, sub, h=58):
    im = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(im)
    d.text((4, 6), title, fill=INK, font=font(19, True))
    d.text((4, 32), sub, fill=MUTED, font=font(11))
    return np.array(im)


def footer(w, text, h=30):
    im = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(im)
    d.text((4, 6), text, fill=MUTED, font=font(10))
    return np.array(im)


def pick_predictions():
    p = VIS / "PREDICTION_SELECTION.csv"
    if not p.exists():
        return []
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    for r in rows:
        r["dice"] = float(r["dice"])
    return rows


def figure1(preds):
    idx = list(csv.DictReader(open(PROC / "index.csv", encoding="utf-8")))
    for r in idx:
        r["bone_px"] = int(r["bone_px"])
    hus = [r for r in idx if r["modality"] == "HUS" and r["bone_px"] > 1500]
    rus = [r for r in idx if r["modality"] == "RUS" and r["bone_px"] > 1500]
    a_r = hus[len(hus) // 2]
    d_r = rus[len(rus) // 2]
    ga, ma = load(a_r["uid"])
    gd, md = load(d_r["uid"])

    # Panel (c): the best agreement among frames that actually have a
    # substantial annotation. Picking on Dice alone selects a tiny edge
    # annotation that scores well but shows the reader nothing.
    for r in preds:
        r["gt_px"] = int(r["gt_px"]); r["pred_px"] = int(r["pred_px"])
    big = [r for r in preds if r["gt_px"] >= 250]
    best = sorted([r for r in (big or preds) if r["modality"] == "HUS"],
                  key=lambda r: -r["dice"]) or sorted(big or preds, key=lambda r: -r["dice"])
    # Panel (e): an informative failure -- the model predicted something and got
    # it wrong. A null prediction renders as an empty panel and teaches nothing.
    informative = [r for r in preds if r["pred_px"] > 200 and r["gt_px"] > 200]
    worst = sorted(informative or preds, key=lambda r: r["dice"])
    ca = focus_crop(ga, [ma])
    cd = focus_crop(gd, [md])
    panels = [
        panel(ga, [], "(a) real human lumbar ultrasound",
              f"handheld · {a_r['subject']} · in vivo", crop=ca),
        panel(ga, [(dil(ma, 1), GT_C)], "(b) PUBLIC EXPERT annotation",
              "physician-annotated visible bone surface", crop=ca),
    ]
    if best:
        u = best[0]["uid"]
        g, m = load(u)
        pv = VIS / "predictions" / f"{u}.png"
        if pv.exists():
            pm = np.array(Image.open(pv).convert("RGB"))
            pmask = (pm[..., 1].astype(int) - pm[..., 0].astype(int)) > 60
            # Predictions are rendered at TRAINING resolution; the ground truth
            # here is native sector resolution. Upsample the prediction rather
            # than downsampling the frame, so the panel shows full-resolution
            # anatomy. This is display only.
            if pmask.shape != g.shape:
                pmask = np.array(Image.fromarray(pmask.astype(np.uint8) * 255)
                                 .resize((g.shape[1], g.shape[0]), Image.NEAREST)) > 127
            # Prediction filled, expert outlined ON TOP: where they agree the
            # green fill shows through a red outline, so overlap is legible
            # rather than one mask simply hiding the other.
            panels.append(panel(g, [(dil(pmask, 1), PR_C), (outline(m, 2), GT_C)],
                                "(c) OUR PREDICTION (held-out subject)",
                                f"green = ours, red outline = expert · Dice {best[0]['dice']:.3f}",
                                crop=focus_crop(g, [m, pmask])))
    panels.append(panel(gd, [(dil(md, 1), GT_C)], "(d) ROBOT-ASSISTED ultrasound",
                        f"same expert annotation · {d_r['subject']}", crop=cd))
    if worst:
        u = worst[0]["uid"]
        g, m = load(u)
        pw = VIS / "predictions" / f"{u}.png"
        wmask = None
        if pw.exists():
            wm = np.array(Image.open(pw).convert("RGB"))
            wmask = (wm[..., 1].astype(int) - wm[..., 0].astype(int)) > 60
            if wmask.shape != g.shape:
                wmask = np.array(Image.fromarray(wmask.astype(np.uint8) * 255)
                                 .resize((g.shape[1], g.shape[0]), Image.NEAREST)) > 127
        ovl = ([(dil(wmask, 1), PR_C)] if wmask is not None else []) + [(outline(m, 2), GT_C)]
        panels.append(panel(g, ovl, "(e) FAILURE case",
                            f"green = ours, red = expert · Dice {worst[0]['dice']:.3f} · {worst[0]['subject']}",
                            crop=focus_crop(g, [m] + ([wmask] if wmask is not None else []))))

    row = hcat(panels)
    conc = concept_panel(300, row.shape[0])
    body = hcat([row, conc])
    fig = vcat([
        header(body.shape[1],
               "Real human lumbar ultrasound: expert annotation, AI perception, and the missing layer",
               "(a)-(e) are REAL data and REAL executed results. (f) is a proposal."),
        body,
        footer(body.shape[1],
               "Ultrasound + expert annotation: Cavalcanti et al., doi:10.48804/3XPCAE, CC-BY-4.0. "
               "Predictions: Lumbar_MarkAny exp005.", h=44),
        footer(body.shape[1],
               "Expert labels mark VISIBLE BONE SURFACE, not puncture targets. "
               "Panels are depth-cropped for display only; all metrics use full frames.", h=22)])
    Image.fromarray(fig).save(OUT / "FIGURE_1_REAL_LUMBAR_EVIDENCE_PIPELINE.png")
    Image.fromarray(fig).save(VIS / "publication_candidates" / "FIGURE_1_REAL_LUMBAR_EVIDENCE_PIPELINE.png")
    print(f"  FIGURE 1: {fig.shape[1]}x{fig.shape[0]}")


def figure2(preds):
    if not preds:
        print("  FIGURE 2 skipped (no predictions yet)"); return
    rows_spec = [
        ("strong handheld", [p for p in preds if p["modality"] == "HUS"], True),
        ("difficult handheld", [p for p in preds if p["modality"] == "HUS"], False),
        ("robot-assisted", [p for p in preds if p["modality"] == "RUS"], True),
        ("failures", preds, False),
    ]
    blocks = []
    for label, pool, best in rows_spec:
        if not pool:
            continue
        pool = sorted(pool, key=lambda r: -r["dice"] if best else r["dice"])[:3]
        tiles = []
        for p in pool:
            f = VIS / "prediction_overlays" / f"{p['uid']}.png"
            if not f.exists():
                continue
            im = Image.open(f)
            w = 640
            tiles.append(np.array(im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)))
        if tiles:
            lab = Image.new("RGB", (max(t.shape[1] for t in tiles), 24), BG)
            ImageDraw.Draw(lab).text((4, 4), label.upper(), fill=INK, font=font(13, True))
            blocks.append(vcat([np.array(lab)] + tiles))
    if not blocks:
        print("  FIGURE 2 skipped (no overlays)"); return
    body = vcat(blocks)
    fig = vcat([
        header(body.shape[1], "Human lumbar ultrasound: expert annotation vs our model",
               "Each row: raw | expert bone surface | our prediction | TP-FN-FP error | "
               "MC-dropout uncertainty. All subjects held out."),
        body,
        footer(body.shape[1],
               "Cavalcanti et al., doi:10.48804/3XPCAE, CC-BY-4.0. Predictions: Lumbar_MarkAny exp005.")])
    Image.fromarray(fig).save(OUT / "FIGURE_2_HUMAN_LUMBAR_AI_RESULTS.png")
    Image.fromarray(fig).save(VIS / "publication_candidates" / "FIGURE_2_HUMAN_LUMBAR_AI_RESULTS.png")
    print(f"  FIGURE 2: {fig.shape[1]}x{fig.shape[0]}")


def main():
    argparse.ArgumentParser().parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    (VIS / "publication_candidates").mkdir(parents=True, exist_ok=True)
    preds = pick_predictions()
    print(f"prediction rows available: {len(preds)}")
    figure1(preds)
    figure2(preds)


if __name__ == "__main__":
    main()
