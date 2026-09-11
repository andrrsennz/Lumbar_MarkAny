#!/usr/bin/env python3
"""
download_kuleuven.py -- Acquire the anchor lumbar-spine ultrasound dataset
(doi:10.48804/3XPCAE) from the KU Leuven RDR Dataverse.

AS OF 2026-09-11 THIS SCRIPT CANNOT COMPLETE FROM THE PROJECT WORKSTATION:
the whole kuleuven.be domain is unreachable at TCP level from this network.
See research/datasets/KULEUVEN_ACCESS_BLOCKER.md for the full diagnosis.
The script is written, tested as far as the network allows, and left ready to
run unchanged from a network that can reach the host.

The full deposit is ~1.01 TB across 1,346 files. Downloading all of it is
usually the wrong move: only 9 of the 63 participants carry expert bone-surface
annotations, and those are the only ones the supervised experiments need.
`--subset annotated` fetches the annotation-bearing material plus the metadata
tables; `--subset all` fetches everything.

Usage
-----
  python scripts/data/download_kuleuven.py --check-only
  python scripts/data/download_kuleuven.py --subset annotated --out data/raw/kuleuven
  python scripts/data/download_kuleuven.py --subset all --out /mnt/big/kuleuven
"""
from __future__ import annotations
import argparse
import csv
import datetime
import hashlib
import json
import pathlib
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DOI = "doi:10.48804/3XPCAE"
DEFAULT_BASE = "https://rdr.kuleuven.be"
UA = {"User-Agent": "Lumbar-MarkAny-research/0.1 (academic dataset acquisition)"}

# Filename fragments that indicate annotation-bearing or metadata content.
# The repository layout is documented in the publication's Data Records section:
#   US/US_labels/...      zipped labelled US scans
#   US/US_recon/...       reconstructions + segmented US
#   US/US_scantype_availability.csv, demographics csv, readme
ANNOTATED_PATTERNS = [
    r"label", r"_seg", r"recon", r"readme", r"demograph",
    r"scantype_availability", r"spatialtrackingvalidation", r"SPAR",
    r"\.csv$", r"\.txt$",
]


def reachable(host: str, port: int = 443, timeout: float = 10.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def api(url: str, timeout: int = 120):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def list_files(base: str):
    """Dataverse: list the files of the latest published version of the dataset."""
    url = f"{base}/api/datasets/:persistentId/versions/:latest/files?persistentId={urllib.parse.quote(DOI)}"
    data = api(url)
    out = []
    for entry in data.get("data", []):
        df = entry.get("dataFile", {}) or {}
        out.append({
            "id": df.get("id"),
            "filename": df.get("filename") or entry.get("label"),
            "directory": entry.get("directoryLabel", "") or "",
            "size": df.get("filesize"),
            "md5": df.get("md5") or (df.get("checksum") or {}).get("value"),
            "contentType": df.get("contentType"),
        })
    return out


def wanted(f, subset: str) -> bool:
    if subset == "all":
        return True
    path = f"{f['directory']}/{f['filename']}"
    return any(re.search(p, path, re.I) for p in ANNOTATED_PATTERNS)


def sha256_of(path: pathlib.Path, bs: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while (b := fh.read(bs)):
            h.update(b)
    return h.hexdigest()


def download(base: str, f, dest: pathlib.Path, retries: int = 5) -> pathlib.Path:
    """Download one datafile, resuming a partial file if one is present."""
    out = dest / (f["directory"] or "") / f["filename"]
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and f.get("size") and out.stat().st_size == f["size"]:
        print(f"  = {out.name} (already complete)")
        return out
    url = f"{base}/api/access/datafile/{f['id']}"
    for attempt in range(1, retries + 1):
        have = out.stat().st_size if out.exists() else 0
        req = urllib.request.Request(url, headers=dict(UA))
        if have:
            req.add_header("Range", f"bytes={have}-")
        try:
            with urllib.request.urlopen(req, timeout=300) as r, open(out, "ab" if have else "wb") as fh:
                while (chunk := r.read(1 << 20)):
                    fh.write(chunk)
            print(f"  + {out.name} ({out.stat().st_size:,} B)")
            return out
        except Exception as e:
            wait = min(60, 5 * attempt)
            print(f"  ! {out.name} attempt {attempt}/{retries}: {e}; retry in {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"failed after {retries} attempts: {f['filename']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=DEFAULT_BASE,
                    help="Dataverse base URL (override only for a verified mirror)")
    ap.add_argument("--subset", choices=["annotated", "all"], default="annotated")
    ap.add_argument("--out", default="data/raw/kuleuven")
    ap.add_argument("--check-only", action="store_true",
                    help="test reachability and print the file manifest, download nothing")
    ap.add_argument("--max-gb", type=float, default=None,
                    help="abort before exceeding this many GB of downloads")
    a = ap.parse_args()

    host = urllib.parse.urlparse(a.base_url).hostname
    print(f"host            : {host}")
    ok = reachable(host)
    print(f"tcp/443 reachable: {ok}")
    if not ok:
        print("\nHOST UNREACHABLE. This is the documented blocker; see "
              "research/datasets/KULEUVEN_ACCESS_BLOCKER.md\n"
              "Re-run this script unchanged from a network that can reach the host.",
              file=sys.stderr)
        return 2

    print("listing files via Dataverse API ...")
    files = list_files(a.base_url)
    sel = [f for f in files if wanted(f, a.subset)]
    tot = sum(f.get("size") or 0 for f in sel)
    print(f"files in deposit : {len(files)}")
    print(f"files selected   : {len(sel)}  (subset={a.subset})")
    print(f"selected bytes   : {tot:,} ({tot/1e9:.2f} GB)")

    dest = pathlib.Path(a.out)
    dest.mkdir(parents=True, exist_ok=True)
    man = dest / "MANIFEST.csv"
    with open(man, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "directory", "filename", "size", "md5", "contentType"])
        w.writeheader()
        w.writerows(sel)
    print(f"manifest written : {man}")

    if a.check_only:
        return 0
    if a.max_gb and tot / 1e9 > a.max_gb:
        print(f"ABORT: selection is {tot/1e9:.1f} GB > --max-gb {a.max_gb}", file=sys.stderr)
        return 3

    log = dest / "DOWNLOAD_LOG.csv"
    new = not log.exists()
    with open(log, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["filename", "directory", "bytes", "sha256",
                                           "md5_declared", "source_url", "downloaded_utc"])
        if new:
            w.writeheader()
        for i, f in enumerate(sel, 1):
            print(f"[{i}/{len(sel)}] {f['directory']}/{f['filename']}")
            p = download(a.base_url, f, dest)
            w.writerow({
                "filename": f["filename"], "directory": f["directory"],
                "bytes": p.stat().st_size, "sha256": sha256_of(p),
                "md5_declared": f.get("md5") or "",
                "source_url": f"{a.base_url}/api/access/datafile/{f['id']}",
                "downloaded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            })
            fh.flush()
    print(f"\ndone -> {dest}\nprovenance log: {log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
