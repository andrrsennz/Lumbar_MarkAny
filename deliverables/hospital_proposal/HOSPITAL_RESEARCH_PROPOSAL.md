# Research collaboration proposal

## AI-assisted lumbar ultrasound for safer, more reproducible neuraxial access

**Version 0.1 · 2026-09-11 · DRAFT FOR DISCUSSION**

**Audience:** hospital director · research office · ethics committee (KEPK) ·
anaesthesiology · neurology · radiology · emergency medicine · engineering
collaborators

> **Status of this document.** This is a proposal for *retrospective,
> observational, non-interventional* research. Nothing described here changes
> patient care. No device is offered for clinical use. No ethics approval has
> been sought yet; approval would be a precondition for any data access.
> Statements are labelled **E1** (we measured it), **E2/E3** (verified external
> evidence), **E5** (our inference) and **E6** (proposal — not yet done).

---

## 1. Executive summary

Lumbar puncture and neuraxial anaesthesia are common procedures that remain
difficult in a predictable subset of patients — those with high BMI, oedema,
degenerative change, scoliosis, previous spine surgery, or impalpable landmarks.
Pre-procedural ultrasound is an established aid, but it is operator-dependent:
the quality of the information depends on who is holding the probe.

We propose to study whether **standardised ultrasound acquisition combined with
automated image interpretation** can make that information more reproducible.
The long-term concept is a clinician-controlled system in which a robot holds
and moves the probe, software interprets the images and proposes a candidate
access window, **a physician reviews and confirms or rejects it**, and only then
is a mechanical guide aligned. The physician performs the puncture throughout.

**We are not asking the hospital to trust an unproven device.** We are asking
for access to de-identified ultrasound images and expert annotations, so that
the perception problem can be studied properly in an Indonesian clinical
population. Everything before that is research groundwork we have already done
ourselves.

**What we have already established, with public data only:**

* A systematic survey of 891 candidate datasets across six international
  research repositories found that, outside a single Swiss/Belgian deposit of
  healthy volunteers, **no public dataset contains real human transcutaneous
  lumbar ultrasound**, and **no public dataset anywhere records where a
  clinician chose to insert a needle.** *(E1)*
* We built and measured a complete image-analysis pipeline — data handling,
  segmentation, held-out evaluation with confidence intervals, uncertainty
  estimation and failure analysis — and validated it on the spinal ultrasound
  data that is publicly available. *(E1)*
* We designed a draft clinical annotation schema so that clinicians are asked
  to review a concrete proposal rather than invent a workflow. *(E6)*

**What we cannot do without the hospital:** everything clinical. That is the
whole point of this proposal.

---

## 2. Background

Ultrasound assistance for neuraxial procedures has been studied for over two
decades, and automated identification of lumbar landmarks in ultrasound has an
academic literature stretching back to at least 2008 *(E3)*. One commercial
device, Rivanna's Accuro, is FDA 510(k) cleared for pre-procedural neuraxial
landmark identification (K171594, 2017; Accuro 3S K243937, 2025; product code
IYO, Class II) *(E4)*. Robot-held ultrasound scanning of the lumbar spine has
been demonstrated in 63 healthy volunteers by a KU Leuven / Balgrist
collaboration, with force-controlled contact at 5 N *(E3)*.

So the individual pieces exist. What does not exist is the connection between
them, validated in a real clinical population.

## 3. The clinical problem

Difficulty is concentrated in identifiable patients, and the consequences are
concrete: repeated attempts, needle redirections, patient discomfort, traumatic
taps, occasional failure and escalation to imaging-guided placement.

We deliberately do **not** quote incidence figures here. Difficult-LP rates vary
widely by setting and definition, and we have not performed a systematic review
adequate to state a number we would defend. The relevant local figures are ones
the hospital holds and we do not — establishing them is itself part of the
proposed work (Work Package 1).

## 4. Why lumbar ultrasound

Palpation of surface landmarks estimates midline and interspace indirectly.
Ultrasound visualises the relevant structures directly — spinous processes,
laminae, the interlaminar window, the posterior complex — and supports an
estimate of depth. The literature on pre-procedural ultrasound for neuraxial
access is substantial *(E3; 442 indexed records in our literature database,
`research/literature/LITERATURE_DATABASE.csv`)*.

Its weakness is reproducibility: image quality and interpretation vary with
operator skill. That is precisely the variable a standardised acquisition
system could address — and precisely the variable no existing product addresses,
because every cleared device is handheld *(E4/E5)*.

## 5. Existing global technology

See `research/competitors/COMPETITOR_MATRIX.csv` for the full matrix with
sources.

| | Handheld AI device (Accuro) | Research robotic US (KU Leuven/Balgrist) | Academic landmark detection | **This proposal** |
|---|---|---|---|---|
| Ultrasound | ✔ | ✔ | ✔ | ✔ |
| Automated anatomy detection | ✔ | ✔ (bone surface) | ✔ | ✔ |
| Robotic acquisition | ✘ | ✔ | ✘ | ✔ (proposed) |
| Probe force control | ✘ | ✔ (5 N) | ✘ | ✔ (proposed) |
| **Clinician-authored procedural target** | ✘ | ✘ | ✘ | **✔ — the gap** |
| Outcome linkage | ✘ | ✘ | ✘ | ✔ (proposed, later phase) |
| Regulatory status | FDA Class II | none (research) | none | **none** |

## 6. Current limitations

1. **Operator dependence persists** in every cleared device, because they are all handheld.
2. **No procedural ground truth exists anywhere.** Public datasets label *visible
   anatomy*. None label the *clinical decision*. *(E1)*
3. **Population mismatch.** The only human lumbar US dataset we could identify
   comprises healthy volunteers aged 20–35 with BMI 19–26, imaged **prone**
   with a **10 MHz linear** probe — the opposite of the difficult-LP population,
   in the wrong position, with the wrong probe class. *(E2 → E5)*
4. **Annotation reliability is unmeasured.** That dataset was annotated by a
   single physician, so no inter-rater agreement exists for this task. *(E2)*
5. **Fragmentation.** Perception, acquisition hardware and needle guidance are
   each studied separately and rarely connected.

## 7. Proposed concept

```
Patient positioned (sitting or lateral decubitus)
    ↓
Ultrasound acquisition  ── robot-held probe, force-limited contact
    ↓
AI: is this view usable?  ── scan-quality gate, reject and re-acquire
    ↓
AI: what anatomy is visible?  ── spinous process, lamina, interlaminar window,
    ↓                            posterior complex, depth estimate
AI: candidate access window proposed  ── WITH an explicit uncertainty estimate,
    ↓                                     and the option to propose nothing
┌─────────────────────────────────────────────────────────┐
│  PHYSICIAN REVIEWS · CONFIRMS · MODIFIES · OR REJECTS   │  ← mandatory gate
└─────────────────────────────────────────────────────────┘
    ↓
Mechanical guide aligned to the confirmed plan
    ↓
PHYSICIAN performs the puncture
    ↓
Procedure metadata recorded for audit and research
```

Two properties are non-negotiable in this design:

* **The physician gate cannot be bypassed.** The system proposes; it never acts
  on its own proposal.
* **The system must be able to say "I don't know."** An access-window proposal
  carries an uncertainty estimate, and refusing to propose is a valid,
  first-class output. A system that always produces a target teaches its users
  that a target always exists.

**Autonomy level targeted for a first product: Level 4** (robot aligns a guide
*after* clinician confirmation). **Not Level 5.** Autonomous needle insertion is
explicitly out of scope. *(E6)*

## 8. Work already completed with public data

All reproducible from `https://github.com/andrrsennz/Lumbar_MarkAny`.

| Work | Result | Label |
|---|---|---|
| Dataset survey, 6 repository APIs, 891 candidates | Only 2 Tier-0 US datasets; neither is real human transcutaneous lumbar US | E1 |
| Literature harvest | 442 records, 20 clinical/technical categories | E1 |
| Verification of the anchor lumbar dataset against its open-access full text | Every count confirmed; **critical limitations identified that the dataset's own summary does not foreground** (9 annotated subjects not 63; single annotator; prone; linear probe) | E1 verifying E2 |
| Independent reproduction of a published dataset's class statistics | All 10 classes matched **exactly** (13 pixels differing in 1.9 billion) | E1 |
| Recovery of an undocumented label encoding | Published as reusable code | E1 |
| Split-integrity audit | Splits verified sweep-disjoint; our leakage hypothesis was **disproved** | E1 |
| Segmentation baseline with correct statistics | Per-class Dice/IoU, bootstrap CIs, explicit handling of absent classes | E1 |
| Draft clinical annotation ontology | 7 layers, A–G, with calibration protocol | E6 |

## 9. Public expert annotation evidence

The best public annotation process we found (Johns Hopkins) used trained
annotators, radiologist adjudication of ambiguous cases, and a second review by
a neurosurgery spine fellow *(E2)*. That two-stage structure is the model we
propose to adopt.

Notably, the *lumbar* dataset has a **weaker** annotation process than the
porcine one — single annotator, no adjudication. Annotation rigour in this field
is not yet where it should be, and a hospital collaboration is an opportunity to
do it properly rather than to copy current practice.

## 10. Our actual experimental results

Reported in full in `experiments/exp003_unet_baseline/metrics.json`.

**These results are on porcine intraoperative spinal-cord ultrasound acquired
after laminectomy. They are not lumbar. They are not transcutaneous. They are
not human.** They demonstrate that our pipeline works correctly — nothing more.
We present them because a proposal that showed no executed work would be a
slide deck, and because showing exactly where our evidence stops is the point.

## 11. Why Indonesian clinical data is necessary

Four gaps that public data cannot close, no matter how much of it is collected:

1. **Population.** Difficult LP is defined by body habitus that the only
   available human lumbar dataset explicitly excludes.
2. **Position and probe.** Prone / 10 MHz linear is a surgical-guidance
   protocol. Neuraxial practice is sitting or lateral decubitus with a
   low-frequency curvilinear probe. The images are not interchangeable.
3. **Labels that do not exist anywhere.** Interspace choice, entry point,
   trajectory, target depth, and the decision *not* to proceed. Only clinicians
   can create these.
4. **Reliability.** How much do two experienced clinicians agree on an entry
   point? Nobody knows. That number sets the engineering tolerance for
   everything downstream, and it cannot be obtained from public data.

## 12. Proposed collaboration

A **retrospective, observational, non-interventional** study in two stages.

* **Stage A — annotation pilot.** A small set of existing de-identified lumbar
  ultrasound studies, annotated independently by ≥2 clinicians, to measure
  agreement and refine the schema. No patient contact.
* **Stage B — model development.** A larger retrospective set for training and
  held-out evaluation, split at the patient level.

Prospective data collection, phantom work and any hardware are **later, separate
proposals requiring their own approvals.** They are not requested here.

## 13. Clinical team roles

| Role | Contribution | Indicative time |
|---|---|---|
| Principal investigator (clinical) | Scientific leadership, ethics sponsor | ongoing |
| Anaesthesiologist(s) | Annotation, schema review, clinical realism | annotation sessions |
| Neurologist / emergency physician | Diagnostic-LP perspective, difficult-case definition | review meetings |
| Radiologist | Image-quality criteria, annotation adjudication | adjudication sessions |
| Research nurse / coordinator | Case identification, de-identification workflow | per protocol |
| Hospital IT / data protection officer | De-identification, transfer, governance | setup + audit |
| Engineering team (us) | Tooling, pipeline, analysis, reporting | full-time |

Time commitments are deliberately left indicative: **we have not yet measured
how long one study takes to annotate.** Establishing that is an explicit output
of the pilot, not an assumption.

## 14. Data requested

### Required

* De-identified lumbar spine B-mode ultrasound — cine loops preferred, DICOM
  preferred (pixel data plus acquisition parameters)
* Acquisition parameters: machine, probe type, frequency, depth, gain, focus
* Patient position and degree of flexion
* Scan plane and approach (midline / paramedian)
* Operator role (pseudonymous)
* De-identified demographics: age band, sex, BMI (or height/weight)

### Nice to have

* Presumed vertebral level and how it was determined
* Difficult-procedure factors: prior spine surgery, scoliosis/deformity,
  oedema, impalpable landmarks
* Any existing spine imaging (CT/MRI) for the same patient, for anatomical
  correlation
* Procedure record: guidance mode, attempts, redirections, success, traumatic tap

### Future prospective only (not requested now)

* Standardised protocol acquisition in both sitting and lateral decubitus
* Real-time needle imaging
* Structured outcome capture
* Patient-reported discomfort

## 15. Annotation requested

Per `research/annotations/HOSPITAL_ANNOTATION_ONTOLOGY_v0.1.md`, staged:

* **Pilot:** Layer B (view), Layer C (quality), Layer D core structures
  (spinous process, lamina, interlaminar window, posterior complex, sacrum).
* **After calibration:** Layer E measurements (only where pixel spacing is
  trustworthy) and Layer F planning labels (access window, entry point,
  trajectory, target depth, confidence, **and the option to record that no safe
  recommendation exists**).
* **Layer G outcomes:** only under a future protocol that explicitly covers them.

Layer F labels are stored **per annotator and never merged**. Disagreement is
data, not noise.

## 16. Ethics and governance

* Submission to the hospital's ethics committee (**KEPK**) before any data
  access. No data moves first.
* Retrospective use of existing images with a waiver of individual consent is
  the expected route for Stage A, **subject entirely to the committee's
  determination** — we do not presume it.
* Any prospective collection requires informed consent under a separate protocol.
* Research use only. No clinical decision support is deployed, and no output is
  returned to the treating team.
* We will comply with Indonesian personal-data protection law (UU PDP) and
  hospital policy. **We are engineers, not lawyers: the hospital's data
  protection officer and legal counsel determine what is permissible, and we
  will follow that determination.**

## 17. Data security

* De-identification **at source, inside the hospital**, before transfer. DICOM
  headers stripped of identifiers; burned-in text screened and removed.
* Pseudonymous study IDs only; the re-identification key never leaves the
  hospital and is never shared with the engineering team.
* Encrypted transfer; encrypted storage at rest; access restricted to named
  researchers under a data-use agreement.
* Defined retention period and documented destruction.
* Cross-border transfer only if explicitly permitted; **if it is not, the
  analysis environment is placed inside the hospital instead.** The technical
  design does not depend on data leaving the institution.
* No patient data will ever be committed to the public code repository.

## 18. Research-only boundary

Stated for the ethics committee without hedging:

* No patient's care is altered by this study.
* No AI output is shown to any clinician during any procedure.
* No device is placed on any patient.
* No robot is involved at any point in the proposed work.
* Withdrawal of the hospital's participation at any time is accepted without
  condition, and derived data destroyed on request.

## 19. Technical work packages

| WP | Title | Output |
|---|---|---|
| WP1 | Local baseline: case identification, current practice, difficulty definition | Feasibility report, local difficulty profile |
| WP2 | Data pipeline: de-identification, transfer, storage, audit | Validated workflow + DPO sign-off |
| WP3 | Annotation infrastructure: CVAT project, schema, manual, training | Working annotation environment |
| WP4 | Calibration study: ≥2 annotators, 20–50 studies, agreement metrics | **Inter-rater agreement — the key missing number** |
| WP5 | Model development: view classification, quality gating, anatomy segmentation | Patient-level held-out metrics with CIs |
| WP6 | Uncertainty and failure analysis | Failure taxonomy; abstention behaviour |
| WP7 | Reporting: publication, protocol for the next phase | Paper + follow-on proposal |

## 20. Milestones

Deliberately expressed as **sequence and gates, not dates.** We do not know the
hospital's committee cycle or case volume, and inventing a timeline would be a
guess presented as a plan.

1. Proposal reviewed by clinical leads → schema revised
2. Ethics submission prepared → submitted → determination
3. WP1–WP3 (no patient data required for WP3)
4. **Gate:** WP4 calibration. *If inter-rater agreement on Layer F is too low to
   be usable, the project stops and reports that finding.* This is a real gate,
   not a formality.
5. WP5–WP6
6. WP7, and decision on prospective phase

## 21. Deliverables to the hospital

Local difficulty/practice profile (WP1); a reusable, validated de-identification
workflow; a working annotation environment the department keeps; the inter-rater
agreement study — publishable in its own right; trained models and code;
co-authored publications; and a follow-on protocol.

## 22. Publications

Target: one methods/agreement paper from WP4, one model paper from WP5–WP6.
All publications state the limitations of the data honestly, including negative
results. **We commit to publishing the inter-rater agreement figure whatever it
is**, including if it undermines the project's premise.

## 23. Authorship principles

ICMJE criteria. Clinical collaborators who contribute to design, annotation,
interpretation or drafting are authors. Annotation volume alone is acknowledged
unless accompanied by intellectual contribution. **Author order is agreed in
writing before the first draft**, not after results are known. The hospital
reviews and approves any manuscript describing its data before submission.

## 24. IP principles

To be agreed in writing before data transfer. Our proposed starting position:

* Analysis code developed in this project is open source (MIT).
* De-identified data remains the hospital's; we receive a defined-purpose
  licence to use it, not ownership.
* Annotations created by hospital clinicians belong to the hospital, with a
  licence to us for the agreed research purposes.
* Any downstream commercial development is a **separate** negotiation, and the
  hospital's contribution is recognised in it. We are raising this now rather
  than later precisely because it is easier to agree before there is anything to
  argue about.
* **We make no claim that anything here is patentable.** That is a question for
  patent counsel, not for us.

## 25. Hospital benefits

Research output and co-authorship; a durable annotation and de-identification
capability; a quantified local picture of neuraxial procedure difficulty;
clinician training exposure to structured image annotation and AI evaluation;
and early involvement in a technology the department would otherwise encounter
only as a finished product to be purchased.

## 26. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Ethics approval delayed or refused | moderate | No work requiring data proceeds; WP3 continues on public data |
| Insufficient case volume | moderate | Establish in WP1 **before** committing; adjust scope or extend |
| Clinician time unavailable | **high** | Stage annotation; measure per-case time early; keyframe rather than per-frame |
| Inter-rater agreement too low to be usable | moderate | **This is a gate, and a publishable finding.** Report it and stop |
| Image quality/heterogeneity too variable | moderate | Quality gating is a modelling target, not only an obstacle |
| De-identification burden underestimated | moderate | Validate the workflow in WP2 before bulk transfer |
| Model underperforms | moderate | Negative results are reported, not buried |
| Scope creep toward clinical deployment | **high** | The research-only boundary (§18) is contractual, not aspirational |

## 27. Timeline

See §20. **No dates are offered**, because none would be credible before the
hospital's constraints are known. We would rather present a defensible sequence
than an impressive-looking Gantt chart built on assumptions.

## 28. Resource categories

Categories only; **no figures**, because we have not obtained quotes and any
number would be invented.

Personnel (clinical annotation time; research coordinator; engineering);
annotation software and hosting; secure storage and compute; de-identification
tooling; ethics and legal review; publication costs; travel for on-site work.
Hardware appears in **no** category — no hardware is proposed in this phase.

## 29. Future clinical translation

Strictly sequential, each gated on the previous succeeding:

Stage 0 public data *(done)* → Stage 1 annotation pilot *(this proposal)* →
Stage 2 local model → Stage 3 phantom robotic scanning → Stage 4 needle-guide
prototype → Stage 5 integrated phantom validation → Stage 6 ethics-approved
observational clinical study → Stage 7 prospective assistive study →
Stage 8 regulatory development.

**Stages 3 onward are not part of this proposal and would each require separate
approval.** We describe them so the hospital can see where the work leads, not
to imply commitment.

## 30. Next steps

1. Clinical leads review this document — particularly the annotation ontology,
   which we expect to be substantially rewritten.
2. A working meeting with anaesthesiology, neurology, radiology and emergency
   medicine to agree what is clinically realistic.
3. WP1 feasibility assessment: does the hospital have sufficient existing
   lumbar ultrasound, and in what form?
4. If yes: co-draft the ethics submission.
5. Agree IP and authorship in writing before any data moves.

---

### Contact and code

All analysis code, dataset registry, provenance logs and experiment records:
`https://github.com/andrrsennz/Lumbar_MarkAny`

We have deliberately made the evidence base auditable, including the parts that
do not favour us — the dataset we could not obtain, the hypothesis we disproved,
and the fact that none of our experiments touched lumbar anatomy.
