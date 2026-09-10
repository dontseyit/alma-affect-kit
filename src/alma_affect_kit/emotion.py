"""OCC emotions: the 24 emotion types, their PAD mapping (paper,
Table 2), the decay functions and the decaying active-emotion instance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

from .pad import PAD

__all__ = [
    "EmotionType",
    "OCCGroup",
    "DEFAULT_EMOTION_PAD_MAP",
    "DecayFunction",
    "ActiveEmotion",
]


class OCCGroup(Enum):
    """OCC emotion groups (used e.g. for personality influences)."""

    WELL_BEING = "well-being"
    PROSPECT_BASED = "prospect-based"
    FORTUNES_OF_OTHERS = "fortunes-of-others"
    ATTRIBUTION = "attribution"
    WELL_BEING_ATTRIBUTION = "well-being/attribution"  # compounds
    ATTRACTION = "attraction"


class EmotionType(Enum):
    """The 24 emotion types supported by ALMA's EmotionEngine."""

    # well-being
    JOY = ("Joy", OCCGroup.WELL_BEING, +1)
    DISTRESS = ("Distress", OCCGroup.WELL_BEING, -1)
    # prospect-based
    HOPE = ("Hope", OCCGroup.PROSPECT_BASED, +1)
    FEAR = ("Fear", OCCGroup.PROSPECT_BASED, -1)
    SATISFACTION = ("Satisfaction", OCCGroup.PROSPECT_BASED, +1)
    FEARS_CONFIRMED = ("FearsConfirmed", OCCGroup.PROSPECT_BASED, -1)
    RELIEF = ("Relief", OCCGroup.PROSPECT_BASED, +1)
    DISAPPOINTMENT = ("Disappointment", OCCGroup.PROSPECT_BASED, -1)
    # fortunes of others
    HAPPY_FOR = ("HappyFor", OCCGroup.FORTUNES_OF_OTHERS, +1)
    RESENTMENT = ("Resentment", OCCGroup.FORTUNES_OF_OTHERS, -1)
    GLOATING = ("Gloating", OCCGroup.FORTUNES_OF_OTHERS, +1)
    PITY = ("Pity", OCCGroup.FORTUNES_OF_OTHERS, -1)
    # attribution
    PRIDE = ("Pride", OCCGroup.ATTRIBUTION, +1)
    SHAME = ("Shame", OCCGroup.ATTRIBUTION, -1)
    ADMIRATION = ("Admiration", OCCGroup.ATTRIBUTION, +1)
    REPROACH = ("Reproach", OCCGroup.ATTRIBUTION, -1)
    # well-being / attribution compounds
    GRATIFICATION = ("Gratification", OCCGroup.WELL_BEING_ATTRIBUTION, +1)
    REMORSE = ("Remorse", OCCGroup.WELL_BEING_ATTRIBUTION, -1)
    GRATITUDE = ("Gratitude", OCCGroup.WELL_BEING_ATTRIBUTION, +1)
    ANGER = ("Anger", OCCGroup.WELL_BEING_ATTRIBUTION, -1)
    # attraction
    LIKING = ("Liking", OCCGroup.ATTRACTION, +1)
    DISLIKING = ("Disliking", OCCGroup.ATTRACTION, -1)
    LOVE = ("Love", OCCGroup.ATTRACTION, +1)
    HATE = ("Hate", OCCGroup.ATTRACTION, -1)

    def __init__(self, label: str, group: OCCGroup, valence: int):
        self.label = label
        self.group = group
        self.valence = valence  # +1 positive emotion, -1 negative emotion

    @classmethod
    def from_name(cls, name: str) -> "EmotionType":
        """Look up an emotion type by label or member name, case-insensitive."""
        try:
            return _EMOTION_LOOKUP[name.lower()]
        except KeyError:
            raise KeyError(f"unknown emotion type: {name!r}") from None

    def __str__(self) -> str:
        return self.label


_EMOTION_LOOKUP: Dict[str, EmotionType] = {}
for _member in EmotionType:
    _EMOTION_LOOKUP[_member.label.lower()] = _member
    _EMOTION_LOOKUP[_member.name.lower()] = _member


#: Mapping of OCC emotions into PAD space (paper, Table 2).
DEFAULT_EMOTION_PAD_MAP: Dict[EmotionType, PAD] = {
    EmotionType.ADMIRATION: PAD(0.5, 0.3, -0.2),        # +P+A-D Dependent
    EmotionType.ANGER: PAD(-0.51, 0.59, 0.25),          # -P+A+D Hostile
    EmotionType.DISLIKING: PAD(-0.4, 0.2, 0.1),         # -P+A+D Hostile
    EmotionType.DISAPPOINTMENT: PAD(-0.3, 0.1, -0.4),   # -P+A-D Anxious
    EmotionType.DISTRESS: PAD(-0.4, -0.2, -0.5),        # -P-A-D Bored
    EmotionType.FEAR: PAD(-0.64, 0.60, -0.43),          # -P+A-D Anxious
    EmotionType.FEARS_CONFIRMED: PAD(-0.5, -0.3, -0.7), # -P-A-D Bored
    EmotionType.GLOATING: PAD(0.3, -0.3, -0.1),         # +P-A-D Docile
    EmotionType.GRATIFICATION: PAD(0.6, 0.5, 0.4),      # +P+A+D Exuberant
    EmotionType.GRATITUDE: PAD(0.4, 0.2, -0.3),         # +P+A-D Dependent
    EmotionType.HAPPY_FOR: PAD(0.4, 0.2, 0.2),          # +P+A+D Exuberant
    EmotionType.HATE: PAD(-0.6, 0.6, 0.3),              # -P+A+D Hostile
    EmotionType.HOPE: PAD(0.2, 0.2, -0.1),              # +P+A-D Dependent
    EmotionType.JOY: PAD(0.4, 0.2, 0.1),                # +P+A+D Exuberant
    EmotionType.LIKING: PAD(0.40, 0.16, -0.24),         # +P+A-D Dependent
    EmotionType.LOVE: PAD(0.3, 0.1, 0.2),               # +P+A+D Exuberant
    EmotionType.PITY: PAD(-0.4, -0.2, -0.5),            # -P-A-D Bored
    EmotionType.PRIDE: PAD(0.4, 0.3, 0.3),              # +P+A+D Exuberant
    EmotionType.RELIEF: PAD(0.2, -0.3, 0.4),            # +P-A+D Relaxed
    EmotionType.REMORSE: PAD(-0.3, 0.1, -0.6),          # -P+A-D Anxious
    EmotionType.REPROACH: PAD(-0.3, -0.1, 0.4),         # -P-A+D Disdainful
    EmotionType.RESENTMENT: PAD(-0.2, -0.3, -0.2),      # -P-A-D Bored
    EmotionType.SATISFACTION: PAD(0.3, -0.2, 0.4),      # +P-A+D Relaxed
    EmotionType.SHAME: PAD(-0.3, 0.1, -0.6),            # -P+A-D Anxious
}


class DecayFunction(Enum):
    """Emotion decay functions provided by the EmotionEngine.

    The papers name three decay functions (linear, exponential and
    tangens hyperbolicus).  Each maps normalized elapsed time
    ``u = t / decay_time`` in [0, 1] to a remaining-intensity factor in
    [1, 0]; at ``u >= 1`` the emotion has fully decayed.
    """

    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    TANGENS_HYPERBOLICUS = "tanhyp"

    def factor(self, u: float) -> float:
        if u <= 0.0:
            return 1.0
        if u >= 1.0:
            return 0.0
        if self is DecayFunction.LINEAR:
            return 1.0 - u
        if self is DecayFunction.EXPONENTIAL:
            # ~0.7% remaining at u == 1
            return math.exp(-5.0 * u)
        # tangens hyperbolicus: sigmoid decay, normalized so factor(0) == 1
        raw = 1.0 - math.tanh(6.0 * u - 3.0)
        return raw / (1.0 - math.tanh(-3.0))

    @classmethod
    def from_name(cls, name: str) -> "DecayFunction":
        name = name.lower()
        for f in cls:
            if f.value == name or f.name.lower() == name:
                return f
        aliases = {"tangens hyperbolicus": cls.TANGENS_HYPERBOLICUS,
                   "tanh": cls.TANGENS_HYPERBOLICUS}
        if name in aliases:
            return aliases[name]
        raise KeyError(f"unknown decay function: {name!r}")


@dataclass
class ActiveEmotion:
    """An elicited emotion instance decaying over time.

    Its intensity starts at ``initial_intensity`` (the appraisal result
    biased by the character's personality baseline for this emotion type)
    and decays back to ``baseline`` within ``decay_time`` seconds.  An
    elicitation weaker than the baseline is raised to the baseline: the
    emotion then stays active at its resting level for ``decay_time``.
    """

    type: EmotionType
    initial_intensity: float
    baseline: float = 0.0
    decay_time: float = 20.0
    decay_function: DecayFunction = DecayFunction.LINEAR
    cause: Optional[str] = None
    age: float = 0.0
    pad: Optional[PAD] = None  # resolved from the configured map by the engine

    def __post_init__(self):
        self.baseline = max(0.0, min(1.0, self.baseline))
        self.initial_intensity = max(self.baseline,
                                     min(1.0, self.initial_intensity))
        self._cached_age = None
        self._cached_intensity = None

    @property
    def intensity(self) -> float:
        """Current intensity: decays from the initial value to baseline."""
        if self._cached_age == self.age:
            return self._cached_intensity
        u = self.age / self.decay_time if self.decay_time > 0 else 1.0
        f = self.decay_function.factor(u)
        value = self.baseline + (self.initial_intensity - self.baseline) * f
        self._cached_age, self._cached_intensity = self.age, value
        return value

    @property
    def expired(self) -> bool:
        """True once the emotion has fully decayed back to its baseline."""
        if self.age >= self.decay_time:
            return True
        return (self.initial_intensity > self.baseline
                and self.intensity - self.baseline <= 1e-6)

    def tick(self, dt: float) -> None:
        """Advance the emotion's age by ``dt`` seconds."""
        self.age += dt

    def __repr__(self) -> str:
        return (f"ActiveEmotion({self.type.label}, intensity={self.intensity:.2f}, "
                f"cause={self.cause!r})")
