#!/usr/bin/env python3
"""
build_literature_db.py -- Harvest a curated literature corpus for the
Lumbar_MarkAny project from Europe PMC (which indexes PubMed/MEDLINE, PMC,
preprint servers and Agricola).

Every record is retrieved from the live Europe PMC REST API; nothing is
hand-typed. Output: research/literature/LITERATURE_DATABASE.csv
"""
import csv, json, time, urllib.parse, urllib.request, pathlib, sys, datetime, re

OUT = pathlib.Path("research/literature")
OUT.mkdir(parents=True, exist_ok=True)
RAW = pathlib.Path("data/registry/literature_raw"); RAW.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Lumbar-MarkAny-research/0.1 (academic literature review)"}
BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

# category -> (query, how many to keep)
QUERIES = {
    "lumbar_puncture_clinical":
        '(TITLE:"lumbar puncture") AND (TITLE:ultrasound OR TITLE:ultrasonography OR ABSTRACT:ultrasound)',
    "difficult_lp_predictors":
        '(TITLE:"lumbar puncture" OR TITLE:"spinal anaesthesia" OR TITLE:"spinal anesthesia") AND (TITLE:difficult OR TITLE:failure OR TITLE:predictors)',
    "ultrasound_assisted_neuraxial":
        '(TITLE:neuraxial OR TITLE:epidural OR TITLE:"spinal anesthesia" OR TITLE:"spinal anaesthesia") AND TITLE:ultrasound',
    "neuraxial_us_rct_meta":
        '((TITLE:ultrasound) AND (TITLE:epidural OR TITLE:spinal OR TITLE:neuraxial)) AND (PUB_TYPE:"Randomized Controlled Trial" OR PUB_TYPE:"Meta-Analysis" OR PUB_TYPE:"Systematic Review")',
    "ai_spinal_ultrasound":
        '(TITLE:ultrasound AND (TITLE:spine OR TITLE:spinal OR TITLE:lumbar OR TITLE:vertebra*)) AND (TITLE:"deep learning" OR TITLE:"machine learning" OR TITLE:segmentation OR TITLE:"neural network" OR TITLE:automatic)',
    "bone_surface_us_segmentation":
        '(TITLE:ultrasound AND TITLE:bone) AND (TITLE:segmentation OR TITLE:"surface" OR TITLE:localization)',
    "robotic_ultrasound":
        '(TITLE:robotic OR TITLE:"robot-assisted" OR TITLE:autonomous) AND TITLE:ultrasound',
    "robotic_us_spine":
        '(TITLE:robot* AND TITLE:ultrasound) AND (TITLE:spine OR TITLE:spinal OR TITLE:lumbar)',
    "us_ct_registration_spine":
        '(TITLE:registration) AND TITLE:ultrasound AND (TITLE:spine OR TITLE:spinal OR TITLE:vertebra*)',
    "needle_ultrasound_tracking":
        '(TITLE:needle) AND TITLE:ultrasound AND (TITLE:tracking OR TITLE:segmentation OR TITLE:detection OR TITLE:localization)',
    "needle_guidance_robotic":
        '(TITLE:needle) AND (TITLE:robot* OR TITLE:automated) AND (TITLE:insertion OR TITLE:guidance OR TITLE:steering)',
    "ar_navigation_lp":
        '(TITLE:"augmented reality" OR TITLE:"mixed reality" OR TITLE:navigation) AND (TITLE:"lumbar puncture" OR TITLE:epidural OR TITLE:spinal)',
    "force_impedance_sensing":
        '(TITLE:"loss of resistance" OR TITLE:bioimpedance OR TITLE:impedance OR TITLE:"force sensing") AND (TITLE:epidural OR TITLE:needle OR TITLE:puncture)',
    "ultrasound_quality_assessment":
        '(TITLE:ultrasound) AND (TITLE:"image quality" OR TITLE:"quality assessment" OR TITLE:confidence)',
    "ultrasound_foundation_models":
        '(TITLE:ultrasound) AND (TITLE:"foundation model" OR TITLE:"self-supervised" OR TITLE:"pretrain*" OR TITLE:"segment anything")',
    "uncertainty_medical_segmentation":
        '(TITLE:uncertainty) AND (TITLE:segmentation OR TITLE:"medical image")',
    "spine_us_3d_reconstruction":
        '(TITLE:ultrasound) AND (TITLE:spine OR TITLE:spinal OR TITLE:scoliosis) AND (TITLE:"3D" OR TITLE:reconstruction OR TITLE:volumetric)',
    "public_us_datasets":
        '(TITLE:ultrasound) AND (TITLE:dataset OR TITLE:"open-source" OR TITLE:benchmark) AND (TITLE:segmentation OR TITLE:"deep learning" OR TITLE:annotated)',
    "domain_shift_medical_imaging":
        '(TITLE:"domain shift" OR TITLE:"domain adaptation" OR TITLE:generalization OR TITLE:generalisation) AND (TITLE:ultrasound OR TITLE:"medical image")',
    "lp_complications_outcomes":
        '(TITLE:"lumbar puncture") AND (TITLE:complication* OR TITLE:"traumatic tap" OR TITLE:headache OR TITLE:success)',
}

FIELDS = ["category","rank","pmid","pmcid","doi","title","authors_first","journal",
          "year","pub_types","is_open_access","in_pmc","license","cited_by",
          "abstract_snippet","europepmc_url","query"]

def search(query, page_size=25):
    url = (BASE + "?query=" + urllib.parse.quote(query) +
           f"&resultType=core&format=json&pageSize={page_size}&sort=CITED%20desc")
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            if attempt == 3:
                print(f"  !! {e}", file=sys.stderr); return {}
            time.sleep(3 * (attempt + 1))

def main():
    rows, seen = [], set()
    raw_all = {}
    for cat, q in QUERIES.items():
        d = search(q)
        res = d.get("resultList", {}).get("result", []) or []
        raw_all[cat] = res
        print(f"{cat:34s} {len(res):3d} hits")
        for i, r in enumerate(res, 1):
            key = r.get("doi") or r.get("pmid") or r.get("id")
            if key in seen:
                continue
            seen.add(key)
            auth = (r.get("authorString") or "").split(",")[0].strip()
            rows.append({
                "category": cat, "rank": i,
                "pmid": r.get("pmid",""), "pmcid": r.get("pmcid",""),
                "doi": r.get("doi",""), "title": (r.get("title") or "").strip().rstrip("."),
                "authors_first": auth, "journal": (r.get("journalInfo") or {}).get("journal",{}).get("title",""),
                "year": r.get("pubYear",""),
                "pub_types": "|".join((r.get("pubTypeList") or {}).get("pubType") or []),
                "is_open_access": r.get("isOpenAccess",""), "in_pmc": r.get("inPMC",""),
                "license": r.get("license",""), "cited_by": r.get("citedByCount",""),
                "abstract_snippet": re.sub(r"\s+"," ",(r.get("abstractText") or ""))[:400],
                "europepmc_url": f"https://europepmc.org/article/MED/{r.get('pmid')}" if r.get("pmid") else "",
                "query": q,
            })
        time.sleep(1.0)

    (RAW/"europepmc_raw.json").write_text(json.dumps(raw_all, indent=1), encoding="utf-8")
    p = OUT/"LITERATURE_DATABASE.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    print(f"\nunique records: {len(rows)} -> {p}")

if __name__ == "__main__":
    main()
