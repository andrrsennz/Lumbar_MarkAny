#!/usr/bin/env python3
"""
build_results_ledger_v2.py -- Regenerate RESULTS_LEDGER.csv from the artefacts
that experiments actually produced, now covering the V2 direct-human-lumbar
runs alongside the V1 porcine ones.

Generated, never hand-typed: a ledger that drifts from its runs is worse than
no ledger. Each V1 row is additionally stamped with `evidence_class` so nobody
can mistake porcine intraoperative results for human lumbar evidence.
"""
from __future__ import annotations
import csv
import json
import pathlib

import numpy as np

EXP = pathlib.Path("experiments")
OUT = pathlib.Path("RESULTS_LEDGER.csv")

FIELDS = ["experiment_id", "evidence_class", "date", "objective", "dataset",
          "species_and_approach", "dataset_version", "subjects_total",
          "train_subjects", "test_subjects", "train_frames", "test_frames",
          "split_strategy", "model", "initialization", "preprocessing",
          "augmentation", "random_seed", "epochs", "batch_size", "optimizer",
          "learning_rate", "hardware", "runtime", "status", "primary_metric",
          "metric_value", "secondary_metrics", "confidence_interval",
          "artifact", "log", "notes"]

SECONDARY = ("SECONDARY METHODOLOGICAL EVIDENCE -- porcine, intraoperative, "
             "post-laminectomy. NOT evidence for a human lumbar-puncture product.")
PRIMARY = "PRIMARY -- real human transcutaneous lumbar ultrasound"


def v1_rows():
    """Carry the V1 rows forward verbatim where they exist, restamped."""
    rows = []
    old = pathlib.Path("RESULTS_LEDGER_V1.csv")
    src = old if old.exists() else OUT
    if not src.exists():
        return rows
    for r in csv.DictReader(open(src, encoding="utf-8")):
        if not r.get("experiment_id", "").startswith(("exp001", "exp002", "exp003", "exp004")):
            continue
        r.setdefault("evidence_class", "")
        r["evidence_class"] = SECONDARY
        r["species_and_approach"] = "porcine, intraoperative, post-laminectomy spinal cord"
        r["split_strategy"] = "official release split (verified sweep-disjoint in exp001)"
        r["subjects_total"] = "unknown - no animal identifier is distributed"
        rows.append({k: r.get(k, "") for k in FIELDS})
    return rows


def exp005_rows():
    p = EXP / "exp005_lumbar_bone_seg" / "results.json"
    c = EXP / "exp005_lumbar_bone_seg" / "config.json"
    if not p.exists():
        return [{"experiment_id": "exp005_lumbar_bone_seg", "status": "NOT RUN",
                 "evidence_class": PRIMARY}]
    res = json.loads(p.read_text(encoding="utf-8"))
    cfg = json.loads(c.read_text(encoding="utf-8")) if c.exists() else {}
    rows = []
    for r in res:
        ps = r["per_subject"]
        rows.append(dict(
            experiment_id=f"exp005_fold{r['fold']}_train{r['train_regime']}_test{r['test_modality']}",
            evidence_class=PRIMARY, date="2026-09-11",
            objective=("Expert bone-surface segmentation in real human lumbar ultrasound; "
                       f"train on {r['train_regime']}, evaluate on held-out {r['test_modality']} subjects"),
            dataset="KU Leuven / Balgrist lumbar spine ultrasound (doi:10.48804/3XPCAE, CC-BY-4.0)",
            species_and_approach=("HUMAN, in-vivo, transcutaneous lumbar; healthy volunteers "
                                  "aged 20-35 BMI 19-26, PRONE, 10 MHz LINEAR probe"),
            dataset_version="US/US_labels, 18 archives, MD5-verified",
            subjects_total=9,
            train_subjects="|".join(r["train_subjects"]),
            test_subjects="|".join(r["test_subjects"]),
            train_frames=r["n_train_frames"], test_frames=r["n_frames_annotated"],
            split_strategy="3-fold grouped CV, SUBJECT-DISJOINT; stats aggregated per subject first",
            model=f"U-Net base={cfg.get('base')} ({cfg.get('height')}x{cfg.get('width')})",
            initialization="random (from scratch)",
            preprocessing=("cropped to live ultrasound sector 810x430, resized; masks "
                           "max-pooled so a 1-2 px contour survives"),
            augmentation="LR flip p=0.5; gain/brightness jitter p=0.5; noise p=0.3",
            random_seed=cfg.get("seed"), epochs=cfg.get("epochs"), batch_size=cfg.get("batch"),
            optimizer="AdamW + cosine annealing; Dice + pos-weighted BCE",
            learning_rate=cfg.get("lr"), hardware=cfg.get("gpu"),
            runtime=f"{r['train_history'].get('sec')} s/epoch",
            status="COMPLETE",
            primary_metric="subject-mean Dice (per-subject means, then averaged)",
            metric_value=round(r["subject_mean_dice"], 4),
            secondary_metrics=(
                f"subject-mean tolerance-F1(2px) {r['subject_mean_tol_f1']:.4f}; "
                f"subject-mean IoU {r['subject_mean_iou']:.4f}; "
                f"subject range {r['subject_min_dice']:.4f}-{r['subject_max_dice']:.4f}; "
                f"frame-mean Dice {r['frame_mean_dice']:.4f}; "
                f"empty-label false-positive rate {r['empty_label_false_positive_rate']}"),
            confidence_interval=(f"SD across {r['n_subjects']} test subjects "
                                 f"{r['subject_sd_dice']:.4f} (n is too small for a meaningful CI; "
                                 f"per-subject values: " +
                                 ", ".join(f"{x['subject']}={x['dice']:.3f}" for x in ps) + ")"),
            artifact=f"experiments/exp005_lumbar_bone_seg/per_frame_fold{r['fold']}_{r['train_regime']}_{r['test_modality']}.npz",
            log="experiments/exp005_lumbar_bone_seg/stdout.log",
            notes=("Expert-annotated VISIBLE BONE SURFACE, not a puncture target. Dice is harsh on a "
                   "1-2 px contour, so tolerance-F1 is reported alongside. Frames the expert left "
                   "empty are excluded from Dice (undefined) and scored separately."),
        ))
    return rows


def exp006_row():
    p = EXP / "exp006_lumbar_uncertainty" / "metrics.json"
    if not p.exists():
        return [{"experiment_id": "exp006_lumbar_uncertainty", "status": "NOT RUN",
                 "evidence_class": PRIMARY}]
    m = json.loads(p.read_text(encoding="utf-8"))
    ab = m["abstention"].get("30%", {})
    pm = m.get("per_modality", {})
    return [dict(
        experiment_id="exp006_lumbar_uncertainty", evidence_class=PRIMARY, date="2026-09-11",
        objective=("Does MC-dropout uncertainty track real error on REAL HUMAN LUMBAR ultrasound, "
                   "and can abstention improve what remains? (exp004 asked this on porcine data)"),
        dataset="KU Leuven / Balgrist (doi:10.48804/3XPCAE, CC-BY-4.0)",
        species_and_approach="HUMAN, in-vivo, transcutaneous lumbar",
        dataset_version="US/US_labels, MD5-verified", subjects_total=9,
        train_subjects="(uses exp005 checkpoints)", test_subjects="all 9, each held out in its own fold",
        train_frames="n/a (inference)", test_frames=m["n_annotated"],
        split_strategy="subject-held-out via the exp005 folds",
        model=f"exp005 U-Net, regime {m['regime']}, bottleneck dropout re-enabled (BatchNorm in eval)",
        initialization="exp005 checkpoints", preprocessing="as exp005", augmentation="none",
        random_seed="stochastic by design", epochs="n/a", batch_size=16,
        optimizer="n/a", learning_rate="n/a", hardware="NVIDIA GeForce RTX 2060",
        runtime=f"{m['mc_passes']} MC passes over every held-out frame", status="COMPLETE",
        primary_metric="Spearman rho between MC-dropout uncertainty and per-frame Dice",
        metric_value=(f"entropy {m['spearman_entropy_vs_dice']:+.4f}; "
                      f"pass-SD {m['spearman_pass_sd_vs_dice']:+.4f}"),
        secondary_metrics=(
            f"mean Dice {m['mean_dice']:.4f}; abstaining on the most-uncertain 30% gives "
            f"{ab.get('dice_on_retained', float('nan')):.4f} on retained vs "
            f"{ab.get('dice_on_declined', float('nan')):.4f} on declined; " +
            "; ".join(f"{k}: rho {v['spearman_entropy_vs_dice']:+.3f}, Dice {v['mean_dice']:.3f}"
                      for k, v in pm.items())),
        confidence_interval="per-subject rho reported in metrics.json; 9 subjects",
        artifact="experiments/exp006_lumbar_uncertainty/per_frame.npz",
        log="experiments/exp006_lumbar_uncertainty/metrics.json",
        notes=("Validates the uncertainty MECHANISM on real human lumbar data. Not a safety claim; "
               "the model is not calibrated for clinical use and this says nothing about puncture "
               "targeting. Supersedes exp004 for any human-lumbar statement."),
    )]


def main():
    if OUT.exists() and not pathlib.Path("RESULTS_LEDGER_V1.csv").exists():
        OUT.replace("RESULTS_LEDGER_V1.csv")
    rows = v1_rows() + exp005_rows() + exp006_row()
    for r in rows:
        for k in FIELDS:
            r.setdefault(k, "")
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    for r in rows:
        cls = "PRIMARY" if r["evidence_class"].startswith("PRIMARY") else "secondary"
        print(f"  {r['experiment_id']:46s} {cls:10s} {str(r['metric_value'])[:34]}")


if __name__ == "__main__":
    main()
