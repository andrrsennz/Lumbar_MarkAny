#!/usr/bin/env python3
"""
discover_sources.py -- Programmatic public-dataset discovery for Lumbar_MarkAny.

Queries public search APIs of open research-data repositories for ultrasound
datasets relevant to lumbar / spinal / needle imaging, plus the broader
ultrasound ecosystem. Writes raw JSON hits to data/registry/discovery_raw/.

NOTE: This script only performs read-only API queries against documented public
endpoints. It does not scrape HTML or bypass access controls.
"""
import json, os, sys, time, urllib.parse, urllib.request, datetime, pathlib

OUT = pathlib.Path("data/registry/discovery_raw")
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Lumbar-MarkAny-research/0.1 (academic dataset discovery)"}
STAMP = datetime.datetime.now(datetime.timezone.utc).isoformat()

QUERIES = [
    # Tier 0 -- lumbar / neuraxial
    "lumbar spine ultrasound", "neuraxial ultrasound", "spinal anesthesia ultrasound",
    "epidural ultrasound", "lumbar puncture ultrasound", "paramedian sagittal oblique",
    # Tier 1 -- spine / robotic / tracked
    "robotic ultrasound spine", "tracked ultrasound spine", "3D ultrasound spine",
    "ultrasound bone surface segmentation", "ultrasound CT registration spine",
    "vertebra ultrasound segmentation", "scoliosis ultrasound",
    # Tier 2 -- needle
    "ultrasound needle segmentation", "needle tip tracking ultrasound",
    "ultrasound guided needle insertion dataset",
    # Tier 3/4 -- broader ultrasound
    "breast ultrasound dataset", "thyroid ultrasound dataset", "fetal ultrasound dataset",
    "cardiac ultrasound dataset", "lung ultrasound dataset", "nerve ultrasound dataset",
    "musculoskeletal ultrasound dataset", "ultrasound segmentation dataset",
]

def fetch(url, timeout=60, retries=4):
    """GET with exponential backoff. Some repositories answer 400/429 under rate limiting."""
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            last = e
            time.sleep(2.0 * (2 ** i))
    raise last

def safe(name, fn):
    try:
        return fn()
    except Exception as e:
        print(f"  !! {name}: {type(e).__name__}: {e}", file=sys.stderr)
        return None

# ---------------- Zenodo ----------------
def zenodo(q):
    u = "https://zenodo.org/api/records?q=" + urllib.parse.quote(q) + "&size=25&type=dataset"
    d = fetch(u)
    out = []
    for h in d.get("hits", {}).get("hits", []):
        m = h.get("metadata", {})
        rt = (m.get("resource_type") or {}).get("type")
        out.append({
            "source": "zenodo", "query": q, "id": h.get("id"),
            "title": m.get("title"), "doi": h.get("doi"),
            "url": h.get("links", {}).get("self_html") or h.get("links", {}).get("html"),
            "license": (m.get("license") or {}).get("id"),
            "access": (h.get("access") or {}).get("record") or m.get("access_right"),
            "published": m.get("publication_date"),
            "files_n": len(h.get("files") or []),
            "size_bytes": sum((f.get("size") or 0) for f in (h.get("files") or [])),
            "resource_type": rt,
            "description": (m.get("description") or "")[:600],
        })
    return out

# ---------------- OpenAIRE (aggregates many EU repos) ----------------
def openaire(q):
    u = ("https://api.openaire.eu/search/datasets?keywords=" +
         urllib.parse.quote(q) + "&size=30&format=json")
    d = fetch(u)
    res = d.get("response", {}).get("results", {}).get("result", []) or []
    out = []
    for r in res:
        try:
            md = r["metadata"]["oaf:entity"]["oaf:result"]
            t = md.get("title")
            t = t.get("$") if isinstance(t, dict) else (t[0].get("$") if isinstance(t, list) and t else None)
            pid = md.get("pid")
            dois = []
            if isinstance(pid, list):
                dois = [p.get("$") for p in pid if p.get("@classid") == "doi"]
            elif isinstance(pid, dict) and pid.get("@classid") == "doi":
                dois = [pid.get("$")]
            out.append({"source": "openaire", "query": q, "title": t,
                        "doi": dois[0] if dois else None,
                        "published": (md.get("dateofacceptance") or {}).get("$")})
        except Exception:
            continue
    return out

# ---------------- Hugging Face ----------------
def huggingface(q):
    u = ("https://huggingface.co/api/datasets?search=" + urllib.parse.quote(q) +
         "&limit=40&full=false")
    d = fetch(u)
    return [{"source": "huggingface", "query": q, "id": h.get("id"),
             "title": h.get("id"), "downloads": h.get("downloads"),
             "likes": h.get("likes"), "gated": h.get("gated"),
             "private": h.get("private"),
             "url": "https://huggingface.co/datasets/" + str(h.get("id"))}
            for h in d]

# ---------------- OSF ----------------
def osf(q):
    u = "https://api.osf.io/v2/nodes/?filter[title]=" + urllib.parse.quote(q) + "&page[size]=20"
    d = fetch(u)
    return [{"source": "osf", "query": q, "id": n.get("id"),
             "title": (n.get("attributes") or {}).get("title"),
             "public": (n.get("attributes") or {}).get("public"),
             "url": "https://osf.io/" + str(n.get("id"))}
            for n in d.get("data", [])]

# ---------------- Dryad ----------------
def dryad(q):
    u = "https://datadryad.org/api/v2/search?q=" + urllib.parse.quote(q) + "&per_page=20"
    d = fetch(u)
    items = (d.get("_embedded") or {}).get("stash:datasets", [])
    return [{"source": "dryad", "query": q, "title": i.get("title"),
             "doi": i.get("identifier"), "license": i.get("license"),
             "size_bytes": i.get("storageSize")} for i in items]

# ---------------- DataCite (cross-repository, very broad) ----------------
def datacite(q):
    u = ("https://api.datacite.org/dois?query=" + urllib.parse.quote(q) +
         "&resource-type-id=dataset&page[size]=50")
    d = fetch(u)
    out = []
    for h in d.get("data", []):
        a = h.get("attributes", {})
        ts = a.get("titles") or [{}]
        out.append({"source": "datacite", "query": q, "doi": a.get("doi"),
                    "title": ts[0].get("title"), "publisher": a.get("publisher"),
                    "year": a.get("publicationYear"), "url": a.get("url"),
                    "rights": [r.get("rightsIdentifier") for r in (a.get("rightsList") or [])]})
    return out

PROVIDERS = [("zenodo", zenodo), ("datacite", datacite), ("huggingface", huggingface),
             ("openaire", openaire), ("osf", osf), ("dryad", dryad)]

def main():
    only = sys.argv[1:] or [p[0] for p in PROVIDERS]
    for name, fn in PROVIDERS:
        if name not in only:
            continue
        allhits = []
        print(f"== {name} ==")
        for q in QUERIES:
            hits = safe(f"{name}:{q}", lambda: fn(q)) or []
            print(f"  {q[:45]:45s} -> {len(hits)}")
            allhits.extend(hits)
            time.sleep(1.5)
        p = OUT / f"{name}.json"
        p.write_text(json.dumps({"fetched_utc": STAMP, "n": len(allhits),
                                 "hits": allhits}, indent=1), encoding="utf-8")
        print(f"  wrote {p} ({len(allhits)} rows)")

if __name__ == "__main__":
    main()
