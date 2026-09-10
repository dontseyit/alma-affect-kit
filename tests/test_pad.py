"""PAD space: octants, strength bands and vector operations."""

import pytest

from alma_affect_kit import PAD, MoodOctant, MoodStrength, SQRT3


class TestOctants:
    """Table 1 of the paper."""

    @pytest.mark.parametrize("point,octant", [
        ((+0.5, +0.5, +0.5), MoodOctant.EXUBERANT),
        ((-0.5, -0.5, -0.5), MoodOctant.BORED),
        ((+0.5, +0.5, -0.5), MoodOctant.DEPENDENT),
        ((-0.5, -0.5, +0.5), MoodOctant.DISDAINFUL),
        ((+0.5, -0.5, +0.5), MoodOctant.RELAXED),
        ((-0.5, +0.5, -0.5), MoodOctant.ANXIOUS),
        ((+0.5, -0.5, -0.5), MoodOctant.DOCILE),
        ((-0.5, +0.5, +0.5), MoodOctant.HOSTILE),
    ])
    def test_all_eight_octants(self, point, octant):
        assert PAD(*point).octant is octant

    def test_paper_example(self):
        """pleasure=0.25, arousal=-0.18, dominance=0.12 -> slightly
        relaxed (paper, section 3)."""
        mood = PAD(0.25, -0.18, 0.12)
        assert mood.octant is MoodOctant.RELAXED
        assert mood.strength is MoodStrength.SLIGHTLY
        assert mood.describe() == "slightly relaxed"


class TestStrength:
    """sqrt(3) divided into three equal parts: slightly, moderate, fully."""

    def test_thresholds(self):
        assert MoodStrength.from_norm(0.0) is MoodStrength.SLIGHTLY
        assert MoodStrength.from_norm(SQRT3 / 3 - 1e-9) is MoodStrength.SLIGHTLY
        assert MoodStrength.from_norm(SQRT3 / 3) is MoodStrength.MODERATE
        assert MoodStrength.from_norm(2 * SQRT3 / 3 - 1e-9) is \
            MoodStrength.MODERATE
        assert MoodStrength.from_norm(2 * SQRT3 / 3) is MoodStrength.FULLY
        assert MoodStrength.from_norm(SQRT3) is MoodStrength.FULLY

    def test_full_corner(self):
        assert PAD(1.0, 1.0, 1.0).strength is MoodStrength.FULLY


class TestVector:
    def test_construction_does_not_clamp(self):
        """Vector algebra must be exact; clamping is explicit via
        clamped() (a constructor clamp silently corrupted difference
        vectors, bending mood trajectories)."""
        p = PAD(2.0, -3.0, 0.5)
        assert p.pleasure == 2.0 and p.arousal == -3.0 and p.dominance == 0.5
        clamped = p.clamped()
        assert clamped.pleasure == 1.0 and clamped.arousal == -1.0 \
            and clamped.dominance == 0.5

    def test_distance_across_the_cube_is_exact(self):
        assert PAD(-1, -1, -1).distance(PAD(1, 1, 1)) == \
            pytest.approx(2 * SQRT3)
        assert PAD(-1, 0, 0).distance(PAD(1, 0, 0)) == pytest.approx(2.0)

    def test_moved_towards_no_overshoot_on_long_deltas(self):
        moved = PAD(-1, -1, -1).moved_towards(PAD(1, 1, 1), 1.8)
        assert moved != PAD(1, 1, 1)  # 2*sqrt(3) away, step only 1.8
        assert moved.distance(PAD(1, 1, 1)) == pytest.approx(2 * SQRT3 - 1.8)

    def test_norm(self):
        assert PAD(1.0, 1.0, 1.0).norm() == pytest.approx(SQRT3)
        assert PAD().norm() == 0.0

    def test_moved_towards_no_overshoot(self):
        start, target = PAD(0, 0, 0), PAD(0.1, 0, 0)
        assert start.moved_towards(target, 5.0) == target

    def test_moved_towards_step(self):
        moved = PAD(0, 0, 0).moved_towards(PAD(1.0, 0, 0), 0.25)
        assert moved.pleasure == pytest.approx(0.25)

    def test_algebra(self):
        a, b = PAD(0.2, 0.4, -0.2), PAD(0.1, -0.1, 0.1)
        assert (a + b).as_tuple() == pytest.approx((0.3, 0.3, -0.1))
        assert (a - b).as_tuple() == pytest.approx((0.1, 0.5, -0.3))
        assert a.scaled(2.0).as_tuple() == pytest.approx((0.4, 0.8, -0.4))
        assert PAD(0.6, 0, 0).normalized().as_tuple() == \
            pytest.approx((1.0, 0.0, 0.0))
