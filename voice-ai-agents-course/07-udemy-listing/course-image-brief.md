# Course Image Brief

**Course:** Production Voice AI Agents with Python: Build, Test, Deploy
**Deliverable:** Udemy course image (thumbnail shown in search, on the landing page and in the Udemy apps)

---

## 1. Technical spec

| Property | Value |
|---|---|
| Size | **750 × 422 px** (16:9). Design at 1500 × 844 (2×) and export down |
| Format | .jpg, .jpeg, .gif or .png (verify the formats Udemy accepts); export PNG or high-quality JPG |
| Color space | sRGB |
| Safe area | Keep the focal subject inside the centre 80%. Udemy overlays badges (e.g., "Bestseller", "Highest rated") and the apps crop slightly |
| Small-size test | Must read clearly at ~240 × 135 px (search-result card on mobile). Check it by zooming out to 25% |

## 2. Udemy image rules to design against

> **Per Udemy image quality standards, verify.** The standards below are how the author understands Udemy's course image guidelines. Check the current guidelines in the Teaching Center before final export, because Udemy may reject images or ask for changes.

- **Little or no text.** Udemy's guidelines have discouraged text on course images (the title already shows next to the image). If you use any text, keep it to one or two short words, large and legible. **Default: no text.**
- **No logos.** No Udemy logo, and no third-party brand logos (LiveKit, OpenAI, Twilio, Deepgram, Cartesia, Pipecat). Using them can imply endorsement and may break trademark rules. Show generic visuals of the concepts instead.
- **No borders or frames** around the image.
- **Relevant and high quality.** The image should show what the course teaches. No blurry, pixelated, stretched or watermarked stock images.
- **No misleading elements.** No fake "Bestseller" badges, star ratings, prices or "free" labels.
- **Appropriate content.** No provocative imagery. People shown must be licensed stock or the instructor, with rights secured.
- **Distinct from other courses.** It must be recognisably part of the series (same palette and style as Courses 1 and 2) but not identical to them.

## 3. Color palette (from `10-graphics/design-system.md`)

| Role | Name | Hex | Use in the image |
|---|---|---|---|
| Background | Deep Navy | `#0A1628` | Dominant canvas (≥ 60% of the area) |
| Elevated surface | Navy Light | `#1A2742` | Cards, phone body, UI panels |
| Primary accent | Electric Teal | `#00D4AA` | Voice waveform, active path, "pass" states |
| Glow | Teal Glow | `#00D4AA33` | Soft glow behind the waveform |
| Secondary accent | Warm Amber | `#FFB020` | Use sparingly: a latency or timing marker only |
| Neutral | Cool Gray | `#94A3B8` | Secondary UI lines, inactive nodes |
| Highlight | White | `#FFFFFF` | Small specular highlights only |

Rules carried over from the design system: never pure black; Alert Red `#FF4B4B` only for failures (avoid it on the thumbnail); teal never on a white background.

**Series recognition:** use the same Deep Navy + Electric Teal base as Courses 1 and 2. For Course 3, the **waveform/voice motif** is the signature element, the way Course 2 uses evaluation/check visuals.

## 4. Three concepts

### Concept A: "The Waveform Call" (recommended)

- **Composition:** a smartphone at a slight 3/4 angle, left of centre (Navy Light body, no brand features), showing an active-call screen with no number, only a generic avatar circle. A bright teal **voice waveform** flows out of the phone to the right, turning into a clean node chain (mic → ear → brain → speaker, as simple glyph icons) that ends at a small calendar card with one teal-highlighted slot.
- **Story:** a phone call becomes an agent that does real work (books the appointment).
- **Text:** none.
- **Why:** reads at small size (bright waveform on dark navy), shows "voice + phone + action", and has no logos.

### Concept B: "Latency Timeline"

- **Composition:** a horizontal turn-taking timeline across the frame: a teal waveform ("caller") on the top track, a second waveform ("agent") on the bottom track, a narrow amber bracket marking the gap between them, and a small stopwatch glyph.
- **Story:** timing and turn-taking, the engineering problem the course solves.
- **Text:** optional single word "LIVE" in a small pill (skip it if Udemy flags text).
- **Risk:** more abstract, so beginners may not see "phone agent" at a glance.

### Concept C: "Riley at the Desk" (illustrated)

- **Composition:** a flat-vector illustrated reception desk (dental clinic cues: a tooth-shaped plant pot, an appointment book) with a friendly abstract "AI" presence shown as a glowing teal orb with a waveform, and a desk phone. Navy background, teal glow.
- **Story:** the running example, an AI receptionist.
- **Text:** none.
- **Risk:** could read as "healthcare course" or "no-code course". It needs a small code bracket `</>` motif on a monitor to signal Python.

## 5. Production checklist

- [ ] Build in Figma at 1500 × 844; export 750 × 422
- [ ] No logos, no borders, no fake badges; text-free (or at most two words)
- [ ] Legible at 240 × 135 (mobile search card)
- [ ] Tested next to the Course 1 and Course 2 images: same family, clearly distinct
- [ ] Stock assets licensed for commercial use; licence saved to `11-course-assets/` equivalent for this course
- [ ] Upload preview checked on desktop, in the mobile app and in search results after publishing
- [ ] A/B plan: keep Concept B as the alternative to test after 30 days if the click-through rate from search looks weak (compare in the instructor dashboard traffic reports, if available)
