#!/usr/bin/env python3
"""
triage_discovery.py -- Consolidate raw discovery hits from all repositories,
de-duplicate, and score each candidate for relevance to the Lumbar_MarkAny
research question (transcutaneous lumbar / neuraxial ultrasound, spine
ultrasound, needle-in-ultrasound, and the wider ultrasound ecosystem).

Scoring is keyword-based and deliberately transparent: it is a triage aid that
ranks candidates for human/agent inspection, NOT an access or licence
determination. Access status is established separately, per candidate, by
actually attempting retrieval (see DATASET_DISCOVERY_LOG.md).
"""
import json
import pathlib
import re
import csv
import collections

RAW = pathlib.Path("data/registry/discovery_raw")
OUT = pathlib.Path("data/registry")

# tier keyword -> (tier, weight)
TIER_TERMS = {
    r"\blumbar\b": ("T0", 6),
    r"neuraxial": ("T0", 8),
    r"epidural": ("T0", 6),
    r"intrathecal|lumbar punctur|spinal an[ae]sthesi": ("T0", 8),
    r"\bspine\b|\bspinal\b|vertebra": ("T1", 4),
    r"scoliosis": ("T1", 3),
    r"bone surface|bone segmentation": ("T1", 4),
    r"robot": ("T1", 4),
    r"\btracked\b|tracking.*(probe|pose)|freehand": ("T1", 3),
    r"\bneedle\b": ("T2", 5),
    r"biops(y|ies)": ("T2", 2),
    r"spinal cord": ("T3", 3),
    r"porcine|\bpig\b|phantom|cadaver": ("T3", 2),
    r"breast|thyroid|fetal|foetal|cardiac|echocardio|lung|liver|kidney|"
    r"prostate|carotid|vascular|nerve|abdominal|ovarian|muscle|musculoskeletal": ("T4", 1),
}
US_TERMS = r"ultraso(und|nograph|nic)|\bb-?mode\b|sonograph|\bUS\b imaging|echograph"
DATASET_TERMS = r"dataset|data set|annotat|segment|label|image|scan|corpus|benchmark|collection"


def load_all():
    rows = []
    # provider JSON files written by discover_sources.py
    for p in RAW.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        for h in d.get("hits", []):
            rows.append(h)
    # curl-harvested Zenodo pages
    for p in (RAW / "zenodo_pages").glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        for h in d.get("hits", {}).get("hits", []):
            m = h.get("metadata", {})
            files = h.get("files") or []
            rows.append({
                "source": "zenodo", "query": p.stem.replace("_", " "),
                "id": h.get("id"), "title": m.get("title"),
                "doi": h.get("doi"),
                "url": (h.get("links") or {}).get("self_html"),
                "license": (m.get("license") or {}).get("id"),
                "access": m.get("access_right"),
                "published": m.get("publication_date"),
                "files_n": len(files),
                "size_bytes": sum((f.get("size") or 0) for f in files),
                "resource_type": (m.get("resource_type") or {}).get("type"),
                "description": re.sub(r"<[^>]+>", " ", m.get("description") or "")[:600],
            })
    return rows


def score(rec):
    # Score the RECORD only. The query string that retrieved a record must not
    # be scored: every query in this project contains "ultrasound", so including
    # it would mark 100% of hits as ultrasound-related regardless of content.
    text = " ".join(str(rec.get(k) or "") for k in ("title", "description")).lower()
    tiers, pts = collections.Counter(), 0
    for pat, (tier, w) in TIER_TERMS.items():
        if re.search(pat, text):
            tiers[tier] += 1
            pts += w
    is_us = bool(re.search(US_TERMS, text))
    is_ds = bool(re.search(DATASET_TERMS, text))
    if not is_us:
        pts -= 6                      # ultrasound is mandatory for this project
    if not is_ds:
        pts -= 2
    best = None
    for t in ("T0", "T1", "T2", "T3", "T4"):
        if tiers.get(t):
            best = t
            break
    return pts, (best or "none"), is_us, is_ds


def main():
    rows = load_all()
    print(f"raw hits loaded: {len(rows)}")
    seen, out = set(), []
    for r in rows:
        key = (r.get("doi") or "").lower() or f"{r.get('source')}:{r.get('id') or r.get('title')}"
        if key in seen:
            continue
        seen.add(key)
        pts, tier, is_us, is_ds = score(r)
        out.append({
            "candidate_id": key[:120],
            "source_repository": r.get("source"),
            "title": (r.get("title") or "").replace("\n", " ")[:220],
            "doi": r.get("doi") or "",
            "url": r.get("url") or "",
            "publisher": r.get("publisher") or "",
            "year": r.get("year") or (str(r.get("published") or "")[:4]),
            "license_declared": (r.get("license")
                                 or "|".join(str(x) for x in (r.get("rights") or []) if x)
                                 or ""),
            "access_declared": r.get("access") or "",
            "files_n": r.get("files_n", ""),
            "size_bytes": r.get("size_bytes", ""),
            "resource_type": r.get("resource_type", ""),
            "matched_query": r.get("query", ""),
            "relevance_score": pts,
            "provisional_tier": tier,
            "mentions_ultrasound": is_us,
            "mentions_dataset": is_ds,
        })
    out.sort(key=lambda x: -x["relevance_score"])
    p = OUT / "DISCOVERY_CANDIDATES.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f"unique candidates: {len(out)} -> {p}")

    byt = collections.Counter(r["provisional_tier"] for r in out)
    print("provisional tier distribution:", dict(byt))
    print("\nTop 30 by relevance score:")
    for r in out[:30]:
        print(f"  {r['relevance_score']:3d} {r['provisional_tier']:4s} {r['source_repository']:12s} "
              f"{r['title'][:88]}")


if __name__ == "__main__":
    main()
