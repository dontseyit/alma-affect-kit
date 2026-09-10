"""Integration: the affect engine running the paper's scenario."""

import pytest

from alma_affect_kit import (AffectConfig, AffectEngine, AppraisalRules, EmotionType,
                    MoodOctant, Personality, bad_act_other, bad_event,
                    good_act_other, good_event)

#: Personalities from the paper (Valerie: section 3; Sven: Fig. 5 output).
VALERIE = Personality(openness=0.4, conscientiousness=0.8, extraversion=0.6,
                      agreeableness=0.3, neuroticism=0.4)
SVEN = Personality(openness=0.3, conscientiousness=-0.6, extraversion=0.7,
                   agreeableness=0.4, neuroticism=-0.1)


def make_engine():
    engine = AffectEngine()
    valerie_rules = (AppraisalRules()
                     .on_event("SunIsShining", good_event(0.7))
                     .on_act("Attack", "direct", bad_event(-0.5),
                             bad_act_other(-0.3), performer="Sven")
                     .on_act("Encourage", "direct", good_event(0.5),
                             good_act_other(0.5)))
    sven_rules = (AppraisalRules()
                  .on_act("Encourage", "direct", good_event(0.6),
                          good_act_other(0.4)))
    engine.add_character("Valerie", VALERIE, valerie_rules)
    engine.add_character("Sven", SVEN, sven_rules)
    return engine


class TestCharacterSetup:
    def test_default_mood_from_personality(self):
        engine = make_engine()
        mood = engine["Valerie"].default_mood
        assert mood.pleasure == pytest.approx(0.38, abs=0.005)
        assert mood.arousal == pytest.approx(-0.08, abs=0.005)
        assert mood.dominance == pytest.approx(0.50, abs=0.005)
        assert mood.octant is MoodOctant.RELAXED

    def test_initial_mood_is_default_mood(self):
        engine = make_engine()
        assert engine["Valerie"].mood == engine["Valerie"].default_mood

    def test_duplicate_character_rejected(self):
        engine = make_engine()
        with pytest.raises(ValueError):
            engine.add_character("Valerie")


class TestAppraisalDispatch:
    def test_event_appraised_via_basic_rules(self):
        engine = make_engine()
        elicited = engine.perceive_event("SunIsShining")
        assert set(elicited) == {"Valerie"}  # Sven has no rule for it
        assert elicited["Valerie"][0].type is EmotionType.JOY

    def test_attack_elicits_distress_reproach_and_anger(self):
        """The Fig. 4 scenario: Sven attacks Valerie."""
        engine = make_engine()
        elicited = engine.perceive_act("Attack", performer="Sven",
                                       addressee="Valerie")
        types = {e.type for e in elicited["Valerie"]}
        assert {EmotionType.DISTRESS, EmotionType.REPROACH,
                EmotionType.ANGER} <= types

    def test_act_rule_performer_filter(self):
        engine = make_engine()
        # an attack by someone else does not match Valerie's Sven-rule
        elicited = engine.perceive_act("Attack", performer="Ghost",
                                       addressee="Valerie")
        assert "Valerie" not in elicited

    def test_personality_bias_raises_intensity(self):
        engine = make_engine()
        biased = engine.appraise("Valerie", good_event(0.5))[0]
        unbiased_config = AffectConfig(apply_personality_bias=False)
        neutral = AffectEngine(unbiased_config)
        neutral.add_character("Valerie", VALERIE)
        plain = neutral.appraise("Valerie", good_event(0.5))[0]
        assert biased.intensity > plain.intensity


class TestDynamics:
    def test_dominant_emotion_threshold(self):
        engine = make_engine()
        # 0.2 plus Valerie's joy baseline (0.12) stays below the 0.4
        # dominance threshold
        engine.appraise("Valerie", good_event(0.2))
        assert engine["Valerie"].dominant_emotion is None
        engine.appraise("Valerie", good_event(0.9))
        dominant = engine["Valerie"].dominant_emotion
        assert dominant is not None and dominant.type is EmotionType.JOY

    def test_emotions_decay_and_expire(self):
        engine = make_engine()
        engine.appraise("Valerie", good_event(0.9))
        engine.run(1.0)
        assert engine["Valerie"].active_emotions
        engine.run(25.0)  # default decay time is 20 s
        assert not engine["Valerie"].active_emotions

    def test_positive_emotions_push_mood_up(self):
        engine = make_engine()
        sven = engine["Sven"]
        start_pleasure = sven.mood.pleasure
        for _ in range(20):  # repeated encouragement from Valerie
            engine.perceive_act("Encourage", performer="Valerie",
                                addressee="Sven")
            engine.run(10.0)
        assert sven.mood.pleasure > start_pleasure

    def test_negative_emotions_pull_mood_down(self):
        engine = make_engine()
        valerie = engine["Valerie"]
        start = valerie.mood.pleasure
        for _ in range(30):
            engine.perceive_act("Attack", performer="Sven",
                                addressee="Valerie")
            engine.run(10.0)
        assert valerie.mood.pleasure < start

    def test_mood_returns_to_default_when_idle(self):
        engine = make_engine()
        valerie = engine["Valerie"]
        for _ in range(30):
            engine.perceive_act("Attack", performer="Sven",
                                addressee="Valerie")
            engine.run(10.0)
        disturbed = valerie.mood.distance(valerie.default_mood)
        engine.run(1300.0)  # > mood return time, no new input
        assert valerie.mood.distance(valerie.default_mood) < 1e-6
        assert disturbed > 0.0

    def test_engine_time_advances(self):
        engine = make_engine()
        engine.step(4)
        assert engine.time == pytest.approx(2.0)  # 4 x 500 ms
        engine.run(3.0)
        assert engine.time == pytest.approx(5.0)


class TestAffectOutput:
    def test_snapshot_structure(self):
        engine = make_engine()
        engine.appraise("Valerie", good_event(0.9, cause="test"))
        engine.update(0.5)
        output = engine.affect_output()["Valerie"]
        assert output["name"] == "Valerie"
        assert output["mood"]["moodword"] == "Relaxed"
        assert output["mood"]["intensity"] in ("slightly", "moderate",
                                               "fully")
        assert output["dominant_emotion"]["name"] == "Joy"
        assert output["active_emotions"][0]["cause"] == "test"
        assert output["personality"]["conscientiousness"] == 0.8

    def test_reset(self):
        engine = make_engine()
        engine.appraise("Valerie", bad_event(-0.9))
        engine.run(60.0)
        engine["Valerie"].reset()
        assert engine["Valerie"].mood == engine["Valerie"].default_mood
        assert not engine["Valerie"].active_emotions
