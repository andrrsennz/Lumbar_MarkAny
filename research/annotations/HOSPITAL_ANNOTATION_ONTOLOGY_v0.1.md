# Hospital annotation ontology — v0.1

> # DRAFT — REQUIRES CLINICIAN REVIEW
>
> Nothing in this document is clinically validated. It is an engineering
> proposal written so that clinicians have something concrete to correct,
> rather than a blank page. Every layer, every label and every field below is
> **open to deletion, renaming or replacement** by the reviewing anaesthesiologist,
> neurologist, radiologist and emergency physician. Where we are unsure, we say so.
>
> **Review status:** not yet reviewed by any clinician. **Version:** 0.1, 2026-09-11.

---

## 0. The one distinction this whole schema is built on

| | **Visible anatomy** | **Clinical procedural decision** |
|---|---|---|
| What it is | What the ultrasound image physically shows | What a clinician would choose to do |
| Who can label it | A trained annotator, reproducibly | Only a qualified clinician |
| Is it in public data? | Yes (bone surface, DS001) | **No — nowhere, in any public dataset** |
| Ground truth? | Yes, with inter-rater agreement | **No — it is expert opinion with variance** |
| Our layers | A–E | F–G |

**Layer D must never be converted into Layer F by an algorithm.** A bone-surface
mask is not a puncture target. If a future pipeline derives a candidate window
from anatomy, that output is a *proposal requiring clinician confirmation*, and
must be stored and evaluated separately from any clinician-authored label.
See `deliverables/paper/CLAIMS_NOT_ALLOWED.md`.

---

## Layer A — acquisition metadata (per cine loop)

Recorded automatically wherever the machine allows; no clinician time.

| Field | Type | Notes |
|---|---|---|
| `study_id` | pseudonymous ID | Never the medical record number. Mapping held only by the hospital. |
| `session_id`, `loop_id`, `frame_index` | int | Frame index must be preserved — it is the only way to do sweep-aware splitting. |
| `machine_manufacturer`, `machine_model` | string | |
| `probe_model`, `probe_type` | enum | `curvilinear` / `linear` / `phased` |
| `frequency_mhz`, `depth_cm`, `gain`, `focus_cm`, `tgc_preset` | numeric | Depth and gain drive most of the appearance shift between operators. |
| `frame_rate_hz` | numeric | |
| `pixel_spacing_mm` | float or `unknown` | **Required** before any millimetre measurement is permitted (Layer E). |
| `patient_position` | enum | `sitting` / `left_lateral` / `right_lateral` / `prone` / `other` |
| `spinal_flexion` | enum | `minimal` / `moderate` / `maximal` / `unknown` |
| `operator_role` | enum | `consultant` / `registrar` / `resident` / `sonographer` / `other` |
| `operator_id_pseudonymous` | string | For operator-effect analysis; not identifying. |
| `scan_plane` | enum | see Layer B |
| `approach` | enum | `midline` / `paramedian` / `unknown` |
| `presumed_level` | enum | `L1-L2` … `L5-S1` / `sacrum` / `uncertain` |
| `level_method` | enum | How the level was established: `palpation` / `sacral_count_us` / `iliac_crest_line` / `imaging_correlation` / `unknown` |
| `acquisition_datetime` | datetime | Only if the ethics protocol permits; otherwise date-shifted or dropped. |

*Open question for clinicians:* is `presumed_level` worth recording when it is
itself uncertain, or does recording an unreliable level create a misleading
label? We propose recording it **with** `level_method` and a confidence, rather
than dropping it.

---

## Layer B — view classification (per frame or per loop)

One label per frame. Terminology to be replaced with whatever the department
actually uses.

| Label | Working definition |
|---|---|
| `transverse_spinous` | Transverse plane, spinous process dominant |
| `transverse_interspinous` | Transverse plane through the interspinous space |
| `parasagittal_transverse_process` | Parasagittal, transverse processes ("trident") |
| `parasagittal_articular_process` | Parasagittal, articular process ("camel hump") |
| `parasagittal_oblique` | Paramedian sagittal oblique — the classic neuraxial window |
| `midline_sagittal` | Midline sagittal through spinous processes |
| `sacral_reference` | Sacrum/L5–S1 for level counting |
| `off_axis_uninterpretable` | Recognisably lumbar but not a usable standard view |
| `not_lumbar` | Wrong region entirely |
| `unknown` | Annotator cannot determine |

*Open question:* should `parasagittal_oblique` be subdivided by whether the
posterior complex is resolved? We think that belongs in Layer C, not B.

---

## Layer C — image quality (per frame)

Quality is the gating variable for any robotic acquisition policy, so it is
deliberately separated from anatomy.

| Field | Values |
|---|---|
| `procedural_usability` | `usable` / `partially_usable` / `unusable` |
| `bone_visibility` | `clear` / `partial` / `absent` |
| `posterior_complex_visibility` | `clear` / `partial` / `absent` / `not_applicable` |
| `acoustic_window_quality` | ordinal 1–5 |
| `shadow_severity` | `none` / `mild` / `moderate` / `severe` |
| `artifact_severity` | `none` / `mild` / `moderate` / `severe` |
| `artifact_type` | multi-select: `reverberation` / `motion` / `poor_contact` / `noise` / `other` |
| `annotator_confidence` | ordinal 1–5 |

`procedural_usability` is the intended primary target for a scan-quality model.
It is a clinical judgement, so it belongs to clinicians even though it is not a
"decision" in the Layer-F sense.

---

## Layer D — visible anatomy (per frame)

Only structures ultrasound can **reliably** show. We propose starting narrow.

| Structure | Geometry | Priority | Note |
|---|---|---|---|
| `skin_surface` | polyline | secondary | Needed for depth measurement |
| `spinous_process` | mask or polyline | **core** | |
| `lamina` | mask or polyline | **core** | |
| `transverse_process` | mask or polyline | secondary | View-dependent |
| `articular_process` | mask or polyline | secondary | |
| `sacrum` | mask or polyline | **core** | Anchor for level counting |
| `interspinous_space` | region | **core** | |
| `interlaminar_window` | region | **core** | The acoustic window that matters |
| `posterior_complex` | polyline | **core** | Ligamentum flavum / dura complex |
| `anterior_complex` | polyline | optional | Only when genuinely visible |
| `vertebral_body` | polyline | optional | |

Each structure additionally carries a **visibility state**:
`clearly_visible` / `partially_visible` / `inferred` / `not_visible`.

**`inferred` is deliberately distinct from `clearly_visible`.** The anchor
dataset's publication explicitly notes that its bone-surface labels show
discontinuities "due to partial uncertainty in identifying the bone surface".
If a clinician is completing a boundary from anatomical knowledge rather than
from echo, the model must be able to learn that difference — and we must be
able to exclude inferred pixels from strict evaluation.

*Do not annotate what ultrasound cannot show.* We propose that any structure
scoring `not_visible` is left empty rather than guessed.

---

## Layer E — measurements (per frame, conditional)

**Gated: only permitted when `pixel_spacing_mm` is known and the geometry is
undistorted.** Otherwise the field must be left null, not estimated.

| Measurement | Definition | Units |
|---|---|---|
| `skin_to_posterior_complex_depth` | Perpendicular skin → posterior complex | mm |
| `interlaminar_window_width` | Widest usable interlaminar gap in-plane | mm |
| `midline_offset` | Lateral offset of the anatomical midline from the probe centreline | mm |
| `estimated_insertion_depth` | Clinician's expected needle depth to CSF | mm |

`estimated_insertion_depth` is arguably a Layer-F judgement rather than a
measurement. We have placed it here because it is numeric and comparable
against outcome, but flag it for clinician arbitration.

---

## Layer F — physician planning labels

> **These are expert opinion, not objective ground truth.** They will vary
> between clinicians, and that variation is itself a research finding, not
> noise to be averaged away.

| Field | Geometry / values |
|---|---|
| `preferred_access_window` | region |
| `acceptable_access_window` | region (may be multiple) |
| `avoid_region` | region (may be multiple) |
| `preferred_entry_point` | point |
| `suggested_insertion_axis` | vector / angle |
| `trajectory_envelope` | cone or polygon expressing acceptable angular tolerance |
| `estimated_target_depth` | mm |
| `chosen_level` | enum |
| `no_safe_recommendation` | **boolean — mandatory** |
| `reasoning_text` | free text |
| `physician_confidence` | ordinal 1–5 |
| `annotator_role`, `years_experience` | metadata |

Three non-negotiable design rules:

1. **`no_safe_recommendation` must always be available.** A schema that forces
   a target teaches the model that a target always exists. Refusal is a valid,
   and clinically important, label.
2. **Every Layer-F label carries a confidence.** Low-confidence labels can be
   down-weighted or held out; they must not be silently equal to confident ones.
3. **Layer F is stored per annotator, never merged.** Consensus, if computed at
   all, is a derived artefact that keeps a pointer to its constituents.

---

## Layer G — procedure outcome

> **Do not collect until an approved ethics protocol explicitly covers it.**
> Listed here so the eventual protocol can be written once, completely.

`attempted_level`, `n_skin_punctures`, `n_redirections`, `csf_obtained`
(bool), `traumatic_tap` (bool + RBC count if available), `procedure_duration_s`,
`guidance_mode` (`landmark` / `us_assisted_preprocedural` / `us_guided_realtime`),
`operator_role`, `patient_bmi`, `difficulty_factors` (multi-select:
obesity / oedema / scoliosis / prior spine surgery / degenerative change /
inability to position / impalpable landmarks), `complications`,
`patient_reported_pain` (0–10).

This layer is what converts the project from an imaging study into a clinical
one, and it is the only layer that can ever validate a Layer-F label.

---

## Annotation calibration plan

A **proposed** starting range, not an asserted sample-size requirement — the
statistician and clinical leads should set the final number.

**Proposed calibration set: 20–50 studies.**

1. ≥2 qualified clinicians annotate every calibration case **independently and blinded** to each other.
2. Agreement is measured per layer with a metric appropriate to the label type:

| Layer | Label type | Metric |
|---|---|---|
| B | categorical view | Cohen's / Fleiss' κ |
| C | ordinal quality | weighted κ, ICC |
| D | masks / polylines | Dice, IoU, mean surface distance |
| E | continuous mm | ICC, Bland–Altman bias and limits of agreement |
| F (point) | entry point | Euclidean distance (mm) |
| F (axis) | trajectory | angular difference (degrees) |
| F (region) | window | IoU; plus % of cases where regions do not intersect at all |
| F (refusal) | `no_safe_recommendation` | raw agreement, κ |

3. Disagreements above a pre-agreed threshold go to a structured adjudication
   session; **the adjudicated cases are recorded as adjudicated**, not silently
   overwritten.
4. The annotation manual is revised from what the disagreements reveal.
5. Calibration repeats on a fresh subset until agreement is stable.

**We should expect Layer F agreement to be moderate at best, and we should
publish that number whatever it is.** If two experienced anaesthesiologists
disagree on the entry point by 8 mm, that is the single most useful number in
the entire study: it sets the tolerance any future robotic alignment has to
meet, and it tells us what "correct" can even mean.

---

## Tooling

Recommendation and rationale in `annotation/manual/TOOLING_ASSESSMENT.md`.
A ready-to-load CVAT label schema is provided at
`annotation/schema/cvat_labels_v0.1.json`, and a converter to a flat
analysis table at `annotation/converters/cvat_to_records.py`.

The intent is that the hospital is handed a working project, not a
specification: **clinicians should not have to invent an annotation workflow.**

---

## Known weaknesses of this draft

Stated plainly so reviewers know where to push hardest.

* The Layer-D structure list is derived from the anatomy named in the
  neuraxial-ultrasound literature and from the anchor dataset's label set. It
  has **not** been checked against what is reliably visible on the specific
  machines and probes the partner hospital uses.
* Layer B view names are the literature's, not necessarily the department's.
* The split of `estimated_insertion_depth` between Layers E and F is unresolved.
* No decision has been made on whether annotation is per-frame or per-loop with
  keyframes. Per-frame is better for training and far more expensive in
  clinician time; keyframe-plus-propagation is the likely compromise and needs
  a pilot before it is committed to.
* Nothing here has been timed. Until we measure how long one loop actually
  takes a clinician to annotate, every throughput estimate in the project plan
  is speculation.
