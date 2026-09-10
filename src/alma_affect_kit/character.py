"""A character's affective state: personality, active emotions and mood."""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Union

from .appraisal import EEC, compute_emotions, merge_eecs
from .config import AffectConfig
from .emotion import ActiveEmotion, EmotionType
from .mood import compute_emotion_center, update_mood, VirtualEmotionCenter
from .pad import PAD
from .personality import Personality, default_mood, emotion_baseline
from .rules import AppraisalRules

__all__ = ["CharacterAffect"]


class CharacterAffect:
    """The layered affective state of one character.

    * **Personality** (long-term): a Big Five profile, fixed.
    * **Mood** (medium-term): a point in PAD space, initialised to the
      personality's default mood and driven by the pull/push mood change
      function and the mood return tendency.
    * **Emotions** (short-term): active OCC emotions elicited by
      appraisals, decaying over time.
    """

    def __init__(self, name: str, personality: Personality = None,
                 rules: AppraisalRules = None,
                 config: AffectConfig = None,
                 initial_mood: PAD = None):
        self.name = name
        self.personality = personality or Personality()
        self.rules = rules or AppraisalRules()
        self.config = config or AffectConfig()
        self.default_mood: PAD = default_mood(
            self.personality, self.config.personality_to_mood)
        self.mood: PAD = initial_mood.clamped() if initial_mood is not None \
            else self.default_mood
        self.active_emotions: List[ActiveEmotion] = []
        self.emotion_center: Optional[VirtualEmotionCenter] = None
        # personality and the baseline table are fixed per character, so
        # the 24 baseline intensities are precomputed here once
        self._baselines = {
            emotion: emotion_baseline(self.personality, emotion,
                                      self.config.personality_baselines)
            for emotion in EmotionType}

    # ------------------------------------------------------------------
    # appraisal -> emotions
    # ------------------------------------------------------------------
    def baseline(self, emotion: EmotionType) -> float:
        """Personality-dependent baseline intensity of an emotion type."""
        if not self.config.apply_personality_bias:
            return 0.0
        return self._baselines[emotion]

    def appraise(self, appraisals: Union[EEC, Sequence[EEC]],
                 merge: bool = True) -> List[ActiveEmotion]:
        """Process one or more EECs and elicit active emotions.

        With ``merge=True`` (default) compatible EECs stemming from the
        same appraised situation are merged first so that OCC compound
        emotions (anger, remorse, gratitude, gratification) can arise.
        Returns the newly elicited active emotions.
        """
        if isinstance(appraisals, EEC):
            appraisals = [appraisals]
        eecs = merge_eecs(list(appraisals)) if merge else list(appraisals)
        elicited: List[ActiveEmotion] = []
        for eec in eecs:
            for emotion_type, intensity in compute_emotions(eec):
                total = min(1.0, intensity + self.baseline(emotion_type))
                if total <= 0.0:
                    continue
                elicited.append(self.elicit(emotion_type, total,
                                            cause=eec.cause))
        return elicited

    def elicit(self, emotion_type: EmotionType, intensity: float,
               cause: str = None) -> ActiveEmotion:
        """Directly elicit an emotion (bypassing appraisal)."""
        emotion = ActiveEmotion(
            type=emotion_type,
            initial_intensity=intensity,
            baseline=self.baseline(emotion_type),
            decay_time=self.config.emotion_decay_time,
            decay_function=self.config.decay_function,
            cause=cause,
            pad=self.config.emotion_pad_map.get(emotion_type),
        )
        self.active_emotions.append(emotion)
        return emotion

    # ------------------------------------------------------------------
    # simulation step
    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        """Advance the character's affective state by ``dt`` seconds."""
        if dt < 0:
            raise ValueError("dt must be >= 0")
        for emotion in self.active_emotions:
            emotion.tick(dt)
        self.active_emotions = [e for e in self.active_emotions
                                if not e.expired]
        self.emotion_center = compute_emotion_center(
            self.active_emotions, self.config)
        self.mood = update_mood(self.mood, self.default_mood,
                                self.emotion_center, dt, self.config)

    # ------------------------------------------------------------------
    # queries
    # ------------------------------------------------------------------
    def emotion_intensity(self, emotion_type: EmotionType) -> float:
        """Current intensity of an emotion type (its baseline if inactive)."""
        active = [e.intensity for e in self.active_emotions
                  if e.type is emotion_type]
        return max(active) if active else self.baseline(emotion_type)

    @property
    def dominant_emotion(self) -> Optional[ActiveEmotion]:
        """The most intense active emotion above the dominance threshold.

        Only the most dominant emotion whose intensity exceeds the
        configured threshold has an impact on behaviour (IVA'03).
        """
        if not self.active_emotions:
            return None
        best = max(self.active_emotions, key=lambda e: e.intensity)
        if best.intensity > self.config.dominant_emotion_threshold:
            return best
        return None

    @property
    def mood_word(self) -> str:
        """Discrete mood description, e.g. ``'slightly relaxed'``."""
        return self.mood.describe()

    def reset(self) -> None:
        """Drop all active emotions and reset the mood to the default."""
        self.active_emotions = []
        self.emotion_center = None
        self.mood = self.default_mood

    @staticmethod
    def _mood_snapshot(pad: PAD) -> Dict:
        return {
            "moodword": pad.octant.label,
            "intensity": pad.strength.value,
            "p": round(pad.pleasure, 4),
            "a": round(pad.arousal, 4),
            "d": round(pad.dominance, 4),
        }

    def affect_output(self) -> Dict:
        """A snapshot of the affective state (the paper's AffectOutput)."""
        dominant = self.dominant_emotion
        return {
            "name": self.name,
            "dominant_emotion": (
                {"name": dominant.type.label,
                 "value": round(dominant.intensity, 4)}
                if dominant else None),
            "mood": self._mood_snapshot(self.mood),
            "default_mood": self._mood_snapshot(self.default_mood),
            "personality": self.personality.as_dict(),
            "active_emotions": [
                {"name": e.type.label, "value": round(e.intensity, 4),
                 "cause": e.cause}
                for e in sorted(self.active_emotions,
                                key=lambda e: -e.intensity)],
        }

    def __repr__(self) -> str:
        return (f"CharacterAffect({self.name!r}, mood={self.mood_word!r}, "
                f"emotions={len(self.active_emotions)})")
