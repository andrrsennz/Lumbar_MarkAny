#!/usr/bin/env python3
"""
build_registry.py -- Emit research/datasets/DATASET_REGISTRY.csv.

Every field below was established during this project by one of:
  (a) reading the authoritative publication full text,
  (b) querying the repository / DOI-provider API,
  (c) inspecting files we actually downloaded.

The `evidence` column records which. Fields that could not be established are
written as "unknown" -- never guessed. `access_status` uses the controlled
vocabulary required by the project brief:
  PUBLIC_DOWNLOADABLE | PUBLIC_AFTER_REGISTRATION | REQUEST_ONLY |
  PAPER_ONLY_NOT_AVAILABLE | UNKNOWN | PUBLIC_BUT_UNREACHABLE_FROM_THIS_NETWORK
"""
import csv
import pathlib

FIELDS = [
    "dataset_id", "dataset_name", "short_name", "relevance_tier",
    "direct_supporting_adjacent", "source_repository", "doi", "publication_doi",
    "institution", "country", "year", "human_animal_phantom", "anatomy",
    "modality", "transcutaneous_or_intraoperative", "acquisition_machine",
    "probe", "frequency", "subjects", "patients", "scans", "images",
    "cine_loops", "annotated_images", "annotation_classes", "annotation_type",
    "annotator_qualification", "tracking_available", "ct_available",
    "mri_available", "robot_data_available", "needle_visible",
    "needle_annotations", "pixel_spacing", "calibration", "demographics",
    "clinical_outcomes", "access_status", "access_method", "dataset_size",
    "compressed_size", "download_status", "local_path", "license",
    "commercial_use_allowed", "derivative_work_allowed", "redistribution_allowed",
    "citation_required", "checksum", "date_accessed", "suitable_for_training",
    "suitable_for_validation", "suitable_for_pretraining",
    "suitable_for_visual_examples", "major_limitations", "notes", "evidence",
]

ACCESSED = "2026-09-11"

ROWS = [
    # ---------------------------------------------------------------- TIER 0
    dict(
        dataset_id="DS001", short_name="KUL-BALGRIST-LUMBAR",
        dataset_name="A large, paired dataset of robotic and handheld lumbar spine ultrasound with ground-truth CT benchmarking",
        relevance_tier="Tier 0", direct_supporting_adjacent="direct",
        source_repository="KU Leuven RDR (Dataverse)", doi="10.48804/3XPCAE",
        publication_doi="10.1038/s41597-025-06047-9",
        institution="KU Leuven + Balgrist University Hospital / University of Zurich",
        country="Belgium / Switzerland", year="2025",
        human_animal_phantom="human", anatomy="lumbar spine L1-L5 (dorsal bone surfaces)",
        modality="B-mode ultrasound (2D) + CT + optical/robot pose tracking",
        transcutaneous_or_intraoperative="transcutaneous (prone, healthy volunteers)",
        acquisition_machine="Aixplorer Ultimate (SuperSonic Imagine)",
        probe="SuperLinear SL10-2 linear transducer", frequency="10 MHz",
        subjects="63", patients="0 (healthy volunteers)",
        scans="223 HUS + 375 RUS = 598", images="unknown (raw frames at 15 Hz)",
        cine_loops="598 tracked sweeps",
        annotated_images="6091 (2353 HUS + 3738 RUS)",
        annotation_classes="1 (bone surface)", annotation_type="pixel mask (.mhd label volumes)",
        annotator_qualification="single physician (paper author N.A.C.), the same person who acquired the HUS data",
        tracking_available="yes (Atracsys optical for HUS; robot end-effector pose for RUS; breathing marker)",
        ct_available="yes (ultra-low-dose CT + L1-L5 STL surface models)",
        mri_available="no", robot_data_available="yes (force-controlled 5 N, max 20 N, max 4 mm/s)",
        needle_visible="no", needle_annotations="no",
        pixel_spacing="unknown from publication (images 1080x1920 px, depth 7.7 cm)",
        calibration="yes (probe-to-image transforms calibrated with custom phantom)",
        demographics="yes (39F/24M, age 20-35 mean 25, BMI 19-26 mean 22)",
        clinical_outcomes="no (no punctures performed)",
        access_status="PUBLIC_BUT_UNREACHABLE_FROM_THIS_NETWORK",
        access_method="Direct download from rdr.kuleuven.be; bulk-download Python script published by KU Leuven",
        dataset_size="1006.21 GB (1346 files, from DataCite metadata)",
        compressed_size="1006.21 GB (1337 zip + 7 csv + 2 txt)",
        download_status="NOT DOWNLOADED - host unreachable (see research/datasets/KULEUVEN_ACCESS_BLOCKER.md)",
        local_path="", license="CC-BY-4.0",
        commercial_use_allowed="yes", derivative_work_allowed="yes",
        redistribution_allowed="yes (with attribution)", citation_required="yes",
        checksum="not computed (not downloaded)", date_accessed=ACCESSED,
        suitable_for_training="yes (bone-surface segmentation)",
        suitable_for_validation="yes, but only 9 annotated subjects",
        suitable_for_pretraining="yes", suitable_for_visual_examples="yes (CC-BY)",
        major_limitations=(
            "Annotated subset is only 9 of 63 subjects (7 HUS+RUS, 2 RUS-only) and was labelled by a "
            "SINGLE annotator, so no inter-rater agreement exists; healthy young volunteers only "
            "(BMI 19-26, age 20-35) which is the opposite of the difficult-LP population; PRONE position, "
            "whereas lumbar puncture is performed sitting or in lateral decubitus; 10 MHz LINEAR probe, "
            "whereas neuraxial practice uses low-frequency curvilinear probes; labels are BONE SURFACE only "
            "-- there are no puncture targets, interspace labels or procedural annotations"),
        notes=("Anchor dataset for this project. Every count above was verified against the open-access "
               "full text (PMC12603223). Total size verified from DataCite file-size metadata."),
        evidence="publication full text (PMC12603223) + DataCite API + Crossref API",
    ),
    # ---------------------------------------------------------------- TIER 1
    dict(
        dataset_id="DS002", short_name="MASOUMI-US-CT",
        dataset_name="Multimodal 3D ultrasound and CT in image-guided spinal surgery: public database and new registration algorithms",
        relevance_tier="Tier 1", direct_supporting_adjacent="supporting",
        source_repository="Zenodo", doi="10.5281/zenodo.4813508",
        publication_doi="unknown (dataset record lists no related identifier)",
        institution="Concordia University (PERFORM Centre / IMPACT lab)", country="Canada",
        year="2021", human_animal_phantom="human (CT only) + ex-vivo canine + ex-vivo lamb phantoms",
        anatomy="lumbar / cervical / thoracic vertebrae",
        modality="CT + real 3D ultrasound (phantoms only) + CT-simulated ultrasound",
        transcutaneous_or_intraoperative="ex-vivo phantom (exposed bone); human data is CT-derived only",
        acquisition_machine="unknown", probe="unknown", frequency="unknown",
        subjects="3 human (TCGA-QQ-A8VG, TCGA-QQ-ASV2, TCGA-QQ-ASVC) + 2 ex-vivo phantoms",
        patients="3 (TCGA archival CT)", scans="8 volumes", images="volumetric (.nii/.mnc)",
        cine_loops="0", annotated_images="21 landmark pairs per phantom (2 phantoms)",
        annotation_classes="anatomical landmark correspondences",
        annotation_type="point landmarks (.tag files)",
        annotator_qualification="unknown", tracking_available="no",
        ct_available="yes", mri_available="no", robot_data_available="no",
        needle_visible="no", needle_annotations="no",
        pixel_spacing="embedded in NIfTI/MINC headers", calibration="fiducial registration silver standard",
        demographics="no", clinical_outcomes="no",
        access_status="PUBLIC_DOWNLOADABLE", access_method="Zenodo direct HTTP download",
        dataset_size="~430 MB uncompressed", compressed_size="148,576,333 bytes",
        download_status="DOWNLOADED AND VERIFIED", local_path="data/raw/masoumi_us_ct/Data.zip",
        license="CC-BY-4.0", commercial_use_allowed="yes", derivative_work_allowed="yes",
        redistribution_allowed="yes (with attribution)", citation_required="yes",
        checksum="see provenance/DATA_DOWNLOAD_LOG.csv", date_accessed=ACCESSED,
        suitable_for_training="no (far too small)", suitable_for_validation="yes (US/CT registration only)",
        suitable_for_pretraining="no", suitable_for_visual_examples="yes (CC-BY)",
        major_limitations=(
            "CRITICAL: the three HUMAN subjects have CT and CT-SIMULATED ultrasound only -- there is no real "
            "human ultrasound in this release. Real ultrasound exists only for the two ex-vivo animal "
            "phantoms (canine cervical/thoracic, lamb lumbar) imaged on exposed bone. Not usable as evidence "
            "about transcutaneous human lumbar imaging."),
        notes="Useful specifically as a CT-to-ultrasound registration benchmark, not as an anatomy dataset.",
        evidence="Zenodo API record + direct inspection of downloaded archive contents",
    ),
    dict(
        dataset_id="DS003", short_name="ULTRABONES100K",
        dataset_name="UltraBones100k: automated labelling method and large-scale dataset for ultrasound-based bone surface extraction",
        relevance_tier="Tier 1", direct_supporting_adjacent="supporting",
        source_repository="unknown (no public repository record located)",
        doi="unknown", publication_doi="10.1016/j.compbiomed.2025.110435 (arXiv:2502.03783)",
        institution="Balgrist University Hospital / ETH Zurich", country="Switzerland",
        year="2025", human_animal_phantom="human ex-vivo (cadaveric)",
        anatomy="lower limb bones (NOT spine)", modality="B-mode ultrasound + CT",
        transcutaneous_or_intraoperative="ex-vivo cadaveric",
        acquisition_machine="unknown", probe="unknown", frequency="unknown",
        subjects="unknown", patients="0", scans="unknown", images="~100,000",
        cine_loops="unknown", annotated_images="~100,000",
        annotation_classes="1 (bone surface)",
        annotation_type="pixel mask, AUTOMATICALLY generated from CT-to-US registration then physics-refined",
        annotator_qualification="automated; quality reviewed by one orthopaedic-sonography expert physician",
        tracking_available="yes (implied by CT-US registration)", ct_available="yes",
        mri_available="no", robot_data_available="unknown", needle_visible="no",
        needle_annotations="no", pixel_spacing="unknown", calibration="unknown",
        demographics="unknown", clinical_outcomes="no",
        access_status="UNKNOWN", access_method="No download link found on the arXiv landing page; publisher version is paywalled (Elsevier)",
        dataset_size="unknown", compressed_size="unknown",
        download_status="NOT DOWNLOADED - availability unverified", local_path="",
        license="unknown (article CC-BY per Crossref; dataset licence not located)",
        commercial_use_allowed="unknown", derivative_work_allowed="unknown",
        redistribution_allowed="unknown", citation_required="yes",
        checksum="", date_accessed=ACCESSED,
        suitable_for_training="potentially (bone-surface pretraining)", suitable_for_validation="unknown",
        suitable_for_pretraining="potentially high value", suitable_for_visual_examples="no (licence unknown)",
        major_limitations=(
            "Lower-limb, not spine. Ex-vivo cadaveric, not in-vivo. Labels are algorithmically derived from "
            "CT registration rather than expert manual annotation. Public availability NOT confirmed -- do "
            "not describe this as a public dataset without re-verification."),
        notes=("Cited by the anchor publication as a generalisation benchmark. Listed here so the gap is "
               "explicit; requires direct author contact to establish access."),
        evidence="Crossref API + arXiv abstract page (2502.03783v4)",
    ),
    # ---------------------------------------------------------------- TIER 3
    dict(
        dataset_id="DS004", short_name="JHU-SPINALCORD-SEG",
        dataset_name="JHU HEPIUS open-source spinal cord ultrasound dataset -- semantic segmentation subset",
        relevance_tier="Tier 3", direct_supporting_adjacent="supporting",
        source_repository="GitHub README pointing to Google Drive",
        doi="unknown (no dataset DOI issued)",
        publication_doi="PMC12475011 (PMID 41006445)",
        institution="Johns Hopkins University (HEPIUS lab)", country="USA", year="2025",
        human_animal_phantom="animal (porcine) + small human test subset",
        anatomy="spinal cord and surrounding structures (dura, pia, CSF, ventral/dorsal space)",
        modality="B-mode ultrasound",
        transcutaneous_or_intraoperative="INTRAOPERATIVE, after laminectomy (bone removed for acoustic window)",
        acquisition_machine="unknown", probe="unknown", frequency="unknown",
        subjects="25 female Yorkshire pigs (~50 lb); human subset 8 patients",
        patients="8 (human subset, 86 images, T11-L1 laminectomy)",
        scans="unknown", images="10,223 (porcine segmentation set)",
        cine_loops="unknown", annotated_images="10,223",
        annotation_classes=("10: Background, Dura, Pia, CSF, Spinal cord, Dorsal Space, Hematoma, "
                            "Ventral Space, Dura/Pia complex, Dura/Ventral Complex"),
        annotation_type="pixel masks (RGB PASCAL-VOC palette PNG), made in CVAT",
        annotator_qualification=("medical and graduate students trained by a board-certified radiologist; "
                                 "ambiguous images verified by the radiologist; all masks re-validated by a "
                                 "neurosurgery spine fellow"),
        tracking_available="no", ct_available="no", mri_available="no",
        robot_data_available="no", needle_visible="no", needle_annotations="no",
        pixel_spacing="images cropped to 690x275 px representing approx. 25 mm x 8 mm",
        calibration="scaled to depth of scan field (per README)", demographics="no",
        clinical_outcomes="no (controlled contusion injury model)",
        access_status="PUBLIC_DOWNLOADABLE", access_method="Google Drive links published in the GitHub README",
        dataset_size="~1.9 GB uncompressed", compressed_size="1,079,559,546 bytes",
        download_status="DOWNLOADED AND VERIFIED", local_path="data/raw/jhu_spinal_cord/jhu_segmentation.zip",
        license="NONE DECLARED (GitHub repo has no licence file; Drive archive contains no licence)",
        commercial_use_allowed="unknown", derivative_work_allowed="unknown",
        redistribution_allowed="NO -- do not redistribute; no licence grant exists",
        citation_required="yes (by academic norm)", checksum="see provenance/DATA_DOWNLOAD_LOG.csv",
        date_accessed=ACCESSED,
        suitable_for_training="yes (methodology development only)", suitable_for_validation="yes",
        suitable_for_pretraining="yes (ultrasound domain)",
        suitable_for_visual_examples="NO -- no licence grant; use our own rendered figures only under fair-dealing/citation, or seek permission",
        major_limitations=(
            "Porcine, not human, for all 10,223 training images. INTRAOPERATIVE after laminectomy, so the "
            "acoustic path has no intervening bone or deep soft tissue -- fundamentally unlike transcutaneous "
            "lumbar imaging for puncture. Target anatomy is the cord and meninges, not the dorsal bone "
            "landmarks used for neuraxial access. No animal identifier is distributed, so animal-level "
            "splitting cannot be reconstructed."),
        notes=("Used in this project ONLY as an engineering substrate to build and validate the segmentation, "
               "evaluation and uncertainty pipeline. All 10 class pixel counts were independently reproduced "
               "from the downloaded masks (exp002) and matched the publication's Table 1 exactly."),
        evidence="publication full text (PMC12475011) + GitHub README + direct inspection of downloaded archive",
    ),
    dict(
        dataset_id="DS005", short_name="JHU-SPINALCORD-DET",
        dataset_name="JHU HEPIUS open-source spinal cord ultrasound dataset -- injury localization subset",
        relevance_tier="Tier 3", direct_supporting_adjacent="supporting",
        source_repository="GitHub README pointing to Google Drive", doi="unknown",
        publication_doi="PMC12475011 (PMID 41006445)",
        institution="Johns Hopkins University (HEPIUS lab)", country="USA", year="2025",
        human_animal_phantom="animal (porcine)", anatomy="spinal cord contusion injury (hematoma)",
        modality="B-mode ultrasound",
        transcutaneous_or_intraoperative="INTRAOPERATIVE, after laminectomy",
        acquisition_machine="unknown", probe="unknown", frequency="unknown",
        subjects="23 pigs (per publication)", patients="0", scans="unknown",
        images="2,245 (877 pre-injury, 1,368 post-injury)", cine_loops="unknown",
        annotated_images="1,368 (only post-injury images carry a box; pre-injury images are negatives)",
        annotation_classes="1 (injury/hematoma bounding box)",
        annotation_type="PASCAL-VOC bounding boxes (.xml)",
        annotator_qualification="as DS004", tracking_available="no", ct_available="no",
        mri_available="no", robot_data_available="no", needle_visible="no",
        needle_annotations="no", pixel_spacing="690x275 px approx. 25 mm x 8 mm",
        calibration="as DS004", demographics="no", clinical_outcomes="no",
        access_status="PUBLIC_DOWNLOADABLE", access_method="Google Drive link in GitHub README",
        dataset_size="~250 MB uncompressed", compressed_size="224,279,362 bytes",
        download_status="DOWNLOADED AND VERIFIED",
        local_path="data/raw/jhu_spinal_cord/jhu_injury_localization.zip",
        license="NONE DECLARED", commercial_use_allowed="unknown",
        derivative_work_allowed="unknown", redistribution_allowed="NO -- no licence grant exists",
        citation_required="yes", checksum="see provenance/DATA_DOWNLOAD_LOG.csv",
        date_accessed=ACCESSED,
        suitable_for_training="yes (methodology only)", suitable_for_validation="yes",
        suitable_for_pretraining="limited", suitable_for_visual_examples="NO -- no licence grant",
        major_limitations=(
            "Not relevant to neuraxial access anatomy; an injury-detection task on exposed porcine cord. "
            "Verified counts: 877 pre-injury images contain zero boxes, 1,368 post-injury images contain "
            "exactly one box each. The 1,368 box-bearing images carry no subject token in their filenames."),
        notes="Counts independently verified by parsing every PNG/XML pair in the downloaded archive.",
        evidence="publication full text + direct parsing of all 2,245 images and 2,246 XML files",
    ),
]


def main():
    out = pathlib.Path("research/datasets/DATASET_REGISTRY.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="raise")
        w.writeheader()
        for r in ROWS:
            for k in FIELDS:
                r.setdefault(k, "unknown")
            w.writerow(r)
    print(f"wrote {out} with {len(ROWS)} datasets and {len(FIELDS)} fields")
    for r in ROWS:
        print(f"  {r['dataset_id']}  {r['relevance_tier']:7s} {r['access_status']:42s} {r['short_name']}")


if __name__ == "__main__":
    main()
