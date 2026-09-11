# KU Leuven / Balgrist expert label audit

**Dataset:** `doi:10.48804/3XPCAE` (CC-BY-4.0) · **Paper:** `doi:10.1038/s41597-025-06047-9`
**Audited:** 2026-09-11, from the files themselves, not from the publication.

Machine-readable companion: `research/datasets/KULEUVEN_LABEL_COUNTS.csv`.

---

## 1. What we retrieved, and how

The V1 record stated this dataset was unreachable. **That was true of our
network and false as a statement about the dataset.** Corrected in full in
`research/datasets/V2_ACCESS_CORRECTION.md`.

* The live Dataverse (v6.7.1) returns a complete file listing: **766 files,
  630.94 GB, every one `restricted: false`**.
* We retrieved **41 files, 1.76 GB**, all MD5-verified against the checksums
  Dataverse publishes: the 18 `US_labels` archives, the 18 `US_recon`
  archives, and the metadata files.
* We did **not** need the 605 GB of per-subject raw scan archives, because
  **each label archive already contains the ultrasound frames themselves**
  (see §3).

## 2. Coverage: exactly nine subjects

| Subject | Scans held | Modalities | Notes |
|---|---|---|---|
| URS08 | H1, R2 | HUS + RUS | |
| URS16 | H3, R1 | HUS + RUS | |
| URS26 | H3, R1 | HUS + RUS | |
| URS31 | D2, R2 | **RUS only** | two robotic protocols, no handheld |
| URS36 | D2, H2 | HUS + RUS | |
| URS40 | H4, R1 | HUS + RUS | |
| URS45 | H2, R2 | HUS + RUS | |
| URS51 | D2, R2 | **RUS only** | two robotic protocols, no handheld |
| URS54 | D1, H3 | HUS + RUS | |

**Seven subjects with both handheld and robotic, two robotic-only** — matching
the publication's description exactly. Scan prefixes follow the paper's Data
Records convention: `H` handheld, `R` robotic "Perpendicular", `D` other
robotic protocols, `M` along-the-spinous-process.

## 3. Archive format (established by inspection)

```
<SUBJ>_<SCAN>/data_list.txt              tab-separated, with header
    #dataPath  labelPath  identifier  originalDataPath
    0.mhd  0-labels.mhd  hmUIBRpK91z8  US/URS08_H1/HUS/1055.png
<SUBJ>_<SCAN>/Labels/<n>.mhd + <n>.raw          the ultrasound frame
<SUBJ>_<SCAN>/Labels/<n>-labels.mhd + .raw      the expert annotation
```

* 2-D MetaImage, `DimSize = 1920 1080`, `ElementType = MET_UCHAR`,
  `CompressedData = True` (payload is raw zlib).
* Rows are stored **bottom-up**; frames must be flipped vertically or the
  anatomy appears inverted.
* **Channel count varies by subject.** URS08/16/26/54 store single-channel
  images; URS31/36/40/45/51 store the same B-mode content as RGB. We verified
  the three channels are **identical** in every RGB archive, so reduction to
  luminance is lossless. Labels are always single-channel.
* `originalDataPath` maps each annotated frame back to its source PNG in the
  full scan archive, so the annotated subset can be traced into the 605 GB
  deposit without downloading it.

## 4. Label semantics — read this before writing any caption

Label arrays contain **exactly two values**:

| value | meaning | typical share |
|---|---|---|
| 1 | background / not annotated | ~99.8% |
| 2 | **annotated bone surface** | ~0.1–0.6% |

There is **no** class for a puncture target, entry point, interspace,
trajectory, depth, or safety window. The annotation is a **thin contour along
visible bone surface**, typically 1–3 px wide.

> These are annotations of VISIBLE ANATOMY. Calling them puncture targets
> would be a fabrication. See `deliverables/paper/CLAIMS_NOT_ALLOWED.md`.

## 5. Frame counts — ours vs the publication

**This is the headline audit result, and the numbers do not match.**

| | HUS | RUS | total |
|---|---|---|---|
| Listed in `data_list.txt` (our count) | **2,382** | **3,800** | **6,182** |
| With a non-empty bone annotation (our count) | **2,322** | **3,676** | **5,998** |
| Reported in the publication | 2,353 | 3,738 | 6,091 |

The published figure (6,091) sits **between** our two defensible counts:
91 fewer than the frames actually listed, and 93 more than the frames that
actually carry an annotation. Neither counting rule reproduces it.

We do **not** assert an error in the publication. Plausible explanations
include a different deposit version, a different inclusion rule, or frames
excluded for reasons not visible in the released files. What we can state is
narrow and checkable: **from the published files, we count 6,182 listed and
5,998 annotated frames**, and every result in this project uses our counts,
not the paper's.

## 6. Empty labels are signal, not corruption

**184 of 6,182 frames (3.0%) carry a completely empty label** — the annotator
identified no bone surface at all.

They are concentrated, not uniform:

| Archive | frames | empty | % |
|---|---|---|---|
| URS08_R2 | 354 | 38 | 10.7% |
| URS16_R1 | 356 | 30 | 8.4% |
| URS51_D2 | 325 | 28 | 8.6% |
| URS26_R1 | 377 | 27 | 7.2% |
| URS16_H3 | 324 | 22 | 6.8% |
| URS26_H3 | 321 | 21 | 6.5% |
| URS08_H1 | 308 | 17 | 5.5% |
| URS31_D2 | 320 | 1 | 0.3% |
| *(10 others)* | | 0 | 0% |

Ten of eighteen archives contain **no** empty frames at all, while seven
contain 5–11%. That pattern looks like a change in annotation practice rather
than a property of the anatomy, and it matters: a model trained without those
frames never learns that "no bone visible" is a valid answer.

We keep them, train on them, and score them separately — Dice is undefined when
both prediction and truth are empty, so scoring them 0 or 1 would silently bias
any average.

## 7. Data-quality quirks found

1. **Stray annotation, URS16_H3 frame 304.** The label spans columns
   **556–1864**, straight across the scanner UI panel — 2,683 px. It cannot be
   anatomy; the live ultrasound sector ends at column 946. Our pipeline clips
   to the sector and records `label_px_outside_sector` rather than silently
   absorbing it (which would have dragged the crop across the whole display) or
   silently dropping the frame.
2. **Minor annotation overshoot.** Across archives, annotations reach columns
   534–957 while the speckle-derived sector is 548–946 in every archive. The
   outermost fan columns carry little temporal variance but were still drawn
   on. The applied crop covers this.
3. **Burned-in identifiers.** Raw frames include a scanner banner with the
   pseudonymous study ID (e.g. "ID: URS8") and the acquisition date. Our
   processed frames are cropped to the ultrasound sector, which removes this
   text from every derived asset.

## 8. Acquisition geometry

The frame grabber captured the entire 1920×1080 scanner display, not just the
image. Locating the live sector is therefore a prerequisite, and it is harder
than it sounds:

* Brightness thresholding **fails**. The right-hand UI panel is *brighter* than
  the ultrasound sector, and sector brightness itself swings with gain between
  scans (URS26_H3 averages ~41, URS08_R2 only ~24). Every absolute or
  percentile-scaled intensity cut we tried either swallowed the UI or collapsed
  a sector to 2 px wide. Both failures were observed and fixed.
* **Temporal standard deviation works perfectly.** Ultrasound speckle changes
  every frame; UI chrome, the depth ruler and the letterbox background are
  static and score **exactly 0**. This yields columns **548–946 in all 18
  archives** without tuning — confirming the display geometry is fixed and only
  imaged depth varies.

Applied crop: rows 150–960, columns 530–960 (**810 × 430**), uniform across
archives, covering all genuine annotations with margin.

## 9. What this does and does not give the project

**Gives us:** real human, in-vivo, transcutaneous lumbar ultrasound with expert
anatomical annotation, across 9 subjects and both acquisition modalities —
enough for a subject-level, cross-acquisition segmentation study.

**Does not give us:** anything procedural. No entry point, no trajectory, no
target depth, no interspace decision, no outcome. And the cohort remains
healthy volunteers aged 20–35 with BMI 19–26, imaged **prone** with a **10 MHz
linear** probe — not the difficult-LP population, not the neuraxial position,
not the neuraxial probe class.

That gap is now sharper, not smaller, and it is the subject of
`research/annotations/PUBLIC_VS_HOSPITAL_ANNOTATION_GAP.md`.
