# Treasure map

## REAL HUMAN LUMBAR ULTRASOUND — OPEN THESE FIRST

- **Best raw + expert annotation (side by side)** — `visuals/ultrasound/real_human_lumbar/side_by_side/URS08_H1_f0237.png`
- **Expert overlay, handheld** — `visuals/ultrasound/real_human_lumbar/hus/URS08_H1_f0237.png`
- **Expert overlay, robot-assisted** — `visuals/ultrasound/real_human_lumbar/rus/URS08_R2_f0050.png`
- **Our prediction vs expert, held-out subject** — `visuals/ultrasound/real_human_lumbar/prediction_overlays/URS08_H1_f0049.png`
- **Failure / high uncertainty** — `visuals/ultrasound/real_human_lumbar/failures/URS08_R2_f0031_dice0.000.png`
- **Difficult cases and expert-left-empty frames** — `visuals/ultrasound/real_human_lumbar/difficult_cases/URS08_H1_f0292_expert_left_empty.png`
- **Contact sheet** — `visuals/ultrasound/real_human_lumbar/contact_sheets/CONTACT_SHEET_DIFFICULT.png`
- **Contact sheet** — `visuals/ultrasound/real_human_lumbar/contact_sheets/CONTACT_SHEET_HUS_GT.png`
- **Contact sheet** — `visuals/ultrasound/real_human_lumbar/contact_sheets/CONTACT_SHEET_PAIRED_HUS_RUS.png`
- **Contact sheet** — `visuals/ultrasound/real_human_lumbar/contact_sheets/CONTACT_SHEET_RUS_GT.png`
- **FIGURE_1_REAL_LUMBAR_EVIDENCE_PIPELINE** — `deliverables/paper_v2_assets/FIGURE_1_REAL_LUMBAR_EVIDENCE_PIPELINE.png`
- **FIGURE_2_HUMAN_LUMBAR_AI_RESULTS** — _not generated_

## Asset counts

| Directory | Files |
|---|---|
| `visuals/ultrasound/real_human_lumbar/raw` | 80 |
| `visuals/ultrasound/real_human_lumbar/expert_labels` | 80 |
| `visuals/ultrasound/real_human_lumbar/expert_overlays` | 80 |
| `visuals/ultrasound/real_human_lumbar/side_by_side` | 80 |
| `visuals/ultrasound/real_human_lumbar/hus` | 31 |
| `visuals/ultrasound/real_human_lumbar/rus` | 49 |
| `visuals/ultrasound/real_human_lumbar/predictions` | 21 |
| `visuals/ultrasound/real_human_lumbar/prediction_overlays` | 21 |
| `visuals/ultrasound/real_human_lumbar/uncertainty` | 21 |
| `visuals/ultrasound/real_human_lumbar/failures` | 9 |
| `visuals/ultrasound/real_human_lumbar/difficult_cases` | 8 |
| `visuals/ultrasound/real_human_lumbar/contact_sheets` | 4 |
| `visuals/ultrasound/real_human_lumbar/publication_candidates` | 1 |

## Where the evidence is

| What | Where |
|---|---|
| Every number, traced to a file | `RESULTS_LEDGER.csv` |
| Every claim, with V2 status | `CLAIMS_LEDGER.csv` |
| Per-asset provenance and licence | `visuals/ultrasound/real_human_lumbar/ANNOTATION_PROVENANCE.csv` |
| Licence verification per source | `PIXEL_LICENSE_LEDGER.csv` |
| Attribution text | `visuals/ultrasound/real_human_lumbar/IMAGE_ATTRIBUTION.md` |
| Download provenance + MD5 | `provenance/KULEUVEN_DOWNLOAD_LOG.csv` |
| Independent verification | `KULEUVEN_VERIFICATION_REPORT.json` |
| Acceptance gate result | `QA_VISUAL_EVIDENCE_REPORT.json` |
| Redistributable data sample | `evidence_samples/kuleuven_lumbar/` |

## What is NOT here

- No puncture target, trajectory or outcome — **none exists in any public dataset**
- No JHU pixels — that dataset declares no licence
- No SUID pixels — request-only, not public
- No hardware, no safety case — the robotic system is a proposal
