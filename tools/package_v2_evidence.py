#!/usr/bin/env python3
"""
package_v2_evidence.py -- Build the V2 portable evidence package.

The difference from V1 is the whole point: **this package physically contains
real human lumbar ultrasound and its real expert annotations.** V1 shipped
empty `visuals/ultrasound/` directories.

Packaging is REFUSED unless tools/qa_visual_evidence.py passes, so a
pixel-less package cannot be produced by accident.

What goes in
  * every curated visual asset (raw frames, expert labels, overlays,
    predictions, failures, uncertainty, contact sheets, figure candidates)
  * a redistributable sample of the source dataset itself, under
    `evidence_samples/kuleuven_lumbar/` -- lawful because the source is
    CC-BY-4.0 and verified in PIXEL_LICENSE_LEDGER.csv
  * all code, docs, ledgers, manifests, experiment configs/logs/metrics
  * a git bundle carrying the full history

What stays out
  * the 6,182-frame processed set and the 1.76 GB of raw archives
    (re-acquirable with tools/download_kuleuven_subset.py)
  * every JHU pixel -- that dataset declares NO licence
  * model checkpoints and the training cache
"""
from __future__ import annotations
import argparse
import csv
import datetime
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import zipfile

ROOT = pathlib.Path(".")
VIS = pathlib.Path("visuals/ultrasound/real_human_lumbar")
PROC = pathlib.Path("data/processed/kuleuven_lumbar")

INCLUDE_DIRS = ["annotation", "deliverables", "experiments", "figures",
                "provenance", "research", "scripts", "src", "tools", "visuals"]
INCLUDE_FILES = ["README.md", "LICENSE", "requirements.txt", ".gitignore",
                 "CLAIMS_LEDGER.csv", "RESULTS_LEDGER.csv",
                 "PIXEL_LICENSE_LEDGER.csv",
                 "QA_VISUAL_EVIDENCE_REPORT.json",
                 "KULEUVEN_VERIFICATION_REPORT.json",
                 "00_VISUAL_INDEX.md", "00_VISUAL_INDEX.html",
                 "00_TREASURE_MAP.md", "START_HERE.md",
                 "data/registry/DISCOVERY_CANDIDATES.csv"]
EXCLUDE_SUFFIX = {".pt", ".pth", ".ckpt", ".onnx", ".npy", ".npz", ".zip",
                  ".7z", ".nii", ".gz", ".mnc", ".dcm", ".pyc"}
EXCLUDE_PARTS = {"__pycache__", ".venv", ".git", "discovery_raw",
                 "literature_raw", "checkpoints", "node_modules"}
MAX_FILE_BYTES = 30 * 1024 * 1024


def wanted(p: pathlib.Path) -> bool:
    if not p.is_file():
        return False
    if any(part in EXCLUDE_PARTS for part in p.parts):
        return False
    if p.suffix.lower() in EXCLUDE_SUFFIX:
        return False
    if p.stat().st_size > MAX_FILE_BYTES:
        print(f"  ! oversized, skipped: {p}", file=sys.stderr)
        return False
    return True


def build_sample(n_per_subject=4):
    """A redistributable slice of the source data: real frames + real expert
    masks, CC-BY-4.0, with provenance and licence travelling alongside."""
    dest = pathlib.Path("evidence_samples/kuleuven_lumbar")
    if dest.exists():
        shutil.rmtree(dest)
    (dest / "images").mkdir(parents=True, exist_ok=True)
    (dest / "masks").mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(PROC / "index.csv", encoding="utf-8")))
    for r in rows:
        r["bone_px"] = int(r["bone_px"])
    chosen = []
    for s in sorted({r["subject"] for r in rows}):
        for mod in ("HUS", "RUS"):
            sel = [r for r in rows if r["subject"] == s and r["modality"] == mod
                   and r["empty_label"] != "True"]
            if not sel:
                continue
            sel.sort(key=lambda r: r["bone_px"])
            k = max(1, n_per_subject // 2)
            idx = [int(i) for i in
                   (len(sel) * 0.15, len(sel) * 0.5, len(sel) * 0.85)][:k + 1]
            for i in idx:
                chosen.append(sel[min(i, len(sel) - 1)])
    seen, uniq = set(), []
    for c in chosen:
        if c["uid"] not in seen:
            seen.add(c["uid"]); uniq.append(c)
    for r in uniq:
        shutil.copy2(PROC / "images" / f"{r['uid']}.png", dest / "images" / f"{r['uid']}.png")
        shutil.copy2(PROC / "masks" / f"{r['uid']}.png", dest / "masks" / f"{r['uid']}.png")
    with open(dest / "SAMPLE_INDEX.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(uniq[0].keys()))
        w.writeheader(); w.writerows(uniq)
    (dest / "LICENSE_AND_ATTRIBUTION.txt").write_text(
        "These ultrasound frames and expert annotations are a redistributed subset of:\n\n"
        "  Cavalcanti NA et al. A large, paired dataset of robotic and handheld lumbar\n"
        "  spine ultrasound with ground-truth CT benchmarking.\n"
        "  KU Leuven Research Data Repository, doi:10.48804/3XPCAE\n"
        "  Paper: doi:10.1038/s41597-025-06047-9\n\n"
        "  Licence: Creative Commons Attribution 4.0 International (CC-BY-4.0)\n"
        "  https://creativecommons.org/licenses/by/4.0/\n\n"
        "Redistribution here is permitted by that licence, with attribution.\n\n"
        "MODIFICATIONS BY THIS PROJECT: decoded from MetaImage; flipped vertically\n"
        "(the source stores rows bottom-up); cropped to the live ultrasound sector\n"
        "(rows 150-960, columns 530-960 of the 1920x1080 screen capture), which\n"
        "removes the scanner UI, the depth ruler and the burned-in study/date banner.\n"
        "Masks are the source expert annotation (label value 2) rendered as 0/255.\n\n"
        "LABEL SEMANTICS: value 2 in the source marks EXPERT-ANNOTATED VISIBLE BONE\n"
        "SURFACE. It is NOT a lumbar-puncture target, entry point, trajectory,\n"
        "interspace choice or safety window. No such annotation exists in the source\n"
        "dataset or, as far as this project could establish, in any public dataset.\n\n"
        "NOTE: the source encodes background as 0 in six archives and 1 in the other\n"
        "twelve; bone surface is 2 throughout. Use (label == 2).\n",
        encoding="utf-8")
    print(f"  evidence sample: {len(uniq)} frame/mask pairs from "
          f"{len({r['subject'] for r in uniq})} subjects")
    return dest


def collect():
    out = []
    for d in INCLUDE_DIRS + ["evidence_samples"]:
        base = ROOT / d
        if not base.exists():
            continue
        out += [p for p in sorted(base.rglob("*")) if wanted(p)]
    for f in INCLUDE_FILES:
        p = ROOT / f
        if p.exists() and wanted(p):
            out.append(p)
    seen, uniq = set(), []
    for p in out:
        if p not in seen:
            seen.add(p); uniq.append(p)
    return uniq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--skip-qa", action="store_true",
                    help="package even if the visual gate fails (not recommended)")
    a = ap.parse_args()

    print("running the visual evidence gate ...")
    rc = subprocess.run([sys.executable, "tools/qa_visual_evidence.py"],
                        capture_output=True, text=True)
    print(rc.stdout[-2500:])
    if rc.returncode != 0 and not a.skip_qa:
        sys.exit("\nPACKAGING REFUSED: the visual evidence gate failed. "
                 "Fix the gaps above, or pass --skip-qa deliberately.")

    print("\nbuilding redistributable sample ...")
    build_sample()

    stamp = datetime.datetime.now().strftime("%Y%m%d")
    out = pathlib.Path(a.out or
                       f"Lumbar_MarkAny_evidence_package_V2_REAL_HUMAN_US_{stamp}.zip").resolve()
    files = collect()
    print(f"\nfiles to package: {len(files)}")

    bundle = ROOT / "Lumbar_MarkAny_repo.bundle"
    try:
        subprocess.run(["git", "bundle", "create", str(bundle), "--all"],
                       check=True, capture_output=True)
        print(f"  git bundle: {bundle.stat().st_size:,} B")
    except Exception as e:
        print(f"  ! git bundle failed: {e}", file=sys.stderr)
        bundle = None

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in files:
            z.write(p, pathlib.Path("Lumbar_MarkAny_V2") / p.relative_to(ROOT))
        if bundle and bundle.exists():
            z.write(bundle, "Lumbar_MarkAny_V2/Lumbar_MarkAny_repo.bundle")
        z.writestr("Lumbar_MarkAny_V2/PACKAGE_MANIFEST.md", manifest(files, bundle))
    if bundle and bundle.exists():
        bundle.unlink()

    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"\nwrote {out}")
    print(f"  size   : {out.stat().st_size:,} bytes ({out.stat().st_size/1e6:.1f} MB)")
    print(f"  sha256 : {digest}")


def manifest(files, bundle):
    import collections
    by = collections.Counter(p.relative_to(ROOT).parts[0] for p in files)
    tot = sum(p.stat().st_size for p in files)
    n_us = len(list((VIS / "raw").glob("*.png")))
    n_ov = len(list((VIS / "expert_overlays").glob("*.png")))
    n_pr = len(list((VIS / "prediction_overlays").glob("*.png")))
    n_sa = len(list(pathlib.Path("evidence_samples/kuleuven_lumbar/images").glob("*.png")))
    L = ["# V2 package manifest", "",
         f"Built {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
         f"Files: {len(files)}   Uncompressed: {tot:,} bytes", "",
         "## This package contains REAL HUMAN LUMBAR ULTRASOUND", "",
         "| | count |", "|---|---|",
         f"| raw real human lumbar frames | {n_us} |",
         f"| expert bone-surface overlays | {n_ov} |",
         f"| model prediction panels | {n_pr} |",
         f"| redistributable source frame/mask pairs (`evidence_samples/`) | {n_sa} |",
         "",
         "Source: Cavalcanti et al., doi:10.48804/3XPCAE, **CC-BY-4.0**. "
         "Redistribution is permitted with attribution; see "
         "`evidence_samples/kuleuven_lumbar/LICENSE_AND_ATTRIBUTION.txt`.", "",
         "> Expert labels mark VISIBLE BONE SURFACE. They are not puncture targets.", "",
         "## Contents by directory", "", "| Directory | Files |", "|---|---|"]
    L += [f"| `{k}` | {v} |" for k, v in sorted(by.items())]
    L += ["", "## Deliberately excluded", "",
          "| Excluded | Size | How to obtain |", "|---|---|---|",
          "| Full processed set (6,182 frames + masks) | ~800 MB | `tools/download_kuleuven_subset.py` then `tools/build_lumbar_dataset.py` |",
          "| Raw KU Leuven archives | 1.76 GB | `tools/download_kuleuven_subset.py --group labels` |",
          "| JHU porcine dataset | 1.30 GB | `scripts/data/download_jhu_spinal.py` — **no declared licence; never redistributed** |",
          "| Model checkpoints, training cache | ~1 GB | re-run exp005 |",
          "", "## Where to start", "",
          "1. `START_HERE.md`", "2. `00_VISUAL_INDEX.html` — real ultrasound on the first screen",
          "3. `00_TREASURE_MAP.md`", "4. `research/datasets/V2_ACCESS_CORRECTION.md`",
          "5. `RESULTS_LEDGER.csv`, `CLAIMS_LEDGER.csv`",
          "6. `deliverables/paper_v2_assets/`", ""]
    if bundle:
        L += ["## Git history", "",
              "```bash", "git clone Lumbar_MarkAny_repo.bundle Lumbar_MarkAny", "```", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
