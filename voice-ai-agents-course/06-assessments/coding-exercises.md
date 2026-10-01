# Udemy Coding Exercises (5)

Five in-browser Python exercises for Udemy's coding exercise feature. Each one is a pure-Python slice of the Riley code base (`03-code/src/maple/`), so students practise the exact business logic the agent relies on without API keys, audio or third-party packages.

| # | Exercise | Student file | Placement (after lecture) | Related lectures | Tests |
|---|---|---|---|---|---|
| CE1 | Find open appointment slots | `scheduler.py` | 5.2 | 5.2, 5.3 | 11 |
| CE2 | Word error rate from scratch | `wer.py` | 9.7 | 9.7 | 10 |
| CE3 | Redact PII from transcripts | `pii.py` | 11.3 | 11.3, 10.3 | 9 |
| CE4 | Latency percentiles and a budget gate | `latency.py` | 9.8 | 1.4, 9.8, 10.5 | 11 |
| CE5 | Cost per minute | `costs.py` | 10.4 | 10.4, 6.4 | 7 |

## How to enter these in Udemy

For each exercise: Curriculum → **+ Curriculum item** → **Coding Exercise** → language **Python 3**. Then fill:

| Udemy field | What to paste from this file |
|---|---|
| Title | The exercise title |
| Learning objective | The "Learning objective" line |
| Instructions (tab 1) | The "Instructions" block |
| Solution file | The "Solution" code, using the file name shown |
| Evaluation file | The "Tests" code (Python `unittest`; class name `Evaluate`) |
| Starter code / student file | The "Starter code" block, using the same file name as the solution |
| Hints | The "Hints" list |
| Solution explanation | The "Solution explanation" paragraph |
| Related lectures | The lecture IDs listed |

Constraints respected: standard library only (`re`, `math`), Python 3.11 syntax, no file or network I/O, each test finishes in milliseconds.

**Verification.** Every solution was run against its evaluation file with `python3 -m unittest` on Python 3.11 (all 48 tests pass), and every starter file was run against the same tests to confirm it imports cleanly and fails (so students start red). Re-run the check with the script in the appendix after any edit.

---

## CE1: Find Open Appointment Slots

**Related lectures:** 5.2 The clinic scheduler: pure Python first; 5.3 Code-along: check availability and book
**Learning objective:** Implement the half-open interval logic behind Riley's `find_available_slots` tool and cap the result so the voice answer stays short.

### Instructions

Riley's `find_available_slots` tool calls a pure-Python function that works out which start times are free on a given day. Implement three functions in `scheduler.py`:

1. `to_minutes("HH:MM")` returns minutes after midnight. Raise `ValueError` for anything that is not a valid 24-hour time (`"24:00"`, `"09:60"`, `"0930"`, `"nine"`).
2. `to_hhmm(minutes)` returns a zero-padded `"HH:MM"` string.
3. `find_available_slots(open_time, close_time, booked, duration_minutes, step_minutes=15, limit=None)` returns the list of free start times:
   - Candidate starts are `open_time`, `open_time + step`, `open_time + 2*step`, and so on.
   - A slot must finish at or before `close_time`.
   - A slot must not overlap any `(start, end)` pair in `booked`. Intervals are **half-open**: a booking ending at 10:00 leaves 10:00 free.
   - `booked` may be in any order.
   - Return at most `limit` slots. On the phone, three options is plenty; reading out twelve is a bad caller experience.
   - Raise `ValueError` if `duration_minutes` or `step_minutes` is not positive, `limit` is less than 1, or `close_time` is not after `open_time`.

Example: `find_available_slots("09:00", "11:00", [("09:30", "10:00")], 30, step_minutes=30)` returns `["09:00", "10:00", "10:30"]`.

### Starter code (`scheduler.py`)

```python
"""Maple Street Dental: find open appointment slots (pure Python, no dependencies)."""


def to_minutes(hhmm: str) -> int:
    """Convert "HH:MM" (24-hour clock) to minutes after midnight.

    Raise ValueError for malformed or out-of-range times.
    """
    # TODO
    raise NotImplementedError


def to_hhmm(minutes: int) -> str:
    """Convert minutes after midnight back to zero-padded "HH:MM"."""
    # TODO
    raise NotImplementedError


def find_available_slots(open_time, close_time, booked, duration_minutes,
                         step_minutes=15, limit=None):
    """Return start times ("HH:MM") where a new appointment fits.

    - Candidate starts: open_time, open_time + step, open_time + 2*step, ...
    - A slot must end at or before close_time.
    - A slot must not overlap any (start, end) pair in `booked`.
      Intervals are half-open: a booking ending at 10:00 leaves 10:00 free.
    - `booked` may be unsorted.
    - Return at most `limit` slots (None = no limit).
    - Raise ValueError if duration/step <= 0, limit < 1, or close <= open.
    """
    # TODO
    raise NotImplementedError
```

### Solution (`scheduler.py`)

```python
"""Maple Street Dental: find open appointment slots (pure Python, no dependencies)."""


def to_minutes(hhmm: str) -> int:
    """Convert "HH:MM" (24-hour clock) to minutes after midnight."""
    parts = hhmm.split(":")
    if len(parts) != 2:
        raise ValueError(f"expected HH:MM, got {hhmm!r}")
    hours, minutes = int(parts[0]), int(parts[1])
    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        raise ValueError(f"time out of range: {hhmm!r}")
    return hours * 60 + minutes


def to_hhmm(minutes: int) -> str:
    """Convert minutes after midnight back to zero-padded "HH:MM"."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def find_available_slots(open_time, close_time, booked, duration_minutes,
                         step_minutes=15, limit=None):
    """Return start times ("HH:MM") where a new appointment fits.

    A slot [start, start + duration) is available when it lies inside opening
    hours and does not overlap any booked (start, end) interval. Intervals are
    half-open, so a booking that ends at 10:00 leaves 10:00 free.
    Candidate starts are open_time, open_time + step, open_time + 2*step, ...
    At most `limit` slots are returned (None means no limit).
    """
    if duration_minutes <= 0 or step_minutes <= 0:
        raise ValueError("duration_minutes and step_minutes must be positive")
    if limit is not None and limit < 1:
        raise ValueError("limit must be at least 1")
    day_start, day_end = to_minutes(open_time), to_minutes(close_time)
    if day_end <= day_start:
        raise ValueError("close_time must be after open_time")

    busy = sorted((to_minutes(s), to_minutes(e)) for s, e in booked)

    slots = []
    start = day_start
    while start + duration_minutes <= day_end:
        end = start + duration_minutes
        if all(end <= b_start or start >= b_end for b_start, b_end in busy):
            slots.append(to_hhmm(start))
            if limit is not None and len(slots) == limit:
                break
        start += step_minutes
    return slots
```

### Tests (evaluation file `test_scheduler.py`)

```python
import unittest

from scheduler import find_available_slots, to_hhmm, to_minutes


class Evaluate(unittest.TestCase):
    def test_to_minutes(self):
        self.assertEqual(to_minutes("00:00"), 0)
        self.assertEqual(to_minutes("09:30"), 570)
        self.assertEqual(to_minutes("17:05"), 1025)

    def test_to_minutes_rejects_bad_input(self):
        for bad in ["24:00", "09:60", "0930", "nine"]:
            with self.assertRaises(ValueError, msg=bad):
                to_minutes(bad)

    def test_to_hhmm_zero_pads(self):
        self.assertEqual(to_hhmm(570), "09:30")
        self.assertEqual(to_hhmm(65), "01:05")

    def test_empty_day_returns_every_step(self):
        self.assertEqual(
            find_available_slots("09:00", "10:00", [], 30),
            ["09:00", "09:15", "09:30"],
        )

    def test_slot_must_end_by_closing_time(self):
        self.assertEqual(find_available_slots("16:00", "17:00", [], 60), ["16:00"])
        self.assertEqual(find_available_slots("16:00", "16:30", [], 60), [])

    def test_booked_interval_blocks_overlapping_slots(self):
        booked = [("09:30", "10:00")]
        self.assertEqual(
            find_available_slots("09:00", "11:00", booked, 30, step_minutes=30),
            ["09:00", "10:00", "10:30"],
        )

    def test_adjacent_bookings_are_allowed(self):
        booked = [("09:00", "09:30"), ("10:00", "10:30")]
        self.assertEqual(
            find_available_slots("09:00", "10:30", booked, 30, step_minutes=15),
            ["09:30"],
        )

    def test_unsorted_bookings(self):
        booked = [("11:00", "11:30"), ("09:00", "10:00")]
        self.assertEqual(
            find_available_slots("09:00", "12:00", booked, 60, step_minutes=30),
            ["10:00"],
        )

    def test_limit_keeps_voice_answers_short(self):
        self.assertEqual(
            find_available_slots("09:00", "17:00", [], 30, step_minutes=30, limit=3),
            ["09:00", "09:30", "10:00"],
        )

    def test_fully_booked_day(self):
        self.assertEqual(
            find_available_slots("09:00", "12:00", [("08:00", "13:00")], 15), []
        )

    def test_invalid_arguments(self):
        with self.assertRaises(ValueError):
            find_available_slots("09:00", "17:00", [], 0)
        with self.assertRaises(ValueError):
            find_available_slots("09:00", "17:00", [], 30, step_minutes=0)
        with self.assertRaises(ValueError):
            find_available_slots("17:00", "09:00", [], 30)
        with self.assertRaises(ValueError):
            find_available_slots("09:00", "17:00", [], 30, limit=0)
```

### Hints

1. Convert everything to integer minutes first; compare integers, never strings.
2. Two half-open intervals `[a, b)` and `[c, d)` do **not** overlap when `b <= c or a >= d`.
3. A `while start + duration <= day_end` loop handles the closing-time rule for free.
4. Check `limit` right after appending, so you stop as soon as you have enough.

### Solution explanation

The solution normalises all times to minutes, sorts the bookings, and walks candidate start times in `step_minutes` increments. For each candidate it checks the half-open non-overlap condition against every booking. The `limit` parameter exists because Riley reads results aloud: the agent offers two or three options, not the whole day. Keeping this logic in `src/maple/scheduler.py` (not inside the agent) is what makes it unit-testable without an LLM. The repo's `ClinicScheduler.find_slots()` builds on exactly this idea, adding per-weekday opening hours, the lunch break, a booking window and parsing of phrases like "next Tuesday".

---

## CE2: Word Error Rate from Scratch

**Related lectures:** 9.7 Measuring STT accuracy with WER
**Learning objective:** Compute word error rate with a word-level edit distance and understand why normalisation changes the score.

### Instructions

WER is the standard metric for speech-to-text accuracy:

`WER = (substitutions + deletions + insertions) / number of words in the reference`

Implement in `wer.py`:

1. `normalize(text)` lowercases the text, replaces every character that is not a letter, digit, underscore, whitespace or apostrophe with a space, and splits on whitespace. `"Dr. O'Neil, 3:30!"` becomes `["dr", "o'neil", "3", "30"]`.
2. `word_error_rate(reference, hypothesis)` normalises both strings and returns the minimum number of word edits (Levenshtein distance over words) divided by the number of reference words.
   - Raise `ValueError` if the reference has no words after normalisation.
   - WER can be greater than 1.0 when the hypothesis contains many inserted words.

Do not import any third-party package (`jiwer` is not available in this runner). The course repo cross-checks this implementation against `jiwer` in `tests/unit/`.

### Starter code (`wer.py`)

```python
"""Word error rate (WER) in pure Python."""
import re


def normalize(text: str) -> list:
    """Return a list of lowercase words.

    Replace every character that is not a letter, digit, underscore,
    whitespace or apostrophe with a space, then split on whitespace.
    "Dr. O'Neil, 3:30!" -> ["dr", "o'neil", "3", "30"]
    """
    # TODO
    raise NotImplementedError


def word_error_rate(reference: str, hypothesis: str) -> float:
    """WER = (substitutions + deletions + insertions) / number of reference words.

    Compare normalized word lists with a word-level Levenshtein distance.
    Raise ValueError if the reference has no words.
    """
    # TODO
    raise NotImplementedError
```

### Solution (`wer.py`)

```python
"""Word error rate (WER) in pure Python."""
import re

_NOT_WORD = re.compile(r"[^\w\s']")


def normalize(text: str) -> list:
    """Lowercase, replace punctuation (except apostrophes) with spaces, split on whitespace."""
    return _NOT_WORD.sub(" ", text.lower()).split()


def word_error_rate(reference: str, hypothesis: str) -> float:
    """WER = (substitutions + deletions + insertions) / number of reference words."""
    ref = normalize(reference)
    hyp = normalize(hypothesis)
    if not ref:
        raise ValueError("reference must contain at least one word")

    # previous[j] = edit distance between the first i-1 reference words and first j hypothesis words
    previous = list(range(len(hyp) + 1))
    for i in range(1, len(ref) + 1):
        current = [i] + [0] * len(hyp)
        for j in range(1, len(hyp) + 1):
            cost = 0 if ref[i - 1] == hyp[j - 1] else 1
            current[j] = min(
                previous[j] + 1,         # deletion
                current[j - 1] + 1,      # insertion
                previous[j - 1] + cost,  # substitution or match
            )
        previous = current
    return previous[-1] / len(ref)
```

### Tests (evaluation file `test_wer.py`)

```python
import unittest

from wer import normalize, word_error_rate


class Evaluate(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize("Dr. O'Neil, 3:30!"), ["dr", "o'neil", "3", "30"])
        self.assertEqual(normalize("  Follow-up   CLEANING "), ["follow", "up", "cleaning"])

    def test_identical_is_zero(self):
        self.assertEqual(word_error_rate("book a cleaning", "book a cleaning"), 0.0)

    def test_case_and_punctuation_are_ignored(self):
        self.assertEqual(word_error_rate("Book a cleaning.", "book a CLEANING"), 0.0)

    def test_one_substitution(self):
        self.assertAlmostEqual(
            word_error_rate("i need a cleaning on tuesday", "i need a cleaning on thursday"),
            1 / 6,
        )

    def test_one_deletion(self):
        self.assertAlmostEqual(word_error_rate("see you next monday", "see you monday"), 0.25)

    def test_one_insertion(self):
        self.assertAlmostEqual(word_error_rate("cancel my appointment", "cancel my my appointment"), 1 / 3)

    def test_empty_hypothesis_is_all_deletions(self):
        self.assertEqual(word_error_rate("hello riley", ""), 1.0)

    def test_wer_can_exceed_one(self):
        self.assertEqual(word_error_rate("yes", "yes yes yes"), 2.0)

    def test_domain_term_split_by_stt(self):
        # "amoxicillin" heard as "a moxy cillin": 1 substitution + 2 insertions over 3 words
        self.assertAlmostEqual(
            word_error_rate("taking amoxicillin daily", "taking a moxy cillin daily"), 1.0
        )

    def test_empty_reference_raises(self):
        with self.assertRaises(ValueError):
            word_error_rate("", "anything")
        with self.assertRaises(ValueError):
            word_error_rate("?!", "")
```

### Hints

1. Build a table where cell `[i][j]` is the edit distance between the first `i` reference words and the first `j` hypothesis words.
2. Row 0 is `0, 1, 2, ...` (all insertions) and column 0 is `0, 1, 2, ...` (all deletions).
3. Each cell is the minimum of: the cell above + 1 (deletion), the cell to the left + 1 (insertion), and the diagonal + 0 or 1 (match or substitution).
4. You only need the previous row to compute the current one.
5. `re.sub(r"[^\w\s']", " ", text)` does most of the normalisation.

### Solution explanation

The solution is the classic dynamic-programming Levenshtein distance applied to word lists instead of characters, keeping only two rows in memory. Normalisation is what makes WER fair: without it, "Book a cleaning." and "book a CLEANING" would score as errors. The domain-term test shows why clinics care: an STT model that hears "amoxicillin" as "a moxy cillin" scores 100% WER on that short sentence, which is why lecture 9.7 adds keyterms for drug names and surnames. The repo's `maple.wer` adds two things on top of this exercise: a small replacement table ("dr" becomes "doctor", "appt" becomes "appointment") so formatting differences are not counted as recognition errors, and `wer_details()`, which reports substitutions, deletions and insertions separately.

---

## CE3: Redact PII from Transcripts

**Related lectures:** 11.3 PII redaction in transcripts and logs; 10.3 Tracing with OpenTelemetry and Langfuse
**Learning objective:** Redact phone numbers, emails, dates of birth and card numbers with regular expressions, using a Luhn check to avoid false positives.

### Instructions

Riley's transcripts go to logs and Langfuse traces. Before they leave the process, redact PII. Implement in `pii.py`:

1. `luhn_valid(number)` returns `True` when the digits in `number` (ignore spaces and dashes) pass the Luhn checksum. Return `False` for fewer than 13 or more than 19 digits.
2. `redact_pii(text)` returns the text with these replacements:

| Tag | What to match |
|---|---|
| `[EMAIL]` | `name@example.com`, including `+`, `.` and multi-part domains |
| `[CARD]` | 13 to 19 digits with optional single spaces or dashes between digits, **only if the digits pass Luhn** |
| `[DOB]` | `MM/DD/YYYY` (month and day may be one digit) or `YYYY-MM-DD`, years 1900 to 2099 |
| `[PHONE]` | US numbers: `5551234567`, `555-123-4567`, `555.123.4567`, `(555) 123-4567`, `+1 555 123 4567`, `1-555-123-4567` |

Everything else, including times like `3:30`, short numbers and ordinary words, must be left exactly as it was.

### Starter code (`pii.py`)

```python
"""Redact PII from call transcripts before they reach logs or traces."""
import re


def luhn_valid(number: str) -> bool:
    """True if the digits in `number` (spaces/dashes ignored) pass the Luhn check.

    Return False if there are fewer than 13 or more than 19 digits.
    """
    # TODO
    raise NotImplementedError


def redact_pii(text: str) -> str:
    """Replace PII with tags and return the new string.

    [EMAIL]  name@example.com
    [CARD]   13-19 digits, optional single spaces/dashes between digits,
             ONLY when the digits pass the Luhn check
    [DOB]    MM/DD/YYYY (month/day may be 1 digit) or YYYY-MM-DD, years 1900-2099
    [PHONE]  US numbers: 5551234567, 555-123-4567, 555.123.4567,
             (555) 123-4567, +1 555 123 4567, 1-555-123-4567

    Everything else must be left exactly as it was.
    """
    # TODO
    raise NotImplementedError
```

### Solution (`pii.py`)

```python
"""Redact PII from call transcripts before they reach logs or traces."""
import re

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
CARD_CANDIDATE = re.compile(r"(?<!\d)\d(?:[ -]?\d){12,18}(?!\d)")
DOB = re.compile(
    r"\b(?:(?:0?[1-9]|1[0-2])/(?:0?[1-9]|[12]\d|3[01])/(?:19|20)\d{2}"
    r"|(?:19|20)\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01]))\b"
)
PHONE = re.compile(
    r"(?<![\w+])(?:\+?1[ .-]?)?(?:\(\d{3}\)|\d{3})[ .-]?\d{3}[ .-]?\d{4}(?!\w)"
)


def luhn_valid(number: str) -> bool:
    """True if the digits in `number` (spaces/dashes ignored) pass the Luhn check."""
    digits = [int(ch) for ch in number if ch.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    total = 0
    for index, digit in enumerate(reversed(digits)):
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def _redact_card(match: re.Match) -> str:
    return "[CARD]" if luhn_valid(match.group(0)) else match.group(0)


def redact_pii(text: str) -> str:
    """Replace emails, card numbers, dates of birth and phone numbers with tags.

    Order matters: emails first (they can contain digits), then Luhn-valid
    card numbers, then dates, then phone numbers.
    """
    text = EMAIL.sub("[EMAIL]", text)
    text = CARD_CANDIDATE.sub(_redact_card, text)
    text = DOB.sub("[DOB]", text)
    text = PHONE.sub("[PHONE]", text)
    return text
```

### Tests (evaluation file `test_pii.py`)

```python
import unittest

from pii import luhn_valid, redact_pii


class Evaluate(unittest.TestCase):
    def test_luhn(self):
        self.assertTrue(luhn_valid("4111 1111 1111 1111"))
        self.assertTrue(luhn_valid("5555-5555-5555-4444"))
        self.assertFalse(luhn_valid("4111 1111 1111 1112"))
        self.assertFalse(luhn_valid("12345"))

    def test_email(self):
        self.assertEqual(
            redact_pii("Send it to jane.doe+dental@example.co.uk please"),
            "Send it to [EMAIL] please",
        )

    def test_phone_formats(self):
        for phone in ["5551234567", "555-123-4567", "555.123.4567",
                      "(555) 123-4567", "+1 555 123 4567", "1-555-123-4567"]:
            self.assertEqual(redact_pii(f"call me at {phone} today"),
                             "call me at [PHONE] today", msg=phone)

    def test_card_numbers_pass_luhn(self):
        self.assertEqual(
            redact_pii("my card is 4111 1111 1111 1111 thanks"),
            "my card is [CARD] thanks",
        )
        self.assertEqual(redact_pii("card 5555-5555-5555-4444"), "card [CARD]")

    def test_non_luhn_long_number_is_kept(self):
        text = "claim number 4111 1111 1111 1112"
        self.assertEqual(redact_pii(text), text)

    def test_dates_of_birth(self):
        self.assertEqual(redact_pii("born 7/4/1986"), "born [DOB]")
        self.assertEqual(redact_pii("DOB 1986-07-04."), "DOB [DOB].")

    def test_times_and_short_numbers_are_kept(self):
        text = "Your cleaning is at 3:30 on the 14th, room 12, 45 minutes."
        self.assertEqual(redact_pii(text), text)

    def test_mixed_transcript(self):
        text = ("I'm Sam, born 01/22/1990, reach me at (555) 867-5309 "
                "or sam@mail.com, card 4111-1111-1111-1111.")
        self.assertEqual(
            redact_pii(text),
            "I'm Sam, born [DOB], reach me at [PHONE] or [EMAIL], card [CARD].",
        )

    def test_clean_text_unchanged(self):
        text = "Can I book a cleaning next Tuesday morning?"
        self.assertEqual(redact_pii(text), text)
```

### Hints

1. Order matters. Redact emails first (they can contain digits), then cards, then dates, then phone numbers; otherwise a phone pattern can eat part of a card number.
2. `re.sub` accepts a function as the replacement. Use one for cards so you can return the original text when the Luhn check fails.
3. Luhn: from the rightmost digit, double every second digit; if the result is over 9, subtract 9; the sum must be divisible by 10.
4. Use lookarounds such as `(?<!\d)` and `(?!\d)` so you never match a phone number inside a longer digit string.

### Solution explanation

Each PII type has its own compiled pattern, applied in a fixed order. Card candidates are matched broadly and then filtered with the Luhn checksum, which keeps claim numbers and other long IDs intact. Phone matching uses lookarounds so it cannot start or end in the middle of a longer token. In production (lecture 11.3) the same function runs inside a log filter and before spans are exported, and STT output often spells numbers as words ("five five five"), so treat regex redaction as one layer of defence and ask your STT provider for digit formatting. The repo's `maple.pii` goes further than this exercise: it also redacts US social security numbers, only tags dates as `[DOB]` when they follow words like "born" or "date of birth", and ships a `PiiRedactingFilter` for Python logging. Handling numbers spoken as words ("five one two...") is a good stretch goal.

---

## CE4: Latency Percentiles and a Budget Gate

**Related lectures:** 1.4 The latency budget; 9.8 Latency testing against a budget; 10.5 Dashboards and alerts that matter
**Learning objective:** Compute p50/p95 latency with linear interpolation and fail a build when any component or the voice-to-voice total exceeds its budget.

### Instructions

Lecture 9.8 exports per-turn metrics from `metrics_collected` events. Each turn looks like `{"eou_delay": 0.45, "llm_ttft": 0.35, "tts_ttfb": 0.20}` (seconds). Implement in `latency.py`:

1. `percentile(values, p)` with linear interpolation (numpy's default): sort, compute `rank = (n - 1) * p / 100`, interpolate between the values at `floor(rank)` and `ceil(rank)`. Raise `ValueError` for an empty list or `p` outside 0 to 100.
2. `voice_to_voice(turn)` returns `eou_delay + llm_ttft + tts_ttfb` for one turn. (This approximates the silence the caller hears after they stop talking; network time is not included.)
3. `check_budget(turns, budget, p=95)`:
   - `budget` maps metric names to maximum seconds, for example `{"llm_ttft": 0.5, "voice_to_voice": 1.2}`. The special name `"voice_to_voice"` is computed per turn.
   - Skip turns that do not contain a metric.
   - A metric passes when its percentile is **less than or equal to** the budget.
   - Return `{"passed": bool, "violations": [...]}`. Each violation is `{"metric": name, "observed": value rounded to 3 dp, "budget": limit}`, sorted by metric name.
   - Raise `ValueError` if `turns` is empty.

### Starter code (`latency.py`)

```python
"""Latency percentiles and budget checks for voice agent turns (all values in seconds)."""
import math

COMPONENTS = ("eou_delay", "llm_ttft", "tts_ttfb")


def percentile(values, p):
    """Linear-interpolation percentile (same as numpy's default method).

    Sort the values, compute rank = (n - 1) * p / 100 and interpolate between
    the two neighbouring values. Raise ValueError for an empty list or p outside 0..100.
    """
    # TODO
    raise NotImplementedError


def voice_to_voice(turn):
    """Return turn["eou_delay"] + turn["llm_ttft"] + turn["tts_ttfb"]."""
    # TODO
    raise NotImplementedError


def check_budget(turns, budget, p=95):
    """Compare the p-th percentile of each budgeted metric with its limit.

    - `turns` is a list of dicts such as {"eou_delay": 0.4, "llm_ttft": 0.3, "tts_ttfb": 0.2}.
    - `budget` maps metric name -> max seconds. "voice_to_voice" is computed per turn.
    - Turns that lack a metric are skipped for that metric.
    - A metric passes when observed <= budget.
    - Return {"passed": bool, "violations": [...]}, where each violation is
      {"metric": name, "observed": p-th percentile rounded to 3 dp, "budget": limit},
      sorted by metric name.
    - Raise ValueError if `turns` is empty (or a metric has no samples).
    """
    # TODO
    raise NotImplementedError
```

### Solution (`latency.py`)

```python
"""Latency percentiles and budget checks for voice agent turns (all values in seconds)."""
import math

COMPONENTS = ("eou_delay", "llm_ttft", "tts_ttfb")


def percentile(values, p):
    """Linear-interpolation percentile (same as numpy's default method)."""
    if not values:
        raise ValueError("values must not be empty")
    if not 0 <= p <= 100:
        raise ValueError("p must be between 0 and 100")
    ordered = sorted(values)
    rank = (len(ordered) - 1) * p / 100
    low, high = math.floor(rank), math.ceil(rank)
    if low == high:
        return float(ordered[low])
    return ordered[low] + (ordered[high] - ordered[low]) * (rank - low)


def voice_to_voice(turn):
    """Approximate voice-to-voice latency for one turn: EOU delay + LLM TTFT + TTS TTFB."""
    return sum(turn[name] for name in COMPONENTS)


def check_budget(turns, budget, p=95):
    """Compare the p-th percentile of each budgeted metric with its limit.

    `budget` maps metric name -> max seconds. The special name "voice_to_voice"
    uses voice_to_voice(turn). A metric passes when observed <= budget.
    Returns {"passed": bool, "violations": [{"metric", "observed", "budget"}, ...]}
    with violations sorted by metric name and observed rounded to 3 decimals.
    """
    if not turns:
        raise ValueError("turns must not be empty")
    violations = []
    for metric in sorted(budget):
        if metric == "voice_to_voice":
            samples = [voice_to_voice(turn) for turn in turns]
        else:
            samples = [turn[metric] for turn in turns if metric in turn]
        observed = round(percentile(samples, p), 3)
        if observed > budget[metric]:
            violations.append({"metric": metric, "observed": observed, "budget": budget[metric]})
    return {"passed": not violations, "violations": violations}
```

### Tests (evaluation file `test_latency.py`)

```python
import unittest

from latency import check_budget, percentile, voice_to_voice

TURNS = [
    {"eou_delay": 0.40, "llm_ttft": 0.30, "tts_ttfb": 0.15},
    {"eou_delay": 0.45, "llm_ttft": 0.35, "tts_ttfb": 0.20},
    {"eou_delay": 0.50, "llm_ttft": 0.40, "tts_ttfb": 0.18},
    {"eou_delay": 0.55, "llm_ttft": 0.90, "tts_ttfb": 0.22},
    {"eou_delay": 0.60, "llm_ttft": 0.45, "tts_ttfb": 0.25},
]


class Evaluate(unittest.TestCase):
    def test_percentile_basic(self):
        self.assertEqual(percentile([1, 2, 3, 4, 5], 50), 3.0)
        self.assertEqual(percentile([5, 1, 4, 2, 3], 0), 1.0)
        self.assertEqual(percentile([5, 1, 4, 2, 3], 100), 5.0)

    def test_percentile_interpolates(self):
        self.assertAlmostEqual(percentile([1, 2, 3, 4], 50), 2.5)
        self.assertAlmostEqual(percentile([0.2, 0.4, 0.3, 1.0], 95), 0.91)
        self.assertAlmostEqual(percentile([10, 20], 90), 19.0)

    def test_percentile_single_value(self):
        self.assertEqual(percentile([0.7], 95), 0.7)

    def test_percentile_errors(self):
        with self.assertRaises(ValueError):
            percentile([], 50)
        with self.assertRaises(ValueError):
            percentile([1, 2], 101)

    def test_voice_to_voice(self):
        self.assertAlmostEqual(voice_to_voice(TURNS[0]), 0.85)

    def test_budget_passes(self):
        report = check_budget(TURNS, {"eou_delay": 0.6, "tts_ttfb": 0.3})
        self.assertEqual(report, {"passed": True, "violations": []})

    def test_budget_catches_llm_spike(self):
        report = check_budget(TURNS, {"eou_delay": 0.6, "llm_ttft": 0.5, "voice_to_voice": 1.2})
        self.assertFalse(report["passed"])
        self.assertEqual([v["metric"] for v in report["violations"]], ["llm_ttft", "voice_to_voice"])
        self.assertAlmostEqual(report["violations"][0]["observed"], 0.81)
        self.assertEqual(report["violations"][0]["budget"], 0.5)
        self.assertAlmostEqual(report["violations"][1]["observed"], 1.596)

    def test_p50_vs_p95(self):
        # the single slow turn breaks p95 but not p50
        self.assertTrue(check_budget(TURNS, {"llm_ttft": 0.5}, p=50)["passed"])
        self.assertFalse(check_budget(TURNS, {"llm_ttft": 0.5}, p=95)["passed"])

    def test_equal_to_budget_passes(self):
        self.assertTrue(check_budget([{"llm_ttft": 0.5}], {"llm_ttft": 0.5})["passed"])

    def test_missing_metric_values_are_skipped(self):
        turns = [{"llm_ttft": 0.3}, {"eou_delay": 0.4}, {"llm_ttft": 0.4}]
        self.assertTrue(check_budget(turns, {"llm_ttft": 0.4})["passed"])

    def test_empty_turns_raise(self):
        with self.assertRaises(ValueError):
            check_budget([], {"llm_ttft": 0.5})
```

### Hints

1. For `[1, 2, 3, 4]` and p=50, rank is 1.5, so the answer is halfway between 2 and 3.
2. `math.floor` and `math.ceil` give you the two neighbours; when they are equal, no interpolation is needed.
3. Iterate over `sorted(budget)` so violations come out in name order without a separate sort.
4. Round only the reported value, after computing the percentile.

### Solution explanation

The percentile function reproduces numpy's default linear method so results match the repo's `latency_report.py`. The budget check shows why averages lie: in the test data one slow LLM turn (0.9 s) leaves p50 comfortably inside the 0.5 s budget but pushes p95 to 0.81 s, and the voice-to-voice p95 to about 1.6 s. Callers remember the worst pauses, so CI gates on p95. The repo's `maple.latency` works in milliseconds, uses a `LatencyBudget` dataclass (default p95 budgets: EOU 700 ms, LLM TTFT 700 ms, TTS TTFB 300 ms, voice-to-voice 1,600 ms) and joins the stages of each turn on LiveKit's `speech_id`; the maths is identical.

---

## CE5: Cost per Minute

**Related lectures:** 10.4 Cost per minute: the number your boss will ask for; 6.4 Head-to-head: cascaded vs realtime
**Learning objective:** Turn a call's usage summary into a cost breakdown and a cost-per-minute figure, including cached prompt tokens.

### Instructions

At the end of each call, `session.usage` tells you how many tokens, audio seconds and characters each model used (the course's `usage_from_model_usage()` in `src/maple/costs.py` flattens it into the keys below). Implement `call_cost(usage, prices, call_seconds)` in `costs.py`.

`usage` keys (missing keys count as 0): `llm_prompt_tokens`, `llm_cached_tokens`, `llm_completion_tokens`, `stt_audio_seconds`, `tts_characters`.

`prices` keys (missing keys count as 0.0, for example no telephony on a web call): `llm_input_per_1m`, `llm_cached_input_per_1m`, `llm_output_per_1m`, `stt_per_minute`, `tts_per_1m_chars`, `telephony_per_minute`.

| Component | Formula |
|---|---|
| `llm` | (prompt − cached) × input rate + cached × cached rate + completion × output rate, all per 1M tokens. Cached tokens are a subset of prompt tokens. |
| `stt` | `stt_audio_seconds / 60 × stt_per_minute` |
| `tts` | `tts_characters / 1,000,000 × tts_per_1m_chars` |
| `telephony` | call minutes × `telephony_per_minute` |

Return `{"breakdown": {"llm", "stt", "tts", "telephony"}, "total": ..., "cost_per_minute": ...}`. Round each breakdown value and the total to 6 decimal places, and `cost_per_minute` (computed from the unrounded total) to 4. Raise `ValueError` if `call_seconds <= 0`, any usage value is negative, or cached tokens exceed prompt tokens.

The prices in the tests are illustrative. Real prices change often; the course repo keeps them in one table in `src/maple/costs.py`.

### Starter code (`costs.py`)

```python
"""Cost per minute for a cascaded voice agent call (STT -> LLM -> TTS + telephony)."""

USAGE_KEYS = (
    "llm_prompt_tokens", "llm_cached_tokens", "llm_completion_tokens",
    "stt_audio_seconds", "tts_characters",
)


def call_cost(usage, prices, call_seconds):
    """Return {"breakdown": {...}, "total": float, "cost_per_minute": float} in USD.

    usage keys  : see USAGE_KEYS (missing keys count as 0)
    prices keys : llm_input_per_1m, llm_cached_input_per_1m, llm_output_per_1m,
                  stt_per_minute, tts_per_1m_chars, telephony_per_minute
                  (missing keys count as 0.0, e.g. no telephony for web calls)

    llm       = uncached prompt tokens * input rate + cached tokens * cached rate
                + completion tokens * output rate   (rates are per 1M tokens;
                cached tokens are a subset of prompt tokens)
    stt       = stt_audio_seconds / 60 * stt_per_minute
    tts       = tts_characters * tts_per_1m_chars / 1M
    telephony = call minutes * telephony_per_minute

    Round each breakdown value and the total to 6 dp; cost_per_minute
    (unrounded total / call minutes) to 4 dp.
    Raise ValueError if call_seconds <= 0, any usage value is negative,
    or cached tokens exceed prompt tokens.
    """
    # TODO
    raise NotImplementedError
```

### Solution (`costs.py`)

```python
"""Cost per minute for a cascaded voice agent call (STT -> LLM -> TTS + telephony)."""

USAGE_KEYS = (
    "llm_prompt_tokens", "llm_cached_tokens", "llm_completion_tokens",
    "stt_audio_seconds", "tts_characters",
)


def call_cost(usage, prices, call_seconds):
    """Return {"breakdown": {...}, "total": float, "cost_per_minute": float} in USD.

    Missing usage keys or price keys count as 0. Cached prompt tokens are a
    subset of prompt tokens and are billed at the cached rate.
    Breakdown values and total are rounded to 6 dp, cost_per_minute to 4 dp.
    """
    if call_seconds <= 0:
        raise ValueError("call_seconds must be positive")
    u = {key: usage.get(key, 0) for key in USAGE_KEYS}
    if any(value < 0 for value in u.values()):
        raise ValueError("usage values must not be negative")
    if u["llm_cached_tokens"] > u["llm_prompt_tokens"]:
        raise ValueError("cached tokens cannot exceed prompt tokens")

    def price(name):
        return prices.get(name, 0.0)

    minutes = call_seconds / 60
    uncached = u["llm_prompt_tokens"] - u["llm_cached_tokens"]
    llm = (
        uncached / 1_000_000 * price("llm_input_per_1m")
        + u["llm_cached_tokens"] / 1_000_000 * price("llm_cached_input_per_1m")
        + u["llm_completion_tokens"] / 1_000_000 * price("llm_output_per_1m")
    )
    stt = u["stt_audio_seconds"] / 60 * price("stt_per_minute")
    tts = u["tts_characters"] / 1_000_000 * price("tts_per_1m_chars")
    telephony = minutes * price("telephony_per_minute")

    breakdown = {"llm": llm, "stt": stt, "tts": tts, "telephony": telephony}
    total = sum(breakdown.values())
    return {
        "breakdown": {name: round(value, 6) for name, value in breakdown.items()},
        "total": round(total, 6),
        "cost_per_minute": round(total / minutes, 4),
    }
```

### Tests (evaluation file `test_costs.py`)

```python
import unittest

from costs import call_cost

# Illustrative prices only. Always check your providers' current pricing pages.
PRICES = {
    "llm_input_per_1m": 0.40,
    "llm_cached_input_per_1m": 0.10,
    "llm_output_per_1m": 1.60,
    "stt_per_minute": 0.0077,
    "tts_per_1m_chars": 50.0,
    "telephony_per_minute": 0.0085,
}


class Evaluate(unittest.TestCase):
    def test_llm_only(self):
        result = call_cost({"llm_prompt_tokens": 1_000_000, "llm_completion_tokens": 500_000},
                           PRICES, 60)
        self.assertAlmostEqual(result["breakdown"]["llm"], 1.2)
        self.assertEqual(result["breakdown"]["stt"], 0)
        self.assertEqual(result["breakdown"]["tts"], 0)
        self.assertAlmostEqual(result["total"], 1.2085)

    def test_cached_tokens_billed_at_cached_rate(self):
        result = call_cost({"llm_prompt_tokens": 1_000_000, "llm_cached_tokens": 600_000},
                           {"llm_input_per_1m": 0.40, "llm_cached_input_per_1m": 0.10}, 60)
        self.assertAlmostEqual(result["breakdown"]["llm"], 0.22)

    def test_typical_three_minute_call(self):
        usage = {
            "llm_prompt_tokens": 42_000,
            "llm_cached_tokens": 30_000,
            "llm_completion_tokens": 1_200,
            "stt_audio_seconds": 180,
            "tts_characters": 2_400,
        }
        result = call_cost(usage, PRICES, 180)
        self.assertAlmostEqual(result["breakdown"]["llm"], 0.00972)
        self.assertAlmostEqual(result["breakdown"]["stt"], 0.0231)
        self.assertAlmostEqual(result["breakdown"]["tts"], 0.12)
        self.assertAlmostEqual(result["breakdown"]["telephony"], 0.0255)
        self.assertAlmostEqual(result["total"], 0.17832)
        self.assertEqual(result["cost_per_minute"], 0.0594)

    def test_tts_dominates(self):
        usage = {"llm_prompt_tokens": 10_000, "llm_completion_tokens": 500,
                 "stt_audio_seconds": 120, "tts_characters": 3_000}
        breakdown = call_cost(usage, PRICES, 120)["breakdown"]
        self.assertEqual(max(breakdown, key=breakdown.get), "tts")

    def test_missing_prices_count_as_zero(self):
        prices = {k: v for k, v in PRICES.items() if k != "telephony_per_minute"}
        result = call_cost({"stt_audio_seconds": 60}, prices, 60)
        self.assertEqual(result["breakdown"]["telephony"], 0)
        self.assertAlmostEqual(result["cost_per_minute"], 0.0077)

    def test_cost_per_minute_uses_call_length(self):
        result = call_cost({}, PRICES, 30)
        self.assertAlmostEqual(result["breakdown"]["telephony"], 0.00425)
        self.assertEqual(result["cost_per_minute"], 0.0085)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            call_cost({}, PRICES, 0)
        with self.assertRaises(ValueError):
            call_cost({"tts_characters": -1}, PRICES, 60)
        with self.assertRaises(ValueError):
            call_cost({"llm_prompt_tokens": 10, "llm_cached_tokens": 20}, PRICES, 60)
```

### Hints

1. Build a normalised usage dict first: `{key: usage.get(key, 0) for key in USAGE_KEYS}`.
2. Validate before you calculate.
3. A tiny helper `price(name)` that returns `prices.get(name, 0.0)` keeps the formulas readable.
4. Compute `cost_per_minute` from the unrounded total, then round.

### Solution explanation

The function separates the four cost centres so students can see where the money goes. With the illustrative prices, a three-minute call costs about $0.18 ($0.059 per minute) and TTS is the largest line, a pattern students will see again in their real Langfuse data in Lab 6. Prompt caching matters because a voice agent re-sends the whole conversation on every turn: in the three-minute example, 30,000 of 42,000 prompt tokens were cached and billed at a quarter of the price. The repo's `maple.costs` uses the same formulas with `PriceTable` and `UsageNumbers` dataclasses, and adds realtime audio-token pricing and a per-minute platform fee so you can compare cascaded and speech-to-speech calls (lecture 6.4).

---

## Appendix: Verification script

Place files as `exN/solution/<module>.py`, `exN/starter/<module>.py` and `exN/test_<module>.py` (N = 1 to 5), then run this script. Solutions must print `OK`; starters must print `FAILED` without import errors.

```bash
#!/bin/bash
# Run each exercise's tests against the solution (must pass) and the starter (must import cleanly and fail).
cd /tmp/claude-0/ex
status=0
for ex in ex1:scheduler ex2:wer ex3:pii ex4:latency ex5:costs; do
  d=${ex%%:*}; m=${ex##*:}
  for kind in solution starter; do
    cp $d/test_$m.py $d/$kind/
    out=$(cd $d/$kind && python3 -m unittest test_$m 2>&1 | tail -3 | tr '\n' ' ')
    echo "$d $m [$kind]: $out"
    if [ $kind = solution ] && ! echo "$out" | grep -q "OK"; then status=1; fi
  done
done
exit $status
```

Last verified run (Python 3.11):

```text
ex1 scheduler [solution]: Ran 11 tests in 0.001s  OK 
ex1 scheduler [starter]: Ran 11 tests in 0.002s  FAILED (errors=11) 
ex2 wer [solution]: Ran 10 tests in 0.001s  OK 
ex2 wer [starter]: Ran 10 tests in 0.002s  FAILED (errors=10) 
ex3 pii [solution]: Ran 9 tests in 0.001s  OK 
ex3 pii [starter]: Ran 9 tests in 0.001s  FAILED (errors=9) 
ex4 latency [solution]: Ran 11 tests in 0.000s  OK 
ex4 latency [starter]: Ran 11 tests in 0.003s  FAILED (errors=11) 
ex5 costs [solution]: Ran 7 tests in 0.000s  OK 
ex5 costs [starter]: Ran 7 tests in 0.001s  FAILED (errors=7)
```
