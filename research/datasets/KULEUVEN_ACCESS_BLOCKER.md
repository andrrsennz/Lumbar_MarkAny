# Anchor dataset access blocker — KU Leuven RDR (`doi:10.48804/3XPCAE`)

**Status: the anchor dataset was NOT downloaded. This is a network-reachability
failure on the machine used for this work, not a licensing, permission, or
availability problem with the dataset itself.**

This document records exactly what was attempted, what was observed, and what
the next operator must do. It exists so that no reader of this evidence package
mistakes "we do not have the data" for "the data is not available".

---

## 1. What the dataset is

| Property | Value | How established |
|---|---|---|
| Title | A large, paired dataset of robotic and handheld lumbar spine ultrasound with ground-truth CT benchmarking | Crossref + DataCite |
| Dataset DOI | `10.48804/3XPCAE` | DataCite API |
| Publication DOI | `10.1038/s41597-025-06047-9` (*Scientific Data*, 2025-11-10) | Crossref API |
| Open-access full text | PMC12603223 / PMID 41213998, CC-BY | Europe PMC API |
| Publisher | KU Leuven RDR (Dataverse instance) | DataCite API |
| Licence | **CC-BY-4.0**, `info:eu-repo/semantics/openAccess` | DataCite `rightsList` |
| Files | **1,346** (1,337 × `application/zip`, 7 × CSV, 2 × TXT) | DataCite `formats` |
| Total size | **1,006,213,593,498 bytes ≈ 1,006 GB ≈ 1.01 TB** | Sum of DataCite `sizes` |
| Largest single file | ~3.27 GB | DataCite `sizes` |

The licence is unambiguous and permissive. Nothing about this dataset is
restricted, gated, or request-only.

---

## 2. What was attempted

All attempts were made on 2026-09-11 from the project workstation.

| Attempt | Target | Result |
|---|---|---|
| `curl https://rdr.kuleuven.be/api/info/version` (×2, 90 s timeout) | repository API | **timeout, no TCP connection** |
| `curl https://rdr.kuleuven.be` | repository root | timeout |
| `Test-NetConnection rdr.kuleuven.be -Port 443` | TCP/443 by name | `TcpTestSucceeded: False` |
| `Test-NetConnection 134.58.134.45 -Port 443` | TCP/443 by **direct IP** | `TcpTestSucceeded: False` |
| `Test-NetConnection rdr.kuleuven.be -Port 80` | TCP/80 | `TcpTestSucceeded: False` |
| `curl https://www.kuleuven.be` | university main site | timeout |
| `curl https://kuleuven.be` | apex domain | timeout |
| `curl https://lirias.kuleuven.be` | institutional repository | timeout |

### Control group (same machine, same minutes)

| Host | HTTP status |
|---|---|
| `zenodo.org` | 200 |
| `figshare.com` | 202 |
| `data.mendeley.com` | 200 |
| `osf.io` | 200 |
| `physionet.org` | 200 |
| `huggingface.co` | 200 |
| `api.datacite.org` | 200 |
| `drive.google.com` | 200 (1.3 GB downloaded successfully) |

### Diagnosis

DNS resolves correctly (`rdr.kuleuven.be → 134.58.134.45`, `2a02:2c40:0:81::81:45`),
so this is not a name-resolution failure. TCP connection fails on **both** ports
**80 and 443**, to **both** the hostname and the raw IP, for **every** host under
`kuleuven.be`, while every other research-data host on the internet responds
normally from the same machine in the same time window.

**Conclusion: the entire `kuleuven.be` domain is blocked at the network path
between this workstation and the destination** (ISP-, route-, or
firewall-level). It is not a KU Leuven server outage — an outage would not
selectively spare every other host on the internet while also blocking the
university's unrelated main website and institutional repository.

This is an **E5 (engineering inference)** conclusion drawn from **E1
(directly executed)** connectivity measurements.

---

## 3. A second, independent blocker: size

Even with full connectivity, the complete dataset is **1.01 TB**. The project
workstation had **135 GB free** on the working volume at the start of this work.
A complete mirror was never feasible here.

This is *not* a reason to give up on the dataset — it is a reason to fetch it
**selectively**. Only 9 of the 63 participants carry expert annotations, and
those 9 participants are the only ones needed for the supervised experiments
this project actually proposes. `scripts/data/download_kuleuven.py` is written
to do exactly that: enumerate the file listing, filter to the annotation-bearing
subset, and fetch only what is required, with resume and checksum recording.

---

## 4. What this changes about the project's claims

It changes them a great deal, and the rest of this package is written
accordingly:

* **No experiment in this package was run on human lumbar ultrasound.** Any
  statement to the contrary would be fabrication. The segmentation results in
  `experiments/exp003_unet_baseline/` are on **porcine intraoperative spinal
  cord** data (DS004) and are presented as *pipeline validation*, not as lumbar
  anatomy performance.
* **The handheld-vs-robotic (HUS/RUS) cross-domain study — the single most
  scientifically interesting direction this dataset enables — could not be
  started.** It remains the recommended first experiment the moment the data is
  in hand. See `deliverables/paper/PAPER_RECOMMENDATION.md`.
* Everything this package states *about* the dataset (counts, protocol,
  annotation provenance, limitations) comes from the **open-access full text**,
  which was retrieved successfully, and is cited as **E2/E3** rather than E1.

---

## 5. What the next operator must do

1. **Re-test reachability** from a different network path:
   ```bash
   python scripts/data/download_kuleuven.py --check-only
   ```
   A university network, a different ISP, or a VPN terminating in the EU are all
   reasonable things to try. Do not assume a VPN is required — try a plain
   different network first.

2. **Confirm free disk space.** Fetch the annotated subset first
   (`--subset annotated`), not the full 1 TB.

3. **Run the acquisition:**
   ```bash
   python scripts/data/download_kuleuven.py --subset annotated --out data/raw/kuleuven
   python scripts/data/verify_checksums.py
   ```

4. **Re-run the registry** so `DS001` moves from
   `PUBLIC_BUT_UNREACHABLE_FROM_THIS_NETWORK` to `DOWNLOADED AND VERIFIED`:
   ```bash
   python scripts/data/build_registry.py
   ```

5. **Only then** begin the HUS/RUS experiments. Do not merge lumbar bone-surface
   labels with the porcine cord label space — they are different tasks with
   different anatomy (see `deliverables/paper/CLAIMS_NOT_ALLOWED.md`).

---

## 6. Alternative access routes not yet exhausted

Listed for completeness; none were used to make any claim in this package.

* KU Leuven publishes a bulk-download helper at
  `https://www.kuleuven.be/rdm/en/rdr/large-downloads` (cited in the paper's
  Usage Notes). Unreachable from here for the same reason.
* The corresponding authors may be able to provide an alternative mirror. The
  paper's *Code availability* section already states that code can be "shared
  upon reasonable request", so the group is contactable.
* Dataverse instances expose a standard `/api/access/datafile/{id}` endpoint;
  if a mirror or proxy of this Dataverse is ever published, the download script
  can be pointed at it with `--base-url`.

**Do not substitute a third-party re-upload for the authoritative repository
without verifying checksums against the original.** No such mirror was located
during this work, and an unverified mirror is not acceptable provenance for a
dataset that will underpin a hospital collaboration proposal.
