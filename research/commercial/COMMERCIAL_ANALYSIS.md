# Commercial analysis

> **No prices, market sizes, or revenue figures appear in this document.** We
> performed no market research, and any number would be invented. What follows
> is qualitative reasoning from verified facts about the regulatory and product
> landscape *(E4)* and from the published literature *(E3)*, plus clearly
> labelled inference *(E5)*.

---

## 1. Who would buy this

| Setting | Procedure | Why they might care | Why they might not |
|---|---|---|---|
| **Obstetric anaesthesia** | labour epidural, CSE, spinal for caesarean | Highest volume of difficult neuraxial access; high BMI prevalence; time pressure; strong existing culture of pre-procedural ultrasound | Throughput is everything — a robot that adds setup time is dead on arrival |
| **General anaesthesia** | spinal for orthopaedic/urology | Elderly, degenerative, post-surgical spines | Often proceeds fine by landmark; ultrasound used selectively |
| **Emergency medicine** | diagnostic LP | Urgency, uncooperative patients, no elective rescheduling | Least tolerant of setup time; most space-constrained |
| **Neurology** | diagnostic and therapeutic LP, intrathecal therapy | Repeat punctures in the same patient make reproducibility genuinely valuable | Lower volume |
| **Interventional radiology** | fluoroscopy-guided rescue LP | Currently the escalation path — a successful device *reduces* their referrals | Misaligned incentive; treat as a stakeholder, not a customer |
| **Simulation / training centres** | teaching neuraxial technique | No patient risk; tolerant of imperfect systems; a credible early revenue path | Lower willingness to pay; not a clinical validation route |

**The most likely beachhead is obstetric anaesthesia** *(E5)*: it concentrates
the difficult-anatomy population, already uses pre-procedural ultrasound, and
has enough procedure volume to justify capital equipment in a single location.

**But the strongest counter-argument sits in the same row of the table.** A
robotic acquisition step that adds even a few minutes of setup is unlikely to
survive in a busy obstetric unit, and we have made no measurement of setup
time because no hardware exists. **Workflow time is the primary commercial
risk, and it is currently unquantified.** It should be measured on a phantom
mock-up long before any hardware is committed to.

## 2. Is lumbar puncture the right beachhead at all?

Argued both ways, honestly.

**For LP specifically:** a narrow intended use is the cheapest regulatory path
and the clearest clinical story. Diagnostic LP in difficult patients is a real,
recognised problem with an existing escalation pathway (fluoroscopy) that is
expensive and irradiating.

**Against:** the addressable volume for *difficult* diagnostic LP alone may be
too small to support capital equipment, and the same perception and acquisition
stack applies to epidural and spinal anaesthesia, which are far higher volume.

**Resolution:** develop the platform so that neuraxial access generally is
reachable, but **claim only what has been validated.** Do not silently broaden
the intended use — that is both a regulatory problem and the kind of drift that
`CLAIMS_NOT_ALLOWED.md` exists to prevent. Broadening indication is a
deliberate, evidenced decision, not a marketing choice.

## 3. Competitive position

From the verified landscape *(E4, `COMPETITOR_MATRIX.csv`)*: Rivanna holds
seven Accuro-family 510(k) clearances spanning 2014–2026, including two needle
guide kits. The segment is commercially live and actively iterating.

**We would not win on landmark detection.** Automated lumbar landmark
identification has been published since 2008 *(E3)* and shipped since 2014
*(E4)*. A better classifier is not a business.

**The one structural gap is that every cleared device is handheld** *(E4/E5)*,
so operator dependence — the actual clinical complaint about pre-procedural
ultrasound — persists in all of them. Robot-held, force-regulated acquisition
is the only approach that addresses it.

**And that gap is only real if robotic acquisition genuinely is more
consistent, which is currently unproven and which the one relevant dataset
ambivalently contradicts** *(C009)*. This is the single assumption on which the
entire commercial thesis rests, and it is testable with data before a cent is
spent on hardware. That test should be done first.

## 4. Business model categories

Categories only, no figures.

* **Capital equipment** — high friction in the target markets; slow procurement.
* **Lease / subscription** — lowers the capital barrier; suits hospitals that
  cannot make a large single purchase.
* **Annual software licence** — the natural home for model updates, which will
  be continuous.
* **Service and calibration contract** — mandatory for anything robotic.
* **Consumables** — sterile probe cover and single-use needle guide insert.
  Precedent exists: Rivanna's needle guide kit is separately cleared under
  product code ITX *(E4)*. A consumable attached to a clinically necessary step
  is the most durable revenue line in this category and should be designed in
  from the start, not bolted on.
* **Training and support** — non-trivial for a robotic system, and a real cost
  as much as a revenue line.

## 5. Where defensibility might come from

Listed as candidates, not claims. **Nothing here is asserted to be patentable**
— see `research/ip/PATENT_LANDSCAPE.md`, and note that no patent database was
reachable.

1. **A clinically annotated Indonesian lumbar ultrasound dataset**, in the
   population and positioning that public data structurally lacks. Data assets
   of this kind are slow to replicate and do not expire.
2. **Clinician-authored procedural target labels** — the layer that does not
   exist in any public dataset *(C013)*.
3. **A measured inter-rater agreement figure** for entry-point selection. Dull
   to describe, genuinely valuable: it sets the tolerance every competitor's
   alignment system must also meet, and nobody has published it.
4. **Quality-driven robotic re-acquisition** — the robot re-scans because the
   model judged the view inadequate.
5. **Calibrated abstention** — a system that reliably declines to propose.
6. **Workflow integration** that makes the setup time acceptable. Unglamorous,
   and probably decisive.

Items 1–3 are *evidence* assets rather than technical ones, and they are the
most durable of the six. They are also precisely what the hospital
collaboration produces.

## 6. Honest commercial risks

| Risk | Comment |
|---|---|
| **Setup time kills adoption** | Unmeasured. The highest-probability failure mode. |
| Robotic consistency premise is false | Testable now with data; would collapse the differentiation |
| Capital cost vs a cleared handheld device | A handheld competitor at a fraction of the price may be "good enough" for most users |
| Regulatory burden of the robotic element | Well beyond the Class II imaging pathway the incumbent uses |
| Reimbursement | No pathway identified; not investigated |
| Incumbent response | Rivanna could add a holder or arm far faster than we could build a product |
| Clinician resistance to a robot at the bedside | Real, and not addressable by engineering alone |

## 7. What should happen before any commercial commitment

1. Run the acquisition-consistency analysis on the anchor data — it is cheap
   and it tests the core premise.
2. Measure setup and scan time on a phantom mock-up with clinicians present.
3. Obtain the inter-rater agreement figure from the hospital pilot.
4. Only then decide whether Architecture D is a product or whether Architecture
   B (AI plus a passive guide) is the honest answer.
