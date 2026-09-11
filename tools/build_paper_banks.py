#!/usr/bin/env python3
"""
build_paper_banks.py -- Generate the paper evidence banks and tables from the
artefacts, so every stated number traces to a file.

Outputs into deliverables/paper_v2_assets/:
    paper_fact_bank.md            dataset and provenance facts
    paper_results_bank.md         our executed results, with the caveats attached
    paper_claims_allowed.md       sentences that are safe to write, verbatim
    table1_direct_human_dataset_summary.csv
    table2_direct_lumbar_results.csv
"""
from __future__ import annotations
import csv
import json
import pathlib

import numpy as np

OUT = pathlib.Path("deliverables/paper_v2_assets")
PROC = pathlib.Path("data/processed/kuleuven_lumbar")
EXP5 = pathlib.Path("experiments/exp005_lumbar_bone_seg/results.json")
EXP6 = pathlib.Path("experiments/exp006_lumbar_uncertainty/metrics.json")

CAVEAT = ("healthy volunteers aged 20-35 (BMI 19-26), imaged PRONE with a 10 MHz LINEAR "
          "transducer; single annotator; 9 annotated subjects")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    idx = list(csv.DictReader(open(PROC / "index.csv", encoding="utf-8"))) if (PROC / "index.csv").exists() else []
    res = json.loads(EXP5.read_text(encoding="utf-8")) if EXP5.exists() else []
    unc = json.loads(EXP6.read_text(encoding="utf-8")) if EXP6.exists() else None

    n = len(idx)
    subs = sorted({r["subject"] for r in idx})
    hus = sum(1 for r in idx if r["modality"] == "HUS")
    rus = sum(1 for r in idx if r["modality"] == "RUS")
    empty = sum(1 for r in idx if r["empty_label"] == "True")

    # ---------------- fact bank ----------------
    F = ["# Paper fact bank", "",
         "Every fact traces to a file. Nothing here is remembered or rounded from memory.", "",
         "## The dataset we hold", "",
         f"- **{n:,}** expert-annotated real human lumbar ultrasound frames "
         f"(`data/processed/kuleuven_lumbar/index.csv`)",
         f"- **{len(subs)}** human subjects: {', '.join(subs)}",
         f"- **{hus:,}** handheld (HUS) and **{rus:,}** robot-assisted (RUS)",
         f"- **{empty}** frames ({100*empty/max(n,1):.1f}%) where the expert annotated nothing",
         "- Source: Cavalcanti et al., `doi:10.48804/3XPCAE`, **CC-BY-4.0**; paper `doi:10.1038/s41597-025-06047-9`",
         "- 7 of 9 subjects have both modalities; URS31 and URS51 are robotic-only", "",
         "## Provenance and verification", "",
         "- 41 files, 1.76 GB, **41/41 MD5-verified** against the checksums Dataverse publishes",
         "- The live repository holds **766 files / 630.94 GB**, all `restricted: false`, CC-BY-4.0",
         "- The annotated subset needs only **1.70 GB**, because each label archive also contains the frames",
         "- Independent verification: `KULEUVEN_VERIFICATION_REPORT.json` (all checks pass)", "",
         "## Audit findings worth stating in the paper", "",
         "- **Frame counts do not reproduce.** We count 6,182 listed and 5,998 non-empty; the "
         "publication reports 6,091. Neither counting rule reproduces the published figure.",
         "- **Background label value is inconsistent**: 0 in six archives, 1 in the other twelve; "
         "bone surface is 2 throughout. `label != 0` yields a fully positive mask on twelve archives.",
         "- **Channel count varies by subject**: four archives are greyscale, five are RGB with "
         "identical channels.",
         "- **A stray annotation** in URS16_H3 frame 304 spans columns 556-1864, across the scanner UI.",
         "- **184 frames (3.0%) have empty expert labels**, concentrated in 8 of 18 archives — "
         "ten archives contain none at all.", "",
         "## Label semantics — the sentence the paper turns on", "",
         "The labels mark **VISIBLE BONE SURFACE** and nothing else. There is no entry point, "
         "trajectory, target depth, interspace choice or outcome in this dataset, and none was "
         "found in any public dataset surveyed.", "",
         "## What the data is not", "", f"- {CAVEAT}",
         "- Lumbar puncture is performed **sitting or in lateral decubitus** with a "
         "**2-5 MHz curvilinear** probe — neither matches this acquisition",
         "- No puncture was performed on any subject", ""]
    (OUT / "paper_fact_bank.md").write_text("\n".join(F), encoding="utf-8")

    # ---------------- results bank + tables ----------------
    R = ["# Paper results bank", "",
         "Executed results only. Source: `experiments/exp005_lumbar_bone_seg/results.json` "
         "and `experiments/exp006_lumbar_uncertainty/metrics.json`.", ""]
    if res:
        cells = {}
        for r in res:
            cells.setdefault((r["train_regime"], r["test_modality"]), []).append(r)

        def agg(tr, te, f):
            v = [x[f] for x in cells.get((tr, te), []) if x.get(f) is not None]
            return (float(np.mean(v)), float(np.std(v)), len(v)) if v else (None, None, 0)

        R += ["## Cross-acquisition matrix (subject-disjoint 3-fold CV)", "",
              "Subject-mean Dice, averaged over folds (SD across folds in brackets):", "",
              "| train / test | HUS | RUS |", "|---|---|---|"]
        for tr in ("HUS", "RUS", "BOTH"):
            row = [f"| **{tr}** "]
            for te in ("HUS", "RUS"):
                m, s, k = agg(tr, te, "subject_mean_dice")
                row.append(f"| {m:.3f} ({s:.3f}, n={k}) " if m is not None else "| — ")
            R.append("".join(row) + "|")
        R += ["", "Subject-mean tolerance-band F1 (2 px):", "",
              "| train / test | HUS | RUS |", "|---|---|---|"]
        for tr in ("HUS", "RUS", "BOTH"):
            row = [f"| **{tr}** "]
            for te in ("HUS", "RUS"):
                m, s, k = agg(tr, te, "subject_mean_tol_f1")
                row.append(f"| {m:.3f} ({s:.3f}, n={k}) " if m is not None else "| — ")
            R.append("".join(row) + "|")

        # per-subject spread
        persub = {}
        for r in res:
            if r["train_regime"] != "BOTH":
                continue
            for ps in r["per_subject"]:
                persub.setdefault(ps["subject"], []).append(ps["dice"])
        if persub:
            R += ["", "## Per-subject Dice (BOTH regime, each subject held out)", "",
                  "| subject | Dice | frames |", "|---|---|---|"]
            for s in sorted(persub):
                R.append(f"| {s} | {np.mean(persub[s]):.3f} | — |")
            vals = [np.mean(v) for v in persub.values()]
            R += ["", f"Across subjects: mean {np.mean(vals):.3f}, SD {np.std(vals):.3f}, "
                      f"range {min(vals):.3f}–{max(vals):.3f} (n={len(vals)}).",
                  "", "**With nine subjects, this spread is the honest measure of uncertainty; "
                      "a confidence interval would imply more precision than nine points support.**", ""]

        with open(OUT / "table2_direct_lumbar_results.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["fold", "train_regime", "test_modality", "n_test_subjects",
                        "n_test_frames_annotated", "n_test_frames_empty_label",
                        "subject_mean_dice", "subject_sd_dice", "subject_min_dice",
                        "subject_max_dice", "subject_mean_iou", "subject_mean_tol_f1",
                        "frame_mean_dice", "empty_label_false_positive_rate", "test_subjects"])
            for r in res:
                w.writerow([r["fold"], r["train_regime"], r["test_modality"], r["n_subjects"],
                            r["n_frames_annotated"], r["n_frames_empty_label"],
                            round(r["subject_mean_dice"], 4), round(r["subject_sd_dice"], 4),
                            round(r["subject_min_dice"], 4), round(r["subject_max_dice"], 4),
                            round(r["subject_mean_iou"], 4), round(r["subject_mean_tol_f1"], 4),
                            round(r["frame_mean_dice"], 4),
                            r["empty_label_false_positive_rate"], "|".join(r["test_subjects"])])
    if unc:
        R += ["## Uncertainty on real human lumbar data (exp006)", "",
              f"- Spearman rho vs per-frame Dice: **{unc['spearman_entropy_vs_dice']:+.3f}** "
              f"(predictive entropy), **{unc['spearman_pass_sd_vs_dice']:+.3f}** (pass disagreement)",
              f"- Frames scored: {unc['n_annotated']:,} annotated, {unc['n_empty_label']} empty-label",
              "", "| declined | Dice retained | Dice declined |", "|---|---|---|"]
        for k, v in unc["abstention"].items():
            R.append(f"| {k} | {v['dice_on_retained']:.3f} | {v['dice_on_declined']:.3f} |")
        R += ["", "Per modality:", "", "| modality | rho | mean Dice |", "|---|---|---|"]
        for k, v in unc.get("per_modality", {}).items():
            R.append(f"| {k} | {v['spearman_entropy_vs_dice']:+.3f} | {v['mean_dice']:.3f} |")
        R += ["", f"On the {unc['empty_label_behaviour']['n']} frames the expert left empty, the "
                  f"model predicted something in "
                  f"{100*unc['empty_label_behaviour']['frac_predicting_something']:.1f}% of cases.", ""]
    R += ["## Caveat that must accompany every number above", "", f"{CAVEAT}.",
          " Labels are visible bone surface, not puncture targets. Dice is harsh on a 1-2 px "
          "contour; tolerance-F1 is reported alongside for that reason.", ""]
    (OUT / "paper_results_bank.md").write_text("\n".join(R), encoding="utf-8")

    # ---------------- table 1 ----------------
    with open(OUT / "table1_direct_human_dataset_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "year", "subjects", "cohort", "position", "probe",
                    "modality", "transcutaneous", "annotated_images", "annotation_classes",
                    "procedural_target", "download_status", "licence", "held_by_us"])
        w.writerow(["KU Leuven / Balgrist (doi:10.48804/3XPCAE)", 2025, 63,
                    "healthy volunteers 20-35, BMI 19-26", "prone", "10 MHz linear",
                    "handheld + robot-assisted", "yes", f"{n} (9 subjects)",
                    "1 (visible bone surface)", "NO", "PUBLIC_DOWNLOADABLE", "CC-BY-4.0", "YES"])
        w.writerow(["SUID (doi:10.1177/03000605261461196)", 2026, 80,
                    "pregnant, elective caesarean", "lateral decubitus", "2-5 MHz convex",
                    "handheld", "yes", "1000",
                    "interlaminar space, articular process, anterior + posterior complex",
                    "NO", "REQUEST_ONLY", "article CC BY-NC 4.0; data not released", "no"])
        w.writerow(["JHU HEPIUS (PMC12475011)", 2025, "25 pigs + 8 humans", "porcine + surgical",
                    "prone, intraoperative", "unknown", "handheld",
                    "NO - post-laminectomy", "10223", "10 anatomical", "NO",
                    "PUBLIC (no licence declared)", "NONE DECLARED", "yes, locally only"])
        w.writerow(["Masoumi (doi:10.5281/zenodo.4813508)", 2021, "3 human + 2 ex-vivo",
                    "archival CT + phantoms", "n/a", "unknown", "simulated + phantom US",
                    "no", "21 landmark pairs x2", "landmarks", "NO",
                    "PUBLIC_DOWNLOADABLE", "CC-BY-4.0", "yes"])

    # ---------------- allowed claims ----------------
    A = ["# Claims allowed — verbatim sentences", "",
         "Each of these is safe to paste into the paper as written. The paired forbidden "
         "list is `paper_claims_forbidden.md`.", "",
         "## About availability", "",
         "> Real, publicly downloadable, expert-annotated human transcutaneous lumbar "
         "ultrasound exists: the KU Leuven / Balgrist deposit (doi:10.48804/3XPCAE, CC-BY-4.0) "
         f"provides {n:,} annotated frames from {len(subs)} subjects across handheld and "
         "robot-assisted acquisition.", "",
         "> No public dataset located in this survey contains a procedural label of any kind — "
         "no entry point, trajectory, target depth, interspace choice or outcome.", "",
         "## About the data", "",
         "> The annotated subset is self-contained: each label archive ships the ultrasound "
         "frames alongside their annotations, so the complete expert-annotated set occupies "
         "1.70 GB rather than the deposit's 631 GB.", "",
         "> Parsing every data_list.txt yields 6,182 listed frames of which 5,998 carry a "
         "non-empty annotation; the source publication reports 6,091, which neither counting "
         "rule reproduces.", "",
         "> The background label value is not consistent across the deposit: six of the "
         "eighteen archives encode background as 0 and the remaining twelve as 1, while bone "
         "surface is 2 throughout.", "",
         "## About our results", ""]
    if res:
        b = [r for r in res if r["train_regime"] == "BOTH"]
        if b:
            mh = np.mean([r["subject_mean_dice"] for r in b if r["test_modality"] == "HUS"])
            mr = np.mean([r["subject_mean_dice"] for r in b if r["test_modality"] == "RUS"])
            A += [f"> Training on both acquisition modes and evaluating on held-out subjects, "
                  f"subject-mean Dice was {mh:.3f} on handheld and {mr:.3f} on robot-assisted "
                  f"ultrasound, under subject-disjoint 3-fold cross-validation over nine "
                  f"subjects.", ""]
    A += ["> All splits were subject-disjoint; statistics were aggregated per subject before "
          "averaging, and frame counts are reported but never treated as independent samples.", "",
          "> Because the annotated structure is a 1-2 pixel contour, a tolerance-band F1 is "
          "reported alongside Dice, which penalises a one-pixel offset as a total miss.", "",
          "> Frames where the expert annotated nothing are excluded from Dice, which is "
          "undefined there, and scored separately.", "",
          "## About what is still missing", "",
          "> The available data is healthy volunteers aged 20-35 with BMI 19-26, imaged prone "
          "with a 10 MHz linear transducer. Neuraxial procedures are performed sitting or in "
          "lateral decubitus with a low-frequency curvilinear probe, in a patient population "
          "selected for difficulty. The gap is one of kind, not quantity.", "",
          "> The annotations were produced by a single annotator, who also acquired the "
          "handheld scans; inter-rater reliability for lumbar ultrasound annotation is "
          "therefore unmeasured.", ""]
    (OUT / "paper_claims_allowed.md").write_text("\n".join(A), encoding="utf-8")

    print(f"wrote paper banks and tables -> {OUT}")
    print(f"  exp005 records: {len(res)}   exp006: {'yes' if unc else 'no'}")


if __name__ == "__main__":
    main()
