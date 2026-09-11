#!/usr/bin/env python3
"""
package_evidence_zip.py -- Build the portable evidence package.

The ZIP is NOT a clone of the Git repository. It is a self-contained,
hand-auditable bundle: everything a reader needs to understand, check and
reproduce the work, plus a git bundle so the full history travels with it.

What is deliberately EXCLUDED, and why:

  * Raw and extracted datasets (1.3 GB held locally, 1.01 TB not obtained).
    The JHU data carries NO declared licence, so redistributing its pixels
    would be wrong regardless of size. Reacquire with scripts/data/.
  * Model checkpoints -- regenerable, and large.
  * The virtual environment and pip caches.
  * Bulk discovery API dumps -- regenerable; the consolidated CSV is included.

What is INCLUDED: all code, all documentation, all manifests and ledgers, all
experiment configs/logs/metrics, all figures, the provenance log with SHA-256
for every acquired archive, and a git bundle of the complete history.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import pathlib
import subprocess
import sys
import zipfile

INCLUDE_DIRS = [
    "annotation", "deliverables", "experiments", "figures", "provenance",
    "research", "scripts", "src", "visuals",
]
INCLUDE_FILES = [
    "README.md", "LICENSE", "requirements.txt", ".gitignore",
    "CLAIMS_LEDGER.csv", "RESULTS_LEDGER.csv",
    # The curated registry lives under research/ and is picked up by INCLUDE_DIRS;
    # this is the consolidated raw-survey table, which does not.
    "data/registry/DISCOVERY_CANDIDATES.csv",
]
# Patterns excluded even inside included directories.
EXCLUDE_SUFFIX = {".pt", ".pth", ".ckpt", ".onnx", ".npz", ".zip", ".7z",
                  ".nii", ".gz", ".mnc", ".dcm", ".stl", ".ply", ".pyc"}
EXCLUDE_PARTS = {"__pycache__", ".venv", "discovery_raw", "literature_raw",
                 ".git", "node_modules", ".ipynb_checkpoints"}
MAX_FILE_BYTES = 25 * 1024 * 1024      # nothing huge should sneak in


def wanted(p: pathlib.Path) -> bool:
    if not p.is_file():
        return False
    if any(part in EXCLUDE_PARTS for part in p.parts):
        return False
    if p.suffix.lower() in EXCLUDE_SUFFIX:
        return False
    if p.stat().st_size > MAX_FILE_BYTES:
        print(f"  ! skipping oversized {p} ({p.stat().st_size:,} B)", file=sys.stderr)
        return False
    return True


def collect(root: pathlib.Path):
    out = []
    for d in INCLUDE_DIRS:
        base = root / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            if wanted(p):
                out.append(p)
    for f in INCLUDE_FILES:
        if not f:
            continue
        p = root / f
        if p.exists() and wanted(p):
            out.append(p)
    # de-duplicate, keep order
    seen, uniq = set(), []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def make_git_bundle(root: pathlib.Path, dest: pathlib.Path) -> pathlib.Path | None:
    """A bundle carries the full history, so the ZIP is not a history-less snapshot."""
    try:
        subprocess.run(["git", "bundle", "create", str(dest), "--all"],
                       cwd=root, check=True, capture_output=True)
        print(f"  git bundle: {dest.name} ({dest.stat().st_size:,} B)")
        return dest
    except Exception as e:
        print(f"  ! git bundle failed: {e}", file=sys.stderr)
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    root = pathlib.Path(a.root).resolve()
    stamp = datetime.datetime.now().strftime("%Y%m%d")
    out = pathlib.Path(a.out or f"Lumbar_MarkAny_evidence_package_{stamp}.zip").resolve()

    files = collect(root)
    print(f"files to package: {len(files)}")

    bundle = make_git_bundle(root, root / "Lumbar_MarkAny_repo.bundle")

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files:
            z.write(p, pathlib.Path("Lumbar_MarkAny") / p.relative_to(root))
        if bundle and bundle.exists():
            z.write(bundle, "Lumbar_MarkAny/Lumbar_MarkAny_repo.bundle")
        manifest = build_manifest(root, files, bundle)
        z.writestr("Lumbar_MarkAny/PACKAGE_MANIFEST.md", manifest)

    if bundle and bundle.exists():
        bundle.unlink()

    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"\nwrote {out}")
    print(f"  size   : {out.stat().st_size:,} bytes ({out.stat().st_size/1e6:.1f} MB)")
    print(f"  sha256 : {digest}")


def build_manifest(root, files, bundle) -> str:
    import collections
    by_top = collections.Counter(p.relative_to(root).parts[0] for p in files)
    total = sum(p.stat().st_size for p in files)
    lines = [
        "# Package manifest",
        "",
        f"Built {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
        f"Files: {len(files)}   Uncompressed: {total:,} bytes",
        "",
        "## Contents by top-level directory",
        "",
        "| Directory | Files |",
        "|---|---|",
    ]
    for k, v in sorted(by_top.items()):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## What is NOT in this package, and how to get it",
        "",
        "| Excluded | Size | How to obtain |",
        "|---|---|---|",
        "| JHU spinal-cord ultrasound (DS004, DS005) | 1.30 GB | `python scripts/data/download_jhu_spinal.py` — **carries no declared licence; not redistributed here** |",
        "| Masoumi US/CT (DS002) | 149 MB | `python scripts/data/download_masoumi.py` or the Zenodo DOI (CC-BY-4.0) |",
        "| KU Leuven lumbar dataset (DS001) | 1.01 TB | `python scripts/data/download_kuleuven.py --subset annotated` — **was unreachable from the authoring network; see KULEUVEN_ACCESS_BLOCKER.md** |",
        "| Model checkpoints | ~30 MB | `python scripts/experiments/train_seg.py --epochs 30` |",
        "| Per-image prediction arrays | ~1 MB | regenerated by the same command |",
        "",
        "## Git history",
        "",
        ("`Lumbar_MarkAny_repo.bundle` contains the complete commit history. Restore with:\n\n"
         "```bash\ngit clone Lumbar_MarkAny_repo.bundle Lumbar_MarkAny\ncd Lumbar_MarkAny\n"
         "git remote set-url origin https://github.com/andrrsennz/Lumbar_MarkAny.git\n```"
         if bundle else "_git bundle unavailable_"),
        "",
        "## Where to start reading",
        "",
        "1. `README.md` — what was attempted, what blocked it, what was done instead",
        "2. `research/datasets/KULEUVEN_ACCESS_BLOCKER.md` — why the anchor dataset is absent",
        "3. `research/datasets/PUBLIC_ULTRASOUND_DATA_LAKE_REPORT.md` — the survey result",
        "4. `RESULTS_LEDGER.csv` and `CLAIMS_LEDGER.csv` — every number and its source",
        "5. `deliverables/paper/CLAIMS_NOT_ALLOWED.md` — read before writing anything",
        "6. `deliverables/hospital_proposal/HOSPITAL_RESEARCH_PROPOSAL.md`",
        "",
        "## Integrity",
        "",
        "SHA-256 for every acquired archive is in `provenance/DATA_DOWNLOAD_LOG.csv`.",
        "Re-verify after download with `python scripts/data/verify_checksums.py`.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
