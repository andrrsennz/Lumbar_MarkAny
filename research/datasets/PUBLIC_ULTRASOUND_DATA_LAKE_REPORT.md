# Public ultrasound data lake report

**Date of survey:** 2026-09-11 · **Evidence labels:** E1 executed here · E2 dataset fact · E3 peer-reviewed external · E5 engineering inference

This report answers the ten questions posed in the project brief, using only
numbers this project measured or verified against primary sources.

---

## Q1. How much public ultrasound data did we identify?

**891 unique candidate records** across six repository APIs (DataCite 334,
Zenodo 337, OpenAIRE 210, HuggingFace 5, Dryad 4, OSF 1). Of these, **420
records' own titles/abstracts mention ultrasound**, and **110 are typed as
`dataset`** rather than article/trial/model. *(E1)*

Tier distribution of the 110 ultrasound-typed datasets:

| Tier | Description | Count |
|---|---|---|
| T0 | Human lumbar / neuraxial ultrasound | **2** |
| T1 | Spine / robotic / tracked / bone-surface ultrasound | 8 |
| T2 | Needle-in-ultrasound | 5 |
| T3 | Supporting spinal / animal / phantom | 10 |
| T4 | Broad ultrasound ecosystem (other organs) | 54 |
| — | Unclassified | 31 |

## Q2. How much was actually downloadable?

Of the datasets assessed in detail (`DATASET_REGISTRY.csv`):

| Access status | Datasets |
|---|---|
| `PUBLIC_DOWNLOADABLE` | 3 (DS002, DS004, DS005) |
| `PUBLIC_BUT_UNREACHABLE_FROM_THIS_NETWORK` | 1 (DS001 — the anchor) |
| `UNKNOWN` | 1 (DS003 UltraBones100k) |

Across the wider 110-dataset pool, the dominant licences were permissive
(`cc-by-4.0` 73, `cc-zero` 19), so **licensing was rarely the binding
constraint. Reachability and relevance were.** *(E1)*

## Q3. How much was downloaded?

**1.45 GB across 3 archives, all checksummed** (`provenance/DATA_DOWNLOAD_LOG.csv`):

| Dataset | Archive | Bytes | SHA-256 (first 16) |
|---|---|---|---|
| DS005 JHU injury localization | `jhu_injury_localization.zip` | 224,279,362 | `8bdf07250c02376f` |
| DS004 JHU segmentation | `jhu_segmentation.zip` | 1,079,559,546 | `8842d153b887c8ef` |
| DS002 Masoumi US/CT | `Data.zip` | 148,576,333 | *(see log)* |

Contents verified by direct inspection, not by trusting the README:

* DS004 — **10,223** image/mask pairs (8,668 train / 895 val / 660 test), exactly matching the publication. *(E1 confirming E2)*
* DS005 — **2,245** PNGs + 2,246 XMLs; 877 pre-injury images contain **zero** boxes, 1,368 post-injury contain **exactly one** each. Matches the publication's 877/1,368 split exactly. *(E1 confirming E2)*
* DS002 — 3 human subjects (CT + **simulated** US only), 2 ex-vivo phantoms (CT + **real** US + simulated US), 21 landmark pairs each. *(E1)*

**Not downloaded: the anchor dataset (1.01 TB, 1,346 files).** Unreachable —
see `KULEUVEN_ACCESS_BLOCKER.md`.

## Q4. How much is directly related to lumbar access?

**None of the data we hold.** This is the most important sentence in this report.

| Dataset held | Species | Path to anatomy | Relation to lumbar puncture |
|---|---|---|---|
| DS004 / DS005 | porcine (+8 human images) | **intraoperative, after laminectomy** | Bone removed to create the acoustic window; target is cord/meninges, not dorsal bone landmarks. **Not** transcutaneous neuraxial imaging. |
| DS002 human subjects | human | CT only | Ultrasound is **simulated from CT**, not acquired. |
| DS002 phantoms | canine / lamb, ex-vivo | exposed bone | Not in-vivo, not human, not transcutaneous. |

The only dataset in the world we identified that *is* directly related — human,
in-vivo, transcutaneous, lumbar, annotated — is DS001, which we could not
reach. And even DS001 carries substantial clinical caveats (Q10).

## Q5. How much has expert annotation?

| Dataset | Annotated units | Annotator | Inter-rater agreement |
|---|---|---|---|
| DS001 (not held) | 6,091 frames from **9 of 63** subjects | **one** physician, who also acquired the HUS data | **none possible — single annotator** *(E2)* |
| DS004 | 10,223 masks, 10 classes | students trained by a board-certified radiologist; ambiguous cases adjudicated by the radiologist; all masks re-validated by a neurosurgery spine fellow | not reported *(E2)* |
| DS005 | 1,368 boxes | as DS004 | not reported *(E2)* |
| DS002 | 21 landmark pairs × 2 phantoms | unknown | not reported *(E2)* |

**DS004 has the more defensible annotation process of the two large sets** —
two-stage clinical review versus DS001's single annotator. That is an
uncomfortable but important observation about our own anchor dataset.

## Q6. What annotation types exist?

* **Pixel masks, single class** — DS001 "bone surface" (`.mhd` label volumes, annotated in ImFusion *Labels*).
* **Pixel masks, 10 classes** — DS004 (RGB PASCAL-VOC palette PNG, made in CVAT).
  The release does **not** document the palette→class mapping; we recovered it
  empirically and it is now published in `src/lumbar_markany/data_jhu.py`. *(E1)*
* **Bounding boxes** — DS005 (PASCAL-VOC XML), single class "injury".
* **Point landmark correspondences** — DS002 (`.tag`), for registration validation.
* **6-DoF pose streams** — DS001 (optical marker quaternions for HUS; robot
  end-effector roll/pitch/yaw for RUS; a separate breathing marker). *(E2)*

Nothing anywhere in this survey annotates a **procedural target**: no entry
point, no needle trajectory, no interspace selection, no operator confidence.

## Q7. Which datasets can legally be redistributed?

| Dataset | Licence | Redistribution |
|---|---|---|
| DS001 | **CC-BY-4.0** | **Yes**, with attribution — including derived figures |
| DS002 | **CC-BY-4.0** | **Yes**, with attribution |
| DS004 / DS005 | **none declared** — no `LICENSE` in the GitHub repo, none in the Drive archives | **No.** Absence of a licence is not permission. |

**Operational consequence, already applied in this package:** no DS004/DS005
image, mask, or derived overlay is redistributed in this repository or in the
portable ZIP. Numerical results computed from them are our own work and are
reported freely; the pixels are not ours to pass on. Figures that need to show
real annotated ultrasound must wait for DS001 (CC-BY) or for hospital data.

## Q8. Which are only useful for pretraining?

* **T4 (54 datasets)** — breast, thyroid, fetal, cardiac, lung, prostate,
  vascular. Useful only for ultrasound-domain representation learning. Their
  label spaces are unrelated to spine anatomy and **must never be merged**.
* **DS004/DS005** — beyond pretraining they served here as an *engineering
  substrate*: the pipeline (loader, loss, subject-aware evaluation, bootstrap
  CIs, uncertainty, failure analysis) was built and validated on them, so that
  it can be pointed at DS001 or hospital data without being written from
  scratch under time pressure.
* **DS002** — too small to train anything; a registration benchmark only.

## Q9. What major dataset gaps exist?

1. **No public transcutaneous human lumbar ultrasound outside DS001.** *(E1)*
2. **No procedural ground truth anywhere.** Not one public dataset records
   where a clinician chose to insert, at what angle, to what depth, or whether
   the puncture succeeded.
3. **No difficult-anatomy population.** DS001 is healthy volunteers, BMI 19–26,
   age 20–35. The patients who actually need ultrasound assistance — obese,
   elderly, degenerative, scoliotic, post-surgical — are absent from every
   public dataset found.
4. **Wrong patient position.** DS001 is **prone**. Lumbar puncture is performed
   **sitting or in lateral decubitus**. Spinal flexion, interspinous gaps and
   soft-tissue geometry all differ. *(E2 → E5)*
5. **Wrong probe class.** DS001 used a **10 MHz linear** transducer at 7.7 cm
   depth. Neuraxial practice uses **low-frequency (2–5 MHz) curvilinear**
   probes for penetration. Images from the two are not interchangeable. *(E2 → E5)*
6. **Single-annotator labels** on the only lumbar dataset, so annotation
   reliability for this task is entirely unmeasured.
7. **No needle-in-lumbar-ultrasound data.** Five Tier-2 needle datasets were
   found; none are neuraxial.
8. **No Indonesian or Southeast Asian data at all**, and no dataset reporting
   the body-habitus distribution of the intended deployment population.

## Q10. Why is Indonesian hospital data still necessary?

Because every gap in Q9 is a gap that public data **structurally cannot close**,
and four of them are not about quantity of data but about *kind*:

* **Population.** A model validated on 63 healthy Swiss volunteers aged 20–35
  with BMI ≤26 has no evidential claim over an Indonesian clinical population.
  Difficult lumbar puncture is defined by the very body habitus DS001 excludes.
* **Position and probe.** Prone / 10 MHz linear is an orthopaedic surgical
  protocol. To support neuraxial access we need sitting or lateral-decubitus
  imaging with a curvilinear probe. No public dataset provides this.
* **Labels that do not exist in any public dataset.** Bone surface is *visible
  anatomy*. Choosing an interspace, an entry point, a trajectory and a target
  depth is a *clinical decision*. Only clinicians can create that layer, and no
  amount of public bone-surface data substitutes for it. This is the boundary
  the whole proposal is built on — see `research/annotations/HOSPITAL_ANNOTATION_ONTOLOGY_v0.1.md`.
* **Reliability.** With a single annotator on DS001, inter-rater agreement for
  lumbar ultrasound annotation is an open question. A hospital collaboration
  with ≥2 independent annotators and adjudication is the only way to measure it.

**What we can honestly tell a hospital:** the public evidence base is sufficient
to build and validate the *engineering pipeline*, and we have done so and
measured it. It is **not** sufficient to make any clinical claim about lumbar
puncture in their patients, and we are not making one.

---

## Summary table

| Question | Answer |
|---|---|
| Candidates identified | 891 records; 420 ultrasound-relevant; 110 typed datasets |
| Tier-0 datasets found | **2** — neither containing real human transcutaneous lumbar US |
| Downloaded | 3 archives, 1.45 GB, all checksummed |
| Directly LP-relevant data held | **none** |
| Anchor dataset | verified in depth, **1.01 TB, unreachable from this network** |
| Redistributable pixels held | DS002 only (CC-BY); DS004/DS005 have **no licence** |
| Public procedural ground truth | **none exists** |
