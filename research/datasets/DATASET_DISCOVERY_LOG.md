# Dataset discovery log

All searches recorded here were executed on **2026-09-11** from the project
workstation. Machine-readable outputs:

* raw API responses — `data/registry/discovery_raw/` (not tracked in Git; regenerate with the scripts below)
* consolidated, de-duplicated, scored candidates — `data/registry/DISCOVERY_CANDIDATES.csv` (891 rows)
* curated registry of datasets actually assessed — `research/datasets/DATASET_REGISTRY.csv`

Reproduce with:

```bash
python scripts/data/discover_sources.py datacite huggingface osf dryad openaire
bash   scripts/data/zenodo_harvest.sh
python scripts/data/triage_discovery.py
```

---

## 1. Repositories queried programmatically

| Repository | Endpoint | Queries | Unique candidates | Outcome |
|---|---|---|---|---|
| DataCite | `api.datacite.org/dois` | 24 | 334 | Worked. Broadest cross-repository index; the single most productive source. |
| Zenodo | `zenodo.org/api/records` | 23 | 337 | Worked **after** fixing `size` (see §3). |
| OpenAIRE | `api.openaire.eu/search/datasets` | 24 | 210 | Worked. Heavily weighted to clinical-trial records rather than imaging data. |
| Hugging Face | `huggingface.co/api/datasets` | 24 | 5 | Worked; almost nothing relevant. |
| Dryad | `datadryad.org/api/v2/search` | 24 | 4 | Worked; nothing relevant. |
| OSF | `api.osf.io/v2/nodes` | 24 | 1 | Worked; title-only filter is very restrictive. |
| **KU Leuven RDR** | `rdr.kuleuven.be/api/...` | — | **0** | **Unreachable at TCP level.** See `KULEUVEN_ACCESS_BLOCKER.md`. |

Query terms spanned all five relevance tiers: lumbar/neuraxial/epidural/spinal-
anaesthesia (Tier 0); robotic, tracked, 3D, bone-surface, US-CT registration,
vertebra, scoliosis (Tier 1); needle segmentation/tracking/insertion (Tier 2);
spinal cord, porcine, phantom (Tier 3); breast, thyroid, fetal, cardiac, lung,
nerve, liver, prostate, musculoskeletal, vascular (Tier 4).

## 2. Targeted (non-programmatic) verification

These were pursued by name because the project brief or the anchor publication
named them.

| Target | How checked | Result |
|---|---|---|
| KU Leuven lumbar HUS/RUS/CT (`10.48804/3XPCAE`) | Crossref, DataCite, Europe PMC full text, TCP probes | Metadata and full text verified in detail; **files unreachable** |
| JHU spinal-cord US dataset | Europe PMC full text → GitHub README → Google Drive | **Downloaded** (both subsets), fully verified |
| UltraBones100k | Crossref, arXiv `2502.03783v4` | Lower-limb cadaveric; **no public download located**; marked UNKNOWN |
| SUID (Spine Ultrasound Image Dataset) | Europe PMC title/abstract searches | **No record located** under that name; not entered in the registry |
| Rivanna Accuro / Accuro 3S | openFDA 510(k) API | 7 clearances verified (see `research/competitors/`) |

## 3. Search failures and how they were resolved

Recording these because a silent API failure looks identical to "no data
exists", and would have produced a materially wrong conclusion.

| Symptom | Real cause | Fix |
|---|---|---|
| Zenodo returned HTTP 400 for every query | `size=40`; anonymous requests are capped at **25** | `size=25`; the error body states this explicitly |
| Zenodo returned 0 rows even on HTTP 200 | `h.get("access", {})` — the key **exists with value `None`**, so the `{}` default never applied and `.get()` raised | `(h.get("access") or {})` |
| 100% of candidates flagged "mentions ultrasound" | The retrieving **query string** was being scored alongside the record, and every query contains "ultrasound" | Score `title`+`description` only |
| `stderr` appeared before `stdout` in logs, implying all queries failed | Python buffers stdout when redirected; stderr is unbuffered | Read the whole log, not the tail |

The first three would each have silently corrupted the headline finding below.

## 4. Results by tier — records whose **own text** mentions ultrasound

| Tier | Any record type | Typed as `dataset` |
|---|---|---|
| T0 — lumbar / neuraxial | 59 | **2** |
| T1 — spine / robotic / tracked | 25 | 8 |
| T2 — needle in ultrasound | 17 | 5 |
| T3 — supporting spinal / animal / phantom | 14 | 10 |
| T4 — broad ultrasound ecosystem | 209 | 54 |
| unclassified | 96 | 31 |
| **total** | **420** | **110** |

Licences among the 110 ultrasound-typed datasets: `cc-by-4.0` 73, `cc-zero` 19,
none declared 10, `cc-by-nc-sa-4.0` 3, `cc-by-nc-4.0` 3, `mit` 2.

### The headline finding

**Across every repository reachable from this machine, exactly two Tier-0
ultrasound datasets were found, and neither contains real human transcutaneous
lumbar ultrasound.**

* `10.5281/zenodo.4813508` (downloaded) — its three *human* subjects have CT and
  **CT-simulated** ultrasound only. Real ultrasound exists solely for two
  **ex-vivo animal** phantoms imaged on exposed bone.
* "Technical Feasibility of Electromagnetic US/CT Fusion Imaging and Virtual
  Navigation…" — a clinical-feasibility record, not an imaging corpus.

Outside the KU Leuven deposit, **no public, annotated, real human transcutaneous
lumbar or neuraxial ultrasound dataset was located.** That single sentence is
the empirical basis for the hospital collaboration proposal, and it is a
*measured* result of this search rather than an assumption.

## 5. Candidates rejected, with reasons

| Candidate / class | Count | Reason for rejection |
|---|---|---|
| Tier-4 organ datasets (breast, thyroid, fetal, cardiac, lung, prostate …) | 54 typed datasets | Not rejected outright — **catalogued for possible pretraining only.** Label spaces must never be merged with spine anatomy. |
| Clinical-trial registry records (OpenAIRE) | ~180 | Trial protocols/results, **no imaging data attached**. Useful as literature, not as data. |
| Non-ultrasound "lumbar" hits (finite-element models, GWAS, vertebral morphometry, cadaveric mechanics) | ~170 | Keyword collision on "lumbar"/"spine"; no imaging. |
| Bibliographic noise (review articles typed as `dataset` on Zenodo) | ~30 | Journal articles mis-typed by depositors. |
| UltraBones100k | 1 | Availability unverifiable; also lower-limb, not spine. Left in registry as UNKNOWN rather than claimed. |
| SUID | 1 | No locatable record. **Not** entered as a dataset. |
| Duplicate mirrors / re-uploads | — | None adopted. Third-party re-uploads of the KU Leuven deposit were deliberately **not** sought as a substitute; unverified mirrors are unacceptable provenance. |

## 6. Tier-1/2 candidates worth pursuing next

Not downloaded in this pass; recorded so the next operator does not re-derive them.

| Dataset | Licence | Why it matters |
|---|---|---|
| Trackerless 3D Freehand Ultrasound Reconstruction Challenge 2024 (train + validation) | `cc-by-nc-sa-4.0` | Directly relevant to sweep reconstruction without external tracking — the fallback if optical/robot tracking is unavailable clinically. NC licence limits commercial use. |
| "Freehand ultrasound without external trackers" | `cc-by-4.0` | Same theme, permissive licence. |
| Shoulder 3D Ultrasound Mosaicking Dataset | `cc-by-4.0` | Pose-estimation vs hybrid alignment for US mosaicking; methodologically transferable to spine sweeps. |
| Micro-Ultrasound Prostate Segmentation Dataset | `cc-by-4.0` | Tier-2/4; clean segmentation benchmark for pretraining studies. |

## 7. Honest limitations of this search

* **One network, one day.** The KU Leuven block means the most important
  repository in this field was never searched from the inside; its holdings
  beyond the anchor deposit are unknown to this survey.
* **API-indexed material only.** Datasets published only as a link on a lab
  webpage, or in supplementary material behind a publisher paywall, are largely
  invisible to this method. The JHU dataset is a case in point — it was found
  via the *paper*, not via any data repository, and a repository-only search
  would have missed it entirely.
* **Keyword triage is not a relevance judgement.** `relevance_score` in
  `DISCOVERY_CANDIDATES.csv` ranks candidates for inspection. Every dataset that
  reached `DATASET_REGISTRY.csv` was then assessed by reading the source
  publication and, where downloaded, by inspecting the actual files.
* **Absence of evidence.** "No public human lumbar US dataset was found" is a
  statement about this search, executed with these queries, from this network.
  It is strong evidence, not proof of non-existence.
