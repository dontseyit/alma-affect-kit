"""OCC appraisal: EECs -> elicited emotions with intensities."""

import pytest

from alma_affect_kit import (EEC, EmotionType, bad_act_other, bad_act_self, bad_event,
                    bad_likely_future_event, compute_emotions, event_for_other,
                    good_act_other, good_act_self, good_event,
                    good_likely_future_event, good_unlikely_future_event,
                    merge_eecs, nasty_thing, nice_thing, prospect_confirmed,
                    prospect_disconfirmed)


def emotions_of(eec):
    return dict(compute_emotions(eec))


class TestWellBeing:
    def test_good_event_elicits_joy(self):
        assert emotions_of(good_event(0.7)) == \
            {EmotionType.JOY: pytest.approx(0.7)}

    def test_bad_event_elicits_distress(self):
        assert emotions_of(bad_event(-0.5)) == \
            {EmotionType.DISTRESS: pytest.approx(0.5)}


class TestProspectBased:
    def test_likely_good_future_event_elicits_hope(self):
        result = emotions_of(good_likely_future_event(0.5, likelihood=0.75))
        assert result == {EmotionType.HOPE: pytest.approx((0.5 + 0.75) / 2)}

    def test_unlikely_good_future_event_weaker_hope(self):
        strong = emotions_of(good_likely_future_event())[EmotionType.HOPE]
        weak = emotions_of(good_unlikely_future_event())[EmotionType.HOPE]
        assert weak < strong

    def test_likely_bad_future_event_elicits_fear(self):
        assert EmotionType.FEAR in emotions_of(bad_likely_future_event(-0.8))

    def test_confirmed_hope_elicits_satisfaction(self):
        assert emotions_of(prospect_confirmed(0.6, realization=1.0)) == \
            {EmotionType.SATISFACTION: pytest.approx(0.8)}

    def test_confirmed_fear_elicits_fears_confirmed(self):
        assert EmotionType.FEARS_CONFIRMED in \
            emotions_of(prospect_confirmed(-0.6))

    def test_disconfirmed_fear_elicits_relief(self):
        assert EmotionType.RELIEF in emotions_of(prospect_disconfirmed(-0.6))

    def test_disconfirmed_hope_elicits_disappointment(self):
        assert EmotionType.DISAPPOINTMENT in \
            emotions_of(prospect_disconfirmed(0.6))


class TestFortunesOfOthers:
    def test_happy_for_liked_other(self):
        assert EmotionType.HAPPY_FOR in \
            emotions_of(event_for_other(0.6, liking=0.5))

    def test_resentment_for_disliked_other(self):
        assert EmotionType.RESENTMENT in \
            emotions_of(event_for_other(0.6, liking=-0.5))

    def test_pity_for_liked_other(self):
        assert EmotionType.PITY in \
            emotions_of(event_for_other(-0.6, liking=0.5))

    def test_gloating_over_disliked_other(self):
        assert EmotionType.GLOATING in \
            emotions_of(event_for_other(-0.6, liking=-0.5))


class TestAttribution:
    def test_own_praiseworthy_act_elicits_pride(self):
        assert emotions_of(good_act_self(0.5)) == \
            {EmotionType.PRIDE: pytest.approx(0.5)}

    def test_own_blameworthy_act_elicits_shame(self):
        assert EmotionType.SHAME in emotions_of(bad_act_self(-0.5))

    def test_others_praiseworthy_act_elicits_admiration(self):
        assert EmotionType.ADMIRATION in emotions_of(good_act_other(0.5))

    def test_others_blameworthy_act_elicits_reproach(self):
        assert EmotionType.REPROACH in emotions_of(bad_act_other(-0.3))


class TestCompounds:
    def test_attack_scenario_elicits_anger(self):
        """AAMAS'05 Fig. 4: an attack is appraised as BadEvent(-0.5) plus
        BadActOther(-0.3); merged this elicits distress, reproach and the
        compound anger."""
        merged = merge_eecs([bad_event(-0.5), bad_act_other(-0.3)])
        assert len(merged) == 1
        result = emotions_of(merged[0])
        assert result[EmotionType.DISTRESS] == pytest.approx(0.5)
        assert result[EmotionType.REPROACH] == pytest.approx(0.3)
        assert result[EmotionType.ANGER] == pytest.approx(0.4)

    def test_gratitude(self):
        result = emotions_of(EEC(desirability=0.6, praiseworthiness=0.4,
                                 agency="other"))
        assert result[EmotionType.GRATITUDE] == pytest.approx(0.5)

    def test_gratification(self):
        result = emotions_of(EEC(desirability=0.6, praiseworthiness=0.4,
                                 agency="self"))
        assert EmotionType.GRATIFICATION in result
        assert EmotionType.PRIDE in result and EmotionType.JOY in result

    def test_remorse(self):
        result = emotions_of(EEC(desirability=-0.6, praiseworthiness=-0.4,
                                 agency="self"))
        assert EmotionType.REMORSE in result

    def test_incompatible_eecs_stay_separate(self):
        merged = merge_eecs([good_act_self(0.5), bad_act_other(-0.3)])
        assert len(merged) == 2

    def test_different_causes_never_merge(self):
        """Two independent appraisals with coincidentally equal values
        are different situations (merging them dropped emotions)."""
        merged = merge_eecs([
            bad_event(-0.5, cause="lost wallet"),
            bad_likely_future_event(-0.5, cause="storm coming")])
        assert len(merged) == 2
        types = {t for eec in merged for t, _ in compute_emotions(eec)}
        assert {EmotionType.DISTRESS, EmotionType.FEAR} <= types

    def test_actual_and_prospective_events_never_merge(self):
        """Even with no causes set, an actual event and a prospective
        one are structurally different situations (joy vs hope)."""
        merged = merge_eecs([good_event(0.5),
                             good_likely_future_event(0.5)])
        assert len(merged) == 2
        merged = merge_eecs([good_event(0.5), prospect_confirmed(0.5)])
        assert len(merged) == 2

    def test_explicit_agency_disagreement_never_merges(self):
        """An explicitly self-caused event must not adopt another
        EEC's 'other' agency (which turned remorse into anger)."""
        merged = merge_eecs([
            EEC(desirability=-0.4, agency="self"),
            EEC(praiseworthiness=-0.5, agency="other")])
        assert len(merged) == 2

    def test_unspecified_agency_adopts_the_explicit_one(self):
        merged = merge_eecs([EEC(desirability=-0.5),
                             EEC(praiseworthiness=-0.3, agency="self")])
        assert len(merged) == 1
        assert merged[0].agency == "self"
        assert EmotionType.REMORSE in dict(compute_emotions(merged[0]))


class TestAttraction:
    def test_nice_thing_elicits_liking(self):
        assert emotions_of(nice_thing(0.5)) == \
            {EmotionType.LIKING: pytest.approx(0.5)}

    def test_nasty_thing_elicits_disliking(self):
        assert EmotionType.DISLIKING in emotions_of(nasty_thing(-0.5))

    def test_love(self):
        result = emotions_of(nice_thing(0.6, liking=0.8))
        assert result[EmotionType.LOVE] == pytest.approx(0.7)

    def test_hate(self):
        result = emotions_of(nasty_thing(-0.6, liking=-0.8))
        assert EmotionType.HATE in result


class TestValidation:
    def test_out_of_range_rejected(self):
        with pytest.raises(ValueError):
            EEC(desirability=1.5)
        with pytest.raises(ValueError):
            EEC(likelihood=-0.1)

    def test_bad_agency_rejected(self):
        with pytest.raises(ValueError):
            EEC(praiseworthiness=0.5, agency="them")

    def test_unspecified_agency_defaults_to_other(self):
        result = dict(compute_emotions(EEC(praiseworthiness=0.5)))
        assert EmotionType.ADMIRATION in result

    def test_neutral_eec_elicits_nothing(self):
        assert compute_emotions(EEC()) == []
