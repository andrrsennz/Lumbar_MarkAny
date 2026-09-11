"""Dataset + palette decoding for the JHU porcine spinal-cord ultrasound release.

The public release ships RGB masks using the PASCAL-VOC colour palette but does
NOT document which palette index corresponds to which anatomical class. The
mapping below was recovered empirically in experiments/exp002_class_distribution
by matching per-class pixel totals against Table 1 of the source publication;
all ten classes matched exactly (relative error 0.0000).
"""
from __future__ import annotations
import pathlib, numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset

# palette index -> class name  (recovered, see exp002)
CLASSES = {
    0: "Background",
    1: "Dura",
    2: "Pia",
    3: "CSF",
    4: "Spinal cord",
    5: "Dorsal Space",
    6: "Hematoma",
    7: "Ventral Space",
    8: "Dura/Pia complex",
    9: "Dura/Ventral Complex",
}
N_CLASSES = 10


def voc_palette(n: int = 256) -> np.ndarray:
    pal = np.zeros((n, 3), dtype=np.uint8)
    for i in range(n):
        r = g = b = 0
        c = i
        for j in range(8):
            r |= ((c >> 0) & 1) << (7 - j)
            g |= ((c >> 1) & 1) << (7 - j)
            b |= ((c >> 2) & 1) << (7 - j)
            c >>= 3
        pal[i] = (r, g, b)
    return pal


_PAL = voc_palette()
# 24-bit packed RGB -> index lookup (fast, exact)
_LUT = np.zeros(1 << 24, dtype=np.uint8)
for _i in range(256):
    _r, _g, _b = (int(x) for x in _PAL[_i])
    _LUT[(_r << 16) | (_g << 8) | _b] = _i


def decode_mask(path) -> np.ndarray:
    """RGB VOC-palette PNG -> (H, W) uint8 class-index array."""
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.uint32)
    packed = (a[..., 0] << 16) | (a[..., 1] << 8) | a[..., 2]
    return _LUT[packed]


class JHUSpinalSeg(Dataset):
    """Official train/val/test split of the JHU segmentation release."""

    def __init__(self, root, split: str, size=(144, 352), augment: bool = False):
        self.root = pathlib.Path(root)
        self.split = split
        self.size = size                     # (H, W)
        self.augment = augment
        img_dir = self.root / f"{split}_images"
        msk_dir = self.root / f"{split}_masks"
        self.items = []
        for ip in sorted(img_dir.glob("*.png")):
            mp = msk_dir / ip.name
            if mp.exists():
                self.items.append((ip, mp))
        if not self.items:
            raise RuntimeError(f"no paired images found for split={split} under {root}")

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        ip, mp = self.items[i]
        H, W = self.size
        img = Image.open(ip).convert("L").resize((W, H), Image.BILINEAR)
        x = np.asarray(img, dtype=np.float32) / 255.0
        m = decode_mask(mp)
        m = np.asarray(Image.fromarray(m).resize((W, H), Image.NEAREST), dtype=np.int64)

        if self.augment:
            rng = np.random
            if rng.rand() < 0.5:                       # rostral-caudal flip
                x = x[:, ::-1].copy(); m = m[:, ::-1].copy()
            if rng.rand() < 0.5:                       # mild gain/brightness jitter
                x = np.clip(x * rng.uniform(0.85, 1.15) + rng.uniform(-0.08, 0.08), 0, 1)
            if rng.rand() < 0.3:                       # mild speckle-ish noise
                x = np.clip(x + rng.normal(0, 0.02, x.shape).astype(np.float32), 0, 1)

        return (torch.from_numpy(x.astype(np.float32))[None],
                torch.from_numpy(m),
                ip.name)
