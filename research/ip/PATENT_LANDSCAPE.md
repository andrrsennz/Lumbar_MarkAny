# Patent landscape

> **This document contains no patent citations, because no patent database was
> reachable from the project network. Nothing below should be read as a
> freedom-to-operate opinion, a novelty assessment, or legal advice of any
> kind — we are not qualified to give any of those, and did not attempt to.**

---

## 1. What was attempted, and what happened

| Source | Endpoint | Result (2026-09-11) |
|---|---|---|
| PatentsView (USPTO) | `search.patentsview.org` | **DNS resolution failed** |
| EPO Open Patent Services | `ops.epo.org` | **HTTP 403** — requires registered OAuth credentials |
| Espacenet | `worldwide.espacenet.com` | **HTTP 403** |
| Google Patents | `patents.google.com` | HTTP 200, but **no public API**; scraping the interface would be unreliable and is not something we will do |

**Consequence: zero patent documents were retrieved or read.** Any list of
patent numbers in this document would therefore be invented, and there is none.

## 2. What can honestly be said instead

The following observations come from sources we *did* verify — the FDA 510(k)
record, the peer-reviewed literature, and the product landscape. They are
**E5 (engineering inference)** about where patent activity is *likely* to be
concentrated. They are hypotheses for a patent attorney to test, not findings.

### Likely crowded

* **Handheld ultrasound devices that automatically identify neuraxial landmarks
  and display a depth-to-epidural estimate.** Rivanna has been shipping and
  iterating in exactly this space since at least 2014 (K132736) with six
  subsequent clearances *(E4)*. A company with an eight-clearance product line
  over twelve years will have filed around it.
* **Passive needle guides that attach to an ultrasound probe.** Cleared as a
  distinct device class (product code ITX) with multiple clearances *(E4)*; a
  long-standing and mechanically simple area.
* **Automatic detection of lumbar level and vertebral landmarks in ultrasound.**
  Academic publication since 2008–2010 *(E3)*. Long publication history usually
  implies both prior art that limits novelty *and* filings by the groups and
  companies involved.
* **Robotic ultrasound scanning with force control.** An active research field
  with commercial interest in tele-ultrasound.
* **Ultrasound-to-CT registration for spinal navigation.** Long-standing in
  surgical navigation.

### Possibly less crowded — worth a targeted search

Each of these is a *combination*, and combinations are where the interesting
questions usually sit:

1. **Robot-held acquisition whose scan policy is driven by an AI image-quality
   assessment** — the robot re-acquires because the model says the view is
   inadequate. We found no product doing this, and the closest research work
   (KU Leuven) uses pre-programmed scan patterns rather than quality-driven
   re-acquisition.
2. **Machine-learning systems trained on clinician-authored procedural targets
   for neuraxial access** — since no such labelled data exists publicly *(E1,
   C013)*, systems that consume it may be correspondingly sparse.
3. **An explicit abstention mechanism** — a guidance system whose defined output
   includes "no safe recommendation", with that state gating downstream
   mechanical action.
4. **Robot-positioned needle guide whose alignment is unlocked only by an
   explicit clinician confirmation step**, with the interlock enforced outside
   the AI path.
5. **Uncertainty-gated target proposal**, where the displayed confidence
   determines whether alignment is permitted at all.

Items 3–5 are all variations on the same underlying idea: *the system's most
important behaviour is knowing when not to act.* Whether that is patentable, or
already claimed, is exactly the question we cannot answer.

## 3. What must be done before any IP position is asserted

1. **Engage a patent attorney.** Nothing in this project substitutes for that.
2. **Run the searches below** through a proper database (Espacenet with
   credentials, EPO OPS, USPTO full-text, Derwent) — ideally via the attorney,
   so the search is privileged and competently constructed.
3. **Do not publish a system description containing a potentially novel
   mechanism before filing**, if filing is intended. This matters *now*: the
   hospital proposal and the paper both describe Architecture D. If any element
   is to be protected, that decision must be made **before** those documents
   circulate outside the team.

### Search strings prepared for that session

```
(lumbar OR neuraxial OR epidural OR intrathecal OR "spinal anesthesia")
   AND ultrasound AND (needle OR puncture OR guide OR trajectory)

ultrasound AND robot* AND (spine OR spinal OR lumbar OR vertebra*)

ultrasound AND ("image quality" OR confidence OR adequacy) AND (robot* OR automatic)
   AND (scan OR acquisition OR reposition*)

needle AND guide AND (robot* OR motor* OR align*) AND ultrasound AND (confirm* OR interlock)

ultrasound AND (uncertainty OR confidence) AND (target OR trajectory OR "insertion point")

"remote center of motion" AND needle AND (ultrasound OR image-guided)

force AND control AND ultrasound AND probe AND (patient OR contact)
```

Classification codes worth constraining by: **A61B 8/** (ultrasound
diagnostics), **A61B 17/34** (trocars, puncture needles), **A61B 34/**
(computer-assisted surgery, robotics), **A61B 90/** (surgical navigation
accessories), **G06T 7/** (image analysis/segmentation).

## 4. Standing rule for this project

Until a qualified search has been done, **no document from this project may
state or imply that anything is patentable, novel over the patent art, or clear
to operate.** `CLAIMS_NOT_ALLOWED.md` §5 enforces this.
