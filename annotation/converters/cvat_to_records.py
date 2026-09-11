#!/usr/bin/env python3
"""
cvat_to_records.py -- Convert a CVAT "CVAT for images 1.1" XML export of the
Lumbar_MarkAny annotation schema into flat analysis tables.

Produces three CSVs, deliberately separated because they are different kinds of
evidence and must never be silently pooled:

  frames.csv       Layer A/B/C -- one row per frame: view, quality, level
  anatomy.csv      Layer D     -- one row per annotated structure (visible anatomy)
  planning.csv     Layer F     -- one row per clinician planning label (expert OPINION)

Layer F rows always carry the annotator id and are never merged across
annotators here. Producing a consensus is a separate, explicit step.

Usage:
    python annotation/converters/cvat_to_records.py export.xml --out data/annotations/ \
        --annotator dr_a --session pilot01
"""
from __future__ import annotations
import argparse
import csv
import pathlib
import xml.etree.ElementTree as ET

PLANNING_PREFIX = "PLANNING_"
META_LABEL = "FRAME_METADATA"

FRAME_FIELDS = ["session", "annotator", "image_name", "frame_id", "width", "height",
                "view", "procedural_usability", "bone_visibility",
                "posterior_complex_visibility", "acoustic_window_quality",
                "shadow_severity", "artifact_severity", "presumed_level",
                "annotator_confidence", "no_safe_recommendation", "no_safe_reason"]
ANAT_FIELDS = ["session", "annotator", "image_name", "structure", "geometry_type",
               "n_points", "points", "visibility", "side", "annotator_confidence"]
PLAN_FIELDS = ["session", "annotator", "image_name", "label", "geometry_type",
               "n_points", "points", "physician_confidence", "chosen_level",
               "estimated_target_depth_mm", "reasoning", "reason"]


def attrs(el):
    """CVAT stores per-shape attributes as <attribute name=...>value</attribute>."""
    return {a.get("name"): (a.text or "").strip() for a in el.findall("attribute")}


def shape_points(el):
    raw = el.get("points")
    if raw:
        pts = [p for p in raw.split(";") if p]
        return len(pts), raw
    # box
    if el.tag == "box":
        b = f"{el.get('xtl')},{el.get('ytl')};{el.get('xbr')},{el.get('ybr')}"
        return 2, b
    return 0, ""


def convert(xml_path: pathlib.Path, out: pathlib.Path, session: str, annotator: str):
    root = ET.parse(xml_path).getroot()
    frames, anat, plan = [], [], []

    for image in root.findall("image"):
        name = image.get("name")
        row = {"session": session, "annotator": annotator, "image_name": name,
               "frame_id": image.get("id"), "width": image.get("width"),
               "height": image.get("height"), "no_safe_recommendation": "false",
               "no_safe_reason": ""}

        # ---- tags (Layer A/B/C metadata, and the refusal tag)
        for tag in image.findall("tag"):
            label = tag.get("label")
            a = attrs(tag)
            if label == META_LABEL:
                for k in ("view", "procedural_usability", "bone_visibility",
                          "posterior_complex_visibility", "acoustic_window_quality",
                          "shadow_severity", "artifact_severity", "presumed_level",
                          "annotator_confidence"):
                    if k in a:
                        row[k] = a[k]
            elif label == PLANNING_PREFIX + "NO_SAFE_RECOMMENDATION":
                # A first-class outcome, not a missing value.
                row["no_safe_recommendation"] = "true"
                row["no_safe_reason"] = a.get("reason", "")
        frames.append(row)

        # ---- shapes
        for tagname in ("polygon", "polyline", "points", "box"):
            for sh in image.findall(tagname):
                label = sh.get("label")
                a = attrs(sh)
                n, pts = shape_points(sh)
                rec = {"session": session, "annotator": annotator, "image_name": name,
                       "geometry_type": tagname, "n_points": n, "points": pts}
                if label.startswith(PLANNING_PREFIX):
                    rec.update({
                        "label": label,
                        "physician_confidence": a.get("physician_confidence", ""),
                        "chosen_level": a.get("chosen_level", ""),
                        "estimated_target_depth_mm": a.get("estimated_target_depth_mm", ""),
                        "reasoning": a.get("reasoning", ""),
                        "reason": a.get("reason", ""),
                    })
                    plan.append(rec)
                else:
                    rec.update({
                        "structure": label,
                        "visibility": a.get("visibility", ""),
                        "side": a.get("side", ""),
                        "annotator_confidence": a.get("annotator_confidence", ""),
                    })
                    anat.append(rec)

    out.mkdir(parents=True, exist_ok=True)
    for fname, fields, rows in (("frames.csv", FRAME_FIELDS, frames),
                                ("anatomy.csv", ANAT_FIELDS, anat),
                                ("planning.csv", PLAN_FIELDS, plan)):
        p = out / fname
        # append if the file exists so several annotators accumulate
        new = not p.exists()
        with open(p, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            if new:
                w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in fields})
        print(f"  {fname}: +{len(rows)} rows -> {p}")

    nrefuse = sum(1 for r in frames if r["no_safe_recommendation"] == "true")
    print(f"\nframes: {len(frames)}  anatomy shapes: {len(anat)}  planning shapes: {len(plan)}")
    print(f"frames with NO_SAFE_RECOMMENDATION: {nrefuse}"
          f" ({100*nrefuse/max(len(frames),1):.1f}%)")
    if plan:
        print("NOTE: planning rows are expert OPINION, stored per annotator. "
              "Do not pool across annotators without an explicit consensus step.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xml", help="CVAT for images 1.1 XML export")
    ap.add_argument("--out", default="data/annotations")
    ap.add_argument("--session", required=True)
    ap.add_argument("--annotator", required=True,
                    help="pseudonymous annotator id -- never a real name")
    a = ap.parse_args()
    convert(pathlib.Path(a.xml), pathlib.Path(a.out), a.session, a.annotator)


if __name__ == "__main__":
    main()
