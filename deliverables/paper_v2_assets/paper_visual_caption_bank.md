# Visual caption bank

Ready-to-use captions. Every one names the species, approach, label semantics
and licence, because `paper_claims_forbidden.md` §7 requires it.

**Attribution string** (append to any figure containing dataset pixels):

> Ultrasound and expert annotation: Cavalcanti et al., KU Leuven RDR,
> doi:10.48804/3XPCAE, CC-BY-4.0.

---

## Figure 1 — `FIGURE_1_REAL_LUMBAR_EVIDENCE_PIPELINE.png`

> **Figure 1. Real human lumbar ultrasound, expert annotation, automated
> perception, and the layer that is still missing.**
> **(a)** Handheld B-mode ultrasound of the lumbar spine in a healthy adult
> volunteer, acquired prone with a 10 MHz linear transducer.
> **(b)** The same frame with the publicly released physician annotation of
> **visible bone surface** (red). This is the only annotated class in the
> dataset: there is no entry point, trajectory, interspace or target depth.
> **(c)** Our segmentation on a subject held out of training (green), against
> the expert annotation (red).
> **(d)** Robot-assisted acquisition in a different subject, with the same
> class of expert annotation.
> **(e)** A failure case: a held-out frame where the model's prediction
> diverges from the expert annotation.
> **(f)** The proposed clinician-in-the-loop system. **No hardware exists and
> nothing in this panel has been clinically validated.**
> Panels (a)–(e) are real data and executed results; panel (f) is a proposal.
> Image panels are depth-cropped for display; all metrics use full frames.

## Figure 2 — `FIGURE_2_HUMAN_LUMBAR_AI_RESULTS.png`

> **Figure 2. Per-frame results on held-out human subjects.**
> Rows: strong handheld cases, difficult handheld cases, robot-assisted cases,
> and failures. Columns: raw ultrasound; expert bone-surface annotation; our
> prediction; per-pixel error (white true positive, red missed, blue spurious);
> Monte-Carlo-dropout uncertainty. Every subject shown was excluded from the
> training set of the model that predicts on it. Failures are included
> deliberately.

## Contact sheets

> **Handheld / robot-assisted contact sheet.** Forty frames sampled at even
> intervals across all annotated frames of that modality — not selected for
> appearance. Red marks the physician's annotation of visible bone surface.

> **Difficult cases.** Left: the twenty frames with the smallest annotated bone
> surface. Right: twenty of the 184 frames (3.0% of the dataset) where the
> expert identified **no** bone surface at all. Dice is undefined on the latter
> and they are scored separately.

> **Paired handheld vs robot-assisted.** Two handheld then two robot-assisted
> frames from each of the seven subjects that have both. Same anatomy, different
> acquisition.

## Individual panels

> **Raw frame.** Real human in-vivo transcutaneous lumbar ultrasound, cropped to
> the live sector (the frame grabber captured the whole scanner display; the
> crop removes the UI, depth ruler and burned-in study banner).

> **Expert annotation.** Physician-annotated visible bone surface, 1–3 px
> contour, dilated by one pixel for display only. **Not** a puncture target.

> **Prediction.** U-Net output on a held-out subject at a 0.5 threshold.

> **Error map.** White true positive, red missed (false negative), blue spurious
> (false positive), each dilated for visibility.

> **Uncertainty.** Per-pixel standard deviation across Monte-Carlo dropout
> passes; warmer is more uncertain.

---

## Phrases that must never appear in a caption

* "puncture target", "entry point", "needle trajectory", "safe window",
  "insertion depth" — over any real frame
* "lumbar puncture accuracy", "validated for neuraxial access"
* "ground truth" without saying *what* — always "expert bone-surface annotation"
* a Dice score without species, position and probe

## Phrases that must appear somewhere in the figure block

* "healthy volunteers, prone, 10 MHz linear probe"
* "single annotator; inter-rater reliability unmeasured"
* "9 annotated subjects"
* "subject-held-out"
