# Image attribution

Copy-ready attribution for every external visual source used in this project.
Per-asset detail is in `ANNOTATION_PROVENANCE.csv`; licence verification is in
`PIXEL_LICENSE_LEDGER.csv`.

---

## KU Leuven / Balgrist lumbar spine ultrasound — the only image source we redistribute

**All real human lumbar ultrasound frames and expert annotations in this
package come from this dataset.**

> Cavalcanti NA, Li R, Arango L, Davoodi A, Van Assche K, Ao Y, Massalimova A,
> Salehi M, Zingg L, Götschi T, Borghesan G, Laux CJ, Sutter R, Farshad M,
> Tummers M, Fürnstahl P, Vander Poorten E, Carrillo F.
> *A large, paired dataset of robotic and handheld lumbar spine ultrasound with
> ground-truth CT benchmarking.*
> KU Leuven Research Data Repository, 2024. **doi:10.48804/3XPCAE**.
> Licensed under **CC-BY-4.0**.
>
> Accompanying publication: *Scientific Data*, 2025.
> **doi:10.1038/s41597-025-06047-9**.

**Short form for figure captions:**

> Ultrasound and expert bone-surface annotation: Cavalcanti et al.,
> doi:10.48804/3XPCAE, CC-BY-4.0.

**For derived panels (overlays, predictions, error and uncertainty maps):**

> Ultrasound and expert annotation from Cavalcanti et al., doi:10.48804/3XPCAE
> (CC-BY-4.0). Segmentation predictions, error and uncertainty maps produced by
> the Lumbar_MarkAny project.

**What we changed, and why it must be stated:** frames were decoded from
MetaImage, flipped vertically (the source stores rows bottom-up), and cropped to
the live ultrasound sector — which removes the scanner UI, the depth ruler and
the burned-in study-ID/date banner. Overlay masks are dilated by 1–2 px for
visibility; **metrics are always computed on the undilated mask.**

**The one thing no caption may say.** These annotations mark
**visible bone surface** (label value 2 of {1, 2}). They are not puncture
targets, entry points, trajectories, interspace choices or safety windows, and
describing them as such would be a fabrication.

---

## Sources cited but NOT redistributed

### SUID — Spine Ultrasound Image Dataset (First Hospital of Putian)

> Lin et al. *An adaptive attention U-network for recognizing ultrasound
> images.* Journal of International Medical Research, 2026.
> **doi:10.1177/03000605261461196** (PMC13328980). Article licensed
> **CC BY-NC 4.0**.

**No pixel from this source appears in this repository or the evidence
package.** The dataset itself is not released — the authors state it is "not
publicly available due to patient consent agreements and ethical restrictions".
The article's own figures are reusable **non-commercially with attribution**,
but we cite rather than copy, and its data is **not** training data for us.

### Johns Hopkins HEPIUS porcine spinal cord ultrasound

> Kumar A, et al. *A novel open-source ultrasound dataset with deep learning
> benchmarks for spinal cord injury localization and anatomical segmentation.*
> PMC12475011.

**No pixel redistributed.** Neither the GitHub repository nor the distributed
archives declare a licence, and absence of a licence is not permission. Used
locally for exp001–exp004 (secondary methodological evidence); numbers computed
from it are our own work and are reported freely.

### Masoumi multimodal spine US/CT

> Masoumi N, Belasso C, Ahmad MO, Benali H, Xiao Y, Rivaz H. *Multimodal 3D
> ultrasound and CT in image-guided spinal surgery: public database and new
> registration algorithms.* Zenodo, **doi:10.5281/zenodo.4813508**, CC-BY-4.0.

Redistributable in principle, but not included: its three human subjects have
**CT-simulated** ultrasound only, so it adds no real human ultrasound evidence.

---

## Assets produced entirely by this project

Contact sheets, composite panels, error maps, uncertainty maps and figure
candidates are our own derivative works over CC-BY-4.0 material. They inherit
CC-BY-4.0 and carry the attribution above. Code is MIT.
