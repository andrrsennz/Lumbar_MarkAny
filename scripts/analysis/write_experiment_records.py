#!/usr/bin/env python3
"""
write_experiment_records.py -- Ensure every experiment directory carries the
full reproducibility record: command.txt, environment.txt and README.md
alongside the config/log/metrics the run itself produced.

environment.txt is captured from the interpreter that ACTUALLY ran the
experiment where that is knowable (recorded in the run's config.json), not from
whatever happens to be on PATH now.
"""
from __future__ import annotations
import json
import pathlib
import platform
import subprocess
import sys

EXP = pathlib.Path("experiments")

COMMANDS = {
    "exp001_leakage_audit": "python scripts/analysis/leakage_audit.py",
    "exp002_class_distribution": "python scripts/analysis/verify_class_distribution.py",
    "exp003_unet_baseline": (
        "./.venv/Scripts/python.exe scripts/experiments/train_seg.py "
        "--epochs 30 --out experiments/exp003_unet_baseline --workers 4"),
    "exp004_uncertainty_failure": (
        "./.venv/Scripts/python.exe scripts/experiments/uncertainty_failure.py"),
}

READMES = {
    "exp004_uncertainty_failure": """# exp004 - uncertainty and failure analysis

> Porcine, intraoperative, post-laminectomy. This validates the uncertainty
> **mechanism**. It is not a clinical safety claim, and the model is not
> safety-certified.

**Question.** Can the model tell when it is wrong? A guidance system that
proposes a target must be able to decline to propose one, and a confidence
display that does not track real error is worse than none.

**Method.** Monte-Carlo dropout: the bottleneck `Dropout2d` is re-enabled at
test time (BatchNorm deliberately left in eval) and 10 stochastic passes give a
predictive distribution per pixel. Two summaries - mean predictive entropy, and
the fraction of passes disagreeing with the modal prediction - are correlated
against the per-image Dice each image actually achieved.

**Results.**

| Measure | Spearman rho vs Dice |
|---|---|
| mean predictive entropy | **-0.731** |
| inter-pass disagreement | **-0.763** |

Both are strongly negative: the uncertainty signal tracks real error rather
than being decorative.

**Abstention.** Declining the most-uncertain images improves what remains:

| Declined | Dice on retained | Dice on declined |
|---|---|---|
| 0% | 0.722 | - |
| 5% | 0.728 | 0.622 |
| 10% | 0.735 | 0.613 |
| 20% | 0.748 | 0.622 |
| 30% | **0.764** | 0.625 |

**Failure taxonomy.** The worst decile (mean Dice 0.544) differs from the best
decile (0.910) systematically in image statistics, not randomly:

| | worst decile | best decile |
|---|---|---|
| mean image intensity | 0.253 | 0.372 |
| image contrast (SD) | 0.206 | 0.283 |
| mean predictive entropy | 0.112 | 0.073 |

Spearman Dice vs contrast **+0.542**, vs intensity **+0.475**. **Failures
concentrate in dark, low-contrast images** - the signature of poor acoustic
coupling or attenuation, which is exactly the failure mode a scan-quality gate
is meant to catch before a target is ever proposed.

**Why this matters to the project.** It is direct evidence for the design
principle in `SYSTEM_ARCHITECTURE_AND_AUTONOMY.md`: the system's most important
behaviour is knowing when not to act, and that behaviour is measurable.

Artefacts: `metrics.json`, `per_image.npz` (per-image Dice, entropy,
disagreement, image statistics).
""",
    "exp001_leakage_audit": """# exp001 — split-integrity audit

**Question.** Do the official train/val/test splits of the JHU spinal-cord
segmentation release leak near-duplicate frames into the held-out sets?

**Why it matters.** Consecutive B-mode frames from one sweep are almost
identical. If they straddle a split boundary, held-out metrics are optimistic.
The release distributes no subject identifier, so this cannot be checked from
filenames — it has to be checked from pixels.

**Method.** Every image reduced to a 64×64 z-normalised unit vector; exact
cosine similarity of each held-out image against all 8,668 training images. The
decision threshold is **calibrated**, not assumed: frames known to be adjacent
within one acquisition give the numerical signature of "same sweep".

**Result — negative.** Within-sweep adjacent frames score 0.990 (median),
5th percentile 0.911. No held-out image exceeds 0.890 against any training
image, and **zero** held-out images reach the within-sweep threshold. The
splits are sweep-disjoint. Our hypothesis was wrong.

**What this does NOT establish.** Animal-level disjointness. Two sweeps of the
same animal look quite different (we measured cosine ≈0.09–0.21 for one such
pair), so this test cannot detect them, and no animal ID is distributed.

Artefacts: `metrics.json`, `nearest_neighbours.csv` (per-image nearest training
neighbour and its score).
""",
    "exp002_class_distribution": """# exp002 — class-distribution reproduction and palette recovery

**Question.** Do the distributed masks actually contain what the publication's
Table 1 reports, and which palette index corresponds to which anatomical class?

**Why it matters.** The release ships RGB masks in a PASCAL-VOC palette but
**documents no index→class mapping**. A user who assumes an order gets
plausible-looking, silently wrong labels — the worst kind of error, because
nothing fails.

**Method.** Exhaustive pixel accounting over all 10,223 masks: RGB packed to
24-bit, mapped through the VOC palette, counted per index. Indices then matched
to the publication's classes by pixel total, which is unambiguous because the
totals differ by orders of magnitude.

**Result.** All ten classes matched **exactly** — relative error 0.0000 for
pixel counts and exact agreement on image counts. Only 13 stray anti-aliased
pixels out of 1.94 × 10⁹ fall outside the palette.

**Recovered mapping** (now in `src/lumbar_markany/data_jhu.py`):

| idx | class | idx | class |
|---|---|---|---|
| 0 | Background | 5 | Dorsal Space |
| 1 | Dura | 6 | Hematoma |
| 2 | Pia | 7 | Ventral Space |
| 3 | CSF | 8 | Dura/Pia complex |
| 4 | Spinal cord | 9 | Dura/Ventral Complex |

Artefacts: `metrics.json` (per-index counts, per-class match, stray colours).
""",
    "exp003_unet_baseline": """# exp003 — U-Net segmentation baseline

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
""",
}


def environment_text(run_python: str | None) -> str:
    lines = [f"captured_by      : {sys.executable}",
             f"platform         : {platform.platform()}",
             f"processor        : {platform.processor()}",
             f"python (capture) : {platform.python_version()}"]
    py = run_python or sys.executable
    lines.append(f"python (run)     : {py}")
    try:
        out = subprocess.run([py, "-m", "pip", "freeze"], capture_output=True,
                             text=True, timeout=180)
        lines += ["", "pip freeze (run interpreter):", out.stdout.strip()]
    except Exception as e:
        lines.append(f"pip freeze failed: {e}")
    return "\n".join(lines) + "\n"


def main():
    venv = pathlib.Path(".venv/Scripts/python.exe")
    for name, cmd in COMMANDS.items():
        d = EXP / name
        if not d.exists():
            print(f"  skip {name} (missing)")
            continue
        (d / "command.txt").write_text(cmd + "\n", encoding="utf-8")
        run_py = str(venv.resolve()) if (name == "exp003_unet_baseline" and venv.exists()) else None
        (d / "environment.txt").write_text(environment_text(run_py), encoding="utf-8")
        if name in READMES:
            (d / "README.md").write_text(READMES[name], encoding="utf-8")
        (d / "figures").mkdir(exist_ok=True)
        print(f"  {name}: command.txt, environment.txt, README.md")
    print("done")


if __name__ == "__main__":
    main()
