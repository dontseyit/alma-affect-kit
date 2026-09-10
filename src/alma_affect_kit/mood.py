"""Mood dynamics (paper, section 3): the virtual emotion centre of the
active emotions, the pull/push mood change function it drives, and the
return of the mood to the default mood.  Speeds are calibrated by
``mood_change_time`` / ``mood_change_distance`` and ``mood_return_time``
(sqrt(3)); see docs/the-model.md and docs/fidelity.md.
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Tuple

from .config import AffectConfig, MoodReturnMode
from .emotion import ActiveEmotion
from .pad import PAD, SQRT3

__all__ = ["VirtualEmotionCenter", "compute_emotion_center", "update_mood"]


class VirtualEmotionCenter:
    """The virtual emotion centre of all active emotions."""

    __slots__ = ("position", "intensity")

    def __init__(self, position: PAD, intensity: float):
        self.position = position
        self.intensity = max(0.0, min(1.0, intensity))

    def __repr__(self) -> str:
        return f"VirtualEmotionCenter({self.position!r}, intensity={self.intensity:.2f})"


def compute_emotion_center(emotions: Iterable[ActiveEmotion],
                           config: AffectConfig
                           ) -> Optional[VirtualEmotionCenter]:
    """Compute the VEC of the active emotions, or None if there are none."""
    points: List[Tuple[PAD, float]] = []
    for emotion in emotions:
        intensity = emotion.intensity
        if intensity <= 0.0:
            continue
        pad = emotion.pad or config.emotion_pad_map.get(emotion.type)
        if pad is None:
            continue
        points.append((pad, intensity))
    if not points:
        return None

    if config.vec_intensity_weighted:
        total = sum(i for _, i in points)
        pos = PAD(sum(p.pleasure * i for p, i in points) / total,
                  sum(p.arousal * i for p, i in points) / total,
                  sum(p.dominance * i for p, i in points) / total)
    else:
        n = len(points)
        pos = PAD(sum(p.pleasure for p, _ in points) / n,
                  sum(p.arousal for p, _ in points) / n,
                  sum(p.dominance for p, _ in points) / n)
    intensity = sum(i for _, i in points) / len(points)
    return VirtualEmotionCenter(pos, intensity)


def _pull_push(mood: PAD, vec: VirtualEmotionCenter, dt: float,
               config: AffectConfig) -> PAD:
    """One pull/push step of length ``dt`` seconds."""
    # full-intensity speed moves mood_change_distance (default: the 1.0
    # between adjacent octant centres) in mood_change_time.
    step = (config.mood_change_distance / config.mood_change_time) \
        * vec.intensity * dt
    if step <= 0.0:
        return mood

    center_norm = vec.position.norm()
    if center_norm == 0.0:
        # VEC at the PAD origin: plain attraction towards it
        return mood.moved_towards(vec.position, step)
    center_dir = vec.position.scaled(1.0 / center_norm)

    # mood is "between the zero point and the VEC" if its projection on
    # the origin->VEC ray has not yet reached the VEC.
    projection = mood.dot(center_dir)
    if projection + 1e-9 < center_norm:
        # pull phase: attract the mood towards the VEC
        return mood.moved_towards(vec.position, step)

    # push phase: push the mood further into its current octant
    direction = mood.normalized()
    if direction.norm() == 0.0:
        direction = center_dir
    return mood + direction.scaled(step)  # clamped by update_mood


def _return_towards_default(mood: PAD, default: PAD, dt: float,
                            config: AffectConfig) -> PAD:
    step = (SQRT3 / config.mood_return_time) * dt
    return mood.moved_towards(default, step)


def update_mood(mood: PAD, default_mood: PAD,
                vec: Optional[VirtualEmotionCenter], dt: float,
                config: AffectConfig) -> PAD:
    """Advance the mood by ``dt`` seconds.

    With a VEC present the pull/push function applies; the return
    tendency applies while idle (default) or always, depending on
    ``config.mood_return_mode``.
    """
    if vec is not None:
        mood = _pull_push(mood, vec, dt, config)
        if config.mood_return_mode == MoodReturnMode.ALWAYS:
            mood = _return_towards_default(mood, default_mood, dt, config)
    else:
        mood = _return_towards_default(mood, default_mood, dt, config)
    return mood.clamped()
