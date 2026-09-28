# Course Image Brief

**Course:** AI Agent Observability & Cost Control: LLMOps in Production
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

- **Little or no text.** Udemy's guidelines have discouraged text on course images (the title already shows next to the image). If you use any text, keep it to one or two short words, large and legible. **Default: no text.** A single currency glyph or number inside the illustration is treated as part of the artwork, not text, but keep it to one element.
- **No logos.** No Udemy logo, and no third-party brand logos (Langfuse, OpenTelemetry, Grafana, Prometheus, OpenAI, LiteLLM, Datadog, LangSmith, Arize). Using them can imply endorsement and may break trademark rules. Show generic visuals of the concepts instead: a trace waterfall, a cost meter, a dashboard panel.
- **No borders or frames** around the image.
- **Relevant and high quality.** The image should show what the course teaches. No blurry, pixelated, stretched or watermarked stock images. No generic "robot brain" stock art.
- **No misleading elements.** No fake "Bestseller" badges, star ratings, prices or "free" labels. No realistic invoice or bank statement, which could read as a real document.
- **Appropriate content.** No provocative imagery. People shown must be licensed stock or the instructor, with rights secured.
- **Distinct from other courses.** It must be recognisably part of the series (same palette and style as Courses 1-3) but not identical to them.

## 3. Color palette (from `../../10-graphics/design-system.md`)

| Role | Name | Hex | Use in the image |
|---|---|---|---|
| Background | Deep Navy | `#0A1628` | Dominant canvas (≥ 60% of the area) |
| Elevated surface | Navy Light | `#1A2742` | Cards, dashboard panels, span bars' track |
| Primary accent | Electric Teal | `#00D4AA` | Healthy spans, the "after" bar, active path |
| Glow | Teal Glow | `#00D4AA33` | Soft glow behind the focal element |
| Secondary accent | Warm Amber | `#FFB020` | The cost or latency marker: one amber element only |
| Failure | Alert Red | `#FF4B4B` | The one runaway span or the "before" bar. Use sparingly; it is the story, not the mood |
| Neutral | Cool Gray | `#94A3B8` | Secondary UI lines, inactive spans, axis ticks |
| Highlight | White | `#FFFFFF` | Small specular highlights only |

Rules carried over from the design system: never pure black; red only for failures; teal never on a white background.

**Series recognition:** use the same Deep Navy + Electric Teal base as Courses 1-3. For Course 4, the **trace waterfall** is the signature element, the way Course 3 uses the voice waveform and Course 2 uses evaluation/check visuals. Someone who has seen the three earlier thumbnails should read this one as "the same series, the operate step".

## 4. Three concepts

### Concept A: "The Waterfall and the Meter" (recommended)

- **Composition:** a trace waterfall fills the left two-thirds: eight to ten horizontal span bars stepping down and right (agent → retriever → generation → tool → generation…), Navy Light tracks with teal fills. One bar near the bottom is longer than the rest and Alert Red: the runaway step. To the right, a compact circular cost meter (Navy Light dial, teal arc, one amber needle) sits at about the same height as the red bar, as if the red span pushed the needle up.
- **Story:** this is what an agent run looks like when you can see it, and one step is where the money went.
- **Text:** none. The meter has no digits.
- **Why:** reads at small size (teal bars on dark navy with one red bar), shows "trace + cost" in one glance, has no logos, and is unmistakably the observability course next to Course 3's waveform.

### Concept B: "Before / After"

- **Composition:** two vertical bars centred, Navy Light tracks. The left bar is tall and Alert Red with a small flame-like taper at the top; the right bar is short and Electric Teal. A thin amber dashed line crosses both at the height of the teal bar (the budget). Behind them, a faint grid suggesting a dashboard.
- **Story:** cost before and after; the budget line the course teaches you to hold.
- **Text:** optional single glyph "$" inside the red bar (skip it if Udemy flags text).
- **Risk:** reads as a generic "savings" image; without the waterfall it could be any FinOps course.

### Concept C: "The Ops Console" (illustrated)

- **Composition:** a stylised laptop at a 3/4 angle showing a four-panel dashboard: a waterfall (teal with one red span), a cost line trending down after a marked point, a p95 line with an amber threshold, and a small green/teal "SLO" gauge. A soft teal glow behind the laptop. No brand chrome on the laptop.
- **Story:** the capstone: the Atlas Ops Console.
- **Text:** none.
- **Risk:** four panels at 240 × 135 px become noise. Needs the waterfall panel to be at least half the screen area to survive the small-size test.

## 5. Production checklist

- [ ] Build in Figma at 1500 × 844; export 750 × 422
- [ ] No logos, no borders, no fake badges; text-free (or at most one glyph)
- [ ] Legible at 240 × 135 (mobile search card): the red span and the meter must still read
- [ ] Tested next to the Course 1, 2 and 3 images: same family, clearly distinct (waterfall vs waveform vs checks)
- [ ] Stock assets licensed for commercial use; licence saved to `11-course-assets/` equivalent for this course
- [ ] Upload preview checked on desktop, in the mobile app and in search results after publishing
- [ ] A/B plan: keep Concept B as the alternative to test after 30 days if the click-through rate from search looks weak (compare in the instructor dashboard traffic reports, if available)
