# Public vs hospital annotation — what is already covered, and what is not

**Revises the V1 hospital ask.** V1 asked for lumbar ultrasound *and* anatomy
annotation. Now that we hold 6,182 expert-annotated real human lumbar frames
and have inspected the labels at the file level, a large part of that ask is
**no longer necessary**, and the remainder is far more specific.

> **Do not ask clinicians to re-annotate what public data already provides
> adequately.** Their time is the scarcest resource in this project. Ask only
> for what genuinely does not exist.

---

## 1. What the public labels actually contain

Verified by decoding the label arrays, not by reading the paper.

| Source | Label content | Values | Verdict |
|---|---|---|---|
| **KU Leuven (held)** | visible **bone surface**, a 1–3 px contour | `{1, 2}` — background, bone surface. Nothing else. | **anatomy only** |
| **SUID (request-only)** | interlaminar spaces, articular processes, **anterior complex**, **posterior complex** | not released | **anatomy, closer to procedural** |
| JHU (secondary) | 10 classes: dura, pia, CSF, cord, hematoma… | intraoperative porcine | not applicable |

**No public dataset — including the one we now hold in full — contains a single
procedural label.** No entry point. No trajectory. No target depth. No
interspace decision. No "do not proceed". No outcome.

## 2. Layer-by-layer verdict against the V1 ontology

`HOSPITAL_ANNOTATION_ONTOLOGY_v0.1.md` proposed seven layers, A–G.

| Layer | Public coverage | Revised hospital ask |
|---|---|---|
| **A** acquisition metadata | **Good.** Machine, probe, frequency, depth, gain, position, and probe pose are all documented in the KU Leuven deposit. | **Reduced to local capture only.** Record what the local scanner emits; do not design a schema from scratch. |
| **B** view classification | **Absent.** Frames are unlabelled by view; the protocol is prone and orthopaedic, so the neuraxial view vocabulary (paramedian sagittal oblique, transverse interspinous…) is not represented at all. | **Still needed, and now the cheapest high-value ask** — one categorical label per frame or keyframe. |
| **C** image quality | **Partially inferable, not labelled.** The 184 frames (3.0%) the expert left empty are an implicit "nothing identifiable here" signal, but there is no graded quality judgement. | **Still needed.** Graded usability is the gate for any robotic re-acquisition policy. |
| **D** visible anatomy | **Largely covered for BONE SURFACE.** 6,182 frames, 9 subjects, two acquisition modalities. | **Narrowed sharply.** Do **not** ask for bone-surface re-tracing as the primary task. Ask for the structures public data lacks: **interlaminar window, posterior complex, anterior complex, interspinous space, sacrum-based level count** — exactly the SUID class set, which does not exist publicly. |
| **E** measurements | **Absent, and not derivable.** No pixel spacing is exposed in the label archives. | **Still needed**, gated on calibrated geometry. Skin-to-posterior-complex depth is the single most clinically actionable number. |
| **F** physician planning | **Completely absent everywhere.** | **THE ASK.** Unchanged and now demonstrably unique. |
| **G** procedure outcome | **Completely absent everywhere.** | **THE ASK** (later protocol). |

## 3. The three gaps that public data structurally cannot close

**(i) The decision layer.** Bone surface is where bone is. A puncture plan is
where a clinician would go, at what angle, to what depth — and when they would
decline. No amount of anatomy annotation produces it, because it is not a
property of the image.

**(ii) Population, position and probe.** The data we hold is healthy
volunteers aged 20–35, BMI 19–26, imaged **prone** with a **10 MHz linear**
probe. Neuraxial practice is sitting or lateral decubitus with a **2–5 MHz
convex** probe, in patients who are often obese, oedematous, degenerative or
post-surgical. SUID demonstrates the correct protocol is achievable in a real
obstetric service — and that such data stays private.

**(iii) Annotation reliability.** The KU Leuven labels come from a **single
annotator**, who was also the operator who acquired the handheld scans. No
inter-rater agreement exists for lumbar ultrasound annotation anywhere we
looked. That number is unknown to the field, and it sets the tolerance every
downstream guidance system must meet.

## 4. The revised hospital ask

**Removed** (public data now suffices for methodology):
* Bulk bone-surface tracing as the primary annotation task.
* Designing acquisition metadata from scratch.
* "Give us some lumbar ultrasound so we can see whether AI works" — we have
  measured that, on real human lumbar data, and can show the numbers.

**Retained and sharpened:**

1. **Local-domain imaging** in the clinically correct configuration —
   sitting/lateral decubitus, curvilinear probe, real patients including
   difficult anatomy. This is a *domain* requirement, not a *volume* one.
2. **Procedural planning labels (Layer F)** from ≥2 independent clinicians,
   with confidence and a first-class "no safe recommendation" option.
3. **The inter-rater agreement study.** How far apart are two experienced
   anaesthesiologists on the entry point? Nobody has published this.
4. **View and quality labels (Layers B, C)** in neuraxial vocabulary.
5. **The SUID-style structure set (Layer D, narrowed)** — interlaminar window,
   anterior/posterior complex — which public data does not provide.
6. **Outcomes (Layer G)** under a later, separately approved protocol.

## 5. Why this is a stronger proposal than V1's

V1 said: *there is no public human lumbar ultrasound, so give us data.* A
reviewer could reasonably have replied that the KU Leuven deposit exists.

V2 says: *we obtained the public human lumbar data, measured our models on it
subject-by-subject, and can show you exactly where perception succeeds and
fails on real patients' anatomy. What no dataset on earth contains — and what
only your clinicians can create — is the decision layer that turns anatomy
perception into a procedure.*

That is a smaller, more credible, better-evidenced request, and it asks
clinicians for the one thing only clinicians can give.
