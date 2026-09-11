# Direct human lumbar / neuraxial ultrasound datasets — 2026 survey

**Revises the V1 survey conclusion**, which counted the anchor deposit as
effectively absent because *we* could not reach it. See
`V2_ACCESS_CORRECTION.md`. This version separates four things V1 conflated:

| Status | Meaning |
|---|---|
| `PUBLIC_DOWNLOADABLE` | The pixels are obtainable now, by anyone, without asking |
| `REQUEST_ONLY` | Real human lumbar data exists but is held privately; authors invite contact |
| `PAPER_FIGURE_ONLY` | Only the article's figures are visible; no dataset released |
| `UNKNOWN` | Availability not established |

**An article figure is not a dataset.** That distinction is enforced in the
machine-readable provenance (`visuals/.../ANNOTATION_PROVENANCE.csv`, column
`evidence_type`: A = dataset pixels, B = dataset expert annotations,
C = publication figure).

---

## The corrected headline

> **Real, public, expert-annotated human transcutaneous lumbar ultrasound DOES
> exist, and we now hold it: 6,182 annotated frames from 9 subjects, both
> handheld and robot-assisted, CC-BY-4.0.**
>
> **What does not exist — in any dataset, public or private, that this survey
> located — is a procedural label.** No entry point, no trajectory, no target
> depth, no interspace decision, no outcome. Verified directly in the label
> arrays: values are `{1, 2}` only.

The hospital argument is therefore *stronger* than V1's, and differently
shaped. It is no longer "we need ultrasound". It is "anatomy perception can now
be measured on real human lumbar data; the clinical decision layer still has no
ground truth anywhere."

---

## Comparison table

| | **KU Leuven / Balgrist** | **SUID (Putian)** | JHU HEPIUS | Masoumi |
|---|---|---|---|---|
| Study / DOI | `10.48804/3XPCAE` · paper `10.1038/s41597-025-06047-9` | `10.1177/03000605261461196` (PMC13328980) | PMC12475011 | `10.5281/zenodo.4813508` |
| Year | 2025 | **2026** | 2025 | 2021 |
| Subjects | **63** (9 annotated) | **80** | 25 pigs + 8 humans | 3 human + 2 ex-vivo |
| Patients vs volunteers | healthy **volunteers**, 20–35 y, BMI 19–26 | **patients** — elective caesarean | animals + surgical patients | archival CT + phantoms |
| Pregnant | no | **yes, all** | n/a | no |
| Position | **prone** | **lateral decubitus** ✔ clinically correct | prone, surgical | n/a |
| Probe | **10 MHz linear** | **2–5 MHz convex** ✔ clinically correct | unknown | unknown |
| HUS / RUS | **both** (223 + 375 scans) | handheld only | handheld | n/a |
| Transcutaneous | **yes** | **yes** | **no** — post-laminectomy | no — exposed bone |
| Annotated images | **6,182 listed / 5,998 non-empty** (our count) | **1,000** | 10,223 | 21 landmark pairs ×2 |
| Annotation classes | **1** — bone surface | **4+** — interlaminar space, articular process, anterior complex, posterior complex | 10 anatomical | landmarks |
| Expert | one physician (also the HUS operator) | clinical team, Putian First Hospital | students → radiologist → spine fellow | unknown |
| Needle present | no | no | no | no |
| **Procedural target** | **no** | **no** | no | no |
| Outcomes | no | no | no | no |
| Tracking | **yes** — optical + robot pose | no | no | no |
| CT/MRI paired | **yes** — CT + L1–L5 STL | no | no | CT |
| **Download status** | **PUBLIC_DOWNLOADABLE — held** | **REQUEST_ONLY** | PUBLIC (no licence declared) | PUBLIC_DOWNLOADABLE |
| Licence | **CC-BY-4.0** | article CC BY-NC 4.0; **data not released** | **none declared** | CC-BY-4.0 |
| Usable for training | **yes** | no | yes (methodology only) | no |
| Usable for paper imagery | **yes, with attribution** | figures only, NC, with attribution | **no** — no licence | yes |
| Clinical relevance | high anatomy, wrong position/probe/cohort | **highest** — correct cohort, position and probe | low | low |

---

## KU Leuven / Balgrist — `PUBLIC_DOWNLOADABLE`, **held**

The only public dataset in this survey with real human transcutaneous lumbar
ultrasound and expert annotation. Full audit in `KULEUVEN_LABEL_AUDIT.md`.

**Strengths:** 9 annotated subjects × both modalities; paired handheld/robotic
in 7 of them; synchronised probe pose; paired CT; CC-BY-4.0; and the annotated
subset is only 1.70 GB.

**Limitations that do not go away by having the data:**
healthy volunteers aged 20–35 with BMI 19–26 — close to the inverse of the
difficult-LP population; **prone**, whereas neuraxial procedures are performed
sitting or in lateral decubitus; **10 MHz linear** probe, an orthopaedic
surgical-guidance protocol, not the low-frequency curvilinear imaging used for
neuraxial access; a **single annotator**, so inter-rater reliability is
unmeasured; and **bone surface only**.

## SUID (Putian) — `REQUEST_ONLY`, **high value**

*"An adaptive attention U-network for recognizing ultrasound images"*,
J Int Med Res 2026, PMC13328980, article CC BY-NC 4.0.

80 pregnant women undergoing elective caesarean under ultrasound-guided
intraspinal anaesthesia at the First Hospital of Putian; 1,000 annotated
images; **lateral position**; **2–5 MHz convex-array probe**; scanning from the
sacrum cranially with interspace counting; ethics approval 2024-167.

Annotated structures — **interlaminar spaces, articular processes, anterior
complex and posterior complex** — are materially closer to procedural relevance
than bone surface alone.

**Availability, in the authors' own words:**

> "The datasets generated and/or analyzed during the current study are not
> publicly available due to patient consent agreements and ethical
> restrictions. Requests for access to the data should be directed to the
> corresponding author."

**Therefore: not public. Do not describe SUID as a public dataset.** Its
article figures are reusable non-commercially with attribution as
`evidence_type = C`; its pixels are not training data for us.

**Why it matters anyway:** it is direct evidence that the cohort, position and
probe class our project needs are achievable in a real obstetric service, and
that a hospital of comparable size can produce 1,000 annotated images. It is a
strong precedent to cite in the Indonesian proposal, and a candidate for a data
access request (`DATA_ACCESS_REQUEST_TEMPLATES.md`).

## JHU HEPIUS — public, but not lumbar

Retained as **secondary methodological evidence only**. Porcine, intraoperative,
post-laminectomy: the bone that neuraxial ultrasound must see *through* has been
surgically removed. **No licence is declared**, so its pixels are not
redistributed by this project.

## Masoumi — public, but not real human ultrasound

Its three *human* subjects have CT and **CT-simulated** ultrasound only; real
ultrasound exists solely for two ex-vivo animal phantoms.

---

## What changed from V1, and why

| V1 said | V2 says |
|---|---|
| "Only 2 Tier-0 datasets, neither with real human transcutaneous lumbar ultrasound" | Wrong as written. The anchor deposit is exactly that, and we hold it. |
| Anchor dataset = 1,006 GB, unreachable | 630.94 GB live; the **annotated subset is 1.70 GB**; retrieved and verified. |
| "Public data cannot close the population/position/probe gap" | **Still true, and now demonstrated rather than asserted** — we have the anatomy data and can see precisely what is missing. |
| "No public dataset records a procedural target" | **Confirmed at the file level**: label values are `{1, 2}`, nothing else. |

## Honest limits of this survey

* Repository- and PubMed-indexed sources, one network, one day.
* `REQUEST_ONLY` is a statement about published availability, not a prediction
  about whether authors would share on request.
* Absence of a procedural-label dataset is a strong negative finding across the
  sources searched — not proof none exists anywhere.
