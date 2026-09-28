# Caller audio samples for `tests/evals/audio_in_eval.py`

Lecture 9.13. Put short recordings of real caller phrases here, each with a text file
holding exactly what was said. The eval transcribes every WAV with Deepgram and fails if
the corpus word error rate (WER) is above the threshold (default 15%).

No audio ships with the repo (voices are personal data). Record your own in ten minutes.

## File layout

```
tests/data/audio/
  book_tuesday_us.wav        # 16-bit PCM WAV, mono, 16 kHz (8 kHz phone audio also works)
  book_tuesday_us.txt        # I'd like to book a cleaning next Tuesday morning.
  insurance_delta_phone.wav
  insurance_delta_phone.txt  # Do you take Delta Dental PPO?
```

The `.txt` must have the same base name as the `.wav`. Write numbers the way you
want them scored; the eval normalises case and punctuation only (see `src/maple/wer.py`).

## What to record (aim for 8-12 clips, 3-8 seconds each)

1. Dates and times: "Can I come in Thursday at nine thirty?", "No, not Tuesday, Thursday."
2. Names and spelling: "It's Siobhan Nguyen, S I O B H A N."
3. Domain terms: "I was prescribed amoxicillin after my root canal.", "Do you take MetLife?"
4. Phone numbers: "My number is five one two, five five five, zero one four two."
5. Different speakers: ask two or three friends with different accents (with their consent).
6. Different conditions: laptop mic, phone speaker in a car, a noisy kitchen, a phone call
   recorded through your Twilio number.

## How to record

- macOS/Linux with ffmpeg: `ffmpeg -f avfoundation -i ":0" -ac 1 -ar 16000 -t 6 book_tuesday_us.wav`
  (Linux: replace `-f avfoundation -i ":0"` with `-f alsa -i default`).
- Audacity: set Project Rate to 16000 Hz, record, then *File > Export > WAV (Signed 16-bit PCM)*.
- Phone audio: record a test call in LiveKit (egress) or Twilio and trim with Audacity.
  Leave it at 8 kHz; that is the point.

## Run it

```bash
export DEEPGRAM_API_KEY=...
python tests/evals/audio_in_eval.py                  # baseline
python tests/evals/audio_in_eval.py --keyterms       # with the dental keyterms
python tests/evals/audio_in_eval.py --behavior       # also replay transcripts through Riley
```

Consent and privacy: only record people who agreed, never commit real patient calls,
and add `tests/data/audio/*.wav` to `.gitignore` if your repo is public.
