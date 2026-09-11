# Claims forbidden — V2

Supersedes and extends `deliverables/paper/CLAIMS_NOT_ALLOWED.md`. Everything
in that file still applies. What changes in V2 is that we now hold real human
lumbar ultrasound, which creates a **new** and more dangerous class of
overclaim: the data is close enough to the clinical target that sloppy wording
will read as a clinical result.

---

## 1. The new risk: "human lumbar" does not mean "lumbar puncture"

| Forbidden | Why | Say instead |
|---|---|---|
| "we segment lumbar puncture anatomy" | We segment **visible bone surface**. The label array has exactly one annotated value. | "expert-annotated visible bone surface in lumbar ultrasound" |
| "our model identifies the puncture site / interspace / window" | No such label exists in any dataset we hold or found. | — omit — |
| "validated on human lumbar puncture data" | The data is healthy volunteers, **prone**, imaged with a **10 MHz linear** probe for orthopaedic guidance. No puncture occurred. | "evaluated on human lumbar ultrasound acquired under an orthopaedic surgical-guidance protocol" |
| "clinically relevant accuracy" | No clinical endpoint was measured. | "Dice and tolerance-band F1 against a single expert's annotation" |
| showing a target, trajectory or needle path on any real frame | Fabrication. Nothing in the data supports it. | If a concept must be drawn, it goes on a **schematic**, marked "CONCEPTUAL — REQUIRES CLINICIAN ANNOTATION" |

## 2. About the cohort and protocol — must accompany every result

Any statement of our lumbar results must carry, in the same breath, that the
data is:

* **healthy volunteers**, aged 20–35, BMI 19–26 — the inverse of the
  difficult-LP population;
* **prone** — lumbar puncture is performed sitting or in lateral decubitus;
* **10 MHz linear probe** — neuraxial practice uses 2–5 MHz curvilinear;
* **a single annotator**, who also acquired the handheld scans, so
  inter-rater reliability is **unmeasured**;
* **9 annotated subjects**, not 63.

Omitting these while quoting a Dice score is the single most likely way this
project misleads someone.

## 3. About the numbers

| Forbidden | Why |
|---|---|
| Quoting "6,091 annotated frames" as our count | We count **6,182 listed / 5,998 non-empty**. The published figure reproduces under neither rule. Cite ours, and note the discrepancy. |
| Quoting frame-level confidence intervals as if frames were independent | Frames within a sweep are near-duplicates. **Subject-level** statistics only; with 9 subjects, intervals are wide and must be shown as such. |
| "state of the art" / "outperforms X" | We ran one architecture at one resolution, and did not reproduce anyone's protocol. |
| Reporting Dice without the tolerance-band F1 | The target is a 1–2 px contour; strict Dice punishes a one-pixel offset as total failure. Reporting only Dice understates, reporting only tolerance-F1 overstates. Report both. |
| Treating the 184 empty-label frames as errors | The expert identified no bone surface. Dice is **undefined** there. Score them separately. |

## 4. About the HUS/RUS comparison

| Forbidden | Why |
|---|---|
| "robotic acquisition is better" | Test it, report it, and accept the answer. The dataset's own SPAR figures (handheld ≥85%, robotic 54–100%) point the other way. |
| Claiming a domain-shift direction from one fold | 3 folds, 9 subjects, 2 of them robotic-only. Report per-fold and per-subject spread, not a single number. |
| Attributing any HUS/RUS difference to the robot alone | Protocol, depth, gain and operator all differ alongside the acquisition mode. Confounded by construction. |

## 5. About the previous experiments

exp001–exp004 are **porcine, intraoperative, post-laminectomy**. In V2 they are
`VALID_BUT_SECONDARY`.

| Forbidden | Say instead |
|---|---|
| Citing exp003's Dice 0.7232 as a lumbar result | "a 10-class baseline on porcine intraoperative spinal-cord ultrasound, used to validate the pipeline" |
| Citing exp004's uncertainty correlation as evidence for lumbar abstention | Cite **exp006**, which repeats it on real human lumbar data. If exp006 disagrees with exp004, report exp006. |

## 6. About availability

| Forbidden | Why |
|---|---|
| "no public human lumbar ultrasound exists" | **Retracted.** It exists, it is CC-BY-4.0, and we hold it. |
| "the KU Leuven dataset is blocked/unavailable" | It is public and was retrieved. Only our workstation's route was blocked. |
| "SUID is a public dataset" | The authors state it is **not** publicly available. Request-only. |
| Redistributing JHU pixels | No licence is declared. Absence of a licence is not permission. |

## 7. The rule that catches everything else

> **Name the species, the approach, the position, the probe and the label
> semantics every time a number appears.**

"Dice 0.6 on human lumbar ultrasound" is misleading.
"Dice 0.6 for expert-annotated visible bone surface on held-out subjects, in
healthy volunteers imaged prone with a 10 MHz linear probe" is a result.
