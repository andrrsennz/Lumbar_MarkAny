# Annotation tooling assessment

Assessed against what this project actually needs: cine-loop (multi-frame)
ultrasound, mixed geometry (masks, polylines, points, regions), per-annotator
storage without merging, a mandatory "no recommendation" outcome, on-premises
deployment for hospital data, and minimal clinician training time.

| Tool | Cine/video | Mixed geometry | Per-frame attributes | Self-host | Clinician learning curve | Licence | Verdict |
|---|---|---|---|---|---|---|---|
| **CVAT** | ✔ native frame-by-frame with interpolation | ✔ polygon, polyline, points, box, mask | ✔ per-shape and per-frame | ✔ Docker, fully offline | moderate | MIT | **Recommended** |
| 3D Slicer | ✔ via sequences | ✔ strongest for 3D/volumetric | partial | ✔ desktop | steep | BSD-style | Best later, for 3D reconstruction and CT–US work |
| MONAI Label | ✔ with a viewer | ✔ | limited | ✔ | moderate–steep | Apache-2.0 | Adopt later, for model-assisted pre-labelling |
| Label Studio | partial (video ok, medical weaker) | ✔ | ✔ | ✔ | **low** | Apache-2.0 (some features gated) | Good fallback if CVAT setup is a barrier |
| ITK-SNAP | ✘ | mask-focused | ✘ | ✔ | low for masks | GPL | Too narrow |
| ImFusion *Labels* | ✔ | ✔ | ✔ | ✔ | low | **commercial** | Used by the anchor dataset's authors; licence cost and lock-in |

## Recommendation: CVAT for the pilot

**Why.** It is the only option that combines native multi-frame handling,
every geometry type this schema needs, per-frame attributes, a genuinely
offline Docker deployment (which matters when hospital data cannot leave the
building), and a permissive licence with no per-seat cost.

**The deciding factor is frame interpolation.** Lumbar ultrasound arrives as
sweeps, and per-frame manual annotation of a 300-frame sweep is not a realistic
ask of a consultant. CVAT lets a clinician annotate keyframes and interpolate
between them, then correct the interpolation. That is the difference between an
annotation pilot that finishes and one that quietly stalls.

**Honest caveat:** CVAT's initial setup is a developer task, not a clinician
task. We provide the project and the label schema pre-built so no clinician
ever sees a configuration screen.

## What we provide

| Artefact | Purpose |
|---|---|
| `annotation/schema/cvat_labels_v0.1.json` | Load directly into a CVAT project — 17 labels covering Layers B–F |
| `annotation/converters/cvat_to_records.py` | CVAT XML → `frames.csv` / `anatomy.csv` / `planning.csv`; tested |
| `annotation/demo_project/sample_cvat_export.xml` | Synthetic fixture exercising every label type including the refusal tag |
| `research/annotations/HOSPITAL_ANNOTATION_ONTOLOGY_v0.1.md` | The schema's rationale, for clinician review |

The converter keeps Layer D (visible anatomy) and Layer F (clinical opinion) in
**separate files**, and stamps every Layer F row with its annotator. Pooling
across annotators is impossible by accident — it requires a deliberate,
separate consensus step.

## Deferred decisions

* **Keyframe interval.** Unknown until we time a real sweep with a real
  clinician. Everything about annotation throughput depends on this number and
  we refuse to guess it.
* **Model-assisted pre-labelling** (MONAI Label / CVAT auto-annotation). Very
  attractive for throughput, but it biases annotators toward the model's
  errors. **Not to be enabled during the calibration study**, because it would
  contaminate the inter-rater agreement measurement that the whole pilot exists
  to produce. Reconsider afterwards.
* **3D Slicer** becomes the right tool once sweeps are reconstructed into
  volumes; not needed for 2D frame annotation.
