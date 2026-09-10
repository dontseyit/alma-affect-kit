"""The affect engine: holds the characters, dispatches perceived world
input through their rules, and advances their affect deterministically
in explicit time steps (``update(dt)``, or ``step()`` at the paper's
500 ms period).
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Union

from .appraisal import EEC
from .character import CharacterAffect
from .config import AffectConfig
from .emotion import ActiveEmotion
from .pad import PAD
from .personality import Personality
from .rules import AppraisalRules

__all__ = ["AffectEngine"]


class AffectEngine:
    """Manages the affect computation for a set of characters."""

    def __init__(self, config: AffectConfig = None):
        self.config = config or AffectConfig()
        self.characters: Dict[str, CharacterAffect] = {}
        self.time: float = 0.0

    # ------------------------------------------------------------------
    # character management
    # ------------------------------------------------------------------
    def add_character(self, name: str, personality: Personality = None,
                      rules: AppraisalRules = None,
                      initial_mood: PAD = None) -> CharacterAffect:
        if name in self.characters:
            raise ValueError(f"character {name!r} already exists")
        character = CharacterAffect(name, personality=personality,
                                    rules=rules, config=self.config,
                                    initial_mood=initial_mood)
        self.characters[name] = character
        return character

    def remove_character(self, name: str) -> None:
        del self.characters[name]

    def character(self, name: str) -> CharacterAffect:
        return self.characters[name]

    def __getitem__(self, name: str) -> CharacterAffect:
        return self.characters[name]

    def __iter__(self):
        return iter(self.characters.values())

    # ------------------------------------------------------------------
    # input: direct appraisal
    # ------------------------------------------------------------------
    def appraise(self, name: str,
                 appraisals: Union[EEC, Sequence[EEC]],
                 merge: bool = True) -> List[ActiveEmotion]:
        """Feed EECs directly to one character's emotion engine."""
        return self.characters[name].appraise(appraisals, merge=merge)

    # ------------------------------------------------------------------
    # input: world events dispatched through the appraisal rules
    # ------------------------------------------------------------------
    def _perceive(self, matcher, characters: Optional[Iterable[str]]
                  ) -> Dict[str, List[ActiveEmotion]]:
        """Appraise one input for every selected character.

        ``matcher(character)`` returns the character's matching EECs.
        Characters whose rules do not match are omitted from the result.
        """
        elicited: Dict[str, List[ActiveEmotion]] = {}
        for character in self._select(characters):
            eecs = matcher(character)
            if eecs:
                elicited[character.name] = character.appraise(eecs)
        return elicited

    def perceive_event(self, event: str,
                       characters: Iterable[str] = None
                       ) -> Dict[str, List[ActiveEmotion]]:
        """An event occurred; every (given) character appraises it with
        its own basic appraisal rules."""
        return self._perceive(
            lambda c: c.rules.match_event(event), characters)

    def perceive_act(self, act: str, performer: str,
                     addressee: str = None,
                     characters: Iterable[str] = None
                     ) -> Dict[str, List[ActiveEmotion]]:
        """A (dialog) act was performed.

        The performer appraises it with its ``self`` act rules, the
        addressee with its ``direct`` rules, and every other character
        with its ``indirect`` (listener) rules.
        """
        def act_scope(character) -> str:
            if character.name == performer:
                return "self"
            if addressee is not None and character.name == addressee:
                return "direct"
            return "indirect"

        return self._perceive(
            lambda c: c.rules.match_act(act, performer, act_scope(c)),
            characters)

    def _perceive_display(self, kind: str, display: str, performer: str,
                          characters: Optional[Iterable[str]]
                          ) -> Dict[str, List[ActiveEmotion]]:
        def matcher(character):
            scope = "self" if character.name == performer else "other"
            match = (character.rules.match_emotion_display
                     if kind == "emotion"
                     else character.rules.match_mood_display)
            return match(display, performer, scope)

        return self._perceive(matcher, characters)

    def perceive_emotion_display(self, display: str, performer: str,
                                 characters: Iterable[str] = None
                                 ) -> Dict[str, List[ActiveEmotion]]:
        """A character visibly displayed an emotion (e.g. a blush of
        shame); it appraises its own display (``self``), the others
        appraise it as observers (``other``)."""
        return self._perceive_display("emotion", display, performer,
                                      characters)

    def perceive_mood_display(self, display: str, performer: str,
                              characters: Iterable[str] = None
                              ) -> Dict[str, List[ActiveEmotion]]:
        """A character visibly displayed a mood (e.g. nervous idle
        behaviour over some amount of time)."""
        return self._perceive_display("mood", display, performer,
                                      characters)

    # ------------------------------------------------------------------
    # simulation
    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        """Advance all characters' affective states by ``dt`` seconds."""
        for character in self.characters.values():
            character.update(dt)
        self.time += dt

    def step(self, steps: int = 1) -> None:
        """Advance by ``steps`` update periods (default period: 500 ms)."""
        for _ in range(steps):
            self.update(self.config.update_period)

    def run(self, duration: float) -> None:
        """Simulate ``duration`` seconds in update-period steps."""
        period = self.config.update_period
        remaining = float(duration)
        while remaining > 1e-9:
            dt = min(period, remaining)
            self.update(dt)
            remaining -= dt

    # ------------------------------------------------------------------
    def affect_output(self) -> Dict[str, Dict]:
        """Snapshot of all characters (the paper's AffectOutput)."""
        return {name: c.affect_output()
                for name, c in self.characters.items()}

    def _select(self, names: Optional[Iterable[str]]
                ) -> List[CharacterAffect]:
        if names is None:
            return list(self.characters.values())
        return [self.characters[n] for n in names]
