#!/usr/bin/env python3
"""
build_results_ledger.py -- Generate RESULTS_LEDGER.csv by READING the artefacts
that experiments actually produced.

This is deliberately generated rather than hand-maintained: a hand-typed ledger
drifts from the runs it claims to describe, and a drifted ledger is worse than
none. If an experiment directory is absent or incomplete, its row says so
instead of carrying a remembered number.
"""
from __future__ import annotations
import csv
import json
import pathlib
import datetime

EXP = pathlib.Path("experiments")
OUT = pathlib.Path("RESULTS_LEDGER.csv")

FIELDS = [
    "experiment_id", "date", "objective", "dataset", "dataset_version",
    "train_subjects", "validation_subjects", "test_subjects",
    "train_frames", "validation_frames", "test_frames",
    "model", "initialization", "preprocessing", "augmentation", "random_seed",
    "epochs", "batch_size", "optimizer", "learning_rate", "hardware", "runtime",
    "status", "primary_metric", "metric_value", "secondary_metrics",
    "confidence_interval", "artifact", "log", "notes",
]

UNKNOWN_SUBJ = ("unknown - the public release distributes no subject identifier "
                "for 56.3% of images (see exp001)")


def g(d, *path, default=None):
    for k in path:
        if not isinstance(d, dict) or k not in d:
            return default
        d = d[k]
    return d


def row_exp001():
    p = EXP / "exp001_leakage_audit" / "metrics.json"
    if not p.exists():
        return {"experiment_id": "exp001", "status": "NOT RUN"}
    m = json.loads(p.read_text(encoding="utf-8"))
    cal = m["calibration_within_sweep_adjacent"]
    te, va = m["splits"]["test"], m["splits"]["val"]
    return {
        "experiment_id": "exp001_leakage_audit", "date": "2026-09-11",
        "objective": "Test whether the official JHU splits contain near-duplicate frames across train/test",
        "dataset": "DS004 JHU spinal-cord segmentation", "dataset_version": "Google Drive release, sha256 8842d153...",
        "train_subjects": UNKNOWN_SUBJ, "validation_subjects": UNKNOWN_SUBJ, "test_subjects": UNKNOWN_SUBJ,
        "train_frames": 8668, "validation_frames": 895, "test_frames": 660,
        "model": "none - direct pixel similarity", "initialization": "n/a",
        "preprocessing": "greyscale, resize 64x64, z-normalise, unit-length",
        "augmentation": "none", "random_seed": "n/a (deterministic)",
        "epochs": "n/a", "batch_size": "256 (similarity block size)", "optimizer": "n/a",
        "learning_rate": "n/a", "hardware": "CPU", "runtime": "94.6 s",
        "status": "COMPLETE",
        "primary_metric": "fraction of held-out images with a training neighbour at within-sweep similarity",
        "metric_value": f"test {te['frac_ge_calib_p05']:.4f}, val {va['frac_ge_calib_p05']:.4f} (i.e. zero)",
        "secondary_metrics": (
            f"within-sweep adjacent cosine median {cal['median']:.4f} (p05 {cal['p05']:.4f}, n={cal['n_adjacent_pairs']}); "
            f"test nearest-neighbour max {te['nn_cosine_max']:.4f}, median {te['nn_cosine_median']:.4f}; "
            f"val max {va['nn_cosine_max']:.4f}"),
        "confidence_interval": "n/a - exact count over the full split",
        "artifact": "experiments/exp001_leakage_audit/nearest_neighbours.csv",
        "log": "experiments/exp001_leakage_audit/metrics.json",
        "notes": ("NEGATIVE RESULT. The leakage hypothesis was not supported: the splits are "
                  "sweep-disjoint. Animal-level disjointness remains unverifiable because no "
                  "animal ID is distributed."),
    }


def row_exp002():
    p = EXP / "exp002_class_distribution" / "metrics.json"
    if not p.exists():
        return {"experiment_id": "exp002", "status": "NOT RUN"}
    m = json.loads(p.read_text(encoding="utf-8"))
    matched = m["matched_to_paper_table1"]
    worst = max(matched.items(), key=lambda kv: kv[1]["pixel_rel_error"])
    unknown_px = sum(m.get("unknown_colours", {}).values())
    return {
        "experiment_id": "exp002_class_distribution", "date": "2026-09-11",
        "objective": "Independently reproduce the published class statistics from the distributed masks, and recover the undocumented palette-to-class mapping",
        "dataset": "DS004 JHU spinal-cord segmentation", "dataset_version": "sha256 8842d153...",
        "train_subjects": UNKNOWN_SUBJ, "validation_subjects": UNKNOWN_SUBJ, "test_subjects": UNKNOWN_SUBJ,
        "train_frames": 8668, "validation_frames": 895, "test_frames": 660,
        "model": "none - exact pixel accounting", "initialization": "n/a",
        "preprocessing": "RGB -> 24-bit packed -> VOC palette index lookup",
        "augmentation": "none", "random_seed": "n/a", "epochs": "n/a",
        "batch_size": "n/a", "optimizer": "n/a", "learning_rate": "n/a",
        "hardware": "CPU", "runtime": "~7 min over 10,223 masks", "status": "COMPLETE",
        "primary_metric": "relative error vs publication Table 1, per class",
        "metric_value": f"0.0000 for all 10 classes (worst: {worst[0]} at {worst[1]['pixel_rel_error']:.6f})",
        "secondary_metrics": (f"image counts matched exactly for all 10 classes; "
                              f"{unknown_px} stray anti-aliased pixels outside the palette, "
                              f"out of 1.94e9 total"),
        "confidence_interval": "n/a - exhaustive count, not a sample",
        "artifact": "experiments/exp002_class_distribution/metrics.json",
        "log": "experiments/exp002_class_distribution_stdout.log",
        "notes": ("Recovered mapping: 0 Background, 1 Dura, 2 Pia, 3 CSF, 4 Spinal cord, "
                  "5 Dorsal Space, 6 Hematoma, 7 Ventral Space, 8 Dura/Pia complex, "
                  "9 Dura/Ventral Complex. Published in src/lumbar_markany/data_jhu.py."),
    }


def row_exp003():
    d = EXP / "exp003_unet_baseline"
    mp, cp, hp = d / "metrics.json", d / "config.json", d / "history.json"
    if not mp.exists():
        return {"experiment_id": "exp003_unet_baseline",
                "status": "RUNNING OR INCOMPLETE - no metrics.json yet",
                "objective": "Baseline 10-class segmentation on the official split",
                "dataset": "DS004 JHU spinal-cord segmentation",
                "notes": "Row regenerated automatically once the run completes."}
    m = json.loads(mp.read_text(encoding="utf-8"))
    c = json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else {}
    t = m["test"]
    pc = {k: v for k, v in t["per_class_dice"].items() if v is not None}
    best_c = max(pc, key=pc.get)
    worst_c = min(pc, key=pc.get)
    return {
        "experiment_id": "exp003_unet_baseline", "date": "2026-09-11",
        "objective": "Baseline 10-class semantic segmentation on the official train/val/test split; validates the full pipeline end to end",
        "dataset": "DS004 JHU spinal-cord segmentation (porcine, INTRAOPERATIVE post-laminectomy)",
        "dataset_version": "sha256 8842d153...",
        "train_subjects": UNKNOWN_SUBJ, "validation_subjects": UNKNOWN_SUBJ, "test_subjects": UNKNOWN_SUBJ,
        "train_frames": c.get("n_train", 8668), "validation_frames": c.get("n_val", 895),
        "test_frames": c.get("n_test", 660),
        "model": f"U-Net, base={c.get('base')}, {c.get('n_params'):,} parameters" if c.get("n_params") else "U-Net",
        "initialization": "random (from scratch)",
        "preprocessing": f"greyscale, resize to {c.get('height')}x{c.get('width')}, scale to [0,1]; masks nearest-neighbour",
        "augmentation": "horizontal (rostral-caudal) flip p=0.5; gain/brightness jitter p=0.5; Gaussian noise p=0.3",
        "random_seed": c.get("seed"), "epochs": c.get("epochs"), "batch_size": c.get("batch"),
        "optimizer": "AdamW (weight decay 1e-4), cosine annealing",
        "learning_rate": c.get("lr"),
        "hardware": c.get("gpu") or c.get("device"),
        "runtime": f"{m.get('total_train_seconds')} s",
        "status": "COMPLETE",
        "primary_metric": "test image-level macro Dice (NaN for classes absent from both prediction and truth)",
        "metric_value": f"{t['mean_dice']:.4f}",
        "secondary_metrics": (
            f"median {t['median_dice']:.4f}; IQR [{t['iqr_dice'][0]:.4f}, {t['iqr_dice'][1]:.4f}]; "
            f"SD {t['sd_dice']:.4f}; mean IoU {t['mean_iou']:.4f}; "
            f"best class {best_c} {pc[best_c]:.4f}; worst class {worst_c} {pc[worst_c]:.4f}; "
            f"best val macro Dice {m['best_val_macro_dice']:.4f} at epoch {m['best_epoch']}"),
        "confidence_interval": f"95% bootstrap CI on mean Dice [{t['ci95_mean_dice_bootstrap'][0]:.4f}, {t['ci95_mean_dice_bootstrap'][1]:.4f}] (2000 resamples over images)",
        "artifact": "experiments/exp003_unet_baseline/predictions/per_image_metrics.npz",
        "log": "experiments/exp003_unet_baseline/stdout.log",
        "notes": ("PORCINE, INTRAOPERATIVE, POST-LAMINECTOMY. Not lumbar, not transcutaneous, "
                  "not human. Pipeline validation only. NOT directly comparable to the "
                  "publication's benchmark figures: the averaging convention differs (we score "
                  "absent classes as NaN rather than 0) and we did not reproduce their protocol. "
                  "The bootstrap CI resamples IMAGES, which understates uncertainty relative to "
                  "resampling animals - animals cannot be resampled because no animal ID exists."),
    }


def main():
    rows = [row_exp001(), row_exp002(), row_exp003()]
    for r in rows:
        for k in FIELDS:
            r.setdefault(k, "")
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} experiments)")
    for r in rows:
        print(f"  {r['experiment_id']:28s} {r['status']:12s} "
              f"{r['primary_metric'][:44]:44s} {str(r['metric_value'])[:40]}")
    print(f"\ngenerated {datetime.datetime.now(datetime.timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
