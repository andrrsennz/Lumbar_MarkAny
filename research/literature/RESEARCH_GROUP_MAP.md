# Research group map

Groups identified from work we actually retrieved and read during this project.
**No group is listed because of institutional reputation**, and no connection
to any of them exists or is implied. Where we are unsure of a group's current
activity, we say so rather than inferring it.

---

## Directly relevant

### KU Leuven (Robot-Assisted Surgery group) + Balgrist University Hospital / University of Zurich
**The closest prior art to this project's acquisition concept.** *(E3)*

* Produced the only in-vivo human paired handheld/robotic lumbar ultrasound
  dataset with CT ground truth — 63 volunteers, 598 tracked sweeps, released
  CC-BY-4.0 (`doi:10.48804/3XPCAE`, *Scientific Data* 2025).
* Force-controlled robotic scanning demonstrated in humans: 5 N target contact,
  20 N maximum, 4 mm/s maximum velocity.
* Related: Li et al., *Robot-assisted ultrasound reconstruction for spine
  surgery: from bench-top to pre-clinical study* (IJCARS 2023,
  `10.1007/s11548-023-02932-z`); Van Assche et al., *Robotic path re-planning
  for US reconstruction of the spine* (IEEE TMRB 2025,
  `10.1109/TMRB.2025.3550662`).
* Funded in part by EU Horizon 2020 **FAROS** (grant 101016985).

**Relevance:** they have solved robot-acquired lumbar ultrasound. They have not
connected it to a clinician-authored procedural target layer. That gap is this
project's thesis, and it is a gap we should be explicit about publicly —
building *on* their released data is the intended relationship, not competition.

### Balgrist / ETH Zurich — ultrasound bone-surface segmentation
* **UltraBones100k** (Wu et al., *Comput Biol Med* 2025;
  `10.1016/j.compbiomed.2025.110435`, arXiv:2502.03783): ~100k ex-vivo human
  lower-limb ultrasound images with **automatically generated**, physics-refined
  bone labels derived from CT registration, reviewed by an orthopaedic
  sonography expert.
* Follow-on work: *UltraBoneUDF* (neural unsigned distance fields for bone
  surface reconstruction), *NeuralBoneReg* (label-free multi-modal bone surface
  registration), and *ExiL* (expert-in-the-loop mask-conditioned progressive
  learning, reporting a reduction in expert annotation time from ~60 s to ~20 s
  per frame). *(E3, arXiv abstracts)*

**Relevance — and this is the most directly transferable idea we found.** Our
binding constraint is clinician annotation time. This group's entire research
line is about *not* depending on manual labels: automated CT-derived labelling
at scale, and expert-in-the-loop refinement that cuts per-frame annotation cost
by roughly two thirds. If the hospital pilot shows that per-frame annotation is
too slow to scale — which is our stated highest-likelihood risk — this is the
literature to adopt rather than re-derive.

### Johns Hopkins University — HEPIUS lab
* Released the largest annotated spinal-cord ultrasound dataset (10,223 porcine
  images, 10 anatomical classes, plus an 8-patient human test subset), with
  benchmarks across YOLOv8, DeepLabv3, SegFormer, U-Net, TransUNet, Swin-UNet
  and SAMed *(E3, PMC12475011)*.
* Two-stage clinical annotation review (radiologist adjudication, then
  neurosurgery spine fellow validation) — **the most rigorous annotation
  process we found in this field**, and the model we propose to adopt.
* Broader programme in implantable/wearable ultrasound for spinal cord injury
  monitoring.

**Relevance:** their data is the engineering substrate for all our executed
work, and their annotation protocol is the template for the hospital pilot.
Note that their release carries **no licence**, which is itself a lesson for
how we publish.

### Concordia University (IMPACT / PERFORM Centre)
* Multimodal US–CT spine registration benchmark with landmark ground truth
  (`10.5281/zenodo.4813508`, CC-BY-4.0) *(E2)*.

**Relevance:** a registration testbed. Its human subjects have only
*CT-simulated* ultrasound, which is itself evidence of how scarce real spine
ultrasound is.

## Adjacent, identified through the literature survey

* **TUM (Computer Aided Medical Procedures)** — robotic ultrasound, ultrasound
  confidence maps, and registration-based motion compensation. Jiang et al.,
  *Precise repositioning of robotic ultrasound… using ultrasound confidence
  optimization* (IEEE TIM), is cited by the anchor publication *(E3)*. **Their
  confidence-driven repositioning is the nearest published work to the
  "quality-driven re-acquisition" idea in our architecture** — it must be read
  carefully before we describe that idea as novel.
* **Hong Kong PolyU and collaborators** — 3D/freehand spine ultrasound for
  scoliosis assessment and spine curvature measurement; volume projection
  imaging *(E3)*.
* **UBC / Vancouver groups** — phase-based bone surface localisation in
  ultrasound and automatic lumbar level identification; among the earliest work
  in this space (2008–2010) *(E3)*.

## Deliberately not listed

Institutions frequently named in AI-for-medicine discussions but for which this
survey surfaced **no directly relevant lumbar/spinal ultrasound work** are
omitted. Listing them would pad the document and imply a landscape we did not
observe.

## How this map should be used

1. **Read before claiming novelty.** Items in the "directly relevant" section —
   particularly TUM's confidence-driven repositioning and the Balgrist automated
   labelling line — overlap with ideas in our architecture. Any novelty claim
   must be made *after* reading them, not before.
2. **Prefer building on released data and methods over re-deriving them.** The
   KU Leuven dataset is CC-BY and was released specifically to be used.
3. **Adopt the annotation practices that are already better than ours** — the
   JHU two-stage review, and the Balgrist annotation-efficiency work.

## Limitations of this map

Assembled from a single-day literature harvest (442 Europe PMC records across
20 categories) plus the reference lists of the two anchor publications. It is
biased toward groups that publish in indexed venues and release data. Groups
working in this area without recent indexed output, or publishing primarily in
conference proceedings that Europe PMC indexes poorly (much of the medical
robotics literature sits in IEEE venues), will be under-represented.
