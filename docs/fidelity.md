# Fidelity Notes

This library reproduces every quantitative parameter published in the
AAMAS'05 paper and its EmotionEngine companion papers (IVA'03, ADS'04).
This page records exactly what is taken from the papers verbatim, and
the documented choices made where the papers are silent or inconsistent.
Everything in the second category is configurable.

**How this was verified.**  All 24 rows of Table 2 (PAD values and
octants), all 8 octant names of Table 1, all nine Big Five → PAD
regression coefficients, the paper's worked personality example and the
Fig. 3 defaults were cross-checked programmatically against the text
extracted from the published PDF, and are pinned in the test suite in
full (not sampled).  Readers are encouraged to repeat the comparison
against the paper themselves; the constants live in `emotion.py`,
`personality.py` and `config.py`.

## Taken verbatim from the publications

| Element | Source |
|---|---|
| The 24 emotion types and their PAD mapping | AAMAS'05, Table 2 |
| The eight mood octant names | AAMAS'05, Table 1 |
| Mood strength = norm of the PAD vector, √3 in three equal parts (slightly / moderate / fully) | AAMAS'05, §3 |
| Big Five → PAD default-mood regression (all coefficients) | AAMAS'05, §3 (Mehrabian 1996) |
| The worked personality example: (0.4, 0.8, 0.6, 0.3, 0.4) → (0.38, −0.08, 0.50), Relaxed | AAMAS'05, §3, a test anchor |
| Emotion decay 20 s, linear, 500 ms period; threshold 0.4 | AAMAS'05, Fig. 3 (see the note on the threshold's meaning below) |
| Three decay functions are *named*: linear, exponential, tangens hyperbolicus | IVA'03 / ADS'04 (their exact curves are not published, see below) |
| Mood change time 10 min (octant centre to octant centre) | AAMAS'05, §3 |
| Mood return time 20 min (over √3) | AAMAS'05, §3 |
| Virtual emotion centre = centre of active emotions, intensity = average intensity, max 1.0 | AAMAS'05, §3 |
| Pull phase / push phase semantics | AAMAS'05, §3 + Fig. 2 |
| EEC variables: desirability, praiseworthiness, appealingness, liking, likelihood, realization; signs select the emotion, magnitudes the intensity | ADS'04, §3.2 |
| Basic appraisal tags (good/bad event, likely/unlikely future, act self/other, nice/nasty thing) | IVA'03, Table 1 |
| Rule hierarchy: basic, act (self/direct/indirect), emotion display, mood display | AAMAS'05, §4 |
| The extravert joy baseline = 0.15 anchor | IVA'03 / ADS'04 |
| AffectML document semantics (AffectComputation, CharacterAffect), expressed in YAML | AAMAS'05, Figs. 3–4 |

## Documented choices

### Emotion intensity combination
The papers say the absolute values of the EEC variables determine the
intensities but give no formula for emotions with two contributing
variables (hope, fear, the confirmations, fortunes-of-others, the
compounds, love/hate).  **Choice:** the mean of the absolute values of
the participating variables.

### Personality baseline table
Only the joy = 0.15 anchor is published, plus qualitative guidance
(positive emotions rise with extraversion and agreeableness, negative
with neuroticism; conscientiousness and openness influence the
attribution and attraction groups).  **Choice:** positive emotions get
weights `{extraversion: 0.15, agreeableness: 0.10}`, negative
`{neuroticism: 0.15}`, with `{conscientiousness: 0.05}` added for
attribution/compound emotions and `{openness: 0.05}` for attraction
emotions; baselines clamp at 0.  Override any of it via
`AffectConfig.personality_baselines`.

### Decay curve shapes
Only the *names* of the three decay functions are published.
**Choice:** linear falls to zero at the decay time; exponential is
`exp(−5·t/T)` (≈0.7 % remaining at the decay time, then cut to zero);
tangens hyperbolicus is a normalised `1 − tanh(6·t/T − 3)` S-curve.  All
three reach 1 at t = 0 and 0 at t = T; the intermediate shape is ours.

### Decay towards the baseline
IVA'03 says personality *biases emotions with a baseline intensity*
(extravert joy baseline 0.15, introvert 0.0).  **Choice:** the baseline
is treated as the emotion's resting level, elicited intensities are
raised by it and decay back *to* it, not to zero.  With
`apply_personality_bias=False` every baseline is zero and emotions decay
to zero.

### The meaning of the 0.4 threshold
Fig. 3 names the element `EmotionBaseline threshold="0.4"`, while the
companion papers describe a threshold that "the most dominant emotion"
must exceed "to have an impact on the character's behaviour".
**Choice:** the value is read as that behaviour threshold
(`dominant_emotion_threshold`); it does not gate whether an emotion
influences the mood.

### Emotion decay time: 20 s vs "for example, 1 minute"
The Fig. 3 document sets `EmotionDecay time="20000"`; the running text
mentions decay "over a certain amount of time (for example, 1 minute)".
**Choice:** the document value (20 s) is the default.

### Which octant centres define the mood change time
The paper calibrates the pull/push speed on the time "to move a current
mood from one mood octant centre to another one" without naming the
pair.  **Choice:** adjacent centres (distance 1.0) by default; the
distance is exposed as `mood_change_distance` (√2 across a face, √3 for
opposite centres).  Only the speed scale changes.

### Unspecified liking in fortunes-of-others appraisals
When an event concerning another character is appraised without a
`liking` value, OCC needs a sign to choose between happy-for/pity and
resentment/gloating.  **Choice:** unspecified liking counts as mildly
positive (0.5).

### Mood return time: 10 vs 20 minutes
The paper's running text says the mood return time "currently is
20 minutes" while its Fig. 3 example document shows
`MoodReturn time="600000"` (10 minutes).  **Choice:** the text value
(1200 s) is the default.

### Mood strength boundary
The paper labels its default-mood example (norm ≈ 0.633) *slightly*
relaxed, although by its own thirds-of-√3 rule (boundary ≈ 0.577) it is
just inside *moderate*, presumably rounding.  **Choice:** the stated
rule is followed exactly, so that example reads *moderate relaxed* here.

### Pull/push geometry
The paper describes pull/push in prose and a 2-D figure.  **Choice:**
"between the zero point and the VEC" is implemented as the mood's
projection onto the origin→VEC ray not yet reaching the VEC's distance;
pull moves straight towards the VEC, push moves radially outward (deeper
into the mood's current octant), clamped to the cube.  Speed is the
published calibration: `vec_intensity / mood_change_time` PAD units per
second.

### Mood return while emotions are active
The paper states the return tendency but not whether it applies during
active emotions.  **Choice:** default `mood_return_mode="idle"` (return
only when no VEC exists, otherwise the two forces of comparable
magnitude would largely cancel); `"always"` is available.

### Virtual emotion centre averaging
"The virtual emotion centre of all currently active emotions" is read as
the plain average of their PAD points (the paper assigns intensity a
separate role: the average of intensities).  **Choice:** plain average
by default; `vec_intensity_weighted=True` switches to an
intensity-weighted position.

### EEC merging for compound emotions
OCC's compound emotions (anger, remorse, gratitude, gratification)
require desirability and praiseworthiness appraised for *one* situation.
The paper's Fig. 4 shows an attack appraised as BadEvent + BadActOther
within one rule but doesn't state the combination mechanics.
**Choice:** basic appraisals emitted for the same input are merged into
one EEC when compatible, same cause, same event structure (actual vs
prospective vs confirmed), no variable set on both sides with different
values, no explicit agency disagreement.  `merge=False` disables it.

### Sub-baseline elicitations
Unspecified in the papers.  **Choice:** an elicitation weaker than the
personality baseline is raised to the baseline and stays active for the
decay time (rather than being dropped), so mild stimuli still reach the
mood dynamics.

### AffectML represented in YAML
The paper defines AffectML as an XML language.  This library keeps
AffectML's *semantics*, the global computation parameters, the
personality definition and the complete appraisal rule hierarchy, but
represents documents in YAML (JSON accepted), with times in seconds
rather than milliseconds.  Every AffectML construct has a one-to-one
YAML equivalent (mapping table on the [Configuration](configuration.md)
page); the paper's own Fig. 3 and Fig. 4 documents are part of the
test suite in translated form.  Two things go slightly beyond the
paper's schema: the mood change time is a first-class parameter (the
paper states it only in prose), and basic rules can be keyed by an
arbitrary event name in addition to the paper's tag-name form.

## Beyond the paper's scope (engineering)

* Strict validation everywhere (value ranges, unknown keys/tags/fields,
  trait-name typos), load-time `ValueError` rather than silent drift.
* Exact PAD vector algebra; the mood is clamped into the cube only at
  assignment points.
* Deterministic `dt`-driven stepping instead of a wall-clock thread.
* The paper's future-work items are *not* implemented (and noted here
  for honesty): mood does not yet influence emotion intensity, appraisal
  rules are static at runtime, and there is no group-mood aggregation.
