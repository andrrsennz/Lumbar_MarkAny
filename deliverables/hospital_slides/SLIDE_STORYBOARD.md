# Hospital presentation — slide storyboard

**18 slides, ~25 minutes plus discussion.** Audience: mixed clinical and
administrative. Assume no ML background and a low tolerance for hype.

## The one rule for this deck

Every slide carries a status marker in a fixed corner position:

| Marker | Meaning |
|---|---|
| 🟢 **VERIFIED TODAY** | We measured it, or it is verified from a primary source |
| 🟡 **PROPOSED NEXT** | The work we are asking to do |
| ⚪ **LONG-TERM VISION** | Where this could lead; not committed, not funded, not approved |

**Never put a conceptual robotics visual on the same slide as a current AI
result without both markers visible.** The single fastest way to lose a
clinical audience is for them to realise, at slide 15, that something on
slide 7 was not real.

---

### 1 — Title 🟢
**AI-assisted lumbar ultrasound for safer, more reproducible neuraxial access**
*A research collaboration proposal*

Speaker note: open by stating the ask in one sentence — de-identified images and
expert annotation for a retrospective study — so nobody spends 20 minutes
wondering what is being sold. Nothing is being sold.

### 2 — The procedure 🟢
Lumbar puncture / neuraxial anaesthesia: what it is, who performs it here, how
often. **Leave the local numbers blank and ask the room to fill them in.**
Visual: simple anatomical schematic (original SVG).

Speaker note: this slide is deliberately a question. We do not know their case
mix and should not pretend to.

### 3 — Where difficulty arises 🟢
Obesity, oedema, degenerative change, scoliosis, prior surgery, impalpable
landmarks. Consequences: repeat attempts, redirections, discomfort, traumatic
tap, failure.
Visual: two-column contrast, easy vs difficult anatomy.

Speaker note: no incidence statistics. We did not do a systematic review and
will not quote a number we cannot defend. Invite their experience instead.

### 4 — The ultrasound opportunity 🟢
Palpation infers; ultrasound shows. Direct visualisation of spinous process,
lamina, interlaminar window, posterior complex, and depth.
Visual: landmark vs ultrasound schematic.

### 5 — What already exists 🟢
Commercial: Rivanna Accuro, FDA 510(k) K171594 (2017), Accuro 3S K243937 (2025),
product code IYO, Class II. Research: KU Leuven/Balgrist robotic lumbar
ultrasound in 63 volunteers. Academic: automated lumbar landmark detection since
2008.
Visual: `fig_competitor_landscape` (from `COMPETITOR_MATRIX.csv`).

Speaker note: say plainly that others are ahead of us commercially. Credibility
with this audience comes from knowing the field, not from claiming a vacuum.

### 6 — What remains unsolved 🟢
1. Every cleared device is **handheld** — operator dependence persists.
2. **No public dataset anywhere records a procedural target.**
3. The only human lumbar dataset is healthy volunteers, **prone**, **10 MHz
   linear** probe — the wrong population, position and probe.
4. Perception, acquisition and guidance are studied separately.

Speaker note: this is the intellectual core of the talk. Slow down here.

### 7 — The proposed platform 🟡 / ⚪
The workflow diagram, with the **physician confirmation gate drawn as a hard
barrier** the arrow cannot bypass.
Visual: `fig_system_workflow.svg`.

Speaker note: state explicitly — the physician always performs the puncture; the
system never inserts anything; autonomous insertion is out of scope, not
merely "later".

### 8 — What exists today 🟢
Transition slide. "Everything after this point is either measured or clearly
marked as proposal."

### 9 — The public data reality 🟢
`fig01_dataset_survey.png` — 891 candidates, 6 repositories, **2 Tier-0
datasets, neither with real human transcutaneous lumbar ultrasound.**

Speaker note: this is the single most persuasive slide in the deck, and it is
persuasive precisely because it is a negative finding about our own field.

### 10 — The one lumbar dataset, and its limits 🟢
63 volunteers, 598 tracked scans, 6,091 annotated frames — but **9 annotated
subjects, one annotator, prone, linear probe, healthy and young.** And we could
not obtain it: the host is unreachable from our network.

Speaker note: volunteering the access failure buys more credibility than any
result in the deck. Do not skip it.

### 11 — What we built and verified 🟢
Three executed results: an exact reproduction of a published dataset's class
statistics; recovery of an undocumented label encoding; a split-integrity audit
whose hypothesis we **disproved**.
Visual: `fig02_class_distribution.png`, `fig03_leakage_audit.png`.

Speaker note: the disproved hypothesis is the point — it demonstrates we report
against our own interest.

### 12 — Our model result 🟢
`fig04_training_curves.png` + `fig05_per_class_dice.png`.
**Caption in large type: "Porcine. Intraoperative. After laminectomy. Not
lumbar. Not human. This validates our pipeline, nothing more."**

Speaker note: say that sentence aloud. Do not let anyone leave thinking we have
a working lumbar model.

### 13 — Robotic acquisition ⚪
Force-controlled robot-held probe as demonstrated by others (5 N contact,
4 mm/s). **We have built no hardware.**
Visual: architecture diagram, clearly marked.

### 14 — What public data cannot provide 🟢
The visible-anatomy vs clinical-decision boundary.

| Bone surface, interlaminar window | Interspace choice, entry point, trajectory, depth, "do not proceed" |
|---|---|
| Public data has this | **Nobody has this** |

### 15 — What only clinicians can add 🟡
The four-column translational figure: real ultrasound → expert anatomy
annotation → model prediction → **the clinician layer, boxed and labelled
"PROPOSED — NOT CURRENT GROUND TRUTH"**.
Visual: `fig_translational_columns.svg`.

Speaker note: the fourth column is the ask, made visual.

### 16 — What we are requesting 🟡
Required / nice-to-have / future-only, per proposal §14–15. Retrospective,
de-identified, no change to care, no device on any patient, ethics approval
first.

### 17 — Governance and safety 🟢 / 🟡
Ethics (KEPK) before any data access; de-identification at source; key never
leaves the hospital; analysis can run inside the hospital if cross-border
transfer is not permitted; clinician-in-the-loop by design; research-only
boundary is contractual.

### 18 — The ask 🟡
One concrete next step: **a working meeting with anaesthesiology, neurology,
radiology and emergency medicine to review the annotation ontology** — which we
expect them to rewrite substantially.

Plus the honest gate: if inter-rater agreement turns out too low to be usable,
we publish that and stop.

---

## Slides deliberately NOT included

* Market size, pricing, or revenue projections — we did no market research.
* A timeline with dates — we do not know their committee cycle or case volume.
* Any image of a robot next to a patient — we have no hardware and no safety case.
* Any claim about first-pass success, complications, or procedure time.
* Any photograph of real ultrasound from the JHU dataset — **it carries no
  licence**, so we show our own charts of statistics instead, never their pixels.

## Q&A preparation

| Likely question | Honest answer |
|---|---|
| "Does it work?" | We don't know for lumbar anatomy. We have not tested it on any. |
| "How accurate is it?" | On porcine cord: see the figure. On human lumbar: no data. |
| "Have you built the robot?" | No. Nothing has been built. |
| "Why should we give you data?" | Because the gaps are structural: population, position, probe, and labels nobody has ever created. |
| "What if our images are poor quality?" | Quality gating is a modelling target, not only an obstacle — and a real distribution of quality is more useful to us than a curated one. |
| "What do we get?" | Co-authorship, a reusable annotation and de-identification capability, a quantified local picture, and early involvement. |
| "What if it fails?" | We publish the negative result. The inter-rater agreement figure is a gate we have committed to publishing whatever it shows. |
