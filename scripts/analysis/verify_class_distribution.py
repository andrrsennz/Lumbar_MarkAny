#!/usr/bin/env python3
"""
verify_class_distribution.py -- Independently recompute the class pixel
statistics of the JHU spinal-cord segmentation dataset from the downloaded
masks, and compare against Table 1 of the source publication
(doi:10.1038/s41597-025-05869-x / PMC12475011).

This is a reproduction check: it verifies that the distributed mask files
actually contain the class distribution the paper reports.
"""
import json, pathlib, collections, sys
import numpy as np
from PIL import Image

ROOT = pathlib.Path("data/extracted/jhu_segmentation/SegmentationDataset")
OUT = pathlib.Path("experiments/exp002_class_distribution")
OUT.mkdir(parents=True, exist_ok=True)

# Standard PASCAL-VOC colour palette (CVAT's default export palette).
def voc_palette(n=256):
    pal = np.zeros((n, 3), dtype=np.uint8)
    for i in range(n):
        r = g = b = 0; c = i
        for j in range(8):
            r |= ((c >> 0) & 1) << (7 - j)
            g |= ((c >> 1) & 1) << (7 - j)
            b |= ((c >> 2) & 1) << (7 - j)
            c >>= 3
        pal[i] = (r, g, b)
    return pal

PAL = voc_palette()
LUT = {tuple(int(x) for x in PAL[i]): i for i in range(256)}

# Table 1 of the publication (pixel instances, images containing the class)
PAPER = {
    "Dorsal Space":        (397_350_611, 10_223),
    "Dura":                (142_857_955,  9_814),
    "Pia":                 (142_721_894,  9_839),
    "CSF":                 (118_161_757,  9_613),
    "Dura/Pia complex":    ( 57_124_376,  2_732),
    "Spinal cord":         (812_894_511, 10_223),
    "Hematoma":            ( 69_727_644,  5_756),
    "Dura/Ventral Complex":( 58_152_053,  2_671),
    "Ventral Space":       ( 89_571_059,  6_099),
    "Background":          ( 18_992_200,  6_385),
}

def main():
    masks = []
    for sp in ("train", "val", "test"):
        masks += sorted((ROOT / f"{sp}_masks").glob("*.png"))
    print(f"masks found: {len(masks)}", flush=True)

    px = collections.Counter()      # palette index -> pixel count
    imgs = collections.Counter()    # palette index -> images containing it
    unknown = collections.Counter()
    for i, p in enumerate(masks):
        a = np.asarray(Image.open(p).convert("RGB"))
        flat = a.reshape(-1, 3)
        # pack RGB into a single int for fast unique
        packed = (flat[:, 0].astype(np.int32) << 16) | (flat[:, 1].astype(np.int32) << 8) | flat[:, 2].astype(np.int32)
        vals, counts = np.unique(packed, return_counts=True)
        for v, c in zip(vals.tolist(), counts.tolist()):
            rgb = ((v >> 16) & 255, (v >> 8) & 255, v & 255)
            idx = LUT.get(rgb)
            if idx is None:
                unknown[rgb] += int(c); continue
            px[idx] += int(c); imgs[idx] += 1
        if (i + 1) % 1000 == 0:
            print(f"  {i+1}/{len(masks)}", flush=True)

    observed = {int(k): {"pixels": int(px[k]), "images": int(imgs[k])} for k in sorted(px)}
    # Match observed palette indices to paper classes by pixel count (unique enough)
    matched, used = {}, set()
    for name, (ppx, pimg) in PAPER.items():
        best, berr = None, None
        for k, v in observed.items():
            if k in used: continue
            err = abs(v["pixels"] - ppx) / ppx
            if berr is None or err < berr:
                best, berr = k, err
        matched[name] = {"palette_index": best, "observed": observed[best],
                         "paper": {"pixels": ppx, "images": pimg},
                         "pixel_rel_error": round(berr, 6),
                         "image_count_delta": observed[best]["images"] - pimg}
        used.add(best)

    res = {"n_masks": len(masks), "observed_by_palette_index": observed,
           "unknown_colours": {str(k): v for k, v in unknown.items()},
           "matched_to_paper_table1": matched}
    (OUT / "metrics.json").write_text(json.dumps(res, indent=2), encoding="utf-8")

    print(f"\n{'class':24s} {'idx':>3s} {'obs_pixels':>14s} {'paper_pixels':>14s} {'relerr':>8s} {'obs_imgs':>8s} {'paper_imgs':>10s}")
    for name, m in matched.items():
        print(f"{name:24s} {m['palette_index']:3d} {m['observed']['pixels']:14,d} "
              f"{m['paper']['pixels']:14,d} {m['pixel_rel_error']:8.4f} "
              f"{m['observed']['images']:8,d} {m['paper']['images']:10,d}")
    if unknown:
        print("\nUNKNOWN colours:", dict(list(unknown.items())[:10]))
    print(f"\nwrote {OUT/'metrics.json'}")

if __name__ == "__main__":
    main()
