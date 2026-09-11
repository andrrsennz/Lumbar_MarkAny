#!/usr/bin/env python3
"""
build_start_here.py -- Generate START_HERE.md and 00_TREASURE_MAP.md from the
artefacts that actually exist.

Generated rather than hand-written so the headline numbers cannot drift from
the runs, and so a missing experiment shows as missing instead of as a
remembered figure.
"""
from __future__ import annotations
import csv
import json
import pathlib

VIS = pathlib.Path("visuals/ultrasound/real_human_lumbar")
PROC = pathlib.Path("data/processed/kuleuven_lumbar")
EXP5 = pathlib.Path("experiments/exp005_lumbar_bone_seg/results.json")
EXP6 = pathlib.Path("experiments/exp006_lumbar_uncertainty/metrics.json")


def n(d, pat="*.png"):
    return len(list((VIS / d).glob(pat))) if (VIS / d).exists() else 0


def best_asset(sub, prefer_max=True, key=None):
    """Pick a representative asset path for the treasure map."""
    ps = sorted((VIS / sub).glob("*.png")) if (VIS / sub).exists() else []
    return ps[0].as_posix() if ps else None


def main():
    stats = {}
    if (PROC / "index.csv").exists():
        rows = list(csv.DictReader(open(PROC / "index.csv", encoding="utf-8")))
        stats.update(frames=len(rows),
                     subjects=len({r["subject"] for r in rows}),
                     hus=sum(1 for r in rows if r["modality"] == "HUS"),
                     rus=sum(1 for r in rows if r["modality"] == "RUS"),
                     empty=sum(1 for r in rows if r["empty_label"] == "True"))

    matrix, exp6 = None, None
    if EXP5.exists():
        res = json.loads(EXP5.read_text(encoding="utf-8"))
        matrix = {}
        for r in res:
            matrix.setdefault((r["train_regime"], r["test_modality"]), []).append(r)
    if EXP6.exists():
        exp6 = json.loads(EXP6.read_text(encoding="utf-8"))

    def cell(tr, te, field="subject_mean_dice"):
        if not matrix or (tr, te) not in matrix:
            return "—"
        v = [x[field] for x in matrix[(tr, te)] if x.get(field) is not None]
        return f"{sum(v)/len(v):.3f}" if v else "—"

    # ---------------- START_HERE ----------------
    S = ["# START HERE", "",
         "## What this package is", "",
         "The V2 evidence vault for **Lumbar_MarkAny** — AI-assisted, robot-acquired "
         "lumbar ultrasound for neuraxial needle access.", "",
         "**The one thing that changed from V1:** this package physically contains "
         "**real human lumbar ultrasound with real expert annotations**, and real "
         "model predictions on held-out human subjects. V1 discussed datasets; V2 "
         "shows them.", "",
         "> **Open `00_VISUAL_INDEX.html` first.** Real ultrasound is on the first screen.", "",
         "---", "", "## The numbers", ""]
    if stats:
        S += [f"| | |", "|---|---|",
              f"| Real human lumbar frames held | **{stats['frames']:,}** |",
              f"| Human subjects | **{stats['subjects']}** |",
              f"| Handheld / robot-assisted | {stats['hus']:,} / {stats['rus']:,} |",
              f"| Frames the expert left empty | {stats['empty']} ({100*stats['empty']/stats['frames']:.1f}%) |",
              f"| Source | KU Leuven / Balgrist, `doi:10.48804/3XPCAE`, **CC-BY-4.0** |", ""]
    if matrix:
        S += ["### Cross-acquisition matrix — subject-mean Dice, subject-disjoint 3-fold CV", "",
              "| train ↓ / test → | HUS | RUS |", "|---|---|---|",
              f"| **HUS** | {cell('HUS','HUS')} | {cell('HUS','RUS')} |",
              f"| **RUS** | {cell('RUS','HUS')} | {cell('RUS','RUS')} |",
              f"| **BOTH** | {cell('BOTH','HUS')} | {cell('BOTH','RUS')} |", "",
              "Tolerance-band F1 (2 px), the fairer metric for a 1–2 px contour:", "",
              "| train ↓ / test → | HUS | RUS |", "|---|---|---|",
              f"| **HUS** | {cell('HUS','HUS','subject_mean_tol_f1')} | {cell('HUS','RUS','subject_mean_tol_f1')} |",
              f"| **RUS** | {cell('RUS','HUS','subject_mean_tol_f1')} | {cell('RUS','RUS','subject_mean_tol_f1')} |",
              f"| **BOTH** | {cell('BOTH','HUS','subject_mean_tol_f1')} | {cell('BOTH','RUS','subject_mean_tol_f1')} |", ""]
    if exp6:
        S += ["### Can the model tell when it is wrong? (real human lumbar data)", "",
              f"- Spearman ρ, uncertainty vs error: **{exp6['spearman_entropy_vs_dice']:+.3f}** "
              f"(entropy), **{exp6['spearman_pass_sd_vs_dice']:+.3f}** (pass disagreement)",
              f"- Declining the most-uncertain 30% raises retained Dice to "
              f"**{exp6['abstention']['30%']['dice_on_retained']:.3f}** "
              f"(declined frames: {exp6['abstention']['30%']['dice_on_declined']:.3f})", ""]

    S += ["---", "", "## What the annotations are — and are not", "",
          "The public expert labels mark **VISIBLE BONE SURFACE** (value 2 of a "
          "`{0 or 1, 2}` mask). They are **not** puncture targets, entry points, "
          "trajectories, interspace choices or safety windows.", "",
          "**No public dataset we could find contains a procedural label of any kind.** "
          "That is the gap only clinicians can close, and it is now the whole of the "
          "hospital ask — see `research/annotations/PUBLIC_VS_HOSPITAL_ANNOTATION_GAP.md`.", "",
          "## What V1 got wrong", "",
          "V1 recorded the anchor dataset as unreachable and concluded that no public "
          "real human transcutaneous lumbar ultrasound existed. **The dataset is public, "
          "CC-BY-4.0, and we now hold the entire annotated subset.** Only our "
          "workstation's network route was blocked. Full correction, including the "
          "retracted and superseded claims: `research/datasets/V2_ACCESS_CORRECTION.md`.", "",
          "exp001–exp004 (porcine, intraoperative) are retained but downgraded to "
          "**secondary methodological evidence**.", "",
          "## Reading order", "",
          "1. `00_VISUAL_INDEX.html` — the evidence, visually",
          "2. `00_TREASURE_MAP.md` — direct paths to the best assets",
          "3. `research/datasets/V2_ACCESS_CORRECTION.md` — what changed and why",
          "4. `research/datasets/KULEUVEN_LABEL_AUDIT.md` — what the data really contains",
          "5. `RESULTS_LEDGER.csv` / `CLAIMS_LEDGER.csv` — every number, traced",
          "6. `deliverables/paper_v2_assets/` — figures and the claims that are allowed", "",
          "## Reproducing", "", "```bash",
          "python tools/download_kuleuven_subset.py --group labels --group recon --group meta",
          "python tools/verify_kuleuven_subset.py",
          "python tools/build_lumbar_dataset.py",
          "python tools/cache_lumbar_arrays.py",
          "./.venv/Scripts/python scripts/experiments/exp005_lumbar_bone_seg.py --epochs 12 --base 16 --height 320 --width 160",
          "./.venv/Scripts/python scripts/experiments/exp006_lumbar_uncertainty.py",
          "python tools/build_visual_library.py && python tools/build_contact_sheets.py",
          "python tools/build_prediction_figures.py && python tools/build_hero_figures.py",
          "python tools/qa_visual_evidence.py", "```", ""]
    pathlib.Path("START_HERE.md").write_text("\n".join(S), encoding="utf-8")

    # ---------------- TREASURE MAP ----------------
    T = ["# Treasure map", "",
         "## REAL HUMAN LUMBAR ULTRASOUND — OPEN THESE FIRST", ""]
    picks = [
        ("Best raw + expert annotation (side by side)", "side_by_side"),
        ("Expert overlay, handheld", "hus"),
        ("Expert overlay, robot-assisted", "rus"),
        ("Our prediction vs expert, held-out subject", "prediction_overlays"),
        ("Failure / high uncertainty", "failures"),
        ("Difficult cases and expert-left-empty frames", "difficult_cases"),
    ]
    for label, sub in picks:
        p = best_asset(sub)
        T.append(f"- **{label}** — `{p}`" if p else
                 f"- **{label}** — _not generated_")
    cs = sorted((VIS / "contact_sheets").glob("*.png")) if (VIS / "contact_sheets").exists() else []
    for c in cs:
        T.append(f"- **Contact sheet** — `{c.as_posix()}`")
    for f in ("FIGURE_1_REAL_LUMBAR_EVIDENCE_PIPELINE.png", "FIGURE_2_HUMAN_LUMBAR_AI_RESULTS.png"):
        p = pathlib.Path("deliverables/paper_v2_assets") / f
        T.append(f"- **{f.split('.')[0]}** — `{p.as_posix()}`" if p.exists()
                 else f"- **{f.split('.')[0]}** — _not generated_")

    T += ["", "## Asset counts", "", "| Directory | Files |", "|---|---|"]
    for d in ("raw", "expert_labels", "expert_overlays", "side_by_side", "hus", "rus",
              "predictions", "prediction_overlays", "uncertainty", "failures",
              "difficult_cases", "contact_sheets", "publication_candidates"):
        T.append(f"| `visuals/ultrasound/real_human_lumbar/{d}` | {n(d)} |")

    T += ["", "## Where the evidence is", "",
          "| What | Where |", "|---|---|",
          "| Every number, traced to a file | `RESULTS_LEDGER.csv` |",
          "| Every claim, with V2 status | `CLAIMS_LEDGER.csv` |",
          "| Per-asset provenance and licence | `visuals/ultrasound/real_human_lumbar/ANNOTATION_PROVENANCE.csv` |",
          "| Licence verification per source | `PIXEL_LICENSE_LEDGER.csv` |",
          "| Attribution text | `visuals/ultrasound/real_human_lumbar/IMAGE_ATTRIBUTION.md` |",
          "| Download provenance + MD5 | `provenance/KULEUVEN_DOWNLOAD_LOG.csv` |",
          "| Independent verification | `KULEUVEN_VERIFICATION_REPORT.json` |",
          "| Acceptance gate result | `QA_VISUAL_EVIDENCE_REPORT.json` |",
          "| Redistributable data sample | `evidence_samples/kuleuven_lumbar/` |", "",
          "## What is NOT here", "",
          "- No puncture target, trajectory or outcome — **none exists in any public dataset**",
          "- No JHU pixels — that dataset declares no licence",
          "- No SUID pixels — request-only, not public",
          "- No hardware, no safety case — the robotic system is a proposal", ""]
    pathlib.Path("00_TREASURE_MAP.md").write_text("\n".join(T), encoding="utf-8")
    print("wrote START_HERE.md and 00_TREASURE_MAP.md")
    if matrix:
        print(f"  matrix cells filled: {len(matrix)}")


if __name__ == "__main__":
    main()
