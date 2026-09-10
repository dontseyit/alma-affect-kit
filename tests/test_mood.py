"""Mood dynamics: virtual emotion centre, pull/push, mood return."""

import pytest

from alma_affect_kit import (ActiveEmotion, AffectConfig, DecayFunction, EmotionType,
                    MoodReturnMode, PAD, compute_emotion_center,
                    update_mood)
from alma_affect_kit.mood import VirtualEmotionCenter


def active(emotion_type, intensity, decay_time=1e9):
    """A long-lived active emotion for steady-state tests."""
    return ActiveEmotion(type=emotion_type, initial_intensity=intensity,
                         decay_time=decay_time,
                         decay_function=DecayFunction.LINEAR)


class TestVirtualEmotionCenter:
    def test_no_active_emotions_no_center(self):
        assert compute_emotion_center([], AffectConfig()) is None

    def test_single_emotion_center_at_its_pad_point(self):
        config = AffectConfig()
        vec = compute_emotion_center([active(EmotionType.JOY, 0.8)], config)
        assert vec.position.as_tuple() == pytest.approx((0.4, 0.2, 0.1))
        assert vec.intensity == pytest.approx(0.8)

    def test_center_is_average_of_points_and_intensities(self):
        config = AffectConfig()
        vec = compute_emotion_center(
            [active(EmotionType.JOY, 1.0),        # ( 0.4,  0.2,  0.1)
             active(EmotionType.DISTRESS, 0.5)],  # (-0.4, -0.2, -0.5)
            config)
        assert vec.position.as_tuple() == pytest.approx((0.0, 0.0, -0.2))
        assert vec.intensity == pytest.approx(0.75)

    def test_intensity_weighted_option(self):
        config = AffectConfig(vec_intensity_weighted=True)
        vec = compute_emotion_center(
            [active(EmotionType.JOY, 1.0),
             active(EmotionType.DISTRESS, 0.5)], config)
        # weighted towards joy
        assert vec.position.pleasure > 0.0


class TestPullPush:
    def test_pull_attracts_mood_towards_center(self):
        config = AffectConfig()
        vec = VirtualEmotionCenter(PAD(0.4, 0.2, 0.1), 1.0)
        mood = update_mood(PAD(), PAD(), vec, 1.0, config)
        assert mood.pleasure > 0.0
        # step length is intensity / mood_change_time
        assert mood.norm() == pytest.approx(1.0 / 600.0)

    def test_mood_change_time_calibration(self):
        """At full intensity the mood travels the distance between two
        octant centres (1.0 PAD unit) in mood_change_time seconds."""
        config = AffectConfig()
        vec = VirtualEmotionCenter(PAD(1.0, 0.0, 0.0), 1.0)
        mood = PAD()
        for _ in range(1200):  # 600 s in 0.5 s steps
            mood = update_mood(mood, PAD(), vec, 0.5, config)
        assert mood.pleasure == pytest.approx(1.0, abs=1e-6)

    def test_mood_change_distance_scales_speed(self):
        """Reading 'octant centre to octant centre' as opposite centres
        (sqrt 3) makes the mood 1.73x faster than the adjacent reading."""
        adjacent = update_mood(PAD(), PAD(), VirtualEmotionCenter(PAD(1, 0, 0), 1.0),
                               1.0, AffectConfig())
        opposite = update_mood(PAD(), PAD(), VirtualEmotionCenter(PAD(1, 0, 0), 1.0),
                               1.0, AffectConfig(mood_change_distance=3 ** 0.5))
        assert opposite.pleasure == pytest.approx(adjacent.pleasure * 3 ** 0.5)
        with pytest.raises(ValueError):
            AffectConfig(mood_change_distance=0)

    def test_intensity_scales_speed(self):
        config = AffectConfig()
        weak = update_mood(PAD(), PAD(),
                           VirtualEmotionCenter(PAD(1, 0, 0), 0.5), 1.0,
                           config)
        strong = update_mood(PAD(), PAD(),
                             VirtualEmotionCenter(PAD(1, 0, 0), 1.0), 1.0,
                             config)
        assert strong.pleasure == pytest.approx(2 * weak.pleasure)

    def test_push_phase_moves_mood_deeper_into_octant(self):
        """Beyond the emotion centre the mood is pushed further into its
        current octant instead of converging on the centre."""
        config = AffectConfig()
        vec = VirtualEmotionCenter(PAD(0.4, 0.2, 0.1), 1.0)
        mood = PAD(0.5, 0.25, 0.125)  # beyond the VEC on the same ray
        before_norm = mood.norm()
        octant = mood.octant
        mood = update_mood(mood, PAD(), vec, 1.0, config)
        assert mood.norm() > before_norm
        assert mood.octant is octant

    def test_push_clamps_at_space_boundary(self):
        config = AffectConfig(mood_change_time=1.0)  # very fast
        vec = VirtualEmotionCenter(PAD(0.4, 0.0, 0.0), 1.0)
        mood = PAD(0.9, 0.0, 0.0)
        for _ in range(10):
            mood = update_mood(mood, PAD(), vec, 1.0, config)
        assert mood.pleasure == 1.0

    def test_mood_always_stays_inside_the_cube(self):
        config = AffectConfig(mood_change_time=1.0)  # extreme push speed
        vec = VirtualEmotionCenter(PAD(0.5, 0.5, 0.5), 1.0)
        mood = PAD(0.6, 0.6, 0.6)
        for _ in range(20):
            mood = update_mood(mood, PAD(), vec, 5.0, config)
            assert all(-1.0 <= c <= 1.0 for c in mood)

    def test_pull_then_push_progression(self):
        """A persistent emotion centre first attracts the mood and then
        pushes it beyond itself (paper, Fig. 2)."""
        config = AffectConfig(mood_change_time=60.0)
        vec = VirtualEmotionCenter(PAD(0.4, 0.2, 0.1), 1.0)
        mood = PAD()
        for _ in range(240):  # 120 s
            mood = update_mood(mood, PAD(), vec, 0.5, config)
        # mood has been pushed beyond the centre, deeper into +P+A+D
        assert mood.norm() > vec.position.norm()
        assert mood.octant is vec.position.octant


class TestMoodReturn:
    def test_returns_to_default_without_active_emotions(self):
        config = AffectConfig()
        mood = update_mood(PAD(0.5, 0.5, 0.5), PAD(0.38, -0.08, 0.5),
                           None, 1.0, config)
        assert mood.distance(PAD(0.38, -0.08, 0.5)) < \
            PAD(0.5, 0.5, 0.5).distance(PAD(0.38, -0.08, 0.5))

    def test_return_time_calibration(self):
        """The mood travels the longest octant distance sqrt(3) back to
        the default mood in mood_return_time seconds (default 20 min)."""
        config = AffectConfig()
        default = PAD(1.0, 1.0, 1.0)
        mood = PAD(0.0, 0.0, 0.0)  # distance sqrt(3) from default
        elapsed = 0.0
        while mood != default and elapsed < 1300:
            mood = update_mood(mood, default, None, 0.5, config)
            elapsed += 0.5
        assert mood == default
        assert elapsed == pytest.approx(1200.0, abs=1.0)

    def test_no_overshoot(self):
        config = AffectConfig(mood_return_time=1.0)
        mood = update_mood(PAD(0.1, 0, 0), PAD(), None, 10.0, config)
        assert mood == PAD()

    def test_idle_mode_suspends_return_while_emotions_active(self):
        config = AffectConfig(mood_return_mode=MoodReturnMode.IDLE)
        vec = VirtualEmotionCenter(PAD(0.4, 0.2, 0.1), 1.0)
        default = PAD(-0.5, -0.5, -0.5)
        mood = update_mood(PAD(), default, vec, 1.0, config)
        # moved towards the VEC, not towards the default mood
        assert mood.pleasure > 0.0

    def test_always_mode_combines_both_forces(self):
        config = AffectConfig(mood_return_mode=MoodReturnMode.ALWAYS)
        vec = VirtualEmotionCenter(PAD(1.0, 0.0, 0.0), 1.0)
        pulled_only = update_mood(PAD(), PAD(), vec, 1.0,
                                  AffectConfig())
        combined = update_mood(PAD(), PAD(), vec, 1.0, config)
        # the return force (towards default at the origin) damps the pull
        assert 0.0 < combined.pleasure < pulled_only.pleasure
