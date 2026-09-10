"""Appraisal: emotion eliciting conditions (EECs), the OCC rules that
turn them into emotions, EEC merging for compound emotions, and the
basic appraisal tag constructors (IVA'03, Table 1).

Variable signs select the emotion type, absolute values set the
intensity; see docs/appraisal.md for the full elicitation reference.
"""

from __future__ import annotations

import dataclasses
import inspect
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Tuple

from .emotion import EmotionType

__all__ = [
    "EEC",
    "EEC_FIELD_NAMES",
    "Prospect",
    "compute_emotions",
    "merge_eecs",
    "build_tag_eec",
    # basic appraisal tag constructors
    "good_event", "bad_event",
    "good_likely_future_event", "bad_likely_future_event",
    "good_unlikely_future_event", "bad_unlikely_future_event",
    "good_act_self", "bad_act_self", "good_act_other", "bad_act_other",
    "nice_thing", "nasty_thing",
    "prospect_confirmed", "prospect_disconfirmed",
    "event_for_other",
    "BASIC_TAGS",
]


class Prospect:
    """Status of an anticipated event, for the confirmation emotions."""

    CONFIRMED = "confirmed"
    DISCONFIRMED = "disconfirmed"


def _check(name: str, value: Optional[float], lo: float = -1.0) -> None:
    if value is not None and not (lo <= value <= 1.0):
        raise ValueError(f"EEC variable {name} must be in [{lo}, 1.0], "
                         f"got {value}")


@dataclass(frozen=True)
class EEC:
    """One emotion eliciting condition (the result of one appraisal).

    ``agency`` is ``'self'``, ``'other'`` or ``None`` (unspecified, which
    the OCC rules treat as ``'other'``).
    """

    desirability: Optional[float] = None
    desirability_for_other: Optional[float] = None
    praiseworthiness: Optional[float] = None
    agency: Optional[str] = None  # None | 'self' | 'other'
    appealingness: Optional[float] = None
    liking: Optional[float] = None
    likelihood: Optional[float] = None
    realization: Optional[float] = None
    prospect: Optional[str] = None  # None | Prospect.CONFIRMED | DISCONFIRMED
    cause: Optional[str] = None

    def __post_init__(self):
        _check("desirability", self.desirability)
        _check("desirability_for_other", self.desirability_for_other)
        _check("praiseworthiness", self.praiseworthiness)
        _check("appealingness", self.appealingness)
        _check("liking", self.liking)
        _check("likelihood", self.likelihood, lo=0.0)
        _check("realization", self.realization, lo=0.0)
        if self.agency not in (None, "self", "other"):
            raise ValueError("agency must be None, 'self' or 'other'")
        if self.prospect not in (None, Prospect.CONFIRMED,
                                 Prospect.DISCONFIRMED):
            raise ValueError("prospect must be None, 'confirmed' or "
                             "'disconfirmed'")

    def with_cause(self, cause: str) -> "EEC":
        """A copy of this EEC with ``cause`` set."""
        return replace(self, cause=cause)


#: All EEC field names (single source of truth for the loaders).
EEC_FIELD_NAMES: Tuple[str, ...] = tuple(
    f.name for f in dataclasses.fields(EEC))

#: The numeric appraisal variables (mergeable value fields).
_VALUE_FIELDS: Tuple[str, ...] = tuple(
    name for name in EEC_FIELD_NAMES
    if name not in ("agency", "prospect", "cause"))


def _mean(*values: float) -> float:
    return sum(abs(v) for v in values) / len(values)


def compute_emotions(eec: EEC) -> List[Tuple[EmotionType, float]]:
    """Map one EEC onto elicited emotions with intensities (OCC rules).

    The signs of the EEC variables select the emotion types; intensities
    are the mean of the absolute values of the participating variables
    (before the personality baseline bias applied by the engine).
    """
    out: List[Tuple[EmotionType, float]] = []
    d = eec.desirability
    p = eec.praiseworthiness
    agency = eec.agency or "other"

    # --- events: well-being / prospect-based --------------------------
    if d is not None and d != 0.0:
        if eec.prospect is not None:
            r = eec.realization if eec.realization is not None else 1.0
            if eec.prospect == Prospect.CONFIRMED:
                out.append((EmotionType.SATISFACTION if d > 0
                            else EmotionType.FEARS_CONFIRMED, _mean(d, r)))
            else:
                out.append((EmotionType.DISAPPOINTMENT if d > 0
                            else EmotionType.RELIEF, _mean(d, r)))
        elif eec.likelihood is not None:
            out.append((EmotionType.HOPE if d > 0 else EmotionType.FEAR,
                        _mean(d, eec.likelihood)))
        else:
            out.append((EmotionType.JOY if d > 0 else EmotionType.DISTRESS,
                        abs(d)))

    # --- events happening to others: fortunes-of-others ---------------
    do = eec.desirability_for_other
    if do is not None and do != 0.0:
        liking = eec.liking if eec.liking is not None else 0.5
        if do > 0:
            emo = EmotionType.HAPPY_FOR if liking >= 0 else EmotionType.RESENTMENT
        else:
            emo = EmotionType.PITY if liking >= 0 else EmotionType.GLOATING
        out.append((emo, _mean(do, liking)))

    # --- actions: attribution ------------------------------------------
    if p is not None and p != 0.0:
        if p > 0:
            emo = (EmotionType.PRIDE if agency == "self"
                   else EmotionType.ADMIRATION)
        else:
            emo = (EmotionType.SHAME if agency == "self"
                   else EmotionType.REPROACH)
        out.append((emo, abs(p)))

    # --- well-being/attribution compounds ------------------------------
    if (d is not None and p is not None and eec.prospect is None
            and eec.likelihood is None):
        if d > 0 and p > 0:
            emo = (EmotionType.GRATIFICATION if agency == "self"
                   else EmotionType.GRATITUDE)
            out.append((emo, _mean(d, p)))
        elif d < 0 and p < 0:
            emo = (EmotionType.REMORSE if agency == "self"
                   else EmotionType.ANGER)
            out.append((emo, _mean(d, p)))

    # --- objects: attraction --------------------------------------------
    a = eec.appealingness
    if a is not None and a != 0.0:
        out.append((EmotionType.LIKING if a > 0 else EmotionType.DISLIKING,
                    abs(a)))
        if eec.liking is not None:
            if a > 0 and eec.liking > 0:
                out.append((EmotionType.LOVE, _mean(a, eec.liking)))
            elif a < 0 and eec.liking < 0:
                out.append((EmotionType.HATE, _mean(a, eec.liking)))

    return out


def _mergeable(a: EEC, b: EEC) -> bool:
    """Whether two EECs describe the same appraised situation."""
    # a value set on both sides with different values is a conflict
    for f in _VALUE_FIELDS:
        va, vb = getattr(a, f), getattr(b, f)
        if va is not None and vb is not None and va != vb:
            return False
    # explicitly different agencies are a conflict
    if a.agency is not None and b.agency is not None and a.agency != b.agency:
        return False
    # different causes are different situations
    if a.cause is not None and b.cause is not None and a.cause != b.cause:
        return False
    # an actual event and a prospective/confirmed one are structurally
    # different situations even when their desirabilities coincide,
    # merging them would change the elicited emotion type (joy vs hope)
    if (a.likelihood is None) != (b.likelihood is None):
        return False
    if a.prospect != b.prospect:
        return False
    return True


def merge_eecs(eecs: List[EEC]) -> List[EEC]:
    """Merge compatible EECs describing the same appraised situation.

    An appraisal rule may emit several basic appraisals for one input
    (e.g. an attack is a *bad event* and a *blameworthy act of another*,
    AAMAS'05 Fig. 4).  OCC treats these as one situation appraised along
    several dimensions, which is what enables the compound emotions
    (anger, remorse, gratitude, gratification).  Two EECs merge only when
    they are compatible: no variable set on both sides with different
    values, no explicit agency disagreement, equal (or absent) causes,
    and the same event structure (actual vs prospective vs confirmed).
    Incompatible EECs stay separate.
    """
    merged: List[EEC] = []
    for eec in eecs:
        for i, m in enumerate(merged):
            if _mergeable(m, eec):
                values = {f: (getattr(m, f) if getattr(m, f) is not None
                              else getattr(eec, f)) for f in _VALUE_FIELDS}
                merged[i] = EEC(agency=m.agency or eec.agency,
                                prospect=m.prospect,
                                cause=m.cause or eec.cause, **values)
                break
        else:
            merged.append(eec)
    return merged


# ---------------------------------------------------------------------------
# Basic appraisal tags (IVA'03, Table 1) with the papers' default degrees:
# "moderately" (0.5) for good/bad, 0.75 / 0.25 for likely / unlikely.
# ---------------------------------------------------------------------------

def good_event(desirability: float = 0.5, cause: str = None) -> EEC:
    return EEC(desirability=abs(desirability), cause=cause)


def bad_event(desirability: float = -0.5, cause: str = None) -> EEC:
    return EEC(desirability=-abs(desirability), cause=cause)


def good_likely_future_event(desirability: float = 0.5,
                             likelihood: float = 0.75,
                             cause: str = None) -> EEC:
    return EEC(desirability=abs(desirability), likelihood=likelihood,
               cause=cause)


def bad_likely_future_event(desirability: float = -0.5,
                            likelihood: float = 0.75,
                            cause: str = None) -> EEC:
    return EEC(desirability=-abs(desirability), likelihood=likelihood,
               cause=cause)


def good_unlikely_future_event(desirability: float = 0.5,
                               likelihood: float = 0.25,
                               cause: str = None) -> EEC:
    return EEC(desirability=abs(desirability), likelihood=likelihood,
               cause=cause)


def bad_unlikely_future_event(desirability: float = -0.5,
                              likelihood: float = 0.25,
                              cause: str = None) -> EEC:
    return EEC(desirability=-abs(desirability), likelihood=likelihood,
               cause=cause)


def good_act_self(praiseworthiness: float = 0.5, cause: str = None) -> EEC:
    return EEC(praiseworthiness=abs(praiseworthiness), agency="self",
               cause=cause)


def bad_act_self(praiseworthiness: float = -0.5, cause: str = None) -> EEC:
    return EEC(praiseworthiness=-abs(praiseworthiness), agency="self",
               cause=cause)


def good_act_other(praiseworthiness: float = 0.5, cause: str = None) -> EEC:
    return EEC(praiseworthiness=abs(praiseworthiness), agency="other",
               cause=cause)


def bad_act_other(praiseworthiness: float = -0.5, cause: str = None) -> EEC:
    return EEC(praiseworthiness=-abs(praiseworthiness), agency="other",
               cause=cause)


def nice_thing(appealingness: float = 0.5, liking: float = None,
               cause: str = None) -> EEC:
    return EEC(appealingness=abs(appealingness), liking=liking, cause=cause)


def nasty_thing(appealingness: float = -0.5, liking: float = None,
                cause: str = None) -> EEC:
    return EEC(appealingness=-abs(appealingness), liking=liking, cause=cause)


def prospect_confirmed(desirability: float, realization: float = 1.0,
                       cause: str = None) -> EEC:
    """A hoped-for (d > 0) or feared (d < 0) event occurred."""
    return EEC(desirability=desirability, realization=realization,
               prospect=Prospect.CONFIRMED, cause=cause)


def prospect_disconfirmed(desirability: float, realization: float = 1.0,
                          cause: str = None) -> EEC:
    """A hoped-for (d > 0) or feared (d < 0) event did not occur."""
    return EEC(desirability=desirability, realization=realization,
               prospect=Prospect.DISCONFIRMED, cause=cause)


def event_for_other(desirability_for_other: float, liking: float = 0.5,
                    cause: str = None) -> EEC:
    """An event of concern to another character (fortunes-of-others)."""
    return EEC(desirability_for_other=desirability_for_other, liking=liking,
               cause=cause)


#: Basic appraisal tag names -> constructors (for declarative rule files).
BASIC_TAGS = {
    "GoodEvent": good_event,
    "BadEvent": bad_event,
    "GoodLikelyFutureEvent": good_likely_future_event,
    "BadLikelyFutureEvent": bad_likely_future_event,
    "GoodUnlikelyFutureEvent": good_unlikely_future_event,
    "BadUnlikelyFutureEvent": bad_unlikely_future_event,
    "GoodActSelf": good_act_self,
    "BadActSelf": bad_act_self,
    "GoodActOther": good_act_other,
    "BadActOther": bad_act_other,
    "NiceThing": nice_thing,
    "NastyThing": nasty_thing,
}

#: Parameter names accepted by each basic tag constructor (precomputed).
_TAG_PARAMS: Dict[str, frozenset] = {
    name: frozenset(inspect.signature(constructor).parameters)
    for name, constructor in BASIC_TAGS.items()}


def build_tag_eec(tag: str, values: Dict[str, object]) -> EEC:
    """Build an EEC from a basic appraisal tag name and EEC field values.

    Used by the YAML/JSON/dict loaders.  A field the tag's
    constructor does not accept is an error unless the constructed EEC
    already carries exactly that value (e.g. a redundant
    ``agency="self"`` on ``GoodActSelf``), a mismatch would otherwise be
    silently dropped, eliciting the wrong emotion.
    """
    if tag not in BASIC_TAGS:
        raise ValueError(f"unknown basic appraisal tag: {tag!r}")
    unknown = set(values) - set(EEC_FIELD_NAMES)
    if unknown:
        raise ValueError(f"unknown EEC field(s): {sorted(unknown)}")
    params = _TAG_PARAMS[tag]
    eec = BASIC_TAGS[tag](**{k: v for k, v in values.items() if k in params})
    for name, value in values.items():
        if name not in params and getattr(eec, name) != value:
            raise ValueError(
                f"field {name!r}={value!r} is not supported by tag {tag!r} "
                f"(use a different tag or a raw EEC)")
    return eec
