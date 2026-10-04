# Avatar Configuration — PENDING

> **Status:** Awaiting the course owner's avatar choice (see `MY_DECISIONS_REQUIRED.md`). Shared by Courses 2, 3 and 4: one avatar, one look, one background across all three courses.
>
> **Look v2 (decided 2026-10-04):** the flat navy colour background and the unspecified "business casual" outfit are replaced by the premium look below. Create it as a new **HeyGen look** on the chosen avatar so the shirt and background change without changing the person or the voice.

| Setting | Value |
|---|---|
| **Avatar** | `PENDING` — chosen by the course owner in HeyGen studio |
| **Look** | `PENDING` — a dedicated look for the courses (spec below); its id goes in `HEYGEN_AVATAR_ID` |
| **Avatar style** | `normal` (full upper body, no circle crop) |
| **Background** | `09-heygen/backgrounds/studio-navy.png` via `HEYGEN_BACKGROUND_IMAGE` (asset id), `fit=cover` |
| **Where the IDs live** | Environment variables `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID`, `HEYGEN_BACKGROUND_IMAGE` only. Never write an ID or API key into this repo (`CLAUDE.md`). |

## The look: premium shirt and premium background

The goal is a presenter who reads as a senior engineer giving a studio talk, not a corporate headshot. Everything is chosen to separate cleanly from the Deep Navy background and to sit with the teal accent.

| Element | Spec | Why |
|---|---|---|
| **Shirt (primary)** | Crisp **white** dress shirt, slim fit, open collar, no tie, sleeves at the wrist (no rolled sleeves) | White gives the strongest separation from navy and keeps the face the brightest thing in frame |
| **Shirt (alternate)** | Light **slate blue** (`#B8C4D6` range) dress shirt, same cut | Same separation, slightly warmer; use only if white blows out in the test render |
| **Jacket** | **Charcoal** (near-black, `#2B2F36` range) unstructured blazer, no pocket square, no lapel pin | Premium without a tie; charcoal is darker than the background so the silhouette still reads |
| **Never** | Navy, teal, cyan, green, black shirts; patterns, logos, hoodies, polos, t-shirts | Navy and teal clothing merges with the background and the accent glow; patterns moiré at 1080p |
| **Framing** | Medium shot, chest up, presenter in the right third of the frame, slight left of the key light | Leaves the left two thirds for lower thirds, code call-outs and picture-in-picture |
| **Background** | `studio-navy.png`: Deep Navy `#0A1628` gradient, soft key light behind the presenter, teal glow low-left, 6 px teal rule at the bottom, faint 96 px grid | Matches every slide, diagram and deck in the three courses (`10-graphics/design-system.md`) |
| **Lighting in the look** | Soft frontal key, slight rim light on the presenter's right shoulder | Matches the key-light position painted into the background so the composite looks lit, not pasted |

## How to create the look in HeyGen

Do this once, on the laptop, before the Section 3 pilot. Field names below are from HeyGen's Avatar Looks documentation and are flagged "verify" against the current reference.

1. **Pick or create the base avatar** (your photo avatar or a stock one) and note its look id. This is the identity reference.
2. **Generate the course look** from that identity with a prompt, in HeyGen Studio ("Looks" on the avatar page) or via the API (`POST /v3/avatars/looks` with `type: "prompt"`, `avatar_id: <base look id>` and a prompt). Prompt to use:

   > Same person. Medium shot, chest up, facing camera, slight friendly smile. Wearing a crisp white slim-fit dress shirt with an open collar, no tie, under a charcoal unstructured blazer. Soft studio key light from the front-left, subtle rim light on the right shoulder. Plain deep navy studio background. Photorealistic, 4K, no text, no logos, no props.

   Generate the alternate with "light slate-blue dress shirt" in place of white.
3. **Save the new look's id** (the `avatar_item.id` / look id in the response, or from the Looks page) and export it as `HEYGEN_AVATAR_ID`. Record the look's **name** here, not the id.
4. **Upload the background** once: `python voice-ai-agents-course/09-production/tools/heygen_batch.py upload-background 09-heygen/backgrounds/studio-navy.png`, then export `HEYGEN_BACKGROUND_IMAGE=<asset id>`. The generate call composites the look over this PNG, so the look's own background is replaced; keep it plain navy anyway so the matte edge is clean.
5. **Test render**: `python heygen_batch.py generate 09-production/scenes/section-03.json --limit 1` (Course 3 lecture 3.3 hook). Check: white shirt not clipping, collar edge clean against the navy, key light on the background behind the shoulder, teal rule visible at the bottom, lower-third area clear.
6. If approved, record the look name and background file below, rename this file to `avatar-config.md`, and generate Section 3 in full before anything else (`PRODUCTION-GUIDE.md`).

## Record of the approved look

| Field | Value |
|---|---|
| Avatar name | PENDING |
| Look name | PENDING ("Course look v2, white shirt" once approved) |
| Shirt used | white / slate blue (circle one after the test render) |
| Background file | `09-heygen/backgrounds/studio-navy.png` |
| Approved on | PENDING |

## Action Items

1. Course owner selects the avatar and the voice (`../voice-config/PENDING.md`) together.
2. Create the course look (above) and upload the background.
3. Set `HEYGEN_API_KEY`, `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID`, `HEYGEN_BACKGROUND_IMAGE` in the shell (or an untracked `.env`).
4. Pilot one scene, then Section 3, then the rest one section at a time.
