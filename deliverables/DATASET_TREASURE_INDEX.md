# Dataset treasure index

The practical companion to `research/datasets/DATASET_REGISTRY.csv`: for each
high-value dataset, what it is, what we actually hold, what it lets us build,
and the one thing most likely to trip someone up.

Ordered by value to *this* project, not by size or fame.

---

## DS001 — KU Leuven / Balgrist paired lumbar HUS + RUS + CT ⭐ the anchor

| | |
|---|---|
| **DOI** | `10.48804/3XPCAE` · paper `10.1038/s41597-025-06047-9` |
| **Licence** | **CC-BY-4.0** — redistribution permitted with attribution |
| **Size** | **1.01 TB**, 1,346 files |
| **We hold** | **Nothing.** Host unreachable from this network. |

**What it is.** 63 healthy volunteers. 223 handheld + 375 robot-assisted lumbar
ultrasound sweeps, each with synchronised 6-DoF probe pose, plus ultra-low-dose
CT and L1–L5 STL surface models. 6,091 frames annotated for bone surface.

**Why it is the anchor.** The only in-vivo human paired handheld/robotic lumbar
ultrasound dataset in existence, and it is openly licensed.

**What it enables.**
* The acquisition-consistency study — the project's strongest available paper
  (`HUS_RUS_ACQUISITION_ANALYSIS.md`). Uses pose data from **all 63** subjects
  and needs no annotations at all.
* Bone-surface segmentation and HUS↔RUS cross-domain transfer (9 subjects).
* CT-to-ultrasound registration; 3D sweep reconstruction.
* The only source of **licensable real lumbar ultrasound images** for figures.

> ⚠ **The trap.** "63 subjects, 6,091 annotated frames" describes two different
> things. Only **9** subjects are annotated, by **one** annotator. And the
> protocol is **prone** with a **10 MHz linear** probe — an orthopaedic
> surgical-guidance setup, not neuraxial anaesthesia practice.

---

## DS004 — JHU HEPIUS porcine spinal-cord segmentation ⭐ the workhorse

| | |
|---|---|
| **Source** | GitHub README → Google Drive · paper PMC12475011 |
| **Licence** | **NONE DECLARED** |
| **Size** | 1.08 GB · **held, checksummed, verified** |

**What it is.** 10,223 B-mode images of porcine spinal cord (pre- and
post-contusion), each with a 10-class mask: Background, Dura, Pia, CSF, Spinal
cord, Dorsal Space, Hematoma, Ventral Space, Dura/Pia complex, Dura/Ventral
Complex. Official split 8,668 / 895 / 660.

**Annotation quality — the best we found.** Trained annotators, radiologist
adjudication of ambiguous cases, then re-validation by a neurosurgery spine
fellow. This is the template for the hospital pilot.

**What we built on it.** The entire pipeline: loader, palette decoding,
augmentation, Dice+CE, per-class evaluation with correct NaN handling,
bootstrap CIs, split-integrity audit. Everything in `experiments/`.

> ⚠ **Two traps, both serious.**
> 1. **The palette→class mapping is undocumented.** Assume an order and you get
>    plausible-looking, silently wrong labels. We recovered it (`exp002`); use
>    `src/lumbar_markany/data_jhu.py`.
> 2. **No licence exists.** Not on the repo, not in the archives. Use locally;
>    do not redistribute pixels or derived overlays.

> ⚠ **And it is the wrong anatomy.** Intraoperative, after laminectomy — the
> bone that neuraxial ultrasound must see through has been surgically removed.

---

## DS005 — JHU injury localization

| | |
|---|---|
| **Licence** | **NONE DECLARED** · **Size** 224 MB · **held and verified** |

2,245 images: 877 pre-injury (zero boxes) + 1,368 post-injury (exactly one box
each). Verified against the publication by parsing every file.

**Use:** an object-detection benchmark in the ultrasound domain. Not relevant to
neuraxial anatomy.

> ⚠ The 1,368 box-bearing images carry **no subject token at all** in their
> filenames.

---

## DS002 — Masoumi multimodal spine US/CT

| | |
|---|---|
| **DOI** | `10.5281/zenodo.4813508` · **CC-BY-4.0** · 149 MB · **held** |

CT + ultrasound + 21 landmark pairs for registration validation.

**Use:** a CT-to-US registration benchmark with landmark ground truth, openly
licensed.

> ⚠ **The trap, and it is a big one.** The three *human* subjects have CT and
> **CT-simulated** ultrasound only. Real ultrasound exists solely for two
> **ex-vivo animal** phantoms imaged on exposed bone. Do not cite this as
> evidence about human lumbar ultrasound.

---

## DS003 — UltraBones100k (not obtained)

| | |
|---|---|
| **Paper** | `10.1016/j.compbiomed.2025.110435` · arXiv 2502.03783 |
| **Availability** | **UNKNOWN** — no public download located |

~100,000 ex-vivo human **lower-limb** ultrasound images with bone labels
generated **automatically** from CT registration and refined for ultrasound
physics, then reviewed by an expert sonographer.

**Why it matters even though we do not have it.** Our binding constraint is
clinician annotation time. This group's whole research line is about not
depending on manual labels. If the hospital pilot shows per-frame annotation is
too slow — our highest-likelihood risk — this is the method to adopt.

> ⚠ Do **not** describe it as a public dataset. We could not confirm access.

---

## Tier-4 pool — catalogued, not downloaded

54 ultrasound datasets typed as `dataset` across breast, thyroid, fetal,
cardiac, lung, prostate, vascular and musculoskeletal imaging, mostly CC-BY-4.0
or CC0. Listed in `data/registry/DISCOVERY_CANDIDATES.csv`.

**Use:** ultrasound-domain representation learning only.

> ⚠ **Never merge their label spaces with spine anatomy.** A breast lesion mask
> and a lamina mask are not the same kind of object. Shared *pixels* can help
> pretraining; shared *labels* are a category error.

---

## Worth pursuing next

| Dataset | Licence | Why |
|---|---|---|
| Trackerless 3D Freehand Ultrasound Reconstruction Challenge 2024 | CC-BY-NC-SA-4.0 | Sweep reconstruction without external tracking — the fallback if optical/robot tracking is impractical clinically. NC limits commercial use. |
| "Freehand ultrasound without external trackers" | CC-BY-4.0 | Same theme, permissive licence |
| Shoulder 3D Ultrasound Mosaicking Dataset | CC-BY-4.0 | Pose estimation vs hybrid alignment; transferable to spine sweeps |
| Micro-Ultrasound Prostate Segmentation | CC-BY-4.0 | Clean segmentation benchmark for pretraining studies |

---

## The index in one table

| ID | Relation to lumbar puncture | Held? | Licence | Can show images? | Best use |
|---|---|---|---|---|---|
| DS001 | **direct** (with caveats) | ✘ unreachable | CC-BY-4.0 | **yes** | acquisition study; the real target |
| DS004 | none (wrong anatomy) | ✔ | **none** | **no** | pipeline development; pretraining |
| DS005 | none | ✔ | **none** | **no** | detection benchmark |
| DS002 | weak (registration only) | ✔ | CC-BY-4.0 | yes | US/CT registration testbed |
| DS003 | none (lower limb) | ✘ | unknown | no | automated-labelling methodology |
| Tier-4 | none | ✘ | mostly CC-BY/CC0 | varies | representation learning only |

**Read the "Can show images?" column before making any figure.** It is the
reason this package contains no picture of real annotated ultrasound.
