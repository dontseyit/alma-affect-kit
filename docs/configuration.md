# Configuration

Every parameter of the model is configurable through `AffectConfig`.
The defaults are the **publication values**, an unconfigured engine
behaves exactly as described in the AAMAS'05 paper.  You can construct
a configuration in code, or load one from a YAML (or JSON) file;
characters' personality and rules profiles are both configurable.

## Parameters

### Emotion parameters

| Parameter | Default | Constraint | What it controls |
|---|---|---|---|
| `emotion_decay_time` | 20 s | > 0 | How long an elicited emotion takes to fade back to its baseline.  Shorter values make characters flare and settle quickly; longer values let single events cast a longer emotional shadow, and, because active emotions drive the mood, also deepen each event's effect on mood. |
| `decay_function` | linear | linear, exponential, tanhyp | The *shape* of the fade.  Linear falls steadily.  Exponential drops fast and trails off, a sharp reaction that quickly loses force.  Tangens hyperbolicus is an S-curve: the emotion holds near full strength briefly, falls through the middle, then eases out, the most natural-looking for visible expressions. |
| `dominant_emotion_threshold` | 0.4 | 0 – 1 | Emotions should not visibly drive behaviour a priori: only the strongest active emotion *above this threshold* is reported as the dominant emotion.  Lower it and characters emote at every little thing; raise it and only strong feelings show. |
| `apply_personality_bias` | on | on/off | Whether personality baselines raise elicited intensities (an extravert feels joy more strongly).  Turn off for personality-neutral emotion strength. |

### Mood parameters

| Parameter | Default | Constraint | What it controls |
|---|---|---|---|
| `mood_change_time` | 600 s (10 min) | > 0 | The mood's responsiveness to emotions: the time a full-intensity emotion centre needs to move the mood between two adjacent octant centres.  Smaller values give volatile, fast-swinging moods; the default gives the paper's deliberately inert medium-term mood. |
| `mood_change_distance` | 1.0 | > 0 | The PAD distance the mood covers in `mood_change_time`.  The paper calibrates on "one mood octant centre to another" without naming the pair; adjacent centres are 1.0 apart (default), centres across a face √2, opposite centres √3.  Only the speed changes; the dynamics are otherwise identical. |
| `mood_return_time` | 1200 s (20 min) | > 0 | How quickly a disturbed mood drifts home: the time to travel the longest octant distance (√3) back to the default mood.  Governs how long a bad stretch lingers after the events stop. |
| `mood_return_mode` | idle | idle, always | *Idle*: the homeward drift acts only while no emotions are active (the paper's reading, while emotions live, they own the mood).  *Always*: the drift is superimposed on the emotional pull, giving a slightly stickier, more anchored mood. |
| `vec_intensity_weighted` | off | on/off | How the emotion centre's position is computed from the active emotions: the plain average of their PAD points (the paper's reading), or an average weighted by intensity so stronger emotions pull the centre towards themselves. |

### Timing and mapping tables

| Parameter | Default | What it controls |
|---|---|---|
| `update_period` | 0.5 s | The step size used by `step()` and `run()`, the paper's 500 ms affect rate.  Must be positive. |
| `emotion_pad_map` | Table 2 of the paper | Where each of the 24 emotion types sits in PAD space, i.e. which mood each emotion pulls towards.  Entries you provide merge over the defaults. |
| `personality_to_mood` | Mehrabian's regression | The Big Five → default-mood weights, per PAD axis.  Must map exactly the three axes; trait names are validated. |
| `personality_baselines` | see [Fidelity Notes](fidelity.md) | The Big Five → per-emotion baseline weights: which traits make which emotions run hot at rest. |

Validation happens on construction and again if a file is loaded;
violations raise a specific errors.

## Value ranges throughout the engine

| Quantity | Range | Handling |
|---|---|---|
| Big Five traits | −1 to +1 | clamped |
| Appraisal variables (desirability, praiseworthiness, appealingness, liking, desirability-for-other) | −1 to +1 | error outside |
| Likelihood, realization | 0 to 1 | error outside |
| Emotion intensities | 0 to 1 | clamped; never below the personality baseline |
| Mood (each PAD axis) | −1 to +1 | kept inside the cube by the engine |

## Configuration files

Configuration and character files are **YAML** documents whose
structure mirrors the library's own field names, with **times in
seconds**.  A configuration file sets any subset of the parameters
above; a character file holds a name, a personality and the appraisal
rule book (basic event rules, act rules with their scope and optional
performer, and emotion/mood display rules).  JSON is accepted with the
identical structure (`.json` files are parsed strictly as JSON; JSON is
otherwise a subset of YAML), and Python dicts can be passed directly.
A mistyped path raises a file-not-found error rather than being
mistaken for document content.

Complete, commented file templates, and the code that loads them, are
on the [Examples](examples.md) page; ready-to-copy files ship in the
repository's `examples/` directory.

## From AffectML to YAML

The paper specifies its configuration in AffectML, an XML-based
language (its Figures 3 and 4).  This library does not read XML;
instead every AffectML construct has a YAML equivalent, so the paper's
documents translate one-to-one.  The only systematic change is the time
unit: AffectML uses milliseconds, YAML uses seconds.

**AffectComputation document → configuration file**

| AffectML | YAML |
|---|---|
| `<EmotionDecay time="20000">` | `emotion_decay_time: 20.0` |
| `<EmotionDecay period="500">` (also `<MoodReturn period>`) | `update_period: 0.5` |
| `<EmotionDecay function="linear">` | `decay_function: linear` |
| `<EmotionBaseline threshold="0.4">` | `dominant_emotion_threshold: 0.4` |
| `<MoodReturn time="1200000">` | `mood_return_time: 1200.0` |
| the mood change time (stated only in the paper's text) | `mood_change_time: 600.0` |
| `<MoodRelations><EmotionRelation name="Anger" p a d/>` | `emotion_pad_map: {Anger: [p, a, d]}` |
| `<PersonalityRelations><PleasureRelation extra agree neur/>` | `personality_to_mood: {pleasure: {extraversion, agreeableness, neuroticism}}` |
| `<ArousalRelation>` / `<DominanceRelation>` | `personality_to_mood: {arousal: {...}, dominance: {...}}` |
| `<RealtimeOutput>` / `<FileLog>` | not applicable, output is read programmatically via `affect_output()` |

**CharacterAffect document → character file**

| AffectML | YAML |
|---|---|
| `<CharacterAffect name="Valerie">` | `name: Valerie` |
| `<Personality open con extra agree neur/>` | `personality: {openness, conscientiousness, extraversion, agreeableness, neuroticism}` |
| `<Basic><GoodEvent desirability="0.7"/></Basic>` (input = the tag name) | `basic: {GoodEvent: [{tag: GoodEvent, desirability: 0.7}]}` |
| a basic rule for a named event | `basic: {SunIsShining: [{tag: GoodEvent, desirability: 0.7}]}` |
| `<SelfAct type="Calm">` | `acts: [{act: Calm, scope: self, appraisals: [...]}]` |
| `<DirectAct type="Attack" performer="Sven">` | `acts: [{act: Attack, scope: direct, performer: Sven, appraisals: [...]}]` |
| `<IndirectAct type="...">` | `acts: [{act: ..., scope: indirect, ...}]` |
| `<SelfEmotion emotion="ReproachDisplay">` / `<OtherEmotion>` | `emotion_displays: [{display: ReproachDisplay, scope: self \| other, performer?, appraisals}]` |
| `<SelfMood mood="...">` / `<OtherMood>` | `mood_displays: [{display: ..., scope: self \| other, ...}]` |
| rule body `<GoodActSelf agency="self" praiseworthiness="0.5"/>` | `{tag: GoodActSelf, agency: self, praiseworthiness: 0.5}` (the redundant `agency` may be kept or dropped) |
| any basic appraisal tag element | `{tag: <TagName>, <its degree>}` |
| `monitored`, `docu` attributes | not applicable (tooling metadata) |

The paper's own Fig. 3 and Fig. 4 documents, translated this way, are
part of the test suite and reproduce the paper's attack scenario
(Distress, Reproach and Anger for Valerie).
