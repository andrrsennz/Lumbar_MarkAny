# Paper fact bank

Every fact traces to a file. Nothing here is remembered or rounded from memory.

## The dataset we hold

- **6,182** expert-annotated real human lumbar ultrasound frames (`data/processed/kuleuven_lumbar/index.csv`)
- **9** human subjects: URS08, URS16, URS26, URS31, URS36, URS40, URS45, URS51, URS54
- **2,382** handheld (HUS) and **3,800** robot-assisted (RUS)
- **184** frames (3.0%) where the expert annotated nothing
- Source: Cavalcanti et al., `doi:10.48804/3XPCAE`, **CC-BY-4.0**; paper `doi:10.1038/s41597-025-06047-9`
- 7 of 9 subjects have both modalities; URS31 and URS51 are robotic-only

## Provenance and verification

- 41 files, 1.76 GB, **41/41 MD5-verified** against the checksums Dataverse publishes
- The live repository holds **766 files / 630.94 GB**, all `restricted: false`, CC-BY-4.0
- The annotated subset needs only **1.70 GB**, because each label archive also contains the frames
- Independent verification: `KULEUVEN_VERIFICATION_REPORT.json` (all checks pass)

## Audit findings worth stating in the paper

- **Frame counts do not reproduce.** We count 6,182 listed and 5,998 non-empty; the publication reports 6,091. Neither counting rule reproduces the published figure.
- **Background label value is inconsistent**: 0 in six archives, 1 in the other twelve; bone surface is 2 throughout. `label != 0` yields a fully positive mask on twelve archives.
- **Channel count varies by subject**: four archives are greyscale, five are RGB with identical channels.
- **A stray annotation** in URS16_H3 frame 304 spans columns 556-1864, across the scanner UI.
- **184 frames (3.0%) have empty expert labels**, concentrated in 8 of 18 archives — ten archives contain none at all.

## Label semantics — the sentence the paper turns on

The labels mark **VISIBLE BONE SURFACE** and nothing else. There is no entry point, trajectory, target depth, interspace choice or outcome in this dataset, and none was found in any public dataset surveyed.

## What the data is not

- healthy volunteers aged 20-35 (BMI 19-26), imaged PRONE with a 10 MHz LINEAR transducer; single annotator; 9 annotated subjects
- Lumbar puncture is performed **sitting or in lateral decubitus** with a **2-5 MHz curvilinear** probe — neither matches this acquisition
- No puncture was performed on any subject
