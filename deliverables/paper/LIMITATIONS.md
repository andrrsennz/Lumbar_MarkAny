# Limitations

Written to be transplanted into a paper's Limitations section with minimal
editing. Ordered by how much each one constrains what may be claimed.

---

## 1. No experiment in this work used human lumbar ultrasound

This is the limitation that governs all the others. The anchor dataset
(`doi:10.48804/3XPCAE`) was unreachable from the project network: the entire
`kuleuven.be` domain failed TCP connection on ports 80 and 443, by hostname and
by direct IP, while every other research-data host tested responded normally.
The deposit is also 1.01 TB against 135 GB of available storage.

Consequently, the cross-acquisition study this project was designed around —
handheld versus robot-assisted lumbar ultrasound — was not performed. All
executed results are on porcine, intraoperative, post-laminectomy spinal-cord
imaging and support no claim about human neuraxial anatomy.

## 2. The experimental substrate is the wrong anatomy, species and approach

The JHU dataset images the **exposed spinal cord after laminectomy**. The
acoustic path contains no intervening bone or deep soft tissue, and the target
structures are cord and meninges rather than the dorsal bone landmarks that
matter for neuraxial access. It is also porcine for all 10,223 training images.
It was used as an engineering substrate — to build and measure the pipeline —
and for nothing else.

## 3. Animal-level generalisation could not be assessed

The public release distributes **no animal identifier**. For 5,756 of 10,223
images (56.3%) the filenames carry no grouping token at all, and for the
remainder the available token is demonstrably not an animal key (the same token
pairs with visually dissimilar images across different acquisition batches).

We therefore verified what we could — that the official splits are
**sweep-disjoint**, by a filename-independent near-duplicate audit calibrated
against within-sweep frame similarity — and we state plainly that
**animal-level disjointness is unverifiable from the public release.** Reported
metrics are held-out at the sweep level, not the animal level.

A direct consequence: our bootstrap confidence intervals resample **images**,
because animals cannot be resampled. Image-level resampling **understates**
uncertainty relative to the animal-level inference that would be correct here.
The intervals should be read as a lower bound on uncertainty.

## 4. Our metrics are not directly comparable to the published benchmarks

The source publication reports DeepLabv3 mean Dice 0.587 and SAMed 0.445.
We did not reproduce their evaluation protocol. In particular, we score a class
as **NaN** when it is absent from both prediction and ground truth, rather than
as 0 or 1; with rare classes present in only ~26% of images, that choice alone
can move a macro average substantially. Our numbers are internally consistent
and reproducible, and **no claim of superiority over the published figures is
made or supported.**

## 5. The dataset survey has bounded scope

The finding that only two Tier-0 ultrasound datasets exist, neither containing
real human transcutaneous lumbar ultrasound, is a statement about **this
search**: these queries, six repository APIs, one network, one date. Three
specific blind spots:

* **Repository-indexed material only.** The JHU dataset itself was found via its
  *paper*, not via any data repository — a repository-only search would have
  missed it. Datasets published on a lab webpage or in paywalled supplementary
  material are largely invisible to this method.
* **KU Leuven was never searched from the inside**, so that repository's
  holdings beyond the anchor deposit are unknown to this survey.
* **Keyword triage is not a relevance judgement.** Tier assignment is automated;
  only the datasets that reached the registry were assessed by reading sources.

It is strong evidence of scarcity. It is not proof of non-existence.

## 6. Limitations inherited from the anchor dataset (which apply even once obtained)

Verified from its open-access full text, and material to any future work:

* **9 annotated subjects, not 63.** Seven with both HUS and RUS; two RUS-only.
  Any cross-domain claim rests on **seven paired subjects**.
* **A single annotator**, who also acquired the handheld images. No second
  reader, no adjudication, no inter-rater agreement. Annotation reliability for
  lumbar ultrasound is unmeasured anywhere in the public literature we surveyed.
* **Healthy volunteers, BMI 19–26, age 20–35** — close to the inverse of the
  population in whom ultrasound assistance is clinically indicated.
* **Prone position**, whereas lumbar puncture is performed sitting or in lateral
  decubitus, changing spinal flexion and interspinous geometry.
* **10 MHz linear transducer at 7.7 cm depth** — an orthopaedic surgical-guidance
  protocol, not the low-frequency curvilinear imaging used for neuraxial access.
* **Bone surface is the only label.** No procedural target of any kind.

## 7. The premise of robotic acquisition is not yet established

The project's central engineering argument is that robot-held acquisition is
more consistent than handheld. The one dataset that could test this reports the
**opposite** at face value: scan-path area ratio ≥85% for handheld versus
54–100% for robotic. The authors attribute the robotic variability to a
deliberately restricted scanning speed, which is plausible but, in the published
analysis, untested against the pose data.

Until that analysis is run, "robotic acquisition improves consistency" is a
**hypothesis, not a premise**, and the architecture built on it is provisional.

## 8. Licensing constrains what can be shown

The JHU data carries no declared licence — neither the repository nor the
archives include one. This project therefore publishes numbers derived from it
but **redistributes none of its pixels**, which is why no figure in this package
shows an annotated ultrasound image. Figures showing real annotated lumbar
ultrasound must wait for the CC-BY anchor dataset or for hospital data.

## 9. Single training run, no hyperparameter study, no seed variance

`exp003` is one run at one seed with one architecture. No hyperparameter search
was performed, no seed-to-seed variance was measured, and no alternative
architecture was compared. It establishes that the pipeline functions and
produces plausible numbers; it does **not** establish that these numbers are the
best achievable, nor how stable they are.

## 10. Everything about hardware is a proposal

No hardware has been built, purchased or specified beyond a paper concept. No
safety case, no workspace measurement, no phantom test, no ergonomic assessment.
The architecture recommendation is reasoned from the literature and from the
regulatory landscape, and is labelled E6 throughout.
