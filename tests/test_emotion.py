"""Emotion layer: the 24 OCC types, Table 2 PAD mapping, decay."""

import pytest

from alma_affect_kit import (ActiveEmotion, DecayFunction, DEFAULT_EMOTION_PAD_MAP,
                    EmotionType, MoodOctant)


class TestEmotionTypes:
    def test_twenty_four_types(self):
        assert len(EmotionType) == 24

    def test_pad_map_covers_all_types(self):
        assert set(DEFAULT_EMOTION_PAD_MAP) == set(EmotionType)

    @pytest.mark.parametrize("emotion,pad,octant", [
        (EmotionType.ADMIRATION, (0.5, 0.3, -0.2), MoodOctant.DEPENDENT),
        (EmotionType.ANGER, (-0.51, 0.59, 0.25), MoodOctant.HOSTILE),
        (EmotionType.FEAR, (-0.64, 0.60, -0.43), MoodOctant.ANXIOUS),
        (EmotionType.GRATIFICATION, (0.6, 0.5, 0.4), MoodOctant.EXUBERANT),
        (EmotionType.JOY, (0.4, 0.2, 0.1), MoodOctant.EXUBERANT),
        (EmotionType.LIKING, (0.40, 0.16, -0.24), MoodOctant.DEPENDENT),
        (EmotionType.RELIEF, (0.2, -0.3, 0.4), MoodOctant.RELAXED),
        (EmotionType.REPROACH, (-0.3, -0.1, 0.4), MoodOctant.DISDAINFUL),
        (EmotionType.SHAME, (-0.3, 0.1, -0.6), MoodOctant.ANXIOUS),
        (EmotionType.GLOATING, (0.3, -0.3, -0.1), MoodOctant.DOCILE),
    ])
    def test_table2_spot_checks(self, emotion, pad, octant):
        entry = DEFAULT_EMOTION_PAD_MAP[emotion]
        assert entry.as_tuple() == pytest.approx(pad)
        assert entry.octant is octant

    #: AAMAS'05 Table 2, transcribed in full (P, A, D, octant).
    PAPER_TABLE_2 = {
        "Admiration": (0.5, 0.3, -0.2, "Dependent"),
        "Anger": (-0.51, 0.59, 0.25, "Hostile"),
        "Disliking": (-0.4, 0.2, 0.1, "Hostile"),
        "Disappointment": (-0.3, 0.1, -0.4, "Anxious"),
        "Distress": (-0.4, -0.2, -0.5, "Bored"),
        "Fear": (-0.64, 0.60, -0.43, "Anxious"),
        "FearsConfirmed": (-0.5, -0.3, -0.7, "Bored"),
        "Gloating": (0.3, -0.3, -0.1, "Docile"),
        "Gratification": (0.6, 0.5, 0.4, "Exuberant"),
        "Gratitude": (0.4, 0.2, -0.3, "Dependent"),
        "HappyFor": (0.4, 0.2, 0.2, "Exuberant"),
        "Hate": (-0.6, 0.6, 0.3, "Hostile"),
        "Hope": (0.2, 0.2, -0.1, "Dependent"),
        "Joy": (0.4, 0.2, 0.1, "Exuberant"),
        "Liking": (0.40, 0.16, -0.24, "Dependent"),
        "Love": (0.3, 0.1, 0.2, "Exuberant"),
        "Pity": (-0.4, -0.2, -0.5, "Bored"),
        "Pride": (0.4, 0.3, 0.3, "Exuberant"),
        "Relief": (0.2, -0.3, 0.4, "Relaxed"),
        "Remorse": (-0.3, 0.1, -0.6, "Anxious"),
        "Reproach": (-0.3, -0.1, 0.4, "Disdainful"),
        "Resentment": (-0.2, -0.3, -0.2, "Bored"),
        "Satisfaction": (0.3, -0.2, 0.4, "Relaxed"),
        "Shame": (-0.3, 0.1, -0.6, "Anxious"),
    }

    def test_table2_complete(self):
        """Every row of the paper's Table 2, values and octant."""
        assert len(self.PAPER_TABLE_2) == 24
        for name, (p, a, d, octant) in self.PAPER_TABLE_2.items():
            entry = DEFAULT_EMOTION_PAD_MAP[EmotionType.from_name(name)]
            assert entry.as_tuple() == (p, a, d), name
            assert entry.octant.label == octant, name

    def test_from_name(self):
        assert EmotionType.from_name("FearsConfirmed") is \
            EmotionType.FEARS_CONFIRMED
        assert EmotionType.from_name("joy") is EmotionType.JOY
        with pytest.raises(KeyError):
            EmotionType.from_name("Ennui")


class TestDecayFunctions:
    @pytest.mark.parametrize("function", list(DecayFunction))
    def test_bounds(self, function):
        assert function.factor(0.0) == pytest.approx(1.0)
        assert function.factor(1.0) == pytest.approx(0.0, abs=0.01)
        assert function.factor(2.0) == 0.0

    @pytest.mark.parametrize("function", list(DecayFunction))
    def test_monotonically_decreasing(self, function):
        values = [function.factor(u / 10) for u in range(11)]
        assert all(a >= b for a, b in zip(values, values[1:]))

    def test_linear_midpoint(self):
        assert DecayFunction.LINEAR.factor(0.5) == pytest.approx(0.5)

    def test_from_name(self):
        assert DecayFunction.from_name("linear") is DecayFunction.LINEAR
        assert DecayFunction.from_name("tanh") is \
            DecayFunction.TANGENS_HYPERBOLICUS


class TestActiveEmotion:
    def make(self, **kw):
        defaults = dict(type=EmotionType.JOY, initial_intensity=0.8,
                        decay_time=20.0,
                        decay_function=DecayFunction.LINEAR)
        defaults.update(kw)
        return ActiveEmotion(**defaults)

    def test_initial_intensity(self):
        assert self.make().intensity == pytest.approx(0.8)

    def test_linear_decay_over_default_20s(self):
        emotion = self.make()
        emotion.tick(10.0)
        assert emotion.intensity == pytest.approx(0.4)
        emotion.tick(10.0)
        assert emotion.expired

    def test_decays_to_personality_baseline(self):
        emotion = self.make(baseline=0.15)
        emotion.tick(10.0)
        assert emotion.intensity == pytest.approx(0.15 + 0.65 * 0.5)
        emotion.tick(10.0)
        assert emotion.intensity == pytest.approx(0.15)
        assert emotion.expired

    def test_intensity_clamped(self):
        assert self.make(initial_intensity=1.7).intensity == 1.0

    def test_elicitation_below_baseline_stays_active(self):
        """A stimulus weaker than the personality baseline is raised to
        the baseline and stays active for decay_time instead of expiring
        at birth (which silently swallowed mild stimuli)."""
        emotion = self.make(initial_intensity=0.10, baseline=0.15)
        assert emotion.intensity == pytest.approx(0.15)
        assert not emotion.expired
        emotion.tick(10.0)
        assert not emotion.expired
        emotion.tick(10.1)  # decay_time reached
        assert emotion.expired
