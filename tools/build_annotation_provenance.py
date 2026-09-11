#!/usr/bin/env python3
"""
build_annotation_provenance.py -- One row per published visual asset, recording
exactly where its pixels came from and what may lawfully be done with them.

The `evidence_type` column enforces the distinction the project must never
blur:
    A  dataset pixels          -- real ultrasound frames from a dataset
    B  dataset expert labels   -- the source annotations for those frames
    C  publication figure      -- an image printed in a paper; NOT training data
    D  our derived rendering   -- overlays, panels, predictions we produced

Unknown fields are written as UNKNOWN rather than guessed.
"""
from __future__ import annotations
import argparse
import csv
import pathlib

VIS = pathlib.Path("visuals/ultrasound/real_human_lumbar")

FIELDS = ["asset_id", "local_file", "evidence_type", "dataset", "dataset_doi",
          "source_article_doi", "source_institution", "licence", "subject_id",
          "scan_id", "modality", "protocol", "frame_id", "original_frame_path",
          "annotation_source_file", "annotation_type", "annotation_semantics",
          "annotator", "annotator_qualification", "transformation", "cropping",
          "resizing", "overlay_colours", "original_or_derived",
          "redistribution_permitted", "paper_use_permitted", "attribution_text",
          "selection_reason", "notes"]

DOI = "doi:10.48804/3XPCAE"
ART = "10.1038/s41597-025-06047-9"
INST = "KU Leuven (Robot-Assisted Surgery) + Balgrist University Hospital / University of Zurich"
ATTR = ("Cavalcanti NA et al. A large, paired dataset of robotic and handheld lumbar spine "
        "ultrasound with ground-truth CT benchmarking. KU Leuven RDR, doi:10.48804/3XPCAE. "
        "Licensed CC-BY-4.0.")
SEM = ("EXPERT-ANNOTATED VISIBLE BONE SURFACE (label value 2 of {1,2}). NOT a puncture target, "
       "entry point, trajectory, interspace choice or safety window.")
CROP = ("cropped to the live ultrasound sector, rows 150-960 cols 530-960 of the 1920x1080 "
        "screen capture; removes scanner UI, depth ruler and the burned-in study/date banner")


def base_row(r, kind, local, evidence_type, transformation, colours, notes=""):
    return dict(
        asset_id=f"{r['asset_id']}::{kind}", local_file=local,
        evidence_type=evidence_type, dataset="KU Leuven / Balgrist lumbar spine ultrasound",
        dataset_doi=DOI, source_article_doi=ART, source_institution=INST,
        licence="CC-BY-4.0", subject_id=r["subject"], scan_id=r["scan"],
        modality=r["modality"], protocol=r["protocol"], frame_id=r["frame_index"],
        original_frame_path=r["original_path"],
        annotation_source_file=f"US/US_labels/{r['source_archive']}",
        annotation_type="binary pixel mask, thin contour (MetaImage .mhd/.raw, zlib)",
        annotation_semantics=SEM,
        annotator="one physician (publication author N.A.C.), who also acquired the handheld scans",
        annotator_qualification="physician; single annotator, so NO inter-rater agreement exists",
        transformation=transformation, cropping=CROP,
        resizing="none (native sector resolution 810x430)",
        overlay_colours=colours, original_or_derived="derived" if evidence_type == "D" else "original",
        redistribution_permitted="yes, with attribution (CC-BY-4.0)",
        paper_use_permitted="yes, with attribution",
        attribution_text=ATTR, selection_reason=r["selection_reason"], notes=notes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(VIS / "ANNOTATION_PROVENANCE.csv"))
    a = ap.parse_args()

    sel = list(csv.DictReader(open(VIS / "SELECTION.csv", encoding="utf-8")))
    rows = []
    for r in sel:
        uid = r["asset_id"]
        rows.append(base_row(r, "raw", f"visuals/ultrasound/real_human_lumbar/raw/{uid}.png",
                             "A", "decoded from MetaImage, flipped vertically (source is bottom-up), cropped",
                             "none (greyscale)",
                             "Real human in-vivo transcutaneous lumbar ultrasound frame."))
        rows.append(base_row(r, "label", f"visuals/ultrasound/real_human_lumbar/expert_labels/{uid}.png",
                             "B", "label value 2 rendered white on black; flipped and cropped identically to the frame",
                             "white on black",
                             "The source expert annotation, unmodified in content."))
        rows.append(base_row(r, "overlay", f"visuals/ultrasound/real_human_lumbar/expert_overlays/{uid}.png",
                             "D", "expert mask dilated by 1 px for visibility and painted over the frame",
                             "red = expert bone surface",
                             "Dilation is for display only; metrics never use the dilated mask."))
        rows.append(base_row(r, "sidebyside", f"visuals/ultrasound/real_human_lumbar/side_by_side/{uid}.png",
                             "D", "three-panel composite: raw | expert label | overlay",
                             "red = expert bone surface", ""))

    # predictions, if the experiment has produced them
    pred = VIS / "PREDICTION_SELECTION.csv"
    if pred.exists():
        for p in csv.DictReader(open(pred, encoding="utf-8")):
            uid = p["uid"]
            stub = dict(asset_id=uid, subject=p["subject"], scan=p["scan"],
                        modality=p["modality"], protocol="", frame_index="",
                        original_path="UNKNOWN", source_archive=f"{p['subject']}_{p['scan']}.zip",
                        selection_reason=f"{p['kind']} (fold {p['fold']}, regime {p['regime']})")
            rows.append(base_row(
                stub, "prediction",
                f"visuals/ultrasound/real_human_lumbar/prediction_overlays/{uid}.png", "D",
                "five-panel composite: raw | expert label | our prediction | TP-FN-FP error | MC-dropout uncertainty",
                "red = expert, green = our prediction, white/red/blue = TP/FN/FP",
                (f"Prediction by the Lumbar_MarkAny U-Net (exp005). The subject was HELD OUT of the "
                 f"model that predicts on it. Dice {p['dice']}, tolerance-F1 {p['tol_f1']}.")))

    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)
    import collections
    print(f"wrote {len(rows)} provenance rows -> {a.out}")
    print("by evidence_type:", dict(collections.Counter(r["evidence_type"] for r in rows)))


if __name__ == "__main__":
    main()
