# exp003 — U-Net segmentation baseline

> **Porcine. Intraoperative. After laminectomy. Not lumbar, not transcutaneous,
> not human.** This run validates the pipeline end to end. It supports no claim
> about human neuraxial anatomy.

**Question.** Does the full pipeline — loader, palette decoding, augmentation,
loss, evaluation, statistics — work correctly and produce sensible numbers on
the official split?

**Method.** U-Net (~7.8 M parameters) on 144×352 greyscale, Dice+CE, AdamW with
cosine annealing, 30 epochs, mixed precision, official train/val/test split
(verified sweep-disjoint in exp001). Augmentation: rostral-caudal flip,
gain/brightness jitter, mild noise.

**Evaluation choices that matter.** A class absent from *both* prediction and
ground truth scores **NaN**, not 0 — scoring it 0 would punish the model for
correctly predicting nothing, and scoring it 1 would inflate the average. With
rare classes present in only ~26% of images this choice moves the macro average
substantially, which is exactly why our numbers are **not** directly comparable
to the published benchmarks.

**Uncertainty.** Bootstrap CIs resample **images**, because animals cannot be
resampled (no animal ID exists). This **understates** uncertainty relative to
the animal-level inference that would be correct.

**A caveat visible in the training curve.** Validation macro Dice oscillates
across a narrow band (0.7312-0.7658, range 0.0345) from roughly epoch 2 onward.
The model plateaus almost immediately, and the selected "best" epoch (21) sits
**inside that noise band** rather than at a meaningful optimum. Checkpoint
selection here is therefore close to arbitrary, and a different seed would very
likely pick a different epoch with indistinguishable test performance. One more
reason to read the reported test figure as "the pipeline works and produces
this order of magnitude", not as a tuned result.

Artefacts: `config.json`, `history.json`, `metrics.json`, `stdout.log`,
`predictions/per_image_metrics.npz`. Checkpoint `best.pt` is not tracked in Git
(regenerate with the command in `command.txt`).
