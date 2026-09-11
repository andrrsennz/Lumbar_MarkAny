# Research roadmap

Each stage has an **entry condition**, a **deliverable**, and an **exit gate**
that can fail. A roadmap whose stages cannot fail is a wish list.

No dates. We do not control the ethics committee cycle, the hospital's case
volume, or funding, and a timeline built on assumptions about those would be
fiction dressed as a plan.

---

## Stage 0 — Public-data foundation · **COMPLETE**

**Deliverable:** this repository.

| Done | Evidence |
|---|---|
| Anchor dataset verified in detail from its open-access full text | `DATASET_REGISTRY.csv` DS001; claims C001–C010 |
| 891-candidate survey across 6 repository APIs | `DATASET_DISCOVERY_LOG.md`; C012–C013 |
| 1.45 GB acquired, checksummed, content-verified | `provenance/DATA_DOWNLOAD_LOG.csv` |
| Published class statistics reproduced exactly; undocumented label encoding recovered | `exp002`; C014–C015 |
| Split integrity audited (hypothesis disproved) | `exp001`; C016–C017 |
| Segmentation pipeline built and measured | `exp003`; C025 |
| Annotation ontology, CVAT schema, tested converter | `annotation/` |
| Proposal, slides, claims discipline | `deliverables/` |

**Exit gate: PASSED, with one item unmet** — the anchor dataset was not
obtained, so the cross-acquisition study was not started.

**Immediate carry-over task (does not require the hospital):** obtain the
anchor dataset from a reachable network and run
`research/robotics/HUS_RUS_ACQUISITION_ANALYSIS.md`. This is the cheapest
remaining high-value work, it needs no approvals, and it tests the project's
core premise.

---

## Stage 1 — Annotation pilot

**Entry:** ethics approval; a data-use agreement; IP and authorship agreed in writing.
**Deliverable:** 20–50 annotated studies; **a measured inter-rater agreement figure**.

**Exit gate — a real one:** if agreement on Layer F (entry point, access window)
is too low to define a usable target, **the project stops at decision support**
and does not proceed to robotic alignment. That result is published either way.

Secondary but decisive: **measure how long one study takes to annotate.** Every
throughput assumption downstream depends on a number nobody currently has.

---

## Stage 2 — Indonesian lumbar ultrasound model

**Entry:** Stage 1 passed; sufficient annotated data.
**Deliverable:** view classification, quality gating, anatomy segmentation, with
**patient-level** held-out evaluation, confidence intervals, uncertainty
estimates and a failure taxonomy.

**Exit gate:** performance and, more importantly, *calibrated abstention* — does
the model reliably decline on images a clinician also judges unusable? A model
that is confidently wrong on poor images is worse than no model.

---

## Stage 3 — Phantom robotic scanning

**Entry:** Stage 2 passed; hardware funded.
**Deliverable:** a robot-held probe performing a lumbar scan pattern on a
phantom, with force limiting verified in hardware.

**Exit gates:**
* Can the required workspace be reached around a **seated, flexed** torso with
  an assistant present? (Never measured by anyone, as far as this survey found.)
* Is total setup + scan time acceptable to clinicians? **This is the
  highest-probability failure in the whole roadmap** — see
  `COMMERCIAL_ANALYSIS.md` §6.

---

## Stage 4 — Needle-guide prototype

**Entry:** Stage 3 passed.
**Deliverable:** a mechanical remote-centre-of-motion guide with a depth stop, a
sterile-drape and quick-release design, and a clinician-confirmation interlock
enforced **outside** the AI path.

**Exit gate:** alignment repeatability on a phantom must be tighter than the
inter-rater disagreement measured in Stage 1. If clinicians disagree with each
other by more than the robot's error, the robot's precision is not the limiting
factor and the value proposition must be restated honestly.

---

## Stage 5 — Integrated phantom validation

**Entry:** Stages 3 and 4 passed.
**Deliverable:** end-to-end scan → perceive → propose → confirm → align on
phantoms, including deliberate failure injection (poor coupling, off-axis
placement, unusable images) to verify the system abstains rather than guesses.

**Exit gate:** no unsafe behaviour under any injected failure; abstention
behaves as specified.

---

## Stage 6 — Observational clinical study

**Entry:** Stage 5 passed; separate ethics approval.
**Deliverable:** the system observes real procedures and records its proposals
**without displaying them**. Retrospective comparison against what the clinician
actually did and what happened.

This is the first stage where the system meets a patient, and it does so
**mute**. That ordering is deliberate and should not be compressed.

---

## Stage 7 — Prospective assistive study

**Entry:** Stage 6 shows agreement with clinical practice and no safety signal.
**Deliverable:** clinicians see the output; endpoints are first-pass success,
attempts, redirections, procedure time, traumatic tap rate, patient discomfort.

**Exit gate:** demonstrated benefit, or an honest null result. A null result
here is a legitimate and publishable end point for the project.

---

## Stage 8 — Regulatory development

**Entry:** Stage 7 positive.
Quality system, risk management, clinical evaluation, and a regulatory strategy
for both the Indonesian market and any target export market. The imaging
component may follow a path analogous to the cleared Class II ultrasound
devices; **the robotic and patient-contacting guide elements would need separate
assessment**, and that assessment requires regulatory counsel we have not
engaged.

---

## Dependency structure

```
Stage 0  ──► anchor-data analysis ──┐   (no approvals needed; do this next)
                                    │
Stage 1 (annotation pilot) ─────────┼──► Stage 2 (model)
      │                             │
      └── agreement gate            └──► Stage 3 (phantom robot)
                                              │
                                    Stage 4 (guide) ──► Stage 5 (integrated)
                                                              │
                                                   Stage 6 ──► 7 ──► 8
```

Stages 1–2 and 3–4 can proceed in parallel **only if** hardware funding is
independent of the clinical pilot. If funding is shared, run Stage 1 first: it
is cheaper, it is the gate that can most cheaply kill the project, and killing
a bad project early is the highest-value outcome available at that point.

## The three findings that would most change this roadmap

1. **Robotic acquisition is no more consistent than handheld** (testable at
   Stage 0 carry-over, with no approvals and no hardware) → drop to
   Architecture B; Stages 3–5 become unnecessary.
2. **Clinician inter-rater agreement is poor** (Stage 1) → stop at decision
   support; Stages 4–7 do not apply.
3. **Setup time is unacceptable** (Stage 3) → the concept fails on workflow
   regardless of technical merit.

All three are cheap to test relative to the cost of ignoring them, and all
three are ordered early on purpose.
