# Claims allowed — verbatim sentences

Each of these is safe to paste into the paper as written. The paired forbidden list is `paper_claims_forbidden.md`.

## About availability

> Real, publicly downloadable, expert-annotated human transcutaneous lumbar ultrasound exists: the KU Leuven / Balgrist deposit (doi:10.48804/3XPCAE, CC-BY-4.0) provides 6,182 annotated frames from 9 subjects across handheld and robot-assisted acquisition.

> No public dataset located in this survey contains a procedural label of any kind — no entry point, trajectory, target depth, interspace choice or outcome.

## About the data

> The annotated subset is self-contained: each label archive ships the ultrasound frames alongside their annotations, so the complete expert-annotated set occupies 1.70 GB rather than the deposit's 631 GB.

> Parsing every data_list.txt yields 6,182 listed frames of which 5,998 carry a non-empty annotation; the source publication reports 6,091, which neither counting rule reproduces.

> The background label value is not consistent across the deposit: six of the eighteen archives encode background as 0 and the remaining twelve as 1, while bone surface is 2 throughout.

## About our results

> Training on both acquisition modes and evaluating on held-out subjects, subject-mean Dice was 0.577 on handheld and 0.572 on robot-assisted ultrasound, under subject-disjoint 3-fold cross-validation over nine subjects.

> All splits were subject-disjoint; statistics were aggregated per subject before averaging, and frame counts are reported but never treated as independent samples.

> Because the annotated structure is a 1-2 pixel contour, a tolerance-band F1 is reported alongside Dice, which penalises a one-pixel offset as a total miss.

> Frames where the expert annotated nothing are excluded from Dice, which is undefined there, and scored separately.

## About what is still missing

> The available data is healthy volunteers aged 20-35 with BMI 19-26, imaged prone with a 10 MHz linear transducer. Neuraxial procedures are performed sitting or in lateral decubitus with a low-frequency curvilinear probe, in a patient population selected for difficulty. The gap is one of kind, not quantity.

> The annotations were produced by a single annotator, who also acquired the handheld scans; inter-rater reliability for lumbar ultrasound annotation is therefore unmeasured.
