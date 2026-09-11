# Data access request templates

For datasets that are real, relevant and **request-only**. These are drafts for
a human to send — nothing here has been sent, and no correspondence has taken
place.

**Send nothing without the PI's approval.** An access request creates an
obligation and a record; it is not a background task.

---

## 1. SUID — Spine Ultrasound Image Dataset (First Hospital of Putian)

**Why this one matters most.** It is the closest public-literature dataset to
our actual clinical target: 80 pregnant women undergoing caesarean under
ultrasound-guided intraspinal anaesthesia, imaged in **lateral decubitus** with
a **2–5 MHz convex probe**, annotated for **interlaminar spaces, articular
processes, and anterior/posterior complex**. That is the correct cohort, the
correct position, the correct probe class, and a more procedurally relevant
label set than anything we hold.

**Status:** not public. The authors state the data is "not publicly available
due to patient consent agreements and ethical restrictions. Requests for access
to the data should be directed to the corresponding author."

**Realistic expectation:** patient-consent restrictions are a genuine barrier,
not a formality. A refusal is likely and would be entirely reasonable. A
federated or model-sharing arrangement may be more achievable than data
transfer, and is worth offering explicitly.

> **Subject:** Access request — Spine Ultrasound Image Dataset (SUID), J Int Med Res 2026
>
> Dear Dr [corresponding author],
>
> I am writing about your paper *An adaptive attention U-network for
> recognizing ultrasound images* (J Int Med Res, 2026;
> doi:10.1177/03000605261461196), and the Spine Ultrasound Image Dataset it
> describes.
>
> We are a research group developing AI-assisted lumbar ultrasound
> interpretation for neuraxial access, in preparation for a collaboration with
> an Indonesian hospital. Our work so far uses the publicly released KU Leuven /
> Balgrist lumbar dataset (doi:10.48804/3XPCAE). That dataset is valuable but
> was acquired **prone, with a 10 MHz linear probe, in healthy volunteers aged
> 20–35** — a configuration quite unlike neuraxial practice. Your cohort,
> patient positioning, probe class and annotated structures are much closer to
> the clinical reality we need to model.
>
> We note your data availability statement, and we understand that patient
> consent and ethical restrictions may make sharing impossible. We would be
> grateful to know whether any of the following is feasible:
>
> 1. access to de-identified images under a data-use agreement, for
>    non-commercial research, with your institution's ethics approval;
> 2. access to a small subset sufficient for external validation only;
> 3. **a federated arrangement in which you retain the data entirely** and we
>    share model weights and an evaluation script for you to run locally;
> 4. if none of the above, simply your guidance on the annotation protocol and
>    class definitions, which would help us align our schema with clinical
>    practice.
>
> We would of course cite your work, and we are happy to discuss co-authorship
> if any collaboration develops. If the answer is no, that is completely
> understood and we will not follow up.
>
> With thanks and regards,
> [name, affiliation, contact]

---

## 2. UltraBones100k (Balgrist / ETH Zurich)

**Why:** ~100,000 ex-vivo human ultrasound images with bone labels generated
**automatically** from CT registration. Lower limb, not spine — so the *data*
is not directly useful to us, but the **method** is: our binding constraint is
clinician annotation time, and this group's entire research line is about not
depending on manual labels.

**Status:** availability unconfirmed; no public download located.

> **Subject:** UltraBones100k availability, and automated bone labelling for spine ultrasound
>
> Dear Dr Wu and colleagues,
>
> We are working on bone-surface perception in lumbar ultrasound, using your
> group's publicly released lumbar dataset (Cavalcanti et al.,
> doi:10.48804/3XPCAE) — thank you for making it available; it is the only
> public source of real human transcutaneous lumbar ultrasound with expert
> annotation that we were able to find.
>
> We are writing about *UltraBones100k* (Comput Biol Med 2025;
> doi:10.1016/j.compbiomed.2025.110435). We could not locate a public download
> and would like to ask (a) whether the dataset is or will be available, and
> (b) whether your automated CT-derived labelling pipeline has been applied, or
> could be applied, to spine data.
>
> Our motivation is practical. The lumbar deposit's annotated subset covers
> nine subjects and was labelled by a single annotator, so manual annotation is
> clearly the bottleneck for scaling. Your approach appears to be the most
> promising route past it, and we would rather build on it than re-derive it.
>
> With thanks and regards,
> [name, affiliation, contact]

---

## 3. Contacting the KU Leuven / Balgrist authors — courtesy, not access

No request is needed: the dataset is CC-BY-4.0 and we hold it. But two things
are worth reporting back, and doing so is good practice.

> **Subject:** Notes from using doi:10.48804/3XPCAE — two small findings
>
> Dear Dr Cavalcanti and colleagues,
>
> Thank you for releasing this dataset. We have been using the `US_labels`
> archives and wanted to share two observations that other users may hit.
>
> 1. **Background label value is not consistent across archives.** Six archives
>    (URS08_R2, URS16_H3, URS16_R1, URS26_H3, URS26_R1, URS31_D2) encode
>    background as 0; the other twelve use 1. Bone surface is 2 throughout, so
>    `label == 2` is correct everywhere, but `label != 0` produces a fully
>    positive mask on the twelve archives that use 1.
>
> 2. **Frame counts.** Parsing every `data_list.txt` we count 6,182 listed
>    frames (2,382 HUS / 3,800 RUS), of which 5,998 carry a non-empty
>    annotation. The publication reports 6,091. We may well be applying a
>    different inclusion rule from yours and would be glad to know which is
>    intended.
>
> We are also happy to report that the annotated subset is entirely
> self-contained — the label archives include the frames themselves — which
> made it possible to work with 1.7 GB rather than the full deposit. That is a
> very practical design and worth highlighting to users.
>
> With thanks and regards,
> [name, affiliation, contact]

---

## Rules for any request sent from this project

1. **State what we already have.** Nobody should be asked for something we
   could have obtained ourselves.
2. **Offer the federated option.** For patient data, "you keep the data, we
   send the model" is often the only feasible route and should be offered
   before it is requested of us.
3. **Accept a refusal in the first reply.** No second ask.
4. **Never imply approval we do not have** — no hospital, ethics committee or
   collaborator may be named as a partner before a written agreement exists.
5. **Record the outcome** in `DATASET_REGISTRY.csv`, including refusals and
   silence, so the availability record stays accurate.
