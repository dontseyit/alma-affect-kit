"""A character's subjective appraisal rules (paper, section 4): basic
event rules, act rules scoped self/direct/indirect, and emotion/mood
display rules scoped self/other.  Each rule's body is a list of EECs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .appraisal import EEC

__all__ = ["ActRule", "DisplayRule", "AppraisalRules"]

_ACT_SCOPES = ("self", "direct", "indirect")
_DISPLAY_SCOPES = ("self", "other")


def _as_list(appraisals) -> List[EEC]:
    if isinstance(appraisals, EEC):
        return [appraisals]
    return list(appraisals)


@dataclass
class ActRule:
    """Appraisal of a (dialog) act, e.g. tease, congratulate, attack."""

    act: str
    scope: str  # 'self' | 'direct' | 'indirect'
    appraisals: List[EEC]
    performer: Optional[str] = None  # only for acts of this character

    def __post_init__(self):
        if self.scope not in _ACT_SCOPES:
            raise ValueError(f"act rule scope must be one of {_ACT_SCOPES}")
        self.appraisals = _as_list(self.appraisals)

    def matches(self, act: str, performer: str, scope: str) -> bool:
        return (self.act == act and self.scope == scope
                and (self.performer is None or self.performer == performer))


@dataclass
class DisplayRule:
    """Appraisal of an emotion or mood display (a visible affect cue)."""

    display: str
    scope: str  # 'self' | 'other'
    appraisals: List[EEC]
    performer: Optional[str] = None

    def __post_init__(self):
        if self.scope not in _DISPLAY_SCOPES:
            raise ValueError(
                f"display rule scope must be one of {_DISPLAY_SCOPES}")
        self.appraisals = _as_list(self.appraisals)

    def matches(self, display: str, performer: str, scope: str) -> bool:
        return (self.display == display and self.scope == scope
                and (self.performer is None or self.performer == performer))


@dataclass
class AppraisalRules:
    """The rule book of one character."""

    #: event/object name -> list of basic appraisals
    basic: dict = field(default_factory=dict)
    acts: List[ActRule] = field(default_factory=list)
    emotion_displays: List[DisplayRule] = field(default_factory=list)
    mood_displays: List[DisplayRule] = field(default_factory=list)

    def __post_init__(self):
        self.basic = {name: _as_list(a) for name, a in self.basic.items()}

    # -- declarative construction helpers ------------------------------
    def on_event(self, name: str, *appraisals: EEC) -> "AppraisalRules":
        self.basic.setdefault(name, []).extend(appraisals)
        return self

    def on_act(self, act: str, scope: str, *appraisals: EEC,
               performer: str = None) -> "AppraisalRules":
        self.acts.append(ActRule(act, scope, list(appraisals), performer))
        return self

    def on_emotion_display(self, display: str, scope: str, *appraisals: EEC,
                           performer: str = None) -> "AppraisalRules":
        self.emotion_displays.append(
            DisplayRule(display, scope, list(appraisals), performer))
        return self

    def on_mood_display(self, display: str, scope: str, *appraisals: EEC,
                        performer: str = None) -> "AppraisalRules":
        self.mood_displays.append(
            DisplayRule(display, scope, list(appraisals), performer))
        return self

    @staticmethod
    def _match_displays(rules: List[DisplayRule], display: str,
                        performer: str, scope: str) -> List[EEC]:
        return [e.with_cause(e.cause or f"{performer}:{display}")
                for rule in rules
                if rule.matches(display, performer, scope)
                for e in rule.appraisals]

    # -- matching -------------------------------------------------------
    def match_event(self, name: str) -> List[EEC]:
        return [e.with_cause(e.cause or name)
                for e in self.basic.get(name, [])]

    def match_act(self, act: str, performer: str, scope: str) -> List[EEC]:
        out: List[EEC] = []
        for rule in self.acts:
            if rule.matches(act, performer, scope):
                out.extend(e.with_cause(e.cause or f"{performer}:{act}")
                           for e in rule.appraisals)
        return out

    def match_emotion_display(self, display: str, performer: str,
                              scope: str) -> List[EEC]:
        return self._match_displays(self.emotion_displays, display,
                                    performer, scope)

    def match_mood_display(self, display: str, performer: str,
                           scope: str) -> List[EEC]:
        return self._match_displays(self.mood_displays, display,
                                    performer, scope)
