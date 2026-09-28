# Udemy Publish Checklist

> Work through this list before you press **Submit for Review**. The Udemy minimums quoted here are as the author understands Udemy's course quality checklist. **Udemy updates these rules, so confirm each one in the Teaching Center and in the "Submit for review" validator in course management.** Items marked (verify) especially need checking.

---

## 0. Pre-flight: curriculum reconciliation

- [ ] **Counts per curriculum v1.1:** "97 lectures, ~11.3 h video". Script count of the section tables: **115 items = 97 lectures** (89 video lectures: 47 screencast, 26 slide, 9 demo, 7 talking-head; 7 labs; 1 challenge, 5.9) **+ 13 quizzes** (12 section quizzes + the practice test) **+ 5 assignments** (4.7, 5.8, 8.7, 9.11, 13.7).
- [ ] **Runtime to reconcile:** the table minutes for the 89 video lectures add up to **687 min (≈11.5 h)**, and 693 min with the 5.9 challenge, while the curriculum header says ≈11.3 h. Use the figure Udemy shows after upload in any public copy. The description says "about 11.3 hours", so update it if the real total differs by more than ~15 min.
- [ ] **Part A / Part B splits** (5.3, 7.5, 8.2, 9.3, 13.2, 13.5) raise the uploaded lecture count by 6 (to about 103 lecture items in Udemy). Udemy counts uploaded items, so don't quote a lecture count in the promo video or social posts. Quote hours instead.
- [ ] Earlier drafts quoted "78 lectures" (v1.0). Search all copy for "78" and "10.5" and remove any leftovers.
- [ ] Section and lecture titles in Udemy match `01-curriculum/curriculum.md` IDs and titles exactly (prefix titles with IDs, e.g., "3.3 Code-along: hello Riley in 30 lines", if you want students to match them to repo files)
- [ ] Every lecture's code references match `03-code/` paths

## 1. Udemy minimum requirements (verify current numbers)

- [ ] **At least 30 minutes of video content** (this course: ~687 min of video lectures)
- [ ] **At least 5 lectures** (this course: 97 lectures, 89 of them video)
- [ ] **Video at least 720p HD**. We export 1920×1080, H.264, 30 fps (per `09-heygen/PRODUCTION-GUIDE.md`)
- [ ] **Audio:** clear, no echo, no background noise, both channels, consistent loudness (-16 LUFS target), with no silent gaps longer than a few seconds except in intentional demo pauses
- [ ] Every video lecture has an **instructional** purpose. No lecture is only a promo
- [ ] Course isn't a duplicate of other published courses by the instructor (it reuses concepts from Course 2 but not footage)
- [ ] Paid course meets Udemy's minimum paid-course video length (historically 30 min; verify)

## 2. Video and audio quality (spot-check every section)

- [ ] Picture: 1080p, no letterboxing, no pixelation, consistent frame rate
- [ ] Screen recordings: code font legible on a 13" laptop at 1080p (JetBrains Mono ≥ 18 pt equivalent; see `09-production/recording-guide.md`)
- [ ] Audio: mono voice centred, stereo mix, -16 LUFS integrated, true peak ≤ -1 dBTP, music ≤ -24 LUFS under voice
- [ ] Phone-call demos: audio audible and intelligible; the caller's number, caller ID and API keys never visible
- [ ] Avatar scenes: lip sync correct, no artefacts, pronunciation checked for LiveKit, Pipecat, Deepgram, Cartesia, Silero, SIP, WER, TTFT, TTFB and Maple Street
- [ ] No uploaded video longer than ~10 min after the Part A/B splits (the curriculum's longest, 13.2 at 15 min, is split)

## 3. Captions and accessibility

- [ ] English captions on every video lecture (Udemy auto-captions reviewed and corrected, or script-based captions uploaded)
- [ ] Domain terms spelled correctly in captions (see the glossary in `10-resources/glossary.md`)
- [ ] Diagrams described in narration, so meaning doesn't depend on seeing them
- [ ] Color never the only signal (pass/fail also uses ✓/✗ glyphs or labels)
- [ ] Downloadable resources are text-based Markdown/PDF (screen-reader friendly)

## 4. Curriculum content in Udemy

- [ ] **Lecture descriptions** entered for every lecture (from `lecture-descriptions.md`)
- [ ] **Resources attached** per `resources-per-lecture.md` (downloads plus external links to the course repo where Udemy allows external resource links; verify)
- [ ] Section titles are descriptive and keyword-bearing (e.g., "Testing and Evaluating Voice Agents")
- [ ] Lecture 1.1 marked as **free preview**. Also consider 1.2, 1.4, 2.6, 3.9 and 9.1 (Udemy allows a limited share of free preview content; verify)
- [ ] Labs uploaded as video walkthrough + article/resource with the lab Markdown

## 5. Quizzes, practice test, coding exercises, assignments

- [ ] 12 section quizzes created (S1, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S14). Every question has an explanation for the correct and incorrect answers
- [ ] **Practice test** (15.2): 40 questions, pass mark and time limit set, and each question has an explanation plus a "related lecture" reference
- [ ] **Coding exercises**: 5 pure-Python exercises (scheduler, WER, PII, latency percentile, cost/min)
  - [ ] Each exercise has instructions, starter code, a solution and hidden tests
  - [ ] Runs in Udemy's in-browser environment: **no network, no third-party packages**, compatible Python version (verify runner version)
  - [ ] Tested by solving each exercise from a student account view
- [ ] **Assignments**: 4.7 Challenge (Riley for your business), Project 1 (5.8), Project 2 (8.7, including the no-phone-number path), Project 3 (9.11), 13.7 Domain swap, plus the capstone brief. Each has instructions, questions and the instructor's example solution
- [ ] **5.9 Challenge (type CE)** depends on `livekit-agents`, so it **can't run in Udemy's in-browser coding exercise runner**. Publish it as a video lecture with a clear pause card and repo links. Optionally add a pure-Python Udemy coding exercise for `scheduler.add_to_waitlist` alongside it
- [ ] **13.1a capstone gate** placed directly before the reference-solution lectures (13.2 onwards)

## 6. Landing page

- [ ] Title ≤ 60 chars and subtitle ≤ 120 chars (`title-and-subtitle.md`, verified by script)
- [ ] Description ≥ 200 words (Udemy minimum, verify); ours is ~970 words (`course-description.md`)
- [ ] 4+ learning objectives, each ≤ 160 chars (ours: 10, verified)
- [ ] Requirements and "who this course is for" filled in
- [ ] Language, level, category, subcategory and primary topic set (`course-settings.md`)
- [ ] Course image 750×422, meets image standards (`course-image-brief.md`)
- [ ] Promo video uploaded and processed (`promo-video-script.md`)
- [ ] Instructor profile complete: photo, headline, bio with real credentials (`instructor-bio.md`)
- [ ] Read the whole landing page in preview mode on desktop and mobile. Check for typos, and that there are no placeholder brackets `[ ]`

## 7. Pricing, promotions and payouts

- [ ] **Premium instructor application approved** (needed to sell paid courses; verify current process)
- [ ] **Payout method** set up (PayPal/Payoneer or current options; verify) and **tax forms** submitted
- [ ] Price tier set (`course-settings.md` §4)
- [ ] Decision made on opting in or out of Udemy promotional programs (verify current program names and terms)
- [ ] Launch coupons drafted but **not created until verified** against current coupon rules (`course-settings.md` §5)

## 8. Messages and communication

- [ ] Welcome message and congratulations message entered, each under 1,000 characters (`welcome-and-congratulations-messages.md`)
- [ ] Q&A on; pinned setup and troubleshooting posts drafted (from `10-resources/troubleshooting.md`); 5 likely questions per section seeded on launch day; pinned "version pins and breaking changes" thread
- [ ] Direct messages on
- [ ] Launch educational announcement drafted

## 9. Policy compliance

### Promotional policy (verify current Trust & Safety / promotional guidelines)

- [ ] No external links, coupons, promotional content or contact details in lecture videos, captions, lecture descriptions, quizzes, messages, Q&A or resources. The **only exception is the final bonus lecture (15.3)**, within Udemy's bonus-lecture rules
- [ ] Bonus lecture (15.3) is the last lecture, is labelled "Bonus", and follows the current rules on what may be linked (Udemy courses with coupons; limits on off-platform links and lead capture; verify)
- [ ] The course repo is referenced as a required learning resource, not as a marketing funnel. If the repo README links to other courses, check this is allowed when linked from within Udemy (verify)
- [ ] No request for reviews in exchange for anything; no "please rate 5 stars"
- [ ] No collection of student emails or personal data through the course

### AI-generated content disclosure (avatar-narrated lectures)

> **Flag: verify Udemy's current policy on AI-generated content, AI avatars and synthetic voices before submission.** Udemy has published guidance on generative-AI use in course creation, and the rules may require disclosure, human instructor presence, or quality thresholds for AI-narrated content.

- [ ] Read Udemy's current AI content policy and record the date checked: `____`
- [ ] Decide on disclosure: at minimum, state in the description, or in lecture 1.5, that "lectures are presented by an AI avatar of the instructor (HeyGen) from instructor-written scripts; all code demos are real recordings"
- [ ] The instructor has rights to their avatar and voice clone (HeyGen consent and verification done in HeyGen). **No avatar or voice resembles a real person other than the instructor**
- [ ] The promo video and lecture 1.1 include real instructor presence where possible (see `promo-video-script.md`)
- [ ] AI-generated scripts, images and captions have been **reviewed by the instructor for accuracy**, especially the API calls (curriculum §6) and the compliance statements
- [ ] Riley's voice (a TTS voice from Cartesia or OpenAI) is clearly a product demo, not presented as a human. This matches the course's own AI-disclosure lesson (4.5, 8.6)

### Content and legal

- [ ] Compliance lecture (8.6) and checklist are labelled "not legal advice"
- [ ] Careers lecture (15.4) and `interview-questions.md` contain **no salary figures** and no promotional content
- [ ] 9.14 LiveKit Simulations: availability and pricing verified; if not available on the free tier, the lecture says so (demo-only)
- [ ] 7.8 multilingual audio and captions checked by native speakers (Spanish, Hindi) or labelled as machine-generated
- [ ] No real patient data, phone numbers or PHI anywhere; Maple Street Dental is fictional and labelled as such
- [ ] Third-party trademarks used descriptively only; no logos in the course image
- [ ] Music and stock assets licensed; licences archived

## 10. Final review

- [ ] One full pass in student preview mode, watching every lecture at 1.5× at minimum
- [ ] Repo freshly cloned on a clean machine: `make install`, `make test` pass; agent tests pass with keys
- [ ] Version banner shown: "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12"
- [ ] `09-production/qa-checklist.md` signed off per lecture
- [ ] Submit for review. Record the submission date and any reviewer feedback in `CHANGELOG`
