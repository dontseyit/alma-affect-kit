"""Loading configurations and character profiles from YAML (default),
JSON or dicts.  Keys mirror the dataclass field names, times are in
seconds, and loading is strict (unknown keys, unsupported tag fields
and out-of-range values raise ``ValueError``).  Templates and the
AffectML -> YAML mapping: docs/examples.md, docs/configuration.md.
"""

from __future__ import annotations

import dataclasses
import json
import os
from typing import Dict, Tuple, Union

import yaml

from .appraisal import EEC, EEC_FIELD_NAMES, build_tag_eec
from .config import AffectConfig
from .emotion import EmotionType
from .pad import PAD
from .personality import Personality
from .rules import AppraisalRules

__all__ = ["load_config", "load_character", "config_from_dict",
           "character_from_dict", "eec_from_dict"]

#: AffectConfig fields settable as plain scalars from external documents.
_TABLE_FIELDS = ("emotion_pad_map", "personality_to_mood",
                 "personality_baselines")
_SCALAR_CONFIG_KEYS = tuple(
    f.name for f in dataclasses.fields(AffectConfig)
    if f.name not in _TABLE_FIELDS)

_FILE_EXTENSIONS = (".yaml", ".yml", ".json")


def eec_from_dict(data: Dict) -> EEC:
    """Build an EEC from ``{tag: <BasicTagName>, ...}`` or raw EEC fields.

    A field the tag does not support raises ``ValueError`` (unless it
    restates the tag's own value) instead of being silently dropped.
    """
    data = dict(data)
    tag = data.pop("tag", None)
    unknown = set(data) - set(EEC_FIELD_NAMES)
    if unknown:
        raise ValueError(f"unknown EEC field(s): {sorted(unknown)}")
    if tag is not None:
        return build_tag_eec(tag, data)
    return EEC(**data)


def _pad_from(value) -> PAD:
    if isinstance(value, dict):
        return PAD(value.get("p", value.get("pleasure", 0.0)),
                   value.get("a", value.get("arousal", 0.0)),
                   value.get("d", value.get("dominance", 0.0)))
    return PAD(*value)


def config_from_dict(data: Dict) -> AffectConfig:
    """Build an :class:`AffectConfig` from a dict (see module docstring).

    Absent keys keep the publication defaults; ``emotion_pad_map``,
    ``personality_to_mood`` and ``personality_baselines`` entries are
    merged over the defaults.
    """
    data = dict(data)
    config = AffectConfig()

    for key in _SCALAR_CONFIG_KEYS:
        if key in data:
            setattr(config, key, data.pop(key))

    for name, value in data.pop("emotion_pad_map", {}).items():
        config.emotion_pad_map[EmotionType.from_name(name)] = _pad_from(value)

    if "personality_to_mood" in data:
        mapping = {k: dict(v) for k, v in config.personality_to_mood.items()}
        for axis, weights in data.pop("personality_to_mood").items():
            if axis not in mapping:
                raise ValueError(f"unknown PAD axis: {axis!r}")
            mapping[axis] = dict(weights)
        config.personality_to_mood = mapping

    if "personality_baselines" in data:
        table = {k: dict(v) for k, v in config.personality_baselines.items()}
        for name, weights in data.pop("personality_baselines").items():
            table[EmotionType.from_name(name)] = dict(weights)
        config.personality_baselines = table

    if data:
        raise ValueError(f"unknown configuration key(s): {sorted(data)}")
    config.validate()  # re-validate after assignments
    return config


def character_from_dict(data: Dict
                        ) -> Tuple[str, Personality, AppraisalRules]:
    """Build ``(name, personality, rules)`` from a dict profile."""
    name = data.get("name", "character")
    personality = Personality(**data.get("personality", {}))

    rules = AppraisalRules()
    appraisal = data.get("appraisal", {})
    unknown = set(appraisal) - {"basic", "acts", "emotion_displays",
                                "mood_displays"}
    if unknown:
        raise ValueError(f"unknown appraisal rule class(es): "
                         f"{sorted(unknown)}")

    for event, entries in appraisal.get("basic", {}).items():
        rules.on_event(event, *[eec_from_dict(e) for e in entries])
    for entry in appraisal.get("acts", []):
        rules.on_act(entry["act"], entry["scope"],
                     *[eec_from_dict(e) for e in entry["appraisals"]],
                     performer=entry.get("performer"))
    for entry in appraisal.get("emotion_displays", []):
        rules.on_emotion_display(
            entry["display"], entry["scope"],
            *[eec_from_dict(e) for e in entry["appraisals"]],
            performer=entry.get("performer"))
    for entry in appraisal.get("mood_displays", []):
        rules.on_mood_display(
            entry["display"], entry["scope"],
            *[eec_from_dict(e) for e in entry["appraisals"]],
            performer=entry.get("performer"))

    return name, personality, rules


def _load_data(source: Union[Dict, str]) -> Dict:
    """Resolve a dict, file path or YAML/JSON document string to a dict."""
    if isinstance(source, dict):
        return source
    if not isinstance(source, str):
        raise TypeError("source must be a dict, a file path or a "
                        "YAML/JSON document string")

    text = source
    extension = os.path.splitext(source)[1].lower()
    if os.path.exists(source):
        with open(source, "r", encoding="utf-8") as fh:
            text = fh.read()
    elif extension in _FILE_EXTENSIONS and "\n" not in source:
        # clearly meant as a file path, not a document
        raise FileNotFoundError(f"no such file: {source!r}")

    # JSON files are parsed strictly; everything else is YAML (of which
    # JSON is a subset, so inline JSON strings work too).
    if extension == ".json":
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("document must be a mapping")
    return data


def load_config(source: Union[Dict, str]) -> AffectConfig:
    """Load an affect configuration from a dict, file path or document.

    YAML is the default format; JSON documents (``.json`` files or JSON
    strings) use the same structure.  Times are in seconds.
    """
    return config_from_dict(_load_data(source))


def load_character(source: Union[Dict, str]
                   ) -> Tuple[str, Personality, AppraisalRules]:
    """Load a character profile from a dict, file path or document.

    Returns ``(name, personality, rules)``, ready for
    :meth:`AffectEngine.add_character`.
    """
    return character_from_dict(_load_data(source))
