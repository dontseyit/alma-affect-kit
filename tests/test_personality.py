"""Personality layer: Big Five -> default mood and emotion baselines."""

import pytest

from alma_affect_kit import (EmotionType, MoodOctant, Personality, default_mood,
                    emotion_baseline)


#: The worked example from the AAMAS'05 paper, section 3.
PAPER_PERSONALITY = Personality(openness=0.4, conscientiousness=0.8,
                                extraversion=0.6, agreeableness=0.3,
                                neuroticism=0.4)


class TestDefaultMood:
    def test_paper_example_values(self):
        """openness=0.4, conscientiousness=0.8, extraversion=0.6,
        agreeableness=0.3, neuroticism=0.4 has the default mood
        (pleasure=0.38, arousal=-0.08, dominance=0.50)."""
        mood = default_mood(PAPER_PERSONALITY)
        assert mood.pleasure == pytest.approx(0.38, abs=0.005)
        assert mood.arousal == pytest.approx(-0.08, abs=0.005)
        assert mood.dominance == pytest.approx(0.50, abs=0.005)

    def test_paper_example_octant_is_relaxed(self):
        assert default_mood(PAPER_PERSONALITY).octant is MoodOctant.RELAXED

    def test_neutral_personality_has_neutral_mood(self):
        mood = default_mood(Personality())
        assert mood.as_tuple() == (0.0, 0.0, 0.0)

    def test_regression_weights(self):
        # pure extravert: P = 0.21, A = 0, D = 0.60
        mood = default_mood(Personality(extraversion=1.0))
        assert mood.pleasure == pytest.approx(0.21)
        assert mood.arousal == pytest.approx(0.0)
        assert mood.dominance == pytest.approx(0.60)
        # pure neurotic: P = 0.19, A = -0.57, D = 0
        mood = default_mood(Personality(neuroticism=1.0))
        assert mood.pleasure == pytest.approx(0.19)
        assert mood.arousal == pytest.approx(-0.57)
        assert mood.dominance == pytest.approx(0.0)


class TestPersonality:
    def test_traits_clamped_to_unit_interval(self):
        p = Personality(openness=2.0, neuroticism=-3.0)
        assert p.openness == 1.0
        assert p.neuroticism == -1.0

    def test_as_dict(self):
        d = PAPER_PERSONALITY.as_dict()
        assert d["conscientiousness"] == 0.8
        assert set(d) == {"openness", "conscientiousness", "extraversion",
                          "agreeableness", "neuroticism"}


class TestEmotionBaselines:
    def test_extravert_joy_baseline_is_015(self):
        """IVA'03: 'an extravert character's baseline intensity for joy is
        0.15, whereas an introvert character's would be 0.0'."""
        extravert = Personality(extraversion=1.0)
        introvert = Personality(extraversion=-1.0)
        assert emotion_baseline(extravert, EmotionType.JOY) == \
            pytest.approx(0.15)
        assert emotion_baseline(introvert, EmotionType.JOY) == 0.0

    def test_agreeableness_raises_positive_baselines(self):
        friendly = Personality(extraversion=1.0, agreeableness=1.0)
        assert emotion_baseline(friendly, EmotionType.JOY) > 0.15

    def test_neurotic_negative_baseline(self):
        neurotic = Personality(neuroticism=1.0)
        stable = Personality(neuroticism=-1.0)
        assert emotion_baseline(neurotic, EmotionType.DISTRESS) == \
            pytest.approx(0.15)
        assert emotion_baseline(stable, EmotionType.DISTRESS) == 0.0

    def test_baselines_never_negative(self):
        for emotion in EmotionType:
            value = emotion_baseline(Personality(openness=-1,
                                                 conscientiousness=-1,
                                                 extraversion=-1,
                                                 agreeableness=-1,
                                                 neuroticism=-1), emotion)
            assert value >= 0.0
