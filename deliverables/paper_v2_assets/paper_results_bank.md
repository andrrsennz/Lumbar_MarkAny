# Paper results bank

Executed results only. Source: `experiments/exp005_lumbar_bone_seg/results.json` and `experiments/exp006_lumbar_uncertainty/metrics.json`.

## Cross-acquisition matrix (subject-disjoint 3-fold CV)

Subject-mean Dice, averaged over folds (SD across folds in brackets):

| train / test | HUS | RUS |
|---|---|---|
| **HUS** | 0.581 (0.000, n=1) | 0.568 (0.000, n=1) |
| **RUS** | — | — |
| **BOTH** | — | — |

Subject-mean tolerance-band F1 (2 px):

| train / test | HUS | RUS |
|---|---|---|
| **HUS** | 0.784 (0.000, n=1) | 0.759 (0.000, n=1) |
| **RUS** | — | — |
| **BOTH** | — | — |
## Caveat that must accompany every number above

healthy volunteers aged 20-35 (BMI 19-26), imaged PRONE with a 10 MHz LINEAR transducer; single annotator; 9 annotated subjects.
 Labels are visible bone surface, not puncture targets. Dice is harsh on a 1-2 px contour; tolerance-F1 is reported alongside for that reason.
