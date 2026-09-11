"""Reader for the KU Leuven / Balgrist lumbar spine ultrasound label archives.

Dataset: doi:10.48804/3XPCAE (CC-BY-4.0)
Paper:   doi:10.1038/s41597-025-06047-9

ARCHIVE FORMAT (established by inspecting the files, not assumed)
-----------------------------------------------------------------
Each `US/US_labels/<SUBJ>_<SCAN>.zip` is self-contained:

    <SUBJ>_<SCAN>/data_list.txt          tab-separated mapping, with header
                                         #dataPath  labelPath  identifier  originalDataPath
    <SUBJ>_<SCAN>/Labels/<n>.mhd|.raw        the ultrasound frame
    <SUBJ>_<SCAN>/Labels/<n>-labels.mhd|.raw the expert annotation

Both are 2-D MetaImage: `NDims = 2`, `DimSize = 1920 1080`, `ElementType =
MET_UCHAR`, single channel, `CompressedData = True` (raw payload is zlib).
Note DimSize is (width height), so the array is reshaped to (1080, 1920).

LABEL SEMANTICS -- verified across all 18 archives, not assumed
---------------------------------------------------------------
    2 = annotated BONE SURFACE, in EVERY archive
    background = 0 in six archives (URS08_R2, URS16_H3, URS16_R1, URS26_H3,
                 URS26_R1, URS31_D2) and 1 in the other twelve.

The background value is therefore NOT consistent across the deposit, and no
frame ever mixes 0 and 1. Consequences for anyone reading these files:

    mask = (label != 0)   -> 100% false positives on the twelve archives
                             whose background is 1
    mask = (label == 1)   -> empty on those same twelve, and wrong on the rest
    mask = (label == 2)   -> CORRECT everywhere

Typically ~0.08% of pixels carry value 2, consistent with a thin surface
contour rather than a filled region.

These are annotations of VISIBLE BONE SURFACE. They are NOT lumbar-puncture
targets, entry points, trajectories, or any procedural label. See
deliverables/paper/CLAIMS_NOT_ALLOWED.md.

SCAN NAMING (from the publication's Data Records section)
--------------------------------------------------------
    H<n>  handheld ultrasound (HUS)
    R<n>  robotic, "Perpendicular" protocol (RUS)
    D<n>  robotic, all other protocols except along-spinous-process (RUS)
    M<n>  robotic, "along the spinous process" (RUS)
"""
from __future__ import annotations

import re
import zipfile
import zlib
from dataclasses import dataclass

import numpy as np

BACKGROUND = 1
BONE_SURFACE = 2

# scan-prefix -> acquisition modality
MODALITY = {"H": "HUS", "R": "RUS", "D": "RUS", "M": "RUS"}
# finer protocol family, kept separate because R/D/M are different robot protocols
PROTOCOL = {"H": "handheld", "R": "robotic_perpendicular",
            "D": "robotic_other", "M": "robotic_along_spinous"}


def parse_mhd(text: str) -> dict:
    out = {}
    for line in text.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


@dataclass(frozen=True)
class FrameRef:
    subject: str          # e.g. URS08
    scan: str             # e.g. H1
    modality: str         # HUS | RUS
    protocol: str
    index: int            # n in <n>.mhd
    data_path: str        # <n>.mhd
    label_path: str       # <n>-labels.mhd
    identifier: str       # dataset's own opaque id
    original_path: str    # e.g. US/URS08_H1/HUS/1055.png
    original_frame: int   # 1055

    @property
    def uid(self) -> str:
        return f"{self.subject}_{self.scan}_f{self.index:04d}"


class LabelArchive:
    """One `US_labels/<SUBJ>_<SCAN>.zip`."""

    def __init__(self, path):
        self.path = str(path)
        self.zip = zipfile.ZipFile(self.path)
        names = self.zip.namelist()
        root = sorted({n.split("/")[0] for n in names if "/" in n})
        if len(root) != 1:
            raise ValueError(f"unexpected archive roots {root} in {path}")
        self.root = root[0]
        self.subject, self.scan = self.root.split("_", 1)
        self.modality = MODALITY.get(self.scan[0], "UNKNOWN")
        self.protocol = PROTOCOL.get(self.scan[0], "unknown")
        self.frames = self._read_list()

    def _read_list(self) -> list[FrameRef]:
        txt = self.zip.read(f"{self.root}/data_list.txt").decode("utf-8", "replace")
        refs = []
        for line in txt.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            data, label, ident, orig = parts[:4]
            m = re.match(r"(\d+)\.mhd$", data)
            if not m:
                continue
            fm = re.search(r"(\d+)\.png$", orig)
            refs.append(FrameRef(
                subject=self.subject, scan=self.scan, modality=self.modality,
                protocol=self.protocol, index=int(m.group(1)),
                data_path=data, label_path=label, identifier=ident,
                original_path=orig, original_frame=int(fm.group(1)) if fm else -1,
            ))
        refs.sort(key=lambda r: r.index)
        return refs

    def _read_meta(self, stem: str, want_gray: bool = True) -> np.ndarray:
        """Decode one MetaImage pair.

        Frames are stored bottom-up, so the array is flipped to normal display
        orientation (skin/near-field at the top).

        Channel count varies BY SUBJECT: URS08/16/26/54 store single-channel
        images, while URS31/36/40/45/51 store the same B-mode content as RGB.
        Labels are always single-channel. RGB frames are reduced to luminance;
        for genuine B-mode content the three channels are identical, and the
        conversion is verified in tools/verify_kuleuven_subset.py.
        """
        head = parse_mhd(self.zip.read(f"{self.root}/Labels/{stem}.mhd").decode("utf-8", "replace"))
        w, h = (int(x) for x in head["DimSize"].split())
        if head.get("ElementType") != "MET_UCHAR":
            raise ValueError(f"unexpected ElementType {head.get('ElementType')}")
        ch = int(head.get("ElementNumberOfChannels", 1))
        payload = self.zip.read(f"{self.root}/Labels/{head.get('ElementDataFile', stem + '.raw')}")
        if head.get("CompressedData", "False").lower() == "true":
            payload = zlib.decompress(payload)
        a = np.frombuffer(payload, dtype=np.uint8)
        if a.size != w * h * ch:
            raise ValueError(f"size mismatch for {stem}: {a.size} != {w*h*ch}")
        a = a.reshape(h, w, ch) if ch > 1 else a.reshape(h, w)
        if ch > 1 and want_gray:
            a = a.max(axis=2)          # channels are identical for B-mode
        return np.flipud(a).copy()

    @property
    def n_channels(self) -> int:
        head = parse_mhd(self.zip.read(f"{self.root}/Labels/0.mhd").decode("utf-8", "replace"))
        return int(head.get("ElementNumberOfChannels", 1))

    def image(self, ref: FrameRef) -> np.ndarray:
        return self._read_meta(ref.data_path[:-4])

    def label(self, ref: FrameRef) -> np.ndarray:
        return self._read_meta(ref.label_path[:-4])

    def bone_mask(self, ref: FrameRef) -> np.ndarray:
        """Boolean mask of annotated bone surface."""
        return self.label(ref) == BONE_SURFACE

    def __len__(self):
        return len(self.frames)

    def __repr__(self):
        return (f"<LabelArchive {self.subject}_{self.scan} "
                f"{self.modality}/{self.protocol} frames={len(self.frames)}>")
