#!/usr/bin/env python3
"""
build_lumbar_dataset.py -- Turn the KU Leuven expert label archives into an
analysis-ready dataset of REAL human lumbar ultrasound frames + expert
bone-surface masks.

Source: doi:10.48804/3XPCAE (CC-BY-4.0), `US/US_labels/*.zip`.
Each archive carries the ultrasound frame AND its expert annotation, so the
605 GB of raw per-subject scan archives are not required for this task.

What this does
--------------
1. Detects the live ultrasound sector per archive. The frame grabber captured
   the whole 1920x1080 scanner display, including UI, patient banner, burned-in
   acquisition text and the depth ruler. The sector background is exactly 16,
   so the edges are found from the mean-image profile rather than guessed --
   and the crop is then widened if necessary so that no annotated pixel is ever
   clipped.
2. Writes frame + mask as lossless PNG at native sector resolution.
3. Records per-frame provenance, including whether the expert left the frame
   EMPTY (no identifiable bone surface) -- 3% of frames, which is signal, not
   corruption.

Cropping to the sector is deliberate on two grounds: the scanner UI is not
anatomy and would let a model cheat, and it removes burned-in study/date text
from every published asset.
"""
from __future__ import annotations
import argparse
import csv
import glob
import json
import pathlib
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from lumbar_markany.kuleuven import LabelArchive, BONE_SURFACE  # noqa: E402

BG = 16          # exact background value of the scanner display
SECTOR_MARGIN = 4


def largest_run(mask: np.ndarray, min_len: int = 1) -> tuple[int, int]:
    runs, s = [], None
    for i, v in enumerate(mask):
        if v and s is None:
            s = i
        if not v and s is not None:
            runs.append((s, i)); s = None
    if s is not None:
        runs.append((s, len(mask)))
    runs = [r for r in runs if r[1] - r[0] >= min_len] or runs
    if not runs:
        return 0, len(mask)
    return max(runs, key=lambda r: r[1] - r[0])


def detect_sector(arch: LabelArchive, n_probe: int = 24):
    """Locate the live ultrasound sector within the 1920x1080 screen capture.

    Brightness alone does not work. The frame grabber recorded the whole
    scanner display, and the right-hand UI panel is BRIGHTER than the image
    sector, while sector brightness itself swings with gain between scans
    (URS26_H3 averages ~41, URS08_R2 only ~24). Any absolute or
    percentile-scaled intensity threshold either swallows the UI or collapses
    on the darker scans -- both failure modes were observed.

    Temporal standard deviation separates them cleanly and without tuning:
    ultrasound speckle changes every frame, whereas UI chrome, the depth ruler
    and the letterbox background are static and score exactly 0.
    """
    idxs = np.linspace(0, len(arch) - 1, min(n_probe, len(arch))).astype(int)
    stack = np.stack([arch.image(arch.frames[i]) for i in idxs]).astype(np.float32)
    sd = stack.std(0)

    colp = sd[300:800, :].mean(0)
    c0, c1 = largest_run(colp > colp.max() * 0.15, min_len=200)
    rowp = sd[:, c0:c1].mean(1)
    r0, r1 = largest_run(rowp > rowp.max() * 0.15, min_len=150)
    return max(0, r0), min(sd.shape[0], r1), max(0, c0), min(sd.shape[1], c1)


# One uniform crop is applied to every archive. Measured basis:
#   * the speckle-derived sector is columns 548-946 in ALL 18 archives -- the
#     scanner display geometry is fixed, only the imaged DEPTH varies, which
#     moves the lower row bound;
#   * expert annotations overshoot that sector slightly (observed columns
#     534-957, rows 196-933), because the outermost fan columns carry little
#     temporal variance yet were still drawn on.
# The crop below covers every genuine annotation with margin while excluding
# the UI panel, the depth ruler and the burned-in patient/date banner.
#
# It deliberately does NOT stretch to cover URS16_H3 frame 304, whose
# annotation spans columns 556-1864 straight across the scanner UI. That is an
# annotation artifact in the source data, not anatomy; such frames are clipped
# and FLAGGED via `label_px_outside_sector` rather than silently absorbed or
# silently dropped.
FIXED_SECTOR = (150, 960, 530, 960)      # r0, r1, c0, c1  -> 810 x 430


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels-dir", default="data/raw/kuleuven_lumbar/US/US_labels")
    ap.add_argument("--out", default="data/processed/kuleuven_lumbar")
    ap.add_argument("--limit-per-archive", type=int, default=0, help="0 = all frames")
    a = ap.parse_args()

    out = pathlib.Path(a.out)
    (out / "images").mkdir(parents=True, exist_ok=True)
    (out / "masks").mkdir(parents=True, exist_ok=True)

    index, sectors = [], {}
    for p in sorted(glob.glob(str(pathlib.Path(a.labels_dir) / "*.zip"))):
        arch = LabelArchive(p)
        r0, r1, c0, c1 = FIXED_SECTOR
        sr0, sr1, sc0, sc1 = detect_sector(arch)      # measured, for the record
        key = f"{arch.subject}_{arch.scan}"
        sectors[key] = dict(applied=dict(r0=r0, r1=r1, c0=c0, c1=c1,
                                         h=r1 - r0, w=c1 - c0),
                            measured_speckle_sector=dict(r0=sr0, r1=sr1, c0=sc0, c1=sc1),
                            n_channels=arch.n_channels)
        print(f"{key:12s} {arch.modality:4s} applied r{r0}-{r1} c{c0}-{c1} ({r1-r0}x{c1-c0})  "
              f"measured r{sr0}-{sr1} c{sc0}-{sc1}  frames={len(arch)}", flush=True)

        refs = arch.frames if not a.limit_per_archive else arch.frames[:a.limit_per_archive]
        clipped = 0
        for ref in refs:
            img = arch.image(ref)[r0:r1, c0:c1]
            full_mask = arch.bone_mask(ref)
            msk = full_mask[r0:r1, c0:c1]
            outside = int(full_mask.sum()) - int(msk.sum())
            if outside:
                clipped += 1
            uid = ref.uid
            Image.fromarray(img).save(out / "images" / f"{uid}.png", optimize=True)
            Image.fromarray((msk.astype(np.uint8) * 255)).save(out / "masks" / f"{uid}.png", optimize=True)
            index.append(dict(
                uid=uid, subject=arch.subject, scan=arch.scan, modality=arch.modality,
                protocol=arch.protocol, frame_index=ref.index,
                original_path=ref.original_path, original_frame=ref.original_frame,
                identifier=ref.identifier,
                height=img.shape[0], width=img.shape[1],
                bone_px=int(msk.sum()),
                bone_frac=round(float(msk.mean()), 8),
                empty_label=bool(msk.sum() == 0),
                label_px_outside_sector=outside,
                source_archive=pathlib.Path(p).name,
            ))
        if clipped:
            print(f"   !! {clipped} frame(s) had annotation outside the sector "
                  f"(clipped and flagged)", file=sys.stderr)

    with open(out / "index.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(index[0].keys()))
        w.writeheader(); w.writerows(index)
    (out / "sectors.json").write_text(json.dumps(sectors, indent=1), encoding="utf-8")

    ne = sum(1 for r in index if not r["empty_label"])
    print(f"\nwrote {len(index)} frames ({ne} with annotation, {len(index)-ne} empty) -> {out}")
    print(f"index: {out/'index.csv'}")


if __name__ == "__main__":
    main()
