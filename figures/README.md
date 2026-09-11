# Figures

| File | Content | Source artefact |
|---|---|---|
| `fig01_dataset_survey` | Public ultrasound dataset survey by relevance tier | `data/registry/DISCOVERY_CANDIDATES.csv` |
| `fig02_class_distribution` | JHU 10-class distribution, independently reproduced | `experiments/exp002_class_distribution/metrics.json` |
| `fig03_leakage_audit` | Split-integrity audit with within-sweep calibration | `experiments/exp001_leakage_audit/` |
| `fig04_training_curves` | U-Net training loss and validation Dice | `experiments/exp003_unet_baseline/history.json` |
| `fig05_per_class_dice` | Per-class test Dice with n per class | `experiments/exp003_unet_baseline/metrics.json` |
| `fig_system_workflow.svg` | Proposed clinical workflow (original diagram, E6) | hand-authored |

Regenerate the data figures with:

```bash
python scripts/figures/make_figures.py
```

Every data figure is drawn from a file under `experiments/` or
`data/registry/`. None contains a hand-typed number.

## Formats

Data figures ship as **SVG** (vector, editable) and **PNG at 300 dpi**.
`fig_system_workflow.svg` is vector only: rasterising it needs a cairo/Inkscape
or browser toolchain that was not available on the authoring machine. SVG is
the preferred format for publication and imports directly into PowerPoint,
Word, Inkscape and any browser, so no rasterisation is required for normal use.

## What is deliberately absent

There is **no figure showing real annotated ultrasound**. The only annotated
ultrasound this project holds is the JHU dataset, which carries **no declared
licence**, so its pixels are not redistributed. The four-column translational
figure described in the slide storyboard and paper outline is therefore
**not made** rather than faked — it needs a licensed real image, which arrives
with the CC-BY anchor dataset or with hospital data.
