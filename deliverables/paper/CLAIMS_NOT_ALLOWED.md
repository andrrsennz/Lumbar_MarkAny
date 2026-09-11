# Claims not allowed

A hard list. If a sentence in any paper, proposal, slide, grant application or
marketing document from this project matches something below, it is wrong and
must be removed — regardless of how well it reads.

This file exists because the gap between what we measured and what the project
*aspires to* is unusually wide, and the temptation to narrow it with language
rather than with evidence is correspondingly strong.

---

## 1. About lumbar puncture

| Forbidden | Why | Say instead |
|---|---|---|
| "lumbar puncture targeting" / "puncture accuracy" / "needle placement accuracy" | We hold **no** puncture data. No entry point, no trajectory, no depth, no outcome, from any source, public or private. | Nothing. There is no defensible weaker version — omit the topic. |
| "autonomous lumbar puncture" | Nothing autonomous exists, was built, or was tested. | "clinician-performed puncture, with machine-assisted acquisition and alignment (proposed, E6)" |
| "improves first-pass success" | No procedure has been performed. | "first-pass success is the proposed primary endpoint of a future study (E6)" |
| "reduces traumatic taps / complications" | No outcome data exists. | — omit — |
| "validated for neuraxial access" | Nothing has been validated for anything clinical. | "pipeline validated on non-clinical data; clinical validation not started" |

## 2. About our experimental results

| Forbidden | Why | Say instead |
|---|---|---|
| "our model segments lumbar anatomy" | `exp003` ran on **porcine spinal cord, intraoperative, after laminectomy**. It has never seen a lumbar vertebra through skin. | "a 10-class segmentation baseline on porcine intraoperative spinal cord ultrasound, used to validate the pipeline" |
| "Dice 0.7x on spinal ultrasound" *(unqualified)* | Ambiguous in exactly the direction that flatters us. | "Dice 0.7x on the JHU porcine intraoperative spinal-cord dataset, official split" |
| "outperforms the published benchmark" | Our metric definition (per-image macro Dice, NaN for classes absent from both prediction and truth) is **not** verified to match theirs. Different NaN handling alone can move macro Dice by a large margin. | "not directly comparable to the published figures; the averaging convention differs and we did not reproduce their protocol" |
| "generalises across subjects" | The release distributes **no animal identifier** for 56.3% of images. Animal-level generalisation is unmeasurable from the public data. | "sweep-level held-out performance; animal-level generalisation could not be assessed because no animal ID is distributed" |
| "we validated on human data" | We did not. The 8-patient human subset was not used in our experiments. | — omit — |

## 3. About the anchor dataset

| Forbidden | Why | Say instead |
|---|---|---|
| "we trained on 6,091 expert-annotated lumbar frames" | We never obtained the data. Zero frames were used. | "the deposit contains 6,091 annotated frames (E2); we were unable to obtain it (see access blocker)" |
| "63 subjects of lumbar training data" | The annotated subset is **9** subjects, not 63. | "63 subjects imaged; **9** carry expert annotations (7 with both HUS and RUS, 2 RUS-only)" |
| "expert-consensus annotations" | **One** annotator — who was also the person who acquired the handheld data. No second reader, no adjudication, no agreement statistic. | "annotated by a single physician; inter-rater reliability is therefore unmeasured" |
| "representative lumbar ultrasound" | Healthy volunteers, BMI 19–26, age 20–35, **prone**, **10 MHz linear** probe. This is close to the inverse of the difficult-LP population and is not the neuraxial imaging protocol. | "healthy-volunteer reference data acquired with an orthopaedic surgical-guidance protocol" |
| "bone surface labels identify the puncture window" | Bone surface is visible anatomy. A window is a clinical decision. | "bone-surface labels describe visible anatomy only; no public dataset contains a procedural target" |

## 4. About robotics

| Forbidden | Why | Say instead |
|---|---|---|
| "our robot" / "our robotic system" | **No hardware has been built, purchased, or specified beyond a paper concept.** | "proposed architecture (E6); no hardware exists" |
| "force-controlled scanning reduces variability" | That is the KU Leuven group's setup, not ours, and even for them the SPAR figures show robotic scans were **more** variable (54–100%) than handheld (≥85%). | "force-controlled robotic acquisition has been demonstrated by others (E3); its effect on consistency is the open question we propose to study" |
| "robot-guided needle alignment" *(present tense)* | Does not exist. | "robot-positioned needle guide with clinician-performed insertion (Architecture D, E6)" |
| "safety-certified" / "fail-safe" | No safety case, no standard, no assessment. | "safety requirements to be defined; no assessment performed" |

## 5. About regulation and market

| Forbidden | Why | Say instead |
|---|---|---|
| "FDA cleared" / "CE marked" (about us) | We have no clearance of any kind. | "Accuro is FDA 510(k) cleared (K171594, product code IYO, Class II); our concept has no regulatory status" |
| "Class II pathway confirmed" | We have not had a regulatory consultation. Predicate similarity is our inference, not a determination. | "Accuro's predicates suggest a Class II 510(k) route for the imaging component; the robotic and guide elements would need separate assessment (E5)" |
| any specific selling price, market size, or revenue figure | We did no market research. Nothing would be traceable to a source. | qualitative business-model categories only |
| "patentable" / "freedom to operate" | We are not qualified to say, and did not perform a clearance search. | "areas that appear crowded / sparse and warrant formal patent counsel (E5)" |

## 6. About Indonesian clinical work

| Forbidden | Why | Say instead |
|---|---|---|
| "approved by the ethics committee" | No submission has been made. | "ethics submission is a prerequisite and has not been prepared" |
| "in collaboration with [hospital]" | No agreement exists. | "proposed collaboration" |
| "we have clinical data" | We have none. | "no clinical data has been collected" |
| naming any clinician as a collaborator or author | No one has agreed. | — omit until written agreement — |

---

## The single rule behind all of this

> **Every number in an output must trace to `RESULTS_LEDGER.csv` (our own runs)
> or to `CLAIMS_LEDGER.csv` with a verifiable external source.**

If it traces to neither, it does not go in the document. Not as a rounded
figure, not as "approximately", not as an illustrative example, not in a
figure caption, and not in a slide.

## Two failure modes specific to this project

1. **Species/approach laundering.** Porcine intraoperative cord results
   gradually becoming "spinal ultrasound AI" and then "our lumbar AI" across
   successive drafts. Guard: every results sentence names the species and the
   surgical approach.
2. **Roadmap tense-slip.** Architecture D described in present tense because it
   has been described often enough to feel real. Guard: every E6 item carries
   the label in the text, not only in a legend.
