# Paper outline

For the paper that is **writable now**, with no new data:

> **What public ultrasound data can and cannot tell us about lumbar puncture:
> a dataset survey and reproducibility audit**

Target: a data/methods venue (*Scientific Data* descriptor-adjacent, a
reproducibility track, or a medical-imaging methods journal). Length ~4,000
words, 5 figures, 3 tables.

The alternative paper — the acquisition-consistency study — cannot be outlined
responsibly until the pose data has been inspected. See `PAPER_RECOMMENDATION.md`.

---

## Title options

1. *What public ultrasound data can and cannot tell us about lumbar puncture: a dataset survey and reproducibility audit* ← recommended
2. *The missing label: procedural targets are absent from every public lumbar ultrasound dataset*
3. *Auditing public spinal ultrasound datasets: undocumented encodings, unreconstructible subject splits, and an absent procedural ground truth*
4. *A reproducibility audit of public ultrasound datasets for neuraxial needle guidance*

Option 2 is the most memorable and states the finding. Option 1 is safer and
better matches what the paper actually delivers, which is a survey plus an
audit. **Recommend 1, with 2 as the running headline in the abstract.**

---

## Abstract — fact bank

Only facts that trace to `CLAIMS_LEDGER.csv`.

* 891 candidate records; 6 repository APIs; 420 ultrasound-relevant; 110 typed datasets *(C012)*
* Tier-0: **2** datasets; **neither** with real human transcutaneous lumbar ultrasound *(C012)*
* **No** public dataset records any procedural target *(C013)*
* The one human lumbar deposit: 63 volunteers but **9** annotated subjects, **one** annotator, **prone**, **10 MHz linear** *(C001, C004, C005, C007)*
* Reproduced 10/10 class statistics exactly; 13 discrepant pixels in 1.94 × 10⁹ *(C014)*
* Recovered an **undocumented** palette→class mapping without which the data silently decodes wrongly *(C015)*
* 56.3% of images carry **no** subject token; animal-level splitting is unreconstructible *(C017)*
* Splits are nevertheless **sweep-disjoint** — our leakage hypothesis was disproved *(C016)*

---

## 1. Introduction

1. Neuraxial access is common and predictably difficult in an identifiable
   subgroup; pre-procedural ultrasound helps but is operator-dependent *(E3)*.
2. Automated interpretation has been pursued since 2008 and is commercially
   cleared *(C020, C026)* — the perception problem is not new.
3. Yet no system links perception to a clinically authored procedural decision.
4. **Question of this paper:** what does the public data actually support? Not
   "can we train a model", but "what claims can public data license".
5. Contributions: (i) a systematic, reproducible survey; (ii) a reproducibility
   audit of the largest public spinal ultrasound release; (iii) a recovered
   label encoding released as code; (iv) an explicit statement of the
   visible-anatomy / clinical-decision boundary.

## 2. Related work

Three strands, from `LITERATURE_DATABASE.csv` (442 records, 20 categories) and
`RESEARCH_GROUP_MAP.md`: clinical ultrasound for neuraxial access; automated
lumbar landmark detection; robotic ultrasound acquisition. Note that all three
exist and none are joined — and that a fourth strand, dataset auditing, is
essentially absent in this domain.

## 3. Methods

### 3.1 Dataset survey
Six repository APIs; 24 queries spanning five relevance tiers; de-duplication;
transparent keyword triage with the scoring function published. **Report the
three API failure modes that would each have silently corrupted the result**
(Zenodo's 25-item page cap returning HTTP 400; a `None`-valued key defeating a
`dict.get` default; query text contaminating relevance scoring). This belongs
in the paper, not in a footnote — it is the difference between a survey and a
guess.

### 3.2 Reproducibility audit
Exhaustive recomputation of per-class pixel and image counts from all 10,223
distributed masks; palette recovery by matching totals against the published
table.

### 3.3 Split-integrity audit
Filename-independent near-duplicate detection: 64×64 z-normalised cosine
similarity of every held-out image against every training image, **calibrated
against within-sweep adjacent-frame similarity** rather than against an assumed
threshold.

### 3.4 Baseline
U-Net, official split, Dice+CE, per-class Dice/IoU with **NaN for classes
absent from both prediction and truth**, image-level macro averaging, bootstrap
CIs. State explicitly that image-level bootstrap understates uncertainty
because animals cannot be resampled.

## 4. Results

| § | Content | Figure/Table |
|---|---|---|
| 4.1 | Survey: tier distribution, licences, the Tier-0 finding | **Fig 1**, Table 1 |
| 4.2 | Audit: exact reproduction; the recovered encoding | **Fig 2**, Table 2 |
| 4.3 | Split integrity: the negative result | **Fig 3** |
| 4.4 | Subject identifiability: 56.3% with no grouping token | Table 2 |
| 4.5 | Baseline performance, per class, with CIs | **Fig 4**, **Fig 5**, Table 3 |

## 5. Discussion

* **The binding constraint is not data volume, it is data *kind*.** 10,223
  annotated porcine frames exist; zero annotated human transcutaneous lumbar
  frames outside one deposit; zero procedural targets anywhere.
* **Undocumented encodings are a silent correctness hazard.** A user who
  assumes a palette order gets plausible-looking, wrong results with no error.
* **Subject identifiers are part of a dataset's contract.** Without them,
  subject-level generalisation — the only kind that matters clinically — is
  unverifiable no matter how careful the user is.
* **Publish the licence.** The most useful dataset we obtained has none, which
  makes redistribution of any derived figure legally uncertain and suppresses
  exactly the downstream use its authors intended.
* **Our leakage hypothesis was wrong**, and saying so matters: audits that only
  report confirmed problems are not audits.

## 6. Limitations

Import `LIMITATIONS.md` wholesale. Lead with: no experiment here used human
lumbar ultrasound; the anchor dataset was unreachable; the substrate is porcine
and intraoperative.

## 7. Conclusion

Public data is sufficient to build and validate the engineering pipeline, and
we did. It is **not** sufficient to support any clinical claim about lumbar
puncture, and the gap is structural — population, positioning, probe class, and
a category of label that nobody has ever created.

---

## Figure plan

| Fig | Content | Status |
|---|---|---|
| 1 | Dataset survey by tier | **rendered** `fig01_dataset_survey` |
| 2 | Class distribution, reproduced | **rendered** `fig02_class_distribution` |
| 3 | Split-integrity audit with calibration | **rendered** `fig03_leakage_audit` |
| 4 | Training curves | **rendered** `fig04_training_curves` |
| 5 | Per-class Dice with n | **rendered** `fig05_per_class_dice` |
| S1 | The four-column translational figure | **not made** — column 1 needs a licensed real ultrasound image, which we do not have. Deferred rather than faked. |

## Table plan

| Table | Content | Source |
|---|---|---|
| 1 | Tier distribution and licences across surveyed datasets | `DISCOVERY_CANDIDATES.csv` |
| 2 | Audit results: reproduced counts, recovered encoding, subject identifiability | `exp001`, `exp002` |
| 3 | Baseline: per-class Dice/IoU, n defined, CIs | `exp003` |

## Authorship and data statement

Data: all sources cited by DOI with licences stated; JHU data not
redistributed (no licence). Code: MIT, public repository. All experiment
configs, logs and metrics included so every number is checkable.
