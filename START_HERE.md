# START HERE

## What this package is

The V2 evidence vault for **Lumbar_MarkAny** — AI-assisted, robot-acquired lumbar ultrasound for neuraxial needle access.

**The one thing that changed from V1:** this package physically contains **real human lumbar ultrasound with real expert annotations**, and real model predictions on held-out human subjects. V1 discussed datasets; V2 shows them.

> **Open `00_VISUAL_INDEX.html` first.** Real ultrasound is on the first screen.

---

## The numbers

| | |
|---|---|
| Real human lumbar frames held | **6,182** |
| Human subjects | **9** |
| Handheld / robot-assisted | 2,382 / 3,800 |
| Frames the expert left empty | 184 (3.0%) |
| Source | KU Leuven / Balgrist, `doi:10.48804/3XPCAE`, **CC-BY-4.0** |

### Cross-acquisition matrix — subject-mean Dice, subject-disjoint 3-fold CV

| train ↓ / test → | HUS | RUS |
|---|---|---|
| **HUS** | 0.581 | 0.568 |
| **RUS** | — | — |
| **BOTH** | — | — |

Tolerance-band F1 (2 px), the fairer metric for a 1–2 px contour:

| train ↓ / test → | HUS | RUS |
|---|---|---|
| **HUS** | 0.784 | 0.759 |
| **RUS** | — | — |
| **BOTH** | — | — |

---

## What the annotations are — and are not

The public expert labels mark **VISIBLE BONE SURFACE** (value 2 of a `{0 or 1, 2}` mask). They are **not** puncture targets, entry points, trajectories, interspace choices or safety windows.

**No public dataset we could find contains a procedural label of any kind.** That is the gap only clinicians can close, and it is now the whole of the hospital ask — see `research/annotations/PUBLIC_VS_HOSPITAL_ANNOTATION_GAP.md`.

## What V1 got wrong

V1 recorded the anchor dataset as unreachable and concluded that no public real human transcutaneous lumbar ultrasound existed. **The dataset is public, CC-BY-4.0, and we now hold the entire annotated subset.** Only our workstation's network route was blocked. Full correction, including the retracted and superseded claims: `research/datasets/V2_ACCESS_CORRECTION.md`.

exp001–exp004 (porcine, intraoperative) are retained but downgraded to **secondary methodological evidence**.

## Reading order

1. `00_VISUAL_INDEX.html` — the evidence, visually
2. `00_TREASURE_MAP.md` — direct paths to the best assets
3. `research/datasets/V2_ACCESS_CORRECTION.md` — what changed and why
4. `research/datasets/KULEUVEN_LABEL_AUDIT.md` — what the data really contains
5. `RESULTS_LEDGER.csv` / `CLAIMS_LEDGER.csv` — every number, traced
6. `deliverables/paper_v2_assets/` — figures and the claims that are allowed

## Reproducing

```bash
python tools/download_kuleuven_subset.py --group labels --group recon --group meta
python tools/verify_kuleuven_subset.py
python tools/build_lumbar_dataset.py
python tools/cache_lumbar_arrays.py
./.venv/Scripts/python scripts/experiments/exp005_lumbar_bone_seg.py --epochs 12 --base 16 --height 320 --width 160
./.venv/Scripts/python scripts/experiments/exp006_lumbar_uncertainty.py
python tools/build_visual_library.py && python tools/build_contact_sheets.py
python tools/build_prediction_figures.py && python tools/build_hero_figures.py
python tools/qa_visual_evidence.py
```
