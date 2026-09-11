# System architecture, autonomy levels and hardware blueprint

**Everything in this document is E6 — proposal. No hardware has been built,
purchased, or specified beyond paper. No safety case exists.**

---

## 1. Candidate architectures

| | **A** software only | **B** AI + passive guide | **C** robot probe + manual needle | **D** force-controlled robot + aligned guide | **E** fully autonomous |
|---|---|---|---|---|---|
| AI image interpretation | ✔ | ✔ | ✔ | ✔ | ✔ |
| Robot holds probe | ✘ | ✘ | ✔ | ✔ | ✔ |
| Probe force control | ✘ | ✘ | optional | ✔ | ✔ |
| Physical needle guide | ✘ | ✔ passive | ✘ | ✔ robot-aligned | ✔ |
| Needle inserted by | clinician | clinician | clinician | **clinician** | **robot** |
| Autonomy level | 0 | 0 | 1–3 | **4** | 5 |
| Engineering complexity | low | low | medium | high | very high |
| Regulatory complexity | moderate (AI claim) | moderate | high | high | **very high** |
| Clinical adoption risk | low | low | medium | medium | **very high** |
| Differentiation vs Accuro | **weak** | weak | moderate | **strong** | strong |

### Assessment

**A is insufficient.** It competes directly with a cleared, iterating commercial
product on that product's own ground, and the project's premise includes
hardware. A better landmark detector is not a defensible contribution — the
academic literature has been doing that since 2008.

**B is the cheapest credible product** and worth keeping as a fallback: a
passive guide is a proven regulatory object (Accuro's own needle guide kit is
cleared under product code ITX). But it does not address operator dependence,
which is the actual unsolved problem.

**C is an awkward middle.** It takes on the full cost and risk of a robot while
capturing only part of the benefit, because without force control the robot
cannot maintain consistent acoustic coupling.

**E is inappropriate as a first product** and arguably inappropriate at all.
Autonomous needle insertion into the neuraxis carries a risk profile that no
current evidence base supports, and proposing it would damage the credibility of
everything else.

### Recommendation: **Architecture D, targeting Autonomy Level 4**

> Force-controlled robotic ultrasound acquisition + AI perception +
> **clinician confirmation gate** + robot-aligned needle guide +
> **clinician-performed insertion**.

The reasoning is that the defensible contribution is *acquisition
standardisation*, not perception. Every cleared competitor is handheld, so the
operator-dependence term remains in all of them. A robot that holds the probe
with regulated contact force is the only way to remove it — and the KU Leuven
group has already demonstrated that this is feasible in humans (5 N target,
20 N maximum, 4 mm/s), which substantially de-risks the acquisition subsystem.

**Caveat that must not be buried:** the same publication reports that robotic
scans had *more* variable coverage than handheld ones (SPAR 54–100% vs ≥85%).
The premise that robotic acquisition is more consistent is therefore **an open
question, not an established fact** — and testing it is the recommended first
experiment (`deliverables/paper/PAPER_RECOMMENDATION.md`). If robotic
acquisition turns out not to improve consistency, Architecture D loses its
rationale and the project should fall back to B.

---

## 2. Autonomy levels

| Level | Definition | Who moves the probe | Who decides the target | Who moves the needle | Regulatory weight |
|---|---|---|---|---|---|
| 0 | Manual scan + AI interpretation | clinician | clinician | clinician | lowest — an imaging/CADe claim |
| 1 | Robot positions probe on command | robot, commanded | clinician | clinician | + robot safety |
| 2 | Robot executes a scan pattern | robot, pre-programmed | clinician | clinician | + autonomous motion |
| 3 | AI selects view; robot optimises pose | robot, AI-directed | clinician | clinician | + closed-loop AI control |
| **4** | **Robot aligns guide after clinician confirmation** | robot | **clinician confirms** | **clinician** | + patient-contacting alignment |
| 5 | Robot inserts the needle | robot | AI proposes | **robot** | **highest — invasive autonomous action** |

**These levels are not regulatory equivalents and must never be presented as a
smooth gradient.** The step from 4 to 5 changes the device from one that
positions a guide to one that performs an invasive act on a patient. Level 4
keeps a human decision and a human hand between the algorithm and the patient.

Level 3 is where the interesting research sits (AI-directed view optimisation),
and it can be developed and validated **on phantoms** without approaching the
Level 4/5 boundary.

---

## 3. Sensors

| Sensor | Purpose | MVP | Future |
|---|---|---|---|
| B-mode ultrasound | primary perception | ✔ | |
| Robot joint encoders | probe pose without external tracking | ✔ | |
| Force/torque sensor at wrist | contact-force regulation, patient safety | ✔ | |
| Emergency stop (hardware) | unconditional halt | ✔ | |
| Mechanical compliance in the mount | passive safety independent of software | ✔ | |
| RGB-D camera | patient surface, setup, gross collision avoidance | | ✔ |
| Optical tracking | ground-truth pose for validation | validation only | |
| EM tracking | needle-tip localisation when out of plane | | ✔ |
| Breathing/motion marker | respiratory compensation | | ✔ |
| Needle insertion-force sensing | tissue-layer discrimination | | ✔ |
| Bioimpedance at needle tip | tissue-type discrimination | | ✔ (research) |

**Design principle:** every safety-critical function must have a non-software
path. Force limiting through a compliant mount and a mechanical hard stop, not
only through a control loop.

---

## 4. Hardware blueprint

Deliberately manufacturer-agnostic. Naming a vendor now would be a decision
made before the requirements are known.

### Manipulator
Options: collaborative arm (fastest, certified force limiting, largest and most
expensive); custom Cartesian stage (smallest workspace, simplest safety case,
most engineering); compact parallel mechanism (small and stiff, complex
kinematics). **Recommendation deferred** until the required workspace is
measured from real patient-positioning geometry — a measurement nobody has made
for the sitting/lateral-decubitus neuraxial setting.

### Probe interface
Rigid printed cradle with a quick-release; a single-use sterile cover; a
disposable needle-guide insert keyed to the cradle. The disposable is both a
sterility requirement and the natural consumable revenue line.

### Needle guidance
A **mechanical remote-centre-of-motion** is preferable to a motorised one: it
constrains the trajectory geometrically rather than by software, which is a far
easier safety argument. Add a physical depth stop set to the clinician-confirmed
target depth.

### Safety chain
Hardware E-stop in series with motor power; force ceiling enforced in hardware;
mechanical hard stops on travel; compliant coupling; quick-release the clinician
can operate one-handed; **guide alignment permitted only after explicit
clinician confirmation**, enforced outside the AI path.

---

## 5. BOM categories

Categories only. **No prices**, because we have not obtained quotes and any
figure would be invented.

Manipulator · force/torque sensor · ultrasound system + curvilinear probe ·
ultrasound frame-grabber or SDK access · probe cradle + sterile covers +
disposable guides · motion controller + real-time host · workstation with GPU ·
safety hardware (E-stop, contactors, hard stops) · optical tracker (validation
only) · phantoms · enclosure and cart · cabling.

---

## 6. What would falsify this architecture

Stated up front, because an architecture that cannot be falsified is marketing.

1. **If robotic acquisition does not measurably improve consistency** over
   handheld in the paired data, Architecture D's core rationale fails.
2. **If clinician inter-rater agreement on entry point is very low**, there is
   no stable target for a guide to align to, and the product should stop at
   Level 0–1 decision support.
3. **If patients cannot tolerate robotic probe contact** in sitting or lateral
   decubitus for the required duration, the acquisition concept fails
   ergonomically regardless of its technical merit.
4. **If the required workspace cannot be reached** around a seated, flexed
   patient with an assistant present, the manipulator class is wrong.

Each of these is testable before any patient is involved. Items 1 and 2 need
only data and clinicians; items 3 and 4 need only a phantom and a mock-up.
