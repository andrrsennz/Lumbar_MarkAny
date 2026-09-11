# exp004 - uncertainty and failure analysis

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
