# HeyGen Backgrounds

Premium studio backgrounds for the avatar beats, 1920×1080 PNG, built from the palette in `10-graphics/design-system.md`. They replace the flat colour used before. The avatar stands in the right third of the frame, where the soft key light is; the left two thirds stay clean for lower thirds and picture-in-picture slides.

| File | Use |
|---|---|
| `studio-navy.png` | Default for every course. Deep Navy gradient, key light right, teal accent low-left, teal rule at the bottom (the same device as the slide footers). |
| `course2-testing.png` | Course 2 variant (teal accent, same as the default). |
| `course3-voice.png` | Course 3 variant: accent shifted toward cyan. |
| `course4-observability.png` | Course 4 variant: accent shifted toward green. |

Use `studio-navy.png` unless you want each course to have its own accent. Never mix backgrounds inside one course (`PRODUCTION-GUIDE.md`, rule 7).

## Use in HeyGen

Upload once, then reference the asset id for every batch:

```bash
cd voice-ai-agents-course/09-production/tools
python heygen_batch.py upload-background ../../../09-heygen/backgrounds/studio-navy.png
export HEYGEN_BACKGROUND_IMAGE=<asset id printed>       # or a public https URL to the PNG
export HEYGEN_BACKGROUND_FIT=cover
python heygen_batch.py generate ../scenes/section-03.json --dry-run --show-payload   # check the payload
```

The upload endpoint and the `background` field names are flagged "verify" in `heygen_batch.py`; check them against the current HeyGen API reference before the first batch. In HeyGen Studio, the same PNG can be set as the scene background when creating or previewing a look.

## Rebuild

```bash
python 09-heygen/backgrounds/build_backgrounds.py     # needs Pillow (tools/requirements.txt)
```

Edit `VARIANTS` in `build_backgrounds.py` to change accents or add a variant.
