# Lumbar_MarkAny

**Public-data feasibility study for AI-assisted, robot-acquired lumbar
ultrasound in support of neuraxial needle access.**

This repository is the research record for Phase 0 of the project: establishing
what public evidence exists, what can actually be obtained, what can honestly be
measured with it, and precisely what is missing that only a clinical partner can
supply.

> **Scope warning.** Nothing here is a medical device, and nothing here has been
> clinically validated. No experiment in this repository was run on human lumbar
> ultrasound. Claims are labelled by evidence level throughout; see
> `CLAIMS_LEDGER.csv`.

---

## The short version

| | |
|---|---|
| **What we set out to do** | Train and evaluate lumbar bone-surface segmentation on the KU Leuven paired handheld/robotic lumbar ultrasound dataset (`doi:10.48804/3XPCAE`). |
| **What blocked it** | The entire `kuleuven.be` domain is unreachable at TCP level from this network, while every other research repository responds normally. The dataset is also 1.01 TB. See [`research/datasets/KULEUVEN_ACCESS_BLOCKER.md`](research/datasets/KULEUVEN_ACCESS_BLOCKER.md). |
| **What we did instead** | Verified the anchor dataset exhaustively from its open-access full text; surveyed 891 candidate datasets across six repositories; acquired and verified 1.45 GB of the spinal ultrasound data that *is* reachable; and built + measured the complete analysis pipeline on it. |
| **Headline survey finding** | Outside the KU Leuven deposit, **no public, annotated, real human transcutaneous lumbar ultrasound dataset was found**, and **no public dataset anywhere records a procedural target** — entry point, trajectory, depth or outcome. |

---

## Evidence labels

Used consistently across every document in this repository.

| Label | Meaning |
|---|---|
| **E1** | Result executed inside this project (code + config + log + output in `experiments/`) |
| **E2** | Public dataset fact, verified against repository metadata or the dataset's publication |
| **E3** | Peer-reviewed finding reported by another group |
| **E4** | Commercial / regulatory fact from an authoritative source (e.g. openFDA) |
| **E5** | Engineering inference drawn from the above |
| **E6** | Future proposal — not implemented, not validated |

---

## What was actually executed (E1)

| Experiment | Question | Result |
|---|---|---|
| [`exp001_leakage_audit`](experiments/exp001_leakage_audit/) | Do the official JHU splits leak near-duplicate frames into the test set? | **No.** Within-sweep adjacent frames have cosine ≈0.99 (median), but no held-out image exceeds 0.89 against any training image. A negative result: our leakage hypothesis was wrong and the splits are sweep-disjoint. |
| [`exp002_class_distribution`](experiments/exp002_class_distribution/) | Do the distributed masks contain what the publication claims? | **Yes, exactly.** All 10 classes reproduced to the pixel (only 13 stray anti-aliased pixels differ across 1.9 billion). Also recovered the **undocumented** palette→class mapping, now published in `src/lumbar_markany/data_jhu.py`. |
| [`exp003_unet_baseline`](experiments/exp003_unet_baseline/) | Baseline 10-class segmentation on the official split. | See `experiments/exp003_unet_baseline/metrics.json`. Reported with per-class Dice/IoU, bootstrap 95% CIs, and explicit NaN handling for absent classes. |

**These results are about porcine intraoperative spinal cord imaging, not lumbar
puncture.** They validate the pipeline; they say nothing about human neuraxial
anatomy. That distinction is enforced in
[`deliverables/paper/CLAIMS_NOT_ALLOWED.md`](deliverables/paper/CLAIMS_NOT_ALLOWED.md).

---

## Layout

```
research/      datasets, literature, annotation ontology, competitors, IP, robotics, system
scripts/       data acquisition, analysis, experiments, figures  (everything is re-runnable)
src/           importable library code
experiments/   one directory per run: config, logs, metrics, predictions
provenance/    download log with SHA-256 for every acquired archive
deliverables/  paper package, hospital proposal, hospital slides
annotation/    CVAT schema, converters, manual
data/          local data lake -- NOT tracked in Git (see .gitignore)
```

---

## Reproducing

```bash
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt

# 1. survey
python scripts/data/discover_sources.py datacite huggingface osf dryad openaire
bash   scripts/data/zenodo_harvest.sh
python scripts/data/triage_discovery.py
python scripts/data/build_registry.py
python scripts/data/build_literature_db.py

# 2. acquire (the anchor dataset step will fail until it is reachable -- by design)
python scripts/data/download_kuleuven.py --check-only
python scripts/data/download_jhu_spinal.py
python scripts/data/verify_checksums.py

# 3. analyse
python scripts/analysis/leakage_audit.py
python scripts/analysis/verify_class_distribution.py
python scripts/experiments/train_seg.py --epochs 30
```

A GPU is optional; `train_seg.py` falls back to CPU. The reported run used an
RTX 2060 (6 GB) at ~105 s/epoch.

---

## Data handling

This repository is **public**. It contains code, documentation, manifests and
small derived tables only.

* **No dataset pixels are redistributed here.** The JHU data carries **no
  licence** — neither the GitHub repository nor the archives declare one — so it
  is used locally and its images are not republished. Absence of a licence is
  not permission.
* The anchor dataset is CC-BY-4.0 and *may* be redistributed with attribution
  once obtained, subject to size limits.
* No patient-identifiable data exists anywhere in this project, and none will be
  committed here when hospital collaboration begins.

---

## Status and honest limitations

* The single most scientifically valuable experiment this project proposed —
  handheld vs robot-assisted cross-domain generalisation — **has not been run**,
  because the data could not be reached. It remains the recommended first
  experiment; see `deliverables/paper/PAPER_RECOMMENDATION.md`.
* All quantitative results are from a porcine, intraoperative, post-laminectomy
  dataset with **no animal identifier**, so animal-level generalisation cannot
  be assessed.
* The dataset survey covers repositories with public search APIs. Datasets
  published only on a lab webpage are largely invisible to it — the JHU dataset
  was found via its *paper*, not via any repository index.

## Citation

If you use this work, cite the underlying datasets and publications, not this
repository alone. See `research/datasets/DATASET_REGISTRY.csv` for the required
attributions.

## Licence

Code in this repository: MIT (see `LICENSE`). Documentation: CC-BY-4.0.
Third-party datasets retain their own licences, which are recorded per dataset
in the registry and are **not** overridden by this repository's licence.
