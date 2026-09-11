# exp001 — split-integrity audit

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
