# Lumbar_MarkAny

**Public-data feasibility study for AI-assisted, robot-acquired lumbar
ultrasound in support of neuraxial needle access.**

This repository is the research record for Phase 0 of the project: establishing
what public evidence exists, what can actually be obtained, what can honestly be
measured with it, and precisely what is missing that only a clinical partner can
supply.

> **Scope warning.** Nothing here is a medical device, and nothing here has been
> clinically validated. Experiments now DO run on real human lumbar ultrasound
> (V2), but that data is healthy volunteers imaged **prone** with a **10 MHz
> linear** probe, annotated for **visible bone surface only** — not the
> population, position, probe or label set of a lumbar puncture. Claims are
> labelled by evidence level and evidence class throughout; see
> `CLAIMS_LEDGER.csv` and `deliverables/paper_v2_assets/paper_claims_forbidden.md`.

---

## The short version — V2

| | |
|---|---|
| **What V1 concluded** | That the anchor lumbar dataset was unreachable, and that no public real human transcutaneous lumbar ultrasound could be obtained. |
| **What was actually true** | The dataset is **public, CC-BY-4.0, and obtainable**. Only this workstation's network route was blocked (the whole 134.58.0.0/16 range, including the S3 host). A proxied request returned `{"status":"OK","version":"6.7.1"}` — the server was up the entire time. |
| **What V2 holds** | **6,182 expert-annotated real human lumbar ultrasound frames from 9 subjects**, handheld and robot-assisted, all MD5-verified. The annotated subset needed **1.70 GB**, not the deposit's 631 GB, because each label archive ships the frames alongside the labels. |
| **What is still missing — and now provably so** | **No procedural label exists in any public dataset.** The KU Leuven labels are `{0 or 1, 2}`: background and **visible bone surface**. No entry point, trajectory, target depth, interspace choice or outcome. |

Full correction, including retracted and superseded claims:
[`research/datasets/V2_ACCESS_CORRECTION.md`](research/datasets/V2_ACCESS_CORRECTION.md).

> **Start with [`START_HERE.md`](START_HERE.md) and `00_VISUAL_INDEX.html`.**
> Real ultrasound is on the first screen.

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

**V2 adds an evidence class.** Experiments are now marked **PRIMARY** (real
human lumbar) or **SECONDARY** (porcine intraoperative). exp001–exp004 are
secondary: verified from their `config.json`, they all read the Johns Hopkins
porcine post-laminectomy dataset. They remain methodologically sound and are
retained, but they are not evidence for a human lumbar-puncture product.

---

## What was actually executed (E1)

| Experiment | Question | Result |
|---|---|---|
| [`exp001_leakage_audit`](experiments/exp001_leakage_audit/) | Do the official JHU splits leak near-duplicate frames into the test set? | **No.** Within-sweep adjacent frames have cosine ≈0.99 (median), but no held-out image exceeds 0.89 against any training image. A negative result: our leakage hypothesis was wrong and the splits are sweep-disjoint. |
| [`exp002_class_distribution`](experiments/exp002_class_distribution/) | Do the distributed masks contain what the publication claims? | **Yes, exactly.** All 10 classes reproduced to the pixel (only 13 stray anti-aliased pixels differ across 1.9 billion). Also recovered the **undocumented** palette→class mapping, now published in `src/lumbar_markany/data_jhu.py`. |
| [`exp003_unet_baseline`](experiments/exp003_unet_baseline/) | Baseline 10-class segmentation on the official split. | Test macro Dice **0.7232** (95% bootstrap CI 0.7142–0.7321, n=660). Per class from 0.947 (Spinal cord) to 0.249 (Dura/Pia complex) — independently reproducing the source paper's qualitative finding that the rare complex classes fail worst. |
| [`exp004_uncertainty_failure`](experiments/exp004_uncertainty_failure/) | Can the model tell when it is wrong? | **Yes, measurably.** MC-dropout uncertainty correlates with real error at Spearman **ρ = −0.731** (entropy) and **−0.763** (pass disagreement). Declining the most-uncertain 30% raises retained Dice to 0.764. Failures concentrate in **dark, low-contrast** images (Dice vs contrast ρ = +0.542). |

### V2 — direct human lumbar (PRIMARY evidence)

| Experiment | Question |
|---|---|
| `exp005_lumbar_bone_seg` | Expert bone-surface segmentation on real human lumbar ultrasound, subject-disjoint 3-fold CV, with the full handheld/robot-assisted cross-domain matrix. |
| `exp006_lumbar_uncertainty` | Does uncertainty track error on **real human lumbar** data? (exp004 asked this on porcine data and cannot carry a human claim.) |

Numbers: `RESULTS_LEDGER.csv` and `experiments/exp005_lumbar_bone_seg/results.json`.

### V1 — porcine (SECONDARY evidence)

**These results are about porcine intraoperative spinal cord imaging, not lumbar
puncture.** They validate the pipeline; they say nothing about human neuraxial
anatomy. The uncertainty result matters to the *design* — it is direct evidence
that a system can be built to know when not to act — but it is not a safety
claim and the model is not safety-certified. That distinction is enforced in
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
python scripts/experiments/uncertainty_failure.py
python scripts/figures/make_figures.py
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

* **Nine annotated subjects.** Every human-lumbar number rests on nine people.
  Statistics are aggregated per subject and the spread across subjects is
  reported, because with nine points a confidence interval would imply more
  precision than the data supports.
* **Wrong population, position and probe.** Healthy volunteers aged 20–35, BMI
  19–26, imaged **prone** with a **10 MHz linear** transducer. Lumbar puncture
  is performed sitting or in lateral decubitus with a 2–5 MHz curvilinear probe,
  in patients selected for difficulty. This gap is one of *kind*, not quantity,
  and no amount of public data closes it.
* **A single annotator**, who also acquired the handheld scans. Inter-rater
  reliability for lumbar ultrasound annotation is unmeasured — by us and, as far
  as this survey found, by anyone.
* **Bone surface only.** The task we can measure is anatomy perception. The
  clinical decision layer has no ground truth anywhere.
* **Any HUS/RUS difference is confounded by construction** — protocol, depth,
  gain and operator all vary alongside the acquisition mode.
* exp001–exp004 remain porcine, intraoperative, with **no animal identifier**,
  so animal-level generalisation was never assessable there.
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
