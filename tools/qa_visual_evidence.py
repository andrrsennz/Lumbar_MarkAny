#!/usr/bin/env python3
"""
qa_visual_evidence.py -- HARD ACCEPTANCE GATE for the V2 evidence package.

V1 shipped with empty `visuals/ultrasound/` directories. This gate exists so
that cannot happen again: packaging is refused unless the project physically
contains real human lumbar ultrasound pixels, their real expert annotations,
overlays, model predictions, failure cases and provenance.

Every check reports PASS/FAIL with the actual number found. Exit code is
non-zero if any required check fails, so it can gate CI or packaging.

Run:  python tools/qa_visual_evidence.py
      python tools/qa_visual_evidence.py --json qa_report.json
"""
from __future__ import annotations
import argparse
import csv
import json
import pathlib
import sys

import numpy as np
from PIL import Image

VIS = pathlib.Path("visuals/ultrasound/real_human_lumbar")
PROC = pathlib.Path("data/processed/kuleuven_lumbar")
EXP5 = pathlib.Path("experiments/exp005_lumbar_bone_seg")
EXP6 = pathlib.Path("experiments/exp006_lumbar_uncertainty")


class QA:
    def __init__(self):
        self.checks = []

    def check(self, name, ok, found, want, detail="", required=True):
        self.checks.append(dict(name=name, passed=bool(ok), found=found,
                                required_minimum=want, detail=detail,
                                required=required))
        flag = "PASS" if ok else ("FAIL" if required else "WARN")
        print(f"  [{flag}] {name:52s} found={found!s:>8}  need>={want}  {detail}")
        return ok

    @property
    def failed(self):
        return [c for c in self.checks if c["required"] and not c["passed"]]


def count_png(d: pathlib.Path) -> int:
    return len(list(d.glob("*.png"))) if d.exists() else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="QA_VISUAL_EVIDENCE_REPORT.json")
    a = ap.parse_args()
    q = QA()

    print("=" * 96)
    print("V2 VISUAL EVIDENCE GATE -- real human lumbar ultrasound must be physically present")
    print("=" * 96)

    # ---- 1. processed dataset ------------------------------------------------
    print("\n1. Processed dataset (real human lumbar frames + expert masks)")
    n_img = count_png(PROC / "images")
    n_msk = count_png(PROC / "masks")
    q.check("processed ultrasound frames", n_img >= 5000, n_img, 5000)
    q.check("processed expert masks", n_msk >= 5000, n_msk, 5000)
    q.check("frames and masks paired", n_img == n_msk, f"{n_img}/{n_msk}", "equal")

    subjects = mods = 0
    if (PROC / "index.csv").exists():
        rows = list(csv.DictReader(open(PROC / "index.csv", encoding="utf-8")))
        subjects = len({r["subject"] for r in rows})
        mods = len({r["modality"] for r in rows})
        ann = sum(1 for r in rows if r["empty_label"] != "True")
        q.check("distinct human subjects", subjects >= 5, subjects, 5)
        q.check("acquisition modalities (HUS+RUS)", mods >= 2, mods, 2)
        q.check("frames with non-empty expert annotation", ann >= 3000, ann, 3000)
    else:
        q.check("index.csv present", False, 0, 1)

    # ---- 2. visual library ---------------------------------------------------
    print("\n2. Curated visual library")
    for sub, want in [("raw", 20), ("expert_labels", 20), ("expert_overlays", 20),
                      ("side_by_side", 20), ("hus", 5), ("rus", 5),
                      ("difficult_cases", 5)]:
        n = count_png(VIS / sub)
        q.check(f"visuals/{sub}", n >= want, n, want)

    n_pred = count_png(VIS / "predictions")
    n_pov = count_png(VIS / "prediction_overlays")
    q.check("visuals/predictions (our model)", n_pred >= 10, n_pred, 10)
    q.check("visuals/prediction_overlays", n_pov >= 10, n_pov, 10)
    n_fail = count_png(VIS / "failures")
    q.check("visuals/failures", n_fail >= 5, n_fail, 5)
    n_unc = count_png(VIS / "uncertainty")
    q.check("visuals/uncertainty", n_unc >= 5, n_unc, 5, required=False)
    n_cs = count_png(VIS / "contact_sheets")
    q.check("contact sheets", n_cs >= 3, n_cs, 3)
    n_pub = count_png(VIS / "publication_candidates")
    q.check("publication candidates", n_pub >= 2, n_pub, 2)

    # ---- 3. the pixels must not be blank ------------------------------------
    print("\n3. Content sanity (assets must contain real image data, not blanks)")
    blanks = checked = 0
    for d in ("raw", "expert_overlays"):
        for p in sorted((VIS / d).glob("*.png"))[:25]:
            arr = np.asarray(Image.open(p).convert("L"))
            checked += 1
            if arr.std() < 3.0:
                blanks += 1
    q.check("sampled assets that are non-blank", blanks == 0,
            f"{checked-blanks}/{checked}", "all", f"{blanks} blank")

    # overlays must actually differ from the raw frame
    diff_ok = 0
    ov = sorted((VIS / "expert_overlays").glob("*.png"))[:10]
    for p in ov:
        raw = VIS / "raw" / p.name
        if not raw.exists():
            continue
        a_ = np.asarray(Image.open(p).convert("RGB")).astype(int)
        b_ = np.asarray(Image.open(raw).convert("RGB")).astype(int)
        if a_.shape == b_.shape and np.abs(a_ - b_).sum() > 0:
            diff_ok += 1
    q.check("overlays differ from their raw frame", diff_ok >= min(8, len(ov)),
            diff_ok, min(8, len(ov)))

    # ---- 4. provenance -------------------------------------------------------
    print("\n4. Provenance and licensing")
    prov = VIS / "ANNOTATION_PROVENANCE.csv"
    n_prov = 0
    if prov.exists():
        pr = list(csv.DictReader(open(prov, encoding="utf-8")))
        n_prov = len(pr)
        types = {r.get("evidence_type") for r in pr}
        q.check("provenance rows", n_prov >= 20, n_prov, 20)
        q.check("evidence_type recorded (A/B/C)", bool(types & {"A", "B", "C"}),
                ",".join(sorted(t for t in types if t)), "A|B|C")
        lic = {r.get("licence") for r in pr}
        q.check("licence recorded for every asset",
                all(r.get("licence") for r in pr), len(lic), "non-empty")
    else:
        q.check("ANNOTATION_PROVENANCE.csv", False, 0, 20)
    q.check("PIXEL_LICENSE_LEDGER.csv",
            pathlib.Path("PIXEL_LICENSE_LEDGER.csv").exists(), "-", "present")

    # ---- 5. direct-human experiment -----------------------------------------
    print("\n5. Direct-human-lumbar experiment")
    res = EXP5 / "results.json"
    n_res = 0
    if res.exists():
        r = json.loads(res.read_text(encoding="utf-8"))
        n_res = len(r)
        q.check("exp005 result records", n_res >= 6, n_res, 6)
        subj_eval = {s for rec in r for s in rec.get("test_subjects", [])}
        q.check("subjects appearing in held-out tests", len(subj_eval) >= 5,
                len(subj_eval), 5)
        mods_eval = {rec.get("test_modality") for rec in r}
        q.check("both modalities evaluated", len(mods_eval) >= 2,
                ",".join(sorted(m for m in mods_eval if m)), 2)
        has_metric = all(rec.get("subject_mean_dice") is not None for rec in r)
        q.check("every record carries a subject-level metric", has_metric,
                n_res, "all")
    else:
        q.check("exp005 results.json", False, 0, 1)
    q.check("exp006 uncertainty on human lumbar data",
            (EXP6 / "metrics.json").exists(), "-", "present", required=False)

    # ---- verdict -------------------------------------------------------------
    print("\n" + "=" * 96)
    fails = q.failed
    status = "PHASE COMPLETE" if not fails else "PHASE NOT COMPLETE"
    print(f"VERDICT: {status}")
    if fails:
        print(f"\n{len(fails)} required check(s) failed:")
        for c in fails:
            print(f"   - {c['name']}: found {c['found']}, need >= {c['required_minimum']}")
    print("=" * 96)

    report = dict(status=status, n_checks=len(q.checks),
                  n_failed=len(fails), checks=q.checks)
    pathlib.Path(a.json).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"report -> {a.json}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
