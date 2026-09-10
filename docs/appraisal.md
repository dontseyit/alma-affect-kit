# Appraisal

Appraisal is how world input becomes emotion. The outcome of one
appraisal is an **emotion eliciting condition** (EEC), a bundle of
variables describing the situation.  The signs of the variables select
which of the 24 emotion types are elicited; the absolute values
determine the intensities.

## EEC variables

| Variable | Range | Meaning |
|---|---|---|
| `desirability` | [-1, 1] | How (un)desirable an event is for the appraising character |
| `desirability_for_other` | [-1, 1] | How (un)desirable an event is for another character |
| `praiseworthiness` | [-1, 1] | How praise- or blameworthy an action is |
| `agency` | `None` / `"self"` / `"other"` | Who performed the action (`None` counts as `"other"`) |
| `appealingness` | [-1, 1] | How (un)appealing an object is |
| `liking` | [-1, 1] | How attracted the character is to the other person/object |
| `likelihood` | [0, 1] | Degree of belief that an anticipated event will occur |
| `realization` | [0, 1] | Degree of belief that an anticipated event has occurred |
| `prospect` | `None` / `"confirmed"` / `"disconfirmed"` | Outcome status of an anticipated event |
| `cause` | str | Free-text elicitor, carried onto the emotions |

Out-of-range values raise `ValueError` at construction.

## Elicitation reference

Where two variables participate, the intensity is the mean of their
absolute values.

**Events (well-being / prospect-based):**

| Condition | Emotion | Intensity |
|---|---|---|
| desirability > 0 | Joy | \|d\| |
| desirability < 0 | Distress | \|d\| |
| d > 0, likelihood set | Hope | mean(\|d\|, l) |
| d < 0, likelihood set | Fear | mean(\|d\|, l) |
| d > 0, prospect confirmed | Satisfaction | mean(\|d\|, r) |
| d < 0, prospect confirmed | FearsConfirmed | mean(\|d\|, r) |
| d > 0, prospect disconfirmed | Disappointment | mean(\|d\|, r) |
| d < 0, prospect disconfirmed | Relief | mean(\|d\|, r) |

**Events happening to others (fortunes-of-others):**

| Condition | Emotion |
|---|---|
| desirability_for_other > 0, liking ≥ 0 | HappyFor |
| desirability_for_other > 0, liking < 0 | Resentment |
| desirability_for_other < 0, liking ≥ 0 | Pity |
| desirability_for_other < 0, liking < 0 | Gloating |

**Actions (attribution):**

| Condition | Emotion |
|---|---|
| praiseworthiness > 0, agency self | Pride |
| praiseworthiness < 0, agency self | Shame |
| praiseworthiness > 0, agency other | Admiration |
| praiseworthiness < 0, agency other | Reproach |

**Compounds (well-being × attribution, both `desirability` and
`praiseworthiness` set in one EEC, no prospect):**

| Condition | Emotion |
|---|---|
| d > 0, p > 0, agency self | Gratification |
| d > 0, p > 0, agency other | Gratitude |
| d < 0, p < 0, agency self | Remorse |
| d < 0, p < 0, agency other | Anger |

**Objects (attraction):**

| Condition | Emotion |
|---|---|
| appealingness > 0 | Liking |
| appealingness < 0 | Disliking |
| appealingness > 0 and liking > 0 | Love |
| appealingness < 0 and liking < 0 | Hate |

## Basic appraisal tags

The papers define symbolic abbreviations for common EECs (IVA'03,
Table 1), available as helper constructors with the papers' default
degrees ("moderately" = 0.5; likely = 0.75, unlikely = 0.25):

| Tag / constructor | EEC it builds |
|---|---|
| `good_event(0.5)` / `bad_event(-0.5)` | desirability ±0.5 |
| `good_likely_future_event(0.5, 0.75)` / `bad_likely_future_event` | desirability ±0.5, likelihood 0.75 |
| `good_unlikely_future_event(0.5, 0.25)` / `bad_unlikely_future_event` | desirability ±0.5, likelihood 0.25 |
| `good_act_self(0.5)` / `bad_act_self(-0.5)` | praiseworthiness ±0.5, agency self |
| `good_act_other(0.5)` / `bad_act_other(-0.5)` | praiseworthiness ±0.5, agency other |
| `nice_thing(0.5)` / `nasty_thing(-0.5)` | appealingness ±0.5 |
| `prospect_confirmed(d)` / `prospect_disconfirmed(d)` | the anticipated event's outcome |
| `event_for_other(d, liking=0.5)` | fortunes-of-others |

Signs are normalised. E.g. `good_event(0.7)` and `good_event(-0.7)` both mean
desirability +0.7.

## Merging: how compounds arise

An appraisal rule may emit several basic appraisals for one input, the
paper's example: an *attack* is a **bad event** *and* a **blameworthy
act of another** (Fig. 4).  OCC treats these as one situation appraised
along several dimensions, which is what elicits the compound emotions.
An attack appraised as a bad event (desirability −0.5) plus a
blameworthy act of another (praiseworthiness −0.3) therefore elicits
three emotions at once: Distress 0.5, Reproach 0.3 and the compound
**Anger** 0.4 (before personality bias).

Merging is deliberately conservative, two EECs merge **only** when they
describe the same situation:

* no variable set on both sides with different values,
* no explicit agency disagreement,
* equal causes (or one/both absent),
* the same event structure, an actual event never merges with a
  prospective or confirmed one (that would turn Joy into Hope).

Incompatible EECs stay separate and elicit independently.  Pass
`merge=False` to `appraise()` to disable merging entirely.

## Personality bias

Each elicited intensity is raised by the character's personality
baseline for that emotion type and clamped to [0, 1]; the emotion then
decays back to the baseline.  Disable with
`AffectConfig(apply_personality_bias=False)`.

## The rule system

A character's profile bundles its personality with **subjective
appraisal rules**, the Python counterpart of AffectML's rule classes:

| Rule class | Matches | Scopes |
|---|---|---|
| `on_event(name, *eecs)` | named events/objects (`perceive_event`) |  |
| `on_act(act, scope, *eecs, performer=None)` | (dialog) acts (`perceive_act`) | `self`, `direct`, `indirect` |
| `on_emotion_display(display, scope, *eecs, performer=None)` | visible emotion cues (`perceive_emotion_display`) | `self`, `other` |
| `on_mood_display(display, scope, *eecs, performer=None)` | visible mood cues (`perceive_mood_display`) | `self`, `other` |

Dispatch for an act: the performer matches its `self` rules, the
target its `direct` rules, and everyone else their `indirect`
(listener) rules.  A rule with `performer="Sven"` only fires for Sven's
acts. All appraisals from one matched input share the input as 
their `cause` and are merged as described above.
