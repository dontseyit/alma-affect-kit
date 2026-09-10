"""PAD (pleasure-arousal-dominance) mood space: vectors, the eight named
octants (paper, Table 1) and the slightly/moderate/fully strength bands
(thirds of sqrt(3)).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

SQRT3 = math.sqrt(3.0)

__all__ = ["PAD", "MoodOctant", "MoodStrength", "SQRT3"]


class MoodOctant(Enum):
    """Discrete mood names for the eight PAD octants (paper, Table 1)."""

    EXUBERANT = ("Exuberant", (+1, +1, +1))
    BORED = ("Bored", (-1, -1, -1))
    DEPENDENT = ("Dependent", (+1, +1, -1))
    DISDAINFUL = ("Disdainful", (-1, -1, +1))
    RELAXED = ("Relaxed", (+1, -1, +1))
    ANXIOUS = ("Anxious", (-1, +1, -1))
    DOCILE = ("Docile", (+1, -1, -1))
    HOSTILE = ("Hostile", (-1, +1, +1))

    def __init__(self, label: str, signs: tuple):
        self.label = label
        self.signs = signs

    @classmethod
    def from_signs(cls, p: float, a: float, d: float) -> "MoodOctant":
        """Octant of a PAD point.  Zero counts as positive, following the
        convention that the push phase starts *at* the emotion centre."""
        key = (1 if p >= 0 else -1, 1 if a >= 0 else -1, 1 if d >= 0 else -1)
        for octant in cls:
            if octant.signs == key:
                return octant
        raise AssertionError("unreachable")

    def __str__(self) -> str:
        return self.label


class MoodStrength(Enum):
    """Mood strength bands: sqrt(3) divided into three equal parts."""

    SLIGHTLY = "slightly"
    MODERATE = "moderate"
    FULLY = "fully"

    @classmethod
    def from_norm(cls, norm: float) -> "MoodStrength":
        if norm < SQRT3 / 3.0:
            return cls.SLIGHTLY
        if norm < 2.0 * SQRT3 / 3.0:
            return cls.MODERATE
        return cls.FULLY

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PAD:
    """A vector in the PAD mood space.

    Components are *not* clamped on construction, so vector algebra
    (differences, sums, scaling) is exact, essential for correct
    distances and movement directions.  Mood points are kept inside the
    [-1, 1] cube by the engine via :meth:`clamped`.
    """

    pleasure: float = 0.0
    arousal: float = 0.0
    dominance: float = 0.0

    def __post_init__(self):
        object.__setattr__(self, "pleasure", float(self.pleasure))
        object.__setattr__(self, "arousal", float(self.arousal))
        object.__setattr__(self, "dominance", float(self.dominance))

    def clamped(self) -> "PAD":
        """This vector with each component clamped to [-1, 1]."""
        def clamp(x: float) -> float:
            return max(-1.0, min(1.0, x))
        return PAD(clamp(self.pleasure), clamp(self.arousal),
                   clamp(self.dominance))

    # -- vector algebra -------------------------------------------------
    def __add__(self, other: "PAD") -> "PAD":
        return PAD(self.pleasure + other.pleasure,
                   self.arousal + other.arousal,
                   self.dominance + other.dominance)

    def __sub__(self, other: "PAD") -> "PAD":
        return PAD(self.pleasure - other.pleasure,
                   self.arousal - other.arousal,
                   self.dominance - other.dominance)

    def scaled(self, k: float) -> "PAD":
        return PAD(self.pleasure * k, self.arousal * k, self.dominance * k)

    def dot(self, other: "PAD") -> float:
        return (self.pleasure * other.pleasure
                + self.arousal * other.arousal
                + self.dominance * other.dominance)

    def norm(self) -> float:
        return math.sqrt(self.dot(self))

    def distance(self, other: "PAD") -> float:
        return (self - other).norm()

    def normalized(self) -> "PAD":
        n = self.norm()
        if n == 0.0:
            return PAD(0.0, 0.0, 0.0)
        return self.scaled(1.0 / n)

    def moved_towards(self, target: "PAD", step: float) -> "PAD":
        """Move ``step`` PAD units towards ``target`` without overshooting."""
        delta = target - self
        dist = delta.norm()
        if dist <= step or dist == 0.0:
            return target
        return self + delta.scaled(step / dist)

    # -- discrete description ------------------------------------------
    @property
    def octant(self) -> MoodOctant:
        return MoodOctant.from_signs(self.pleasure, self.arousal, self.dominance)

    @property
    def strength(self) -> MoodStrength:
        return MoodStrength.from_norm(self.norm())

    def describe(self) -> str:
        """Discrete mood description, e.g. ``'slightly relaxed'``."""
        return f"{self.strength.value} {self.octant.label.lower()}"

    def as_tuple(self) -> tuple:
        return (self.pleasure, self.arousal, self.dominance)

    def __iter__(self):
        return iter(self.as_tuple())

    def __repr__(self) -> str:
        return (f"PAD(P={self.pleasure:+.2f}, A={self.arousal:+.2f}, "
                f"D={self.dominance:+.2f})")
