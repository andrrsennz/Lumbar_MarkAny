# Handheld vs robot-assisted lumbar ultrasound acquisition — analysis plan

> **Status: SPECIFIED, NOT EXECUTED.** The pose data this analysis requires is
> in `doi:10.48804/3XPCAE`, which was unreachable from the project network. No
> number in this document is a result. Where a figure appears, it is quoted
> from the dataset's publication (E2/E3) and attributed.

This is the analysis that `PAPER_RECOMMENDATION.md` ranks as the strongest
available scientific contribution. It is written out in full so it can be run
as soon as the data is obtained, rather than designed under time pressure then.

---

## 1. Why this analysis and not a segmentation study

The obvious study — train a segmentation model on handheld data, test on
robotic — rests on **seven paired subjects**, labelled by **one annotator**
*(E2, claims C004/C005)*. That is a thin basis for a cross-domain claim.

The pose data is a much stronger asset:

| | Annotated frames | Tracked sweeps |
|---|---|---|
| Subjects covered | **9** | **63** |
| Units | 6,091 frames | 598 sweeps (223 HUS + 375 RUS) |
| Label dependency | single annotator | **none — geometry, not opinion** |

Pose analysis needs no annotation at all, so it inherits none of the
annotation's reliability problems, and it covers seven times more subjects.

**And there is a repeatability experiment already built into the protocol:**
the "Perpendicular" robotic scan was **repeated three times per subject** *(E2 —
this is the stated reason 375 RUS scans exist against 223 HUS)*. That gives a
direct estimate of acquisition-induced variance, separable from between-subject
anatomical variance. The published paper does not exploit it.

## 2. The question

> Does robot-assisted acquisition produce more consistent lumbar ultrasound
> sweeps than handheld acquisition — and if so, does that consistency
> translate into more reliable automated perception?

**The honest starting position is that the answer may be no.** The dataset's
own technical validation reports scan-path area ratio (SPAR) ≥85% for handheld
but **54–100% for robotic** *(E2, claim C009)* — i.e. robotic coverage was
*more* variable. The authors attribute this to a deliberately restricted
scanning speed (4 mm/s) imposed for volunteer comfort, which is plausible but
is not tested against the pose data in the publication.

Disentangling "robotic acquisition is inherently less consistent" from "robotic
acquisition was speed-limited in this protocol" is the analytical core of the
study, and it is directly testable: if the speed explanation holds, normalising
coverage by scan duration should remove the difference.

## 3. Data required

Per the publication's Data Records section *(E2)*:

* `HUS_pose.txt` — optical marker pose per frame: `x, y, z, qx, qy, qz, qw, timestamp`
* `RUS_pose.txt`, `MUS_pose.txt`, `DUS_pose.txt` — robot end-effector pose:
  `x, y, z, roll, pitch, yaw` (+ timestamp synchronisation)
* `body_marker.csv` — breathing marker, quaternion + timestamp
* CT-derived L1–L5 STL surface models — for anatomical normalisation
* `SPAR_results.txt` and `URSn_Xn_SPAR.png` — the authors' own coverage figures
* `US_scantype_availability.csv` — which scan types exist per subject

## 4. Metrics

Only metrics the pose stream can actually support. Each is computed per sweep,
then aggregated **per subject** before any group comparison.

| Metric | Definition | Why |
|---|---|---|
| Path length | ∫‖dp‖ over the sweep | gross motion |
| Duration | t_end − t_start | the speed confound |
| Mean / peak speed | ‖dp/dt‖ | tests the speed explanation directly |
| Spectral arc length (SPARC) | smoothness measure on the speed profile | robust, dimensionless, standard in motion analysis; preferred over raw jerk, which is noise-sensitive |
| Normalised jerk | ∫‖d³p/dt³‖ dt, normalised | reported alongside SPARC for comparability |
| Orientation variability | angular dispersion of the probe normal | how much the probe tilts through a sweep |
| Craniocaudal coverage | y-extent of tracked frames | reproduces the authors' SPAR numerator |
| **Coverage / L1–L5 extent** | above ÷ CT model extent | the authors' SPAR — recomputed independently |
| **Coverage rate** | coverage ÷ duration | **the speed-corrected comparison** |
| Repeat variability | SD across the 3 repeated Perpendicular RUS scans | acquisition-induced variance, within subject |
| Breathing displacement | RMS body-marker motion | confounder, and a covariate |

## 5. Statistical approach

* **Unit of analysis is the subject, never the sweep.** Sweeps within a subject
  are not independent.
* Paired comparison HUS vs RUS **within subject** (most subjects have both);
  Wilcoxon signed-rank as the primary test, with effect size and bootstrap CIs.
* Repeatability from the 3× Perpendicular repeats: intraclass correlation and
  within-subject SD.
* Speed as a covariate, and the coverage-rate metric, to test the authors'
  stated explanation for the SPAR difference.
* Correct for multiple comparisons across metrics; pre-specify **coverage rate**
  and **SPARC** as primary, everything else as exploratory.
* Report the comparison even if it favours handheld. That outcome is the one
  that most changes the project's direction, so it must not be soft-pedalled.

## 6. Link to perception (secondary)

Only for the 9 annotated subjects, and reported as exploratory given n:

1. Train on HUS, test on held-out HUS subjects.
2. Train on RUS, test on held-out RUS subjects.
3. Cross-domain: HUS→RUS and RUS→HUS.
4. Combined training, evaluated separately per domain.
5. Correlate per-subject segmentation performance against that subject's
   acquisition-consistency metrics.

Leave-one-subject-out is the only defensible protocol at n=9, and the resulting
intervals will be wide. **State the width; do not hide it behind a point
estimate.**

## 7. What would change the project's direction

| Finding | Consequence |
|---|---|
| Robotic acquisition is more consistent after speed correction | Architecture D's premise holds; proceed |
| Robotic is no more consistent even after correction | **Architecture D loses its rationale**; fall back to Architecture B (AI + passive guide) |
| Consistency does not correlate with perception performance | The robot may help workflow and ergonomics but not AI reliability; the claim must be narrowed accordingly |
| Pose data is too noisy or sparse to support these metrics | Candidate 4 collapses; fall back to the segmentation paper with its n=9 limitation stated in the abstract |

## 8. Implementation

`scripts/analysis/acquisition_metrics.py` is **not yet written**, deliberately:
the pose file format is documented in prose in the publication but has not been
inspected, and writing a parser against a format description rather than
against real files produces code that looks finished and silently is not.

First step once the data lands: open one `HUS_pose.txt` and one `RUS_pose.txt`,
confirm the column order, units, timestamp base and coordinate frames, and
confirm that the robot poses really are Euler angles while the optical poses are
quaternions (as the publication states). Only then write the parser.
