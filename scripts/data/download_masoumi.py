#!/usr/bin/env python3
"""
download_masoumi.py -- Acquire the multimodal spine US/CT registration dataset
(doi:10.5281/zenodo.4813508, CC-BY-4.0).

WHAT THIS DATASET ACTUALLY CONTAINS -- read before citing it:

  HumanSubjects/   3 subjects (TCGA-QQ-A8VG, TCGA-QQ-ASV2, TCGA-QQ-ASVC)
                   CT + *CT-SIMULATED* ultrasound. There is NO real human
                   ultrasound in this release.
  CaninePhantom/   ex-vivo canine cervical/thoracic: CT + REAL US + simulated US
                   + 21 landmark pairs (Landmarks.tag)
  Lamb/            ex-vivo lamb lumbar: CT + REAL US + simulated US + landmarks

It is a CT-to-ultrasound REGISTRATION benchmark, not an anatomy dataset, and it
is not evidence about transcutaneous human lumbar imaging.

Licence: CC-BY-4.0 -- redistribution with attribution is permitted.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import pathlib
import urllib.request
import zipfile

RECORD = "4813508"
API = f"https://zenodo.org/api/records/{RECORD}"
UA = {"User-Agent": "Lumbar-MarkAny-research/0.1 (academic dataset acquisition)"}
EXPECTED_BYTES = 148_576_333
EXPECTED_INNER = {"CaninePhantom.zip", "HumanSubjects.zip", "Lamb.zip"}


def sha256(p: pathlib.Path, bs: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while (b := f.read(bs)):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/raw/masoumi_us_ct")
    ap.add_argument("--inspect", action="store_true",
                    help="list inner archive contents after download")
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    req = urllib.request.Request(API, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        rec = json.loads(r.read().decode("utf-8", "replace"))
    lic = (rec["metadata"].get("license") or {}).get("id")
    print(f"record  : {rec['metadata']['title'][:80]}")
    print(f"licence : {lic}")

    target = None
    for f in rec.get("files", []):
        if f["key"].lower().endswith(".zip"):
            target = f
            break
    if target is None:
        raise SystemExit("no zip file found in the Zenodo record")

    dest = out / target["key"]
    if dest.exists() and dest.stat().st_size == EXPECTED_BYTES:
        print(f"already present: {dest}")
    else:
        url = target["links"]["self"]
        print(f"downloading {target['key']} ({target['size']:,} B) ...")
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as fh:
            while (chunk := r.read(1 << 20)):
                fh.write(chunk)

    size = dest.stat().st_size
    print(f"size    : {size:,} bytes {'(matches expected)' if size == EXPECTED_BYTES else '(UNEXPECTED)'}")
    print(f"sha256  : {sha256(dest)}")

    with zipfile.ZipFile(dest) as z:
        inner = set(z.namelist())
        print(f"inner   : {sorted(inner)}")
        missing = EXPECTED_INNER - inner
        if missing:
            print(f"WARNING: expected members missing: {missing}")
        if a.inspect:
            for name in sorted(inner & EXPECTED_INNER):
                with zipfile.ZipFile(io.BytesIO(z.read(name))) as iz:
                    print(f"\n  {name}:")
                    for n in sorted(iz.namelist()):
                        info = iz.getinfo(n)
                        if info.file_size:
                            print(f"    {info.file_size:>12,d}  {n}")

    print("\nREMINDER: the human subjects here have CT-SIMULATED ultrasound only.")


if __name__ == "__main__":
    main()
