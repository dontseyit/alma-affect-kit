"""alma-affect-kit - ALMA, A Layered Model of Affect, as a Python engine."

A reimplementation of ALMA (Gebhard, AAMAS 2005) for games and
simulations: OCC emotions (short-term), PAD moods (medium-term) and Big
Five personality (long-term) with the publication's dynamics and
defaults.  See the docs (docs/index.md) for the model, usage and
examples.
"""

from .appraisal import (
    BASIC_TAGS, EEC, Prospect, compute_emotions, merge_eecs,
    good_event, bad_event,
    good_likely_future_event, bad_likely_future_event,
    good_unlikely_future_event, bad_unlikely_future_event,
    good_act_self, bad_act_self, good_act_other, bad_act_other,
    nice_thing, nasty_thing,
    prospect_confirmed, prospect_disconfirmed, event_for_other,
)
from .loaders import (character_from_dict, config_from_dict, eec_from_dict,
                      load_character, load_config)
from .character import CharacterAffect
from .config import AffectConfig, MoodReturnMode
from .emotion import (ActiveEmotion, DecayFunction,
                      DEFAULT_EMOTION_PAD_MAP, EmotionType, OCCGroup)
from .engine import AffectEngine
from .mood import (VirtualEmotionCenter, compute_emotion_center,
                   update_mood)
from .pad import PAD, MoodOctant, MoodStrength, SQRT3
from .personality import (DEFAULT_PERSONALITY_BASELINES,
                          DEFAULT_PERSONALITY_TO_MOOD, Personality,
                          default_mood, emotion_baseline)
from .rules import ActRule, AppraisalRules, DisplayRule

from ._version import __version__

__all__ = [
    "__version__",
    # engine
    "AffectEngine", "CharacterAffect", "AffectConfig", "MoodReturnMode",
    # personality
    "Personality", "default_mood", "emotion_baseline",
    "DEFAULT_PERSONALITY_TO_MOOD", "DEFAULT_PERSONALITY_BASELINES",
    # PAD / mood
    "PAD", "MoodOctant", "MoodStrength", "SQRT3",
    "VirtualEmotionCenter", "compute_emotion_center", "update_mood",
    # emotions
    "EmotionType", "OCCGroup", "ActiveEmotion", "DecayFunction",
    "DEFAULT_EMOTION_PAD_MAP",
    # appraisal
    "EEC", "Prospect", "compute_emotions", "merge_eecs", "BASIC_TAGS",
    "good_event", "bad_event",
    "good_likely_future_event", "bad_likely_future_event",
    "good_unlikely_future_event", "bad_unlikely_future_event",
    "good_act_self", "bad_act_self", "good_act_other", "bad_act_other",
    "nice_thing", "nasty_thing",
    "prospect_confirmed", "prospect_disconfirmed", "event_for_other",
    # rules & loading (YAML, JSON, dict)
    "AppraisalRules", "ActRule", "DisplayRule",
    "load_config", "load_character",
    "config_from_dict", "character_from_dict", "eec_from_dict",
]
