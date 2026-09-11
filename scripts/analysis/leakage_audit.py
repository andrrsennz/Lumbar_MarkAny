#!/usr/bin/env python3
"""
leakage_audit.py -- Filename-independent near-duplicate audit of the official
JHU spinal-cord ultrasound segmentation splits.

Motivation
----------
Consecutive B-mode frames from one ultrasound sweep are highly correlated. If
frames from the same sweep/animal appear in both the training and the test
split, held-out metrics are optimistic. The public release does not expose a
documented animal identifier (56.3% of images are named `scaled-dicom-<n>.png`
with no grouping token), so split disjointness cannot be checked from
filenames. This script therefore checks the *pixels*.

Method
------
1. Load every image, convert to greyscale, resize to 64x64, z-normalise.
2. Cosine similarity between each test/val image and every training image
   (exact, dense, via matrix product on unit vectors).
3. Report the distribution of each held-out image's nearest training neighbour.
4. Calibrate the threshold using a within-sweep baseline: similarity between
   frames known to come from the same acquisition (same `predictN_scaled-Axxxx`
   prefix, adjacent frame indices). This tells us what "same sweep" looks like
   numerically, rather than assuming a threshold.

Outputs JSON + CSV to experiments/exp001_leakage_audit/.
"""
import os, re, json, csv, time, pathlib, sys
import numpy as np
from PIL import Image

ROOT = pathlib.Path("data/extracted/jhu_segmentation/SegmentationDataset")
OUT = pathlib.Path("experiments/exp001_leakage_audit")
OUT.mkdir(parents=True, exist_ok=True)
SIZE = 64

def listing(split):
    d = ROOT / f"{split}_images"
    return sorted(p for p in d.iterdir() if p.suffix.lower() == ".png")

def load_matrix(paths):
    """Return (n, SIZE*SIZE) float32 matrix of z-normalised, unit-length rows."""
    M = np.zeros((len(paths), SIZE * SIZE), dtype=np.float32)
    for i, p in enumerate(paths):
        im = Image.open(p).convert("L").resize((SIZE, SIZE), Image.BILINEAR)
        v = np.asarray(im, dtype=np.float32).ravel()
        v -= v.mean()
        s = np.linalg.norm(v)
        M[i] = v / s if s > 1e-6 else v
    return M

def acq_key(name):
    m = re.match(r"^(.*?)_scaled-(A\d+)_frame(\d+)\.png$", name)
    return (f"{m.group(1)}|{m.group(2)}", int(m.group(3))) if m else (None, None)

def main():
    t0 = time.time()
    paths = {s: listing(s) for s in ("train", "val", "test")}
    for s, ps in paths.items():
        print(f"{s:6s} {len(ps)} images")
    mats = {}
    for s, ps in paths.items():
        print(f"loading {s} ...", flush=True)
        mats[s] = load_matrix(ps)
    print(f"loaded in {time.time()-t0:.1f}s", flush=True)

    # ---- calibration: within-acquisition adjacent-frame similarity (train only)
    groups = {}
    for i, p in enumerate(paths["train"]):
        k, f = acq_key(p.name)
        if k:
            groups.setdefault(k, []).append((f, i))
    adj = []
    for k, lst in groups.items():
        lst.sort()
        for (f1, i1), (f2, i2) in zip(lst, lst[1:]):
            if f2 == f1 + 1:
                adj.append(float(mats["train"][i1] @ mats["train"][i2]))
    adj = np.array(adj, dtype=np.float32)
    calib = {
        "n_adjacent_pairs": int(adj.size),
        "mean": float(adj.mean()) if adj.size else None,
        "p05": float(np.percentile(adj, 5)) if adj.size else None,
        "p25": float(np.percentile(adj, 25)) if adj.size else None,
        "median": float(np.median(adj)) if adj.size else None,
    }
    print("within-sweep adjacent-frame cosine:", calib, flush=True)

    # ---- nearest training neighbour for each held-out image
    results = {"calibration_within_sweep_adjacent": calib, "splits": {}}
    rows = []
    T = mats["train"]
    for s in ("val", "test"):
        Q = mats[s]
        best = np.zeros(len(Q), dtype=np.float32)
        besti = np.zeros(len(Q), dtype=np.int64)
        B = 256
        for a in range(0, len(Q), B):
            sim = Q[a:a + B] @ T.T          # (b, n_train)
            besti[a:a + B] = sim.argmax(1)
            best[a:a + B] = sim.max(1)
        thr = calib["p05"] if calib["p05"] is not None else 0.9
        res = {
            "n": int(len(Q)),
            "nn_cosine_mean": float(best.mean()),
            "nn_cosine_median": float(np.median(best)),
            "nn_cosine_p90": float(np.percentile(best, 90)),
            "nn_cosine_max": float(best.max()),
            "frac_ge_0.99": float((best >= 0.99).mean()),
            "frac_ge_0.95": float((best >= 0.95).mean()),
            "frac_ge_calib_p05": float((best >= thr).mean()),
            "calib_p05_threshold": float(thr),
        }
        results["splits"][s] = res
        print(s, json.dumps(res, indent=1), flush=True)
        for i in range(len(Q)):
            rows.append({"split": s, "image": paths[s][i].name,
                         "nearest_train_image": paths["train"][besti[i]].name,
                         "cosine": round(float(best[i]), 6)})

    (OUT / "metrics.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    with open(OUT / "nearest_neighbours.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["split", "image", "nearest_train_image", "cosine"])
        w.writeheader(); w.writerows(rows)
    print(f"done in {time.time()-t0:.1f}s -> {OUT}")

if __name__ == "__main__":
    main()
