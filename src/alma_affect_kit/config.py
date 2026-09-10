"""Affect computation parameters with the publication defaults
(AAMAS'05 section 3 and Fig. 3).  Every parameter's meaning, default,
source and valid range is documented in docs/configuration.md; the
choices where the paper is ambiguous are in docs/fidelity.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping

from .emotion import DecayFunction, DEFAULT_EMOTION_PAD_MAP, EmotionType
from .pad import PAD
from .personality import (DEFAULT_PERSONALITY_BASELINES,
                          DEFAULT_PERSONALITY_TO_MOOD, TRAITS)

__all__ = ["AffectConfig", "MoodReturnMode"]


class MoodReturnMode:
    """When the mood-return tendency applies.

    ``IDLE``  -- only while no active emotions exist (default; with active
    emotions the virtual emotion centre drives the mood, without it the
    mood slowly drifts back to the default mood).
    ``ALWAYS`` -- the return tendency is applied on every update, in
    addition to the pull/push force.
    """

    IDLE = "idle"
    ALWAYS = "always"


@dataclass
class AffectConfig:
    """Global affect computation parameters (see module docstring)."""

    # -- emotions -------------------------------------------------------
    #: Seconds an elicited emotion needs to decay back to its baseline.
    emotion_decay_time: float = 20.0
    #: Decay function: linear, exponential or tangens hyperbolicus.
    decay_function: DecayFunction = DecayFunction.LINEAR
    #: Only the most dominant emotion whose intensity exceeds this
    #: threshold impacts behaviour (``Character.dominant_emotion``).
    dominant_emotion_threshold: float = 0.4
    #: Mapping of the 24 OCC emotion types into PAD space (Table 2).
    emotion_pad_map: Dict[EmotionType, PAD] = field(
        default_factory=lambda: dict(DEFAULT_EMOTION_PAD_MAP))

    # -- personality ----------------------------------------------------
    #: Big Five -> default PAD mood regression weights (Mehrabian).
    personality_to_mood: Mapping[str, Mapping[str, float]] = field(
        default_factory=lambda: {k: dict(v) for k, v in
                                 DEFAULT_PERSONALITY_TO_MOOD.items()})
    #: Big Five -> per-emotion baseline intensity weights.
    personality_baselines: Mapping[EmotionType, Mapping[str, float]] = field(
        default_factory=lambda: {k: dict(v) for k, v in
                                 DEFAULT_PERSONALITY_BASELINES.items()})
    #: If True, elicited intensities are biased (increased) by the
    #: personality baseline of the emotion, and decay back to it.
    apply_personality_bias: bool = True

    # -- mood dynamics --------------------------------------------------
    #: Seconds the pull/push function needs to move the mood from one
    #: octant centre to another, given a persistent emotion centre of
    #: full intensity ("usual mood change time", 10 min).
    mood_change_time: float = 600.0
    #: PAD distance the mood travels in ``mood_change_time``.  The paper
    #: says "from one mood octant centre to another one" without saying
    #: which pair: adjacent centres are 1.0 apart (default), centres
    #: across a face sqrt(2), opposite centres sqrt(3).
    mood_change_distance: float = 1.0
    #: Seconds the mood needs to travel the longest octant distance
    #: (sqrt(3)) back to the default mood (20 min).
    mood_return_time: float = 1200.0
    #: When the mood-return tendency applies (see MoodReturnMode).
    mood_return_mode: str = MoodReturnMode.IDLE
    #: If True, the virtual emotion centre position is the
    #: intensity-weighted average of the active emotions' PAD points;
    #: if False (default, per the paper) the plain average.
    vec_intensity_weighted: bool = False

    # -- engine ---------------------------------------------------------
    #: Default simulation step in seconds (``period="500"``).
    update_period: float = 0.5

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        """Coerce and validate all parameters; raises ``ValueError``.

        Called on construction; loaders call it again after assigning
        fields from external documents.
        """
        if isinstance(self.decay_function, str):
            self.decay_function = DecayFunction.from_name(self.decay_function)
        if self.emotion_decay_time <= 0:
            raise ValueError("emotion_decay_time must be > 0")
        if self.update_period <= 0:
            raise ValueError("update_period must be > 0")
        if self.mood_change_time <= 0 or self.mood_return_time <= 0:
            raise ValueError("mood times must be > 0")
        if self.mood_change_distance <= 0:
            raise ValueError("mood_change_distance must be > 0")
        if self.mood_return_mode not in (MoodReturnMode.IDLE,
                                         MoodReturnMode.ALWAYS):
            raise ValueError("mood_return_mode must be 'idle' or 'always'")
        if not 0.0 <= self.dominant_emotion_threshold <= 1.0:
            raise ValueError("dominant_emotion_threshold must be in [0, 1]")
        axes = set(self.personality_to_mood)
        if axes != {"pleasure", "arousal", "dominance"}:
            raise ValueError(f"personality_to_mood must map exactly the "
                             f"axes pleasure/arousal/dominance, got "
                             f"{sorted(axes)}")
        for axis, weights in self.personality_to_mood.items():
            unknown = set(weights) - set(TRAITS)
            if unknown:
                raise ValueError(f"unknown trait(s) in personality_to_mood"
                                 f"[{axis!r}]: {sorted(unknown)}")
        for emotion, weights in self.personality_baselines.items():
            unknown = set(weights) - set(TRAITS)
            if unknown:
                raise ValueError(f"unknown trait(s) in personality_baselines"
                                 f"[{emotion}]: {sorted(unknown)}")
