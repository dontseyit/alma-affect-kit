"""alma-affect-kit quick start: one character, a few appraisals, mood over time."""

from alma_affect_kit import (AffectEngine, Personality, bad_act_other, bad_event,
                    good_event)

engine = AffectEngine()  # publication defaults

# Big Five personality in [-1, 1]; the paper's example character
valerie = engine.add_character("Valerie", Personality(
    openness=0.4, conscientiousness=0.8, extraversion=0.6,
    agreeableness=0.3, neuroticism=0.4))

print(f"default mood: {valerie.default_mood!r} -> {valerie.mood_word}")

# something good happens
engine.appraise("Valerie", good_event(0.7, cause="sun is shining"))
engine.update(0.5)
print(f"after a good event: dominant={valerie.dominant_emotion}")

# let the emotion decay (default: 20 s, linear)
engine.run(25.0)
print(f"after 25 s: active emotions={valerie.active_emotions}, "
      f"mood={valerie.mood_word}")

# a stream of bad experiences darkens the mood (pull/push function)
for _ in range(40):
    engine.appraise("Valerie", [bad_event(-0.5, cause="attack"),
                                bad_act_other(-0.3, cause="attack")])
    engine.run(15.0)
print(f"after repeated attacks: mood={valerie.mood!r} -> {valerie.mood_word}")

# without new input the mood slowly returns to the default mood (20 min)
engine.run(1300.0)
print(f"after 20+ quiet minutes: mood={valerie.mood!r} -> {valerie.mood_word}")
