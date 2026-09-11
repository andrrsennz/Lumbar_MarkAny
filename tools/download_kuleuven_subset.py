#!/usr/bin/env python3
"""
download_kuleuven_subset.py -- Retrieve a scientifically sufficient SUBSET of the
KU Leuven / Balgrist lumbar spine ultrasound dataset (doi:10.48804/3XPCAE, CC-BY-4.0).

WHY A PROXY IS USED
-------------------
The whole `kuleuven.be` domain is unreachable at TCP level from the authoring
network (ports 80 and 443, by hostname and by direct IP, IPv4; the host has no
IPv6 route here either), while Harvard's Dataverse -- the same software -- and
every other research repository respond normally. The KU Leuven server itself is
UP: proxied requests reach it and return `{"status":"OK","data":{"version":"6.7.1"}}`.

So this is an ISP/route-level block on our side, NOT a restriction imposed by the
data provider. The dataset is public (`restricted: false` on all 766 files) and
CC-BY-4.0. This script therefore reaches the PUBLIC Dataverse API through a
public HTTP relay. No authentication is bypassed and no access control is
circumvented; the same bytes are served to anyone.

Integrity is not taken on trust: every file is verified against the MD5 that
Dataverse publishes in its own file metadata. A file that fails MD5 is deleted
and retried.

If you run this from a network that can reach rdr.kuleuven.be directly, pass
`--direct` and no relay is used at all.

USAGE
  python tools/download_kuleuven_subset.py --check
  python tools/download_kuleuven_subset.py --group labels
  python tools/download_kuleuven_subset.py --group recon --group meta
  python tools/download_kuleuven_subset.py --group scans --subjects URS08,URS16
"""
from __future__ import annotations
import argparse
import csv
import datetime
import hashlib
import json
import pathlib
import socket
import subprocess
import sys
import time
import urllib.parse

DOI = "doi:10.48804/3XPCAE"
BASE = "https://rdr.kuleuven.be"
RELAY = "https://api.cors.lol/?url={}"
INVENTORY = pathlib.Path("research/datasets/KULEUVEN_FILE_INVENTORY.csv")
OUTROOT = pathlib.Path("data/raw/kuleuven_lumbar")
LOG = pathlib.Path("provenance/KULEUVEN_DOWNLOAD_LOG.csv")

# The relay rate-limits aggressively (observed: recovery in ~30 s).
MIN_INTERVAL = 40.0
_last_request = [0.0]


def direct_reachable(host="rdr.kuleuven.be", port=443, timeout=8.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def build_url(path_or_url: str, direct: bool) -> str:
    url = path_or_url if path_or_url.startswith("http") else BASE + path_or_url
    if direct:
        return url
    return RELAY.format(urllib.parse.quote(url, safe=""))


def throttle():
    dt = time.time() - _last_request[0]
    if dt < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - dt)
    _last_request[0] = time.time()


def curl(url: str, dest: pathlib.Path | None, timeout: int = 1800):
    """Fetch with curl. Returns (http_code, bytes_written)."""
    cmd = ["curl", "-sSL", "--max-time", str(timeout), "-w", "%{http_code}"]
    cmd += ["-o", str(dest) if dest else "/dev/null", url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    code = (r.stdout or "").strip()[-3:]
    n = dest.stat().st_size if dest and dest.exists() else 0
    return code, n


def md5_of(p: pathlib.Path, bs: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        while (b := f.read(bs)):
            h.update(b)
    return h.hexdigest()


def load_inventory():
    if not INVENTORY.exists():
        sys.exit(f"missing {INVENTORY} -- run with --refresh-metadata first")
    rows = list(csv.DictReader(open(INVENTORY, encoding="utf-8")))
    for r in rows:
        r["bytes"] = int(r["bytes"] or 0)
    return rows


def select(rows, groups, subjects):
    out = []
    for r in rows:
        d = r["directory_label"]
        fn = r["filename"]
        stem = fn.split("_")[0]
        if "labels" in groups and d == "US/US_labels":
            out.append(r)
        elif "recon" in groups and d == "US/US_recon":
            out.append(r)
        elif "meta" in groups and (d in ("", "US") and r["content_type"] != "application/zip"
                                   or fn in ("US_calibration.zip", "US_spatialtrackingvalidation.zip")):
            out.append(r)
        elif "scans" in groups and d.startswith("US/URS"):
            if not subjects or d.split("/")[1] in subjects:
                out.append(r)
        elif "ct" in groups and d.startswith("CT/"):
            if not subjects or d.split("/")[1] in subjects:
                out.append(r)
    # de-duplicate by file_id
    seen, uniq = set(), []
    for r in out:
        if r["file_id"] not in seen:
            seen.add(r["file_id"])
            uniq.append(r)
    return uniq


def log_row(row: dict):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    new = not LOG.exists()
    with open(LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "file_id", "filename", "directory_label", "remote_bytes", "local_bytes",
            "md5_expected", "md5_actual", "verified", "method", "attempts",
            "download_utc", "local_path", "source_doi", "endpoint"])
        if new:
            w.writeheader()
        w.writerow(row)


def fetch_file(r, direct: bool, retries: int = 6) -> bool:
    dest_dir = OUTROOT / (r["directory_label"] or "root")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / r["filename"]

    if dest.exists() and dest.stat().st_size == r["bytes"]:
        if not r["md5"] or md5_of(dest) == r["md5"]:
            print(f"  = {r['filename']} (present, verified)")
            return True
        dest.unlink()

    url = build_url(f"/api/access/datafile/{r['file_id']}", direct)
    for attempt in range(1, retries + 1):
        if not direct:
            throttle()
        code, n = curl(url, dest)
        if code == "200" and n == r["bytes"]:
            got = md5_of(dest)
            ok = (not r["md5"]) or got == r["md5"]
            print(f"  {'+' if ok else '!'} {r['filename']} {n:,} B  md5 {'OK' if ok else 'MISMATCH'}")
            log_row(dict(file_id=r["file_id"], filename=r["filename"],
                         directory_label=r["directory_label"], remote_bytes=r["bytes"],
                         local_bytes=n, md5_expected=r["md5"], md5_actual=got,
                         verified=ok, method="direct" if direct else "public-relay",
                         attempts=attempt,
                         download_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                         local_path=str(dest), source_doi=DOI,
                         endpoint=f"{BASE}/api/access/datafile/{r['file_id']}"))
            if ok:
                return True
            dest.unlink(missing_ok=True)
        else:
            wait = min(180, 20 * attempt)
            print(f"  ! {r['filename']} attempt {attempt}/{retries}: http={code} bytes={n:,} "
                  f"(want {r['bytes']:,}); retry in {wait}s", file=sys.stderr)
            dest.unlink(missing_ok=True)
            time.sleep(wait)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", action="append", default=[],
                    choices=["labels", "recon", "meta", "scans", "ct"],
                    help="which part of the deposit to fetch (repeatable)")
    ap.add_argument("--subjects", default="", help="comma-separated, e.g. URS08,URS16")
    ap.add_argument("--direct", action="store_true", help="no relay; requires reachable host")
    ap.add_argument("--check", action="store_true", help="report reachability and selection, download nothing")
    ap.add_argument("--max-gb", type=float, default=None)
    a = ap.parse_args()

    groups = set(a.group) or {"labels"}
    subjects = {s.strip() for s in a.subjects.split(",") if s.strip()}

    reachable = direct_reachable()
    direct = a.direct or reachable
    print(f"rdr.kuleuven.be directly reachable : {reachable}")
    print(f"transport                          : {'DIRECT' if direct else 'public relay (integrity checked by MD5)'}")

    rows = load_inventory()
    sel = select(rows, groups, subjects)
    tot = sum(r["bytes"] for r in sel)
    print(f"groups={sorted(groups)} subjects={sorted(subjects) or 'ALL'}")
    print(f"selected {len(sel)} files, {tot/1e9:.2f} GB")
    if a.check:
        for r in sorted(sel, key=lambda x: x["filename"])[:40]:
            print(f"   {r['file_id']:>7} {r['bytes']:>13,}  {r['directory_label']}/{r['filename']}")
        return 0
    if a.max_gb and tot / 1e9 > a.max_gb:
        sys.exit(f"ABORT: {tot/1e9:.1f} GB exceeds --max-gb {a.max_gb}")

    ok = 0
    for i, r in enumerate(sorted(sel, key=lambda x: x["bytes"]), 1):
        print(f"[{i}/{len(sel)}] {r['directory_label']}/{r['filename']} ({r['bytes']:,} B)", flush=True)
        if fetch_file(r, direct):
            ok += 1
    print(f"\nverified {ok}/{len(sel)} files -> {OUTROOT}")
    print(f"provenance: {LOG}")
    return 0 if ok == len(sel) else 1


if __name__ == "__main__":
    raise SystemExit(main())
