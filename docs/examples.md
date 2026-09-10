# Examples

All the runnable code in one place.  The concepts behind each snippet
are explained in [Usage](usage.md), [Appraisal](appraisal.md),
[Simulation](simulation.md) and [Configuration](configuration.md).

## Quick start

```python
from alma_affect_kit import AffectEngine, Personality, good_event

engine = AffectEngine()                       # publication defaults

valerie = engine.add_character("Valerie", Personality(
    openness=0.4, conscientiousness=0.8, extraversion=0.6,
    agreeableness=0.3, neuroticism=0.4))

print(valerie.default_mood)                   # PAD(P=+0.38, A=-0.08, D=+0.50)
print(valerie.mood_word)                      # 'moderate relaxed'

engine.appraise("Valerie", good_event(0.7, cause="sun is shining"))
engine.update(0.5)                            # advance 500 ms
print(valerie.dominant_emotion)               # ActiveEmotion(Joy, ...)

engine.run(25.0)                              # emotions decay (20 s default)
print(valerie.active_emotions)                # []
```

## Direct appraisals

```python
from alma_affect_kit import (good_event, bad_event, bad_act_other,
                         bad_likely_future_event, prospect_disconfirmed,
                         event_for_other, nice_thing, EEC)

engine.appraise("Valerie", good_event(0.7))                  # Joy
engine.appraise("Valerie", bad_likely_future_event(-0.8))    # Fear
engine.appraise("Valerie", prospect_disconfirmed(-0.8))      # Relief
engine.appraise("Valerie", event_for_other(-0.6, liking=0.7))  # Pity
engine.appraise("Valerie", nice_thing(0.6, liking=0.8))      # Liking + Love

# one situation appraised along two dimensions -> the compound Anger
engine.appraise("Valerie", [bad_event(-0.5), bad_act_other(-0.3)])
# -> Distress 0.5, Reproach 0.3, Anger 0.4   (before personality bias)

# raw EECs give full control
engine.appraise("Valerie", EEC(desirability=0.6,
                               praiseworthiness=0.4))        # + Gratitude
```

## Building a rule book

```python
from alma_affect_kit import (AppraisalRules, good_event, bad_event,
                         bad_act_other, event_for_other)

valerie_rules = (AppraisalRules()
    .on_event("SunIsShining", good_event(0.7))
    .on_act("Attack", "direct", bad_event(-0.5), bad_act_other(-0.3),
            performer="Sven")               # only when Sven attacks her
    .on_act("GoodJoke", "indirect", good_event(0.3))   # as a listener
    .on_emotion_display("BlushOfShame", "other", event_for_other(-0.3)))

engine.add_character("Valerie", personality, valerie_rules)
```

## Perceiving world input

```python
engine.perceive_event("SunIsShining")       # everyone appraises it
engine.perceive_act("Attack", performer="Sven", addressee="Valerie")
engine.perceive_emotion_display("BlushOfShame", performer="Sven")
engine.perceive_mood_display("NervousIdle", performer="Sven")

# scope an input to the characters who can perceive it
engine.perceive_act("Whisper", performer="Sven", addressee="Valerie",
                    characters=["Sven", "Valerie"])
```

Every call returns what it elicited, per character:
`{"Valerie": [ActiveEmotion(Distress, ...), ...]}`.

## Reading affect for behaviour

```python
from alma_affect_kit import MoodOctant

octant = character.mood.octant
if octant is MoodOctant.HOSTILE:
    reply = pick_short_harsh_line()
elif octant is MoodOctant.RELAXED:
    reply = pick_lengthy_friendly_line()

if (dominant := character.dominant_emotion):
    face.show(dominant.type.label, dominant.intensity)

snapshot = character.affect_output()     # JSON-able, for saves/telemetry
```

## Game-loop integration

```python
# fixed-timestep affect alongside a variable frame rate
AFFECT_STEP = 0.5                        # the paper's 500 ms period
accumulator = 0.0

def game_tick(frame_dt):
    global accumulator
    world.simulate(frame_dt)
    accumulator += frame_dt
    while accumulator >= AFFECT_STEP:
        engine.update(AFFECT_STEP)
        accumulator -= AFFECT_STEP
    render(world, engine.affect_output())

def on_player_insulted_npc(npc, player):
    engine.perceive_act("Insult", performer=player.name,
                        addressee=npc.name)
```

Calling `engine.update(frame_dt)` directly every frame works just as
well, per-frame updates are cheap.

## Configuring the engine in code

```python
from alma_affect_kit import AffectConfig, AffectEngine, DecayFunction

config = AffectConfig(emotion_decay_time=60.0,
                      decay_function=DecayFunction.EXPONENTIAL,
                      mood_change_time=120.0,
                      mood_return_mode="always")
engine = AffectEngine(config)
```

## Loading configuration and character files

```python
from alma_affect_kit import AffectEngine, load_config, load_character

engine = AffectEngine(load_config("affect.yaml"))
engine.add_character(*load_character("valerie.yaml"))
engine.add_character(*load_character("sven.json"))    # JSON works too
```

### YAML configuration template (times in seconds)

```yaml
# affect.yaml: all values shown are the defaults
emotion_decay_time: 20.0
decay_function: linear            # linear | exponential | tanhyp
dominant_emotion_threshold: 0.4
update_period: 0.5
mood_change_time: 600.0
mood_return_time: 1200.0
mood_return_mode: idle            # idle | always
vec_intensity_weighted: false
emotion_pad_map:                  # optional overrides, merged over Table 2
  Anger: [-0.51, 0.59, 0.25]
personality_to_mood:              # optional per-axis overrides
  pleasure: {extraversion: 0.21, agreeableness: 0.59, neuroticism: 0.19}
personality_baselines:            # optional per-emotion overrides
  Joy: {extraversion: 0.15, agreeableness: 0.10}
```

### YAML character template

```yaml
name: Valerie
personality: {openness: 0.4, conscientiousness: 0.8, extraversion: 0.6,
              agreeableness: 0.3, neuroticism: 0.4}
appraisal:
  basic:
    SunIsShining:
      - {tag: GoodEvent, desirability: 0.7}
  acts:
    - act: Disturb
      scope: direct               # self | direct | indirect
      performer: Sven             # optional filter
      appraisals:
        - {tag: BadEvent, desirability: -0.5}
        - {tag: BadActOther, praiseworthiness: -0.6}
  emotion_displays:
    - display: ReproachDisplay
      scope: self                 # self | other
      appraisals:
        - {tag: BadEvent, desirability: -0.3}
  mood_displays: []
```

An appraisal entry is either `{tag: <BasicTagName>, ...}` or a raw EEC
such as `{desirability: -0.5, praiseworthiness: -0.3, agency: other}`.

### The paper's Fig. 4 character in YAML

The AAMAS'05 paper's own example character specification (an AffectML
document), translated one-to-one, see the mapping table on the
[Configuration](configuration.md) page:

```yaml
name: Valerie
personality: {openness: 0.4, conscientiousness: 0.8, extraversion: 0.6,
              agreeableness: 0.3, neuroticism: 0.4}
appraisal:
  basic:
    GoodEvent:                              # paper form: input = tag name
      - {tag: GoodEvent, desirability: 0.7}
  acts:
    - act: Calm                             # <SelfAct type="Calm">
      scope: self
      appraisals:
        - {tag: GoodActSelf, praiseworthiness: 0.5}
    - act: Attack                           # <DirectAct type="Attack"
      scope: direct                         #            performer="Sven">
      performer: Sven
      appraisals:
        - {tag: BadEvent, desirability: -0.5}
        - {tag: BadActOther, praiseworthiness: -0.3}
  emotion_displays:
    - display: ReproachDisplay              # <SelfEmotion emotion=...>
      scope: self
      appraisals:
        - {tag: BadEvent, desirability: -0.3}
```

## Shipped example scripts

The repository's `examples/` directory contains ready-to-run material:

| File | What it shows |
|---|---|
| `examples/quickstart.py` | One character: appraisals, decay, a mood arc, the return to the default mood |
| `examples/virtualhuman.py` | The paper's Valerie-and-Sven lesson scenario, loading profiles from files |
| `examples/affect.yaml` | Commented configuration template with every parameter at its publication default |
| `examples/valerie.yaml` | Valerie's profile: personality, event, act and display rules |
| `examples/sven.yaml` | Sven's profile |
