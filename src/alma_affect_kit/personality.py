"""Big Five personality and its two mappings: the default mood
(Mehrabian's Big Five -> PAD regression, paper section 3) and the
per-emotion baseline intensities.

The baseline weight table is this library's documented interpolation
of the papers' qualitative guidance, anchored at the one published
value (extravert joy baseline 0.15), see docs/fidelity.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping

from .emotion import EmotionType, OCCGroup
from .pad import PAD

__all__ = [
    "Personality",
    "TRAITS",
    "DEFAULT_PERSONALITY_TO_MOOD",
    "DEFAULT_PERSONALITY_BASELINES",
    "default_mood",
    "emotion_baseline",
]

#: Trait keys used in mapping tables.
TRAITS = ("openness", "conscientiousness", "extraversion", "agreeableness",
          "neuroticism")


def _clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


@dataclass(frozen=True)
class Personality:
    """Big Five personality profile; each trait in [-1, 1]."""

    openness: float = 0.0
    conscientiousness: float = 0.0
    extraversion: float = 0.0
    agreeableness: float = 0.0
    neuroticism: float = 0.0

    def __post_init__(self):
        for t in TRAITS:
            object.__setattr__(self, t, _clamp(getattr(self, t)))

    def as_dict(self) -> Dict[str, float]:
        return {t: getattr(self, t) for t in TRAITS}

    def __repr__(self) -> str:
        return ("Personality(" +
                ", ".join(f"{t[:5]}={getattr(self, t):+.2f}" for t in TRAITS) +
                ")")


#: Mehrabian's Big Five -> PAD regression (publication defaults).
DEFAULT_PERSONALITY_TO_MOOD: Dict[str, Dict[str, float]] = {
    "pleasure": {"extraversion": 0.21, "agreeableness": 0.59,
                 "neuroticism": 0.19},
    "arousal": {"openness": 0.15, "agreeableness": 0.30,
                "neuroticism": -0.57},
    "dominance": {"openness": 0.25, "conscientiousness": 0.17,
                  "extraversion": 0.60, "agreeableness": -0.32},
}


def default_mood(personality: Personality,
                 weights: Mapping[str, Mapping[str, float]] = None) -> PAD:
    """Compute a character's default mood from its Big Five profile.

    The result is clamped into the PAD cube (extreme trait combinations
    can push a regression axis slightly beyond 1.0).
    """
    if weights is None:
        weights = DEFAULT_PERSONALITY_TO_MOOD
    traits = personality.as_dict()

    def axis(name: str) -> float:
        return sum(w * traits[t] for t, w in weights[name].items())

    return PAD(axis("pleasure"), axis("arousal"),
               axis("dominance")).clamped()


def _positive_weights() -> Dict[str, float]:
    return {"extraversion": 0.15, "agreeableness": 0.10}


def _negative_weights() -> Dict[str, float]:
    return {"neuroticism": 0.15}


def _build_default_baselines() -> Dict[EmotionType, Dict[str, float]]:
    table: Dict[EmotionType, Dict[str, float]] = {}
    for emotion in EmotionType:
        if emotion.valence > 0:
            weights = _positive_weights()
        else:
            weights = _negative_weights()
        # attribution & attraction groups: additionally influenced by
        # conscientiousness resp. openness (ADS'04, section 3.1)
        if emotion.group in (OCCGroup.ATTRIBUTION,
                             OCCGroup.WELL_BEING_ATTRIBUTION):
            weights = dict(weights, conscientiousness=0.05)
        elif emotion.group is OCCGroup.ATTRACTION:
            weights = dict(weights, openness=0.05)
        table[emotion] = weights
    return table


#: Default personality -> emotion-baseline weight table.  For each emotion
#: the baseline intensity is ``clamp01(sum(weight * trait))``.
DEFAULT_PERSONALITY_BASELINES: Dict[EmotionType, Dict[str, float]] = \
    _build_default_baselines()


def emotion_baseline(personality: Personality, emotion: EmotionType,
                     table: Mapping[EmotionType, Mapping[str, float]] = None
                     ) -> float:
    """Baseline intensity of ``emotion`` for the given personality."""
    table = table if table is not None else DEFAULT_PERSONALITY_BASELINES
    weights = table.get(emotion, {})
    traits = personality.as_dict()
    value = sum(w * traits[t] for t, w in weights.items())
    return max(0.0, min(1.0, value))
