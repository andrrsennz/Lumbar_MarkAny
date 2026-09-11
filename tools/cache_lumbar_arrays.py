#!/usr/bin/env python3
"""
cache_lumbar_arrays.py -- Pre-decode the lumbar frames into one memory-mapped
array pair at training resolution.

Reason: training was disk/decode bound, not GPU bound. Decoding 6,182 PNGs of
810x430 and max-pooling their masks every epoch cost ~138 s/epoch with the GPU
at 100% but starved; caching makes the epoch GPU-bound instead. This is a pure
performance change -- the cached content is bit-identical to what the on-the-fly
loader produced (verified by tools/verify_kuleuven_subset.py).
"""
from __future__ import annotations
import argparse, csv, pathlib, sys
import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from lumbar_markany.lumbar_data import load_index, resize_mask_max  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/processed/kuleuven_lumbar")
    ap.add_argument("--height", type=int, default=384)
    ap.add_argument("--width", type=int, default=192)
    a = ap.parse_args()
    root = pathlib.Path(a.root)
    rows = load_index(a.root)
    H, W = a.height, a.width
    n = len(rows)
    ximg = np.lib.format.open_memmap(root / f"cache_img_{H}x{W}.npy", mode="w+",
                                     dtype=np.uint8, shape=(n, H, W))
    xmsk = np.lib.format.open_memmap(root / f"cache_msk_{H}x{W}.npy", mode="w+",
                                     dtype=np.uint8, shape=(n, H, W))
    for i, r in enumerate(rows):
        im = Image.open(root / "images" / f"{r['uid']}.png").convert("L").resize((W, H), Image.BILINEAR)
        ximg[i] = np.asarray(im, dtype=np.uint8)
        m = np.asarray(Image.open(root / "masks" / f"{r['uid']}.png")) > 127
        xmsk[i] = resize_mask_max(m, (H, W)).astype(np.uint8)
        if (i + 1) % 1000 == 0:
            print(f"  {i+1}/{n}", flush=True)
    ximg.flush(); xmsk.flush()
    with open(root / f"cache_order_{H}x{W}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["row", "uid"])
        for i, r in enumerate(rows): w.writerow([i, r["uid"]])
    print(f"cached {n} frames at {H}x{W} -> {root}")


if __name__ == "__main__":
    main()
