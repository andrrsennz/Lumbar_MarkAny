# Paper recommendation

**Date:** 2026-09-11 · **Status:** recommendation based on what was actually
achievable in Phase 0, with the anchor dataset unreachable.

---

## 1. The honest position first

We cannot currently write the paper this project was designed to produce.

The intended contribution — cross-acquisition generalisation between handheld
and robot-assisted lumbar ultrasound — requires `doi:10.48804/3XPCAE`, which is
unreachable from this network (`KULEUVEN_ACCESS_BLOCKER.md`). Everything we
executed ran on porcine, intraoperative, post-laminectomy spinal cord imaging.
That data cannot support any claim about human neuraxial anatomy.

So this document does two things: it ranks the candidate papers **conditional on
getting the data**, and it states what is publishable **right now, without it**.

---

## 2. What is publishable right now (no new data needed)

### Recommended immediate output — a short methods/resource paper

> **"What public ultrasound data can and cannot tell us about lumbar puncture:
> a reproducibility audit and dataset survey"**

Everything needed already exists in this repository:

| Component | Evidence | Where |
|---|---|---|
| Systematic survey of 891 candidate datasets across 6 repository APIs, with the finding that **only 2 Tier-0 ultrasound datasets exist and neither contains real human transcutaneous lumbar ultrasound** | E1 | `DATASET_DISCOVERY_LOG.md` |
| Exact independent reproduction of a published dataset's Table 1 — all 10 classes, all pixel counts, 13 discrepant pixels in 1.9 billion | E1 | `exp002` |
| Recovery of an **undocumented** palette→class mapping that the release omits, without which the dataset cannot be correctly decoded | E1 | `src/lumbar_markany/data_jhu.py` |
| A filename-independent near-duplicate audit of published train/test splits, with calibration against within-sweep similarity | E1 | `exp001` |
| Documentation that 56.3% of that dataset's images carry **no subject identifier**, so animal-level splitting is not reconstructible from the public release | E1 | `exp001` |
| A baseline with correct NaN handling for absent classes, subject-aware caveats and bootstrap CIs | E1 | `exp003` |

**Why this is worth publishing.** The reproducibility finding is genuinely
useful to anyone who downloads that dataset: without the palette map they will
silently decode the wrong classes, and without the subject-ID finding they will
report animal-level generalisation they cannot actually demonstrate. The survey
finding is the quantitative answer to "why do we need hospital data?", which is
a question every group in this field has to answer and almost none answer with
numbers.

**Honest limitation to state in the paper:** this is a resource/audit
contribution, not a modelling advance. It should be framed as such — a short
paper in a data/methods venue, not a claim of clinical novelty.

**What it must NOT claim:** anything about lumbar puncture performance.

---

## 3. Candidate papers conditional on obtaining the anchor dataset

Scored 1–5 per criterion. "Dataset support" reflects what
`doi:10.48804/3XPCAE` actually contains, which we verified in detail from the
full text even though we could not download it.

| # | Candidate | Novelty | Clinical relevance | Dataset support | Quantitative strength | Reproducibility | Robotics relevance | Feasibility | **Total** |
|---|---|---|---|---|---|---|---|---|---|
| **4** | **Quantitative analysis of robot-assisted vs handheld lumbar ultrasound acquisition** | 4 | 4 | **5** | 4 | 5 | **5** | **5** | **32** |
| 1 | Cross-acquisition generalisation of lumbar bone-surface segmentation (HUS↔RUS) | 4 | 3 | 4 | 4 | 5 | 4 | 4 | 28 |
| 3 | Uncertainty-aware lumbar bone segmentation across acquisition domains | 3 | 4 | 3 | 3 | 5 | 3 | 4 | 25 |
| 2 | Evaluating robotic vs handheld lumbar ultrasound for AI bone-surface perception | 2 | 3 | 4 | 3 | 5 | 4 | 4 | 25 |
| 5 | *Discovered empirically* — reserved | — | — | — | — | — | — | — | — |

### Recommendation: Candidate 4, with Candidate 1 as the second results section

> **"Quantitative characterisation of robot-assisted versus handheld lumbar
> ultrasound acquisition, and its consequences for automated bone-surface
> perception"**

**Why 4 over 1.** Candidate 1 is the more conventional ML paper, and it is
weaker than it looks: the annotated subset is **9 subjects**, of whom only 7
have both HUS and RUS. A cross-domain claim resting on 7 paired subjects,
labelled by a **single annotator**, is a thin result no matter how carefully the
statistics are done. It is worth reporting, but it should not carry the paper.

Candidate 4 rests on much stronger ground. The dataset ships **598 tracked
sweeps** with full 6-DoF pose streams (optical for handheld, robot end-effector
for robotic) plus a breathing marker — and the tracking data covers **all 63
subjects**, not just the 9 annotated ones. That is a 9× larger evidential base,
and it addresses the question that actually motivates the hardware: *does
putting the probe on a robot make acquisition more consistent, and does that
consistency matter downstream?*

**The measurements are already latent in the data:** the authors define a
scan-path area ratio (SPAR) and report handheld ≥85% versus robotic 54–100%.
That difference is currently presented as a technical-validation footnote. It is
actually the interesting finding, and it is under-analysed — the robotic
variability is attributed to deliberately restricted scanning speed, which is
testable against the pose data rather than assumed.

**Proposed analyses** (all supportable by the released pose streams):
trajectory length and duration; velocity and acceleration profiles; motion
smoothness (jerk); orientation variability; coverage of the L1–L5 extent
relative to the CT model; repeat-scan variability (the "Perpendicular" RUS
protocol was repeated **three times per scan**, which is a built-in
repeatability experiment nobody has exploited); and breathing-marker
displacement as a confounder.

**Then, and only then,** link acquisition consistency to perception: does a
model trained on the more consistent domain generalise better? That is
Candidate 1, demoted to a supporting section where its 7-subject weakness is
survivable.

---

## 4. What would make this genuinely novel rather than incremental

The field already has 15+ years of lumbar landmark detection (see
`COMPETITOR_MATRIX.csv`, final row). **Another segmentation model is not a
contribution.** The defensible gaps are:

1. **Acquisition standardisation as an AI problem, not a robotics demo.** Nobody
   has quantified how much of ultrasound AI's variance is attributable to
   *how the probe was moved*, using paired same-subject handheld/robotic data.
   This dataset is the only one in the world that permits it.
2. **The repeatability experiment hiding in the protocol.** Three repeats of the
   same robotic scan per subject gives a direct estimate of acquisition-induced
   variance, separable from anatomical variance.
3. **The visible-anatomy / clinical-decision boundary**, stated formally and
   with an ontology (`HOSPITAL_ANNOTATION_ONTOLOGY_v0.1.md`). Every paper in
   this space blurs it. Naming it precisely, and showing that no public dataset
   crosses it, is a real conceptual contribution.

---

## 5. What this project must not write

Enumerated in full in `CLAIMS_NOT_ALLOWED.md`. The three that matter most:

* Never "lumbar puncture targeting", "autonomous puncture", or "puncture
  accuracy" — we have no puncture data of any kind.
* Never present porcine intraoperative cord results as lumbar anatomy results.
* Never describe a bone-surface mask as a target, a window, or a trajectory.

---

## 6. Decision gate

**Do not select a final paper direction yet.** The ranking above is conditional
on data we do not have. Re-run this assessment after:

1. the anchor dataset is downloaded and its pose streams are inspected (are the
   RUS repeats really three per subject? is the breathing marker synchronised
   well enough to use?); and
2. the acquisition analysis in `research/robotics/HUS_RUS_ACQUISITION_ANALYSIS.md`
   has been executed on real data rather than specified.

If the pose data turns out to be noisier or sparser than the paper implies,
Candidate 4 collapses and Candidate 1 becomes the fallback — with its
9-subject, single-annotator limitation stated in the abstract, not buried.
