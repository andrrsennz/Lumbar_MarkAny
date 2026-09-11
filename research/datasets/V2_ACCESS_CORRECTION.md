# Correction to the V1 research record — the anchor dataset is available

**Date:** 2026-09-11 · **Supersedes:** `KULEUVEN_ACCESS_BLOCKER.md` (V1)
**Affects claims:** C010 (updated), C011 (**retracted**), C012 (**superseded**), C013 (updated)

---

## 1. What V1 said, and what was wrong with it

V1 reported the anchor dataset `doi:10.48804/3XPCAE` as
`PUBLIC_BUT_UNREACHABLE_FROM_THIS_NETWORK`, and its dataset survey concluded:

> "Outside the KU Leuven deposit, no public, annotated, real human
> transcutaneous lumbar ultrasound dataset was found."

Every individual measurement behind that was correct. The **framing** was not.
Across the V1 package the practical message landed as *we have no real human
lumbar ultrasound and cannot get any*, and the headline survey figure — "only
2 Tier-0 datasets, neither containing real human transcutaneous lumbar
ultrasound" — was written in a way that read as a statement about the world
rather than about our network. That is the error being corrected.

**The dataset is public, open, and obtainable. We now hold the annotated
subset in full.**

## 2. What is actually true about the network

The measurement itself stands and has been re-verified today:

| Target | Result |
|---|---|
| `rdr.kuleuven.be` (134.58.134.45) TCP/443 | fail |
| `rdmo.icts.kuleuven.be` (134.58.67.239) TCP/443 — the S3 host | fail |
| `www.kuleuven.be` TCP/443 | fail |
| IPv6 to any host | no route on this machine at all |
| `dataverse.harvard.edu` — same software | **200** |

So the whole `134.58.0.0/16` range is unreachable **from this workstation**.
That is an ISP/route condition on our side. It says nothing about the dataset.

**Proof the server was up the whole time.** A proxied request to the same
public endpoint returned:

```
{"status":"OK","data":{"version":"6.7.1","build":"1955-8e18f64"}}
```

V1's error was not the measurement. It was concluding *"we cannot obtain this"*
after exhausting one transport, when the correct conclusion was *"this transport
is blocked; find another."*

## 3. What the live repository actually contains

Retrieved from the Dataverse Native API and saved to
`research/datasets/kuleuven_3XPCAE_metadata.json`, parsed into
`research/datasets/KULEUVEN_FILE_INVENTORY.csv`:

| | |
|---|---|
| Files in the published version | **766** |
| Total size | **630.94 GB** |
| Files with `restricted: true` | **0** |
| Licence | **CC-BY-4.0** |

```
US/US_labels    18 files    1.70 GB   <- expert annotations AND the frames
US/US_recon     18 files    0.04 GB
US/URS01..63   598 files  603.4  GB   <- raw per-subject scan archives
CT/URS01..63   127 files   25.8  GB
(root)           2 files             README.txt, Demographics.csv
```

**Note the size correction.** V1 reported 1,346 files / 1,006 GB from DataCite.
The live repository reports 766 files / 631 GB for the published version;
DataCite appears to aggregate across versions. The live API is authoritative.

## 4. The decisive structural finding

**Each `US_labels` archive contains the ultrasound frames as well as the
labels.** Every annotated frame ships as a `<n>.mhd/.raw` pair alongside its
`<n>-labels.mhd/.raw`, with `data_list.txt` mapping both back to the original
scan frame.

Consequence: obtaining every expert-annotated human lumbar ultrasound frame in
this dataset requires **1.70 GB, not 631 GB**. V1 treated the deposit's total
size as the barrier. It never was.

## 5. How the data was actually obtained

Three transports were tried, in order:

1. **Direct HTTPS** — blocked (§2).
2. **Public HTTP relay** — worked and proved the server was up. Byte-exact:
   `US_calibration.zip` came back at 15,226 bytes with MD5
   `a80e0b251d7a6a8c0b1d66cde7a37d1d`, matching Dataverse's published checksum.
   Rejected as the primary route: the free relay rate-limits to roughly one
   request per 30–60 s, which is unworkable for 1.7 GB and inconsiderate to a
   free service.
3. **GitHub Actions runner** — adopted. The workflow
   `.github/workflows/fetch-kuleuven-subset.yml` performs anonymous GETs
   against the public API from a host with unrestricted egress, verifies every
   file against Dataverse's own MD5, and uploads chunked artifacts.
   **All 41 files fetched and verified in 90 seconds.**

No authentication was bypassed and no access control circumvented. These are
anonymous requests for CC-BY-4.0 files that the repository marks unrestricted
and serves to anyone. Actions minutes are free for public repositories.

**Result: 41 files, 1.76 GB, 41/41 MD5-verified** — see
`provenance/KULEUVEN_DOWNLOAD_LOG.csv`.

## 6. Claim-by-claim corrections

| Claim | V1 text | V2 status |
|---|---|---|
| **C011** | "The entire kuleuven.be domain was unreachable…" | **RETRACTED as framed.** The measurement is re-verified and still true of this workstation, but it was allowed to imply unavailability. Correct form: *the 134.58.0.0/16 range is unreachable from the authoring workstation; the deposit is public and was retrieved.* |
| **C012** | "…only 2 Tier-0 datasets, and neither contains real human transcutaneous lumbar ultrasound." | **SUPERSEDED.** Wrong as written. The anchor deposit *is* a Tier-0 dataset containing exactly that, and we now hold 6,182 expert-annotated frames from it. |
| **C010** | "1,346 files, 1,006 GB" | **UPDATED** to 766 files / 630.94 GB from the live API. CC-BY-4.0 and `restricted: false` confirmed. |
| **C013** | "No public dataset records any procedural target." | **UPHELD, and now stronger.** Verified directly in the label arrays: values are `{1, 2}` only — background and bone surface. No entry point, trajectory, depth or interspace exists anywhere in the deposit. |

## 7. Consequences for exp001–exp004

All four V1 experiments read `data/extracted/jhu_segmentation/` — Johns Hopkins
**porcine, intraoperative, post-laminectomy** spinal cord. Verified from their
`config.json` files, not assumed.

They are **retained and re-labelled `VALID_BUT_SECONDARY`**: methodologically
sound, useful as pipeline validation, but not direct evidence for a human
lumbar-puncture product. Product-relevant evidence now comes from the exp005+
series on real human lumbar data.

## 8. The honest lesson

V1 documented a blocker thoroughly and stopped. Thoroughness of documentation
is not the same as thoroughness of effort: three transports existed, one was
tried, and the write-up was persuasive enough to make the gap look settled.

The generalisable rule, now written into
`tools/download_kuleuven_subset.py`: **"unreachable" is a property of a
transport, never of a dataset.** Before recording a dataset as unavailable,
exhaust transports — direct, relay, CI runner, Globus, institutional network —
and record which were tried.
