# API Reference

Everything below is importable from the top-level package:
`from alma_affect_kit import ...`

## Engine

### `AffectEngine(config: AffectConfig = None)`

Multi-character real-time affect computation.

| Member | Description |
|---|---|
| `add_character(name, personality=None, rules=None, initial_mood=None) -> CharacterAffect` | Create a character (raises on duplicate names) |
| `remove_character(name)` | Remove a character |
| `character(name)` / `engine[name]` | Look a character up |
| `iter(engine)` | Iterate over characters |
| `appraise(name, eec_or_list, merge=True) -> [ActiveEmotion]` | Feed EECs directly to one character |
| `perceive_event(event, characters=None) -> {name: [ActiveEmotion]}` | Dispatch a named event through basic rules |
| `perceive_act(act, performer, addressee=None, characters=None)` | Dispatch an act (self/direct/indirect scoping) |
| `perceive_emotion_display(display, performer, characters=None)` | Dispatch a visible emotion cue (self/other) |
| `perceive_mood_display(display, performer, characters=None)` | Dispatch a visible mood cue (self/other) |
| `update(dt)` | Advance all characters by `dt` seconds |
| `step(steps=1)` | Advance in update periods (default 0.5 s) |
| `run(duration)` | Simulate `duration` seconds in period slices |
| `time` | Accumulated simulated seconds |
| `affect_output() -> {name: dict}` | JSON-able snapshots of all characters |

### `CharacterAffect`

One character's layered affective state (created via `add_character`).

| Member | Description |
|---|---|
| `name`, `personality`, `rules`, `config` | Identity and setup |
| `mood: PAD` / `mood_word: str` | Current mood and its description (`'slightly relaxed'`) |
| `default_mood: PAD` | Personality-derived resting mood |
| `active_emotions: [ActiveEmotion]` | Currently decaying emotions |
| `emotion_center: VirtualEmotionCenter \| None` | Current VEC (recomputed each update) |
| `dominant_emotion -> ActiveEmotion \| None` | Most intense active emotion above the threshold |
| `emotion_intensity(EmotionType) -> float` | Current level (the baseline when inactive) |
| `baseline(EmotionType) -> float` | Personality baseline intensity |
| `appraise(eecs, merge=True)` / `elicit(type, intensity, cause=None)` | Elicit emotions via appraisal / directly |
| `update(dt)` | Advance this character |
| `reset()` | Drop emotions, mood → default mood |
| `affect_output() -> dict` | JSON-able snapshot |

## Configuration

### `AffectConfig`

All model parameters with publication defaults; see
[Configuration](configuration.md) for the full table.  `validate()`
re-checks after field assignment.  `MoodReturnMode.IDLE / .ALWAYS` name
the two return modes.

## Personality

| Symbol | Description |
|---|---|
| `Personality(openness, conscientiousness, extraversion, agreeableness, neuroticism)` | Frozen Big Five profile, traits clamped to [-1, 1]; `as_dict()` |
| `TRAITS` | The five trait names |
| `default_mood(personality, weights=None) -> PAD` | Mehrabian's Big Five → PAD regression (clamped into the cube) |
| `emotion_baseline(personality, emotion, table=None) -> float` | Baseline intensity of one emotion type |
| `DEFAULT_PERSONALITY_TO_MOOD` | The regression weights |
| `DEFAULT_PERSONALITY_BASELINES` | The default baseline weight table |

## PAD space

| Symbol | Description |
|---|---|
| `PAD(pleasure, arousal, dominance)` | Frozen vector; exact algebra (`+`, `-`, `scaled`, `dot`, `norm`, `distance`, `normalized`, `moved_towards`), `clamped()` into the cube, `octant`, `strength`, `describe()`, `as_tuple()` |
| `MoodOctant` | The eight named octants (Table 1); `from_signs(p, a, d)`, `.label`, `.signs` |
| `MoodStrength` | `SLIGHTLY` / `MODERATE` / `FULLY`; `from_norm(n)` |
| `SQRT3` | √3, the longest octant distance |

## Emotions

| Symbol | Description |
|---|---|
| `EmotionType` | The 24 OCC types; `.label`, `.group` (`OCCGroup`), `.valence` (±1), `from_name("FearsConfirmed")` |
| `OCCGroup` | well-being, prospect-based, fortunes-of-others, attribution, well-being/attribution, attraction |
| `DEFAULT_EMOTION_PAD_MAP` | Table 2: `{EmotionType: PAD}` |
| `DecayFunction` | `LINEAR` / `EXPONENTIAL` / `TANGENS_HYPERBOLICUS`; `factor(u)`, `from_name` |
| `ActiveEmotion` | A decaying emotion instance: `type`, `intensity`, `initial_intensity`, `baseline`, `age`, `cause`, `pad`, `expired`, `tick(dt)` |

## Appraisal

| Symbol | Description |
|---|---|
| `EEC(...)` | One emotion eliciting condition; validated on construction; `with_cause(str)` |
| `EEC_FIELD_NAMES` | All EEC field names |
| `Prospect.CONFIRMED / .DISCONFIRMED` | Prospect outcome constants |
| `compute_emotions(eec) -> [(EmotionType, intensity)]` | The OCC rules |
| `merge_eecs([eec]) -> [eec]` | Merge same-situation EECs (enables compounds) |
| `good_event, bad_event, good/bad_likely/unlikely_future_event, good/bad_act_self, good/bad_act_other, nice_thing, nasty_thing, prospect_confirmed, prospect_disconfirmed, event_for_other` | Basic appraisal tag constructors |
| `BASIC_TAGS` | Tag name → constructor mapping |

## Rules

| Symbol | Description |
|---|---|
| `AppraisalRules` | A character's rule book; builders `on_event`, `on_act`, `on_emotion_display`, `on_mood_display` (chainable); matchers `match_event`, `match_act`, `match_emotion_display`, `match_mood_display` |
| `ActRule(act, scope, appraisals, performer=None)` | scope: `self` / `direct` / `indirect` |
| `DisplayRule(display, scope, appraisals, performer=None)` | scope: `self` / `other` |

## Loading

| Symbol | Description |
|---|---|
| `load_config(source) -> AffectConfig` | dict / file path / document string; YAML (default) or JSON |
| `load_character(source, format=None) -> (name, Personality, AppraisalRules)` | Same formats; feed to `add_character(*...)` |
| `config_from_dict(dict)` / `character_from_dict(dict)` / `eec_from_dict(dict)` | The dict-level builders |

## Mood dynamics (lower level)

| Symbol | Description |
|---|---|
| `VirtualEmotionCenter(position: PAD, intensity)` | The VEC |
| `compute_emotion_center(emotions, config) -> VirtualEmotionCenter \| None` | VEC of the active emotions |
| `update_mood(mood, default_mood, vec, dt, config) -> PAD` | One pull/push or return step (result clamped into the cube) |

These are what `CharacterAffect.update()` uses internally; they are
exposed for custom integrations and testing.
