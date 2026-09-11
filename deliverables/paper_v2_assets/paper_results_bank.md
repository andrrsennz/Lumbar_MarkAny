# Paper results bank

Executed results only. Source: `experiments/exp005_lumbar_bone_seg/results.json` and `experiments/exp006_lumbar_uncertainty/metrics.json`.

## Cross-acquisition matrix (subject-disjoint 3-fold CV)

Subject-mean Dice, averaged over folds (SD across folds in brackets):

| train / test | HUS | RUS |
|---|---|---|
| **HUS** | 0.498 (0.072, n=3) | 0.490 (0.066, n=3) |
| **RUS** | 0.562 (0.035, n=3) | 0.560 (0.032, n=3) |
| **BOTH** | 0.577 (0.035, n=3) | 0.572 (0.029, n=3) |

Subject-mean tolerance-band F1 (2 px):

| train / test | HUS | RUS |
|---|---|---|
| **HUS** | 0.695 (0.078, n=3) | 0.679 (0.069, n=3) |
| **RUS** | 0.755 (0.028, n=3) | 0.753 (0.024, n=3) |
| **BOTH** | 0.767 (0.033, n=3) | 0.760 (0.020, n=3) |

## Per-subject Dice (BOTH regime, each subject held out)

| subject | Dice | frames |
|---|---|---|
| URS08 | 0.623 | — |
| URS16 | 0.615 | — |
| URS26 | 0.560 | — |
| URS31 | 0.606 | — |
| URS36 | 0.555 | — |
| URS40 | 0.548 | — |
| URS45 | 0.537 | — |
| URS51 | 0.597 | — |
| URS54 | 0.537 | — |

Across subjects: mean 0.575, SD 0.033, range 0.537–0.623 (n=9).

**With nine subjects, this spread is the honest measure of uncertainty; a confidence interval would imply more precision than nine points support.**

## Uncertainty on real human lumbar data (exp006)

- Spearman rho vs per-frame Dice: **-0.228** (predictive entropy), **-0.280** (pass disagreement)
- Frames scored: 5,998 annotated, 184 empty-label

| declined | Dice retained | Dice declined |
|---|---|---|
| 5% | 0.577 | 0.516 |
| 10% | 0.580 | 0.521 |
| 20% | 0.585 | 0.530 |
| 30% | 0.588 | 0.542 |

Per modality:

| modality | rho | mean Dice |
|---|---|---|
| HUS | -0.219 | 0.571 |
| RUS | -0.243 | 0.576 |

On the 184 frames the expert left empty, the model predicted something in 78.3% of cases.

## Caveat that must accompany every number above

healthy volunteers aged 20-35 (BMI 19-26), imaged PRONE with a 10 MHz LINEAR transducer; single annotator; 9 annotated subjects.
 Labels are visible bone surface, not puncture targets. Dice is harsh on a 1-2 px contour; tolerance-F1 is reported alongside for that reason.
