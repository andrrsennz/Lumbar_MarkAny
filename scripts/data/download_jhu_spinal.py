#!/usr/bin/env python3
"""
download_jhu_spinal.py -- Acquire the Johns Hopkins HEPIUS spinal-cord
ultrasound dataset.

Provenance chain (each link verified 2026-09-11):
  publication  PMC12475011 / PMID 41006445
    -> "Data availability" names github.com/HEPIUSLAB/ultrasound_spinal_cord_dataset
       -> that repository contains ONLY a README (4 KB); no data
          -> the README links two Google Drive files, which hold the actual data

LICENCE WARNING
---------------
Neither the GitHub repository nor the archives declare a licence. Absence of a
licence is NOT a grant of permission. This script downloads the data for local
research use; it does not entitle you to redistribute the images, masks, or any
derived overlay. This project therefore publishes numbers computed from this
data but never the pixels.

Expected contents (verified against the publication):
  injury localization : 2,245 PNG + 2,246 XML
                        877 pre-injury  (zero bounding boxes)
                      1,368 post-injury (exactly one box each)
  segmentation        : 10,223 image/mask pairs
                        train 8,668 / val 895 / test 660
"""
from __future__ import annotations
import argparse
import hashlib
import pathlib
import subprocess
import sys
import zipfile

FILES = {
    "jhu_injury_localization.zip": {
        "gdrive_id": "1C3NgTmC8gBNG8mL632Oz2i1j156zhSXk",
        "expected_bytes": 224_279_362,
        "sha256": "8bdf07250c02376feac7a635f9e095125922a4935ac0c4c822e4bcb11f733fa1",
        "expect": {".png": 2245, ".xml": 2246},
    },
    "jhu_segmentation.zip": {
        "gdrive_id": "1r3UNudTpPJyO1kJdVfQqPsBDduAWp2iS",
        "expected_bytes": 1_079_559_546,
        "sha256": "8842d153b887c8ef8bf2e1c687b26b92a0fc91b37f118ac04865d15b8bffe057",
        "expect": {".png": 20446},  # 10,223 images + 10,223 masks
    },
}


def sha256(p: pathlib.Path, bs: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while (b := f.read(bs)):
            h.update(b)
    return h.hexdigest()


def fetch(gid: str, dest: pathlib.Path) -> None:
    """Google Drive serves large files behind a confirmation interstitial;
    gdown handles the token exchange."""
    subprocess.run([sys.executable, "-m", "gdown", gid, "-O", str(dest)], check=True)


def verify(p: pathlib.Path, spec: dict) -> bool:
    ok = True
    size = p.stat().st_size
    if size != spec["expected_bytes"]:
        print(f"  ! size {size:,} != expected {spec['expected_bytes']:,}")
        ok = False
    else:
        print(f"  = size {size:,} bytes")
    digest = sha256(p)
    if spec.get("sha256") and digest != spec["sha256"]:
        print(f"  ! sha256 {digest}\n    expected {spec['sha256']}")
        ok = False
    else:
        print(f"  = sha256 {digest}")
    with zipfile.ZipFile(p) as z:
        names = [n for n in z.namelist() if not n.startswith("__MACOSX")]
        for ext, n in spec["expect"].items():
            got = sum(1 for x in names if x.lower().endswith(ext))
            flag = "=" if got == n else "!"
            print(f"  {flag} {ext}: {got:,} (expected {n:,})")
            ok &= (got == n)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/raw/jhu_spinal_cord")
    ap.add_argument("--extract-to", default="data/extracted")
    ap.add_argument("--skip-extract", action="store_true")
    a = ap.parse_args()

    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    allok = True

    for name, spec in FILES.items():
        p = out / name
        print(f"\n=== {name} ===")
        if p.exists() and p.stat().st_size == spec["expected_bytes"]:
            print("  already present")
        else:
            fetch(spec["gdrive_id"], p)
        allok &= verify(p, spec)

        if not a.skip_extract:
            dest = pathlib.Path(a.extract_to) / name.replace(".zip", "")
            if dest.exists():
                print(f"  extracted already at {dest}")
            else:
                with zipfile.ZipFile(p) as z:
                    members = [n for n in z.namelist()
                               if not n.startswith("__MACOSX")
                               and n.lower().endswith((".png", ".xml"))]
                    z.extractall(dest, members=members)
                print(f"  extracted {len(members):,} files -> {dest}")

    print("\nALL CHECKS PASSED" if allok else "\nSOME CHECKS FAILED -- inspect above")
    print("Reminder: this dataset carries NO declared licence. Do not redistribute.")
    return 0 if allok else 1


if __name__ == "__main__":
    raise SystemExit(main())
