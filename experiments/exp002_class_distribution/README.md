# exp002 — class-distribution reproduction and palette recovery

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
