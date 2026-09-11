#!/usr/bin/env python3
"""verify_checksums.py -- record/verify SHA256 + size for every acquired archive."""
import hashlib, pathlib, csv, sys, datetime, json

TARGETS = [
    ("jhu_spinal_cord_detection", "data/raw/jhu_spinal_cord/jhu_injury_localization.zip",
     "https://drive.google.com/file/d/1C3NgTmC8gBNG8mL632Oz2i1j156zhSXk/view"),
    ("jhu_spinal_cord_segmentation", "data/raw/jhu_spinal_cord/jhu_segmentation.zip",
     "https://drive.google.com/file/d/1r3UNudTpPJyO1kJdVfQqPsBDduAWp2iS/view"),
]
OUT = pathlib.Path("provenance/DATA_DOWNLOAD_LOG.csv")
OUT.parent.mkdir(parents=True, exist_ok=True)

def sha256(p, bs=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while (b := f.read(bs)):
            h.update(b)
    return h.hexdigest()

def main():
    rows = []
    for ds, rel, url in TARGETS:
        p = pathlib.Path(rel)
        if not p.exists():
            print(f"MISSING {rel}"); continue
        d = sha256(p)
        st = p.stat()
        rows.append({
            "dataset_id": ds, "local_path": rel, "source_url": url,
            "bytes": st.st_size, "size_mb": round(st.st_size / 1e6, 2),
            "sha256": d,
            "downloaded_utc": datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc).isoformat(),
            "recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        })
        print(f"{ds:32s} {st.st_size:>13,d} B  {d}")
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("wrote", OUT)

if __name__ == "__main__":
    main()
