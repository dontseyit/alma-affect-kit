"""Loaders: YAML / JSON / dict profiles, strictness, and parity with the
paper's AffectML documents (Figs. 3 and 4 of AAMAS'05)."""

import json
from pathlib import Path

import pytest
import yaml

from alma_affect_kit import (AffectEngine, DecayFunction, EmotionType,
                         character_from_dict, config_from_dict,
                         eec_from_dict, load_character, load_config)

EXAMPLES = Path(__file__).parent.parent / "examples"

CONFIG = {
    "emotion_decay_time": 30.0,
    "decay_function": "exponential",
    "dominant_emotion_threshold": 0.3,
    "mood_change_time": 300.0,
    "emotion_pad_map": {"Anger": [-0.6, 0.7, 0.3]},
    "personality_to_mood": {
        "pleasure": {"extraversion": 0.5, "agreeableness": 0.5}},
    "personality_baselines": {"Joy": {"extraversion": 0.2}},
}

VALERIE = {
    "name": "Valerie",
    "personality": {"openness": 0.4, "conscientiousness": 0.8,
                    "extraversion": 0.6, "agreeableness": 0.3,
                    "neuroticism": 0.4},
    "appraisal": {
        "basic": {"SunIsShining": [{"tag": "GoodEvent",
                                    "desirability": 0.7}]},
        "acts": [{"act": "Attack", "scope": "direct", "performer": "Sven",
                  "appraisals": [
                      {"tag": "BadEvent", "desirability": -0.5},
                      {"tag": "BadActOther", "praiseworthiness": -0.3}]}],
        "emotion_displays": [{"display": "ReproachDisplay", "scope": "self",
                              "appraisals": [{"tag": "BadEvent",
                                              "desirability": -0.3}]}],
    },
}

#: The paper's Fig. 3 AffectComputation document, expressed in YAML
#: (AffectML milliseconds -> seconds).
PAPER_FIG3_YAML = """
emotion_decay_time: 20.0          # <EmotionDecay time="20000" .../>
update_period: 0.5                # ... period="500"
decay_function: linear            # ... function="linear"
dominant_emotion_threshold: 0.4   # <EmotionBaseline threshold="0.4"/>
mood_return_time: 600.0           # <MoodReturn time="600000"/>
emotion_pad_map:                  # <MoodRelations>
  Admiration: [0.5, 0.3, -0.2]
  Anger: [-0.51, 0.59, 0.25]
personality_to_mood:              # <PersonalityRelations>
  pleasure: {extraversion: 0.21, agreeableness: 0.59, neuroticism: 0.19}
  arousal: {openness: 0.15, agreeableness: 0.30, neuroticism: -0.57}
  dominance: {openness: 0.25, conscientiousness: 0.17, extraversion: 0.60,
              agreeableness: -0.32, neuroticism: 0.0}
"""

#: The paper's Fig. 4 CharacterAffect document, expressed in YAML.
PAPER_FIG4_YAML = """
name: Valerie                                     # <CharacterAffect name=...>
personality:                                      # <Personality open=.../>
  openness: 0.4
  conscientiousness: 0.8
  extraversion: 0.6
  agreeableness: 0.3
  neuroticism: 0.4
appraisal:
  basic:                                          # <Basic>
    GoodEvent:                                    #   <GoodEvent desirability="0.7"/>
      - {tag: GoodEvent, desirability: 0.7}       #   (input = tag name, paper form)
  acts:
    - act: Calm                                   # <SelfAct type="Calm">
      scope: self
      appraisals:
        - {tag: GoodActSelf, agency: self, praiseworthiness: 0.5}
    - act: Attack                                 # <DirectAct type="Attack"
      scope: direct                               #            performer="Sven">
      performer: Sven
      appraisals:
        - {tag: BadEvent, desirability: -0.5}
        - {tag: BadActOther, agency: other, praiseworthiness: -0.3}
  emotion_displays:
    - display: ReproachDisplay                    # <SelfEmotion emotion=...>
      scope: self
      appraisals:
        - {tag: BadEvent, desirability: -0.3}
"""


class TestEECFromDict:
    def test_tag_entry(self):
        eec = eec_from_dict({"tag": "GoodEvent", "desirability": 0.7})
        assert eec.desirability == 0.7

    def test_tag_defaults(self):
        assert eec_from_dict({"tag": "BadEvent"}).desirability == -0.5

    def test_raw_eec(self):
        eec = eec_from_dict({"desirability": -0.5,
                             "praiseworthiness": -0.3, "agency": "other"})
        assert eec.praiseworthiness == -0.3

    def test_unknown_tag_rejected(self):
        with pytest.raises(ValueError):
            eec_from_dict({"tag": "WeirdEvent"})

    def test_unknown_field_rejected(self):
        with pytest.raises(ValueError):
            eec_from_dict({"desirable": 0.7})


class TestConfigFromDict:
    def test_fields_and_defaults(self):
        config = config_from_dict(CONFIG)
        assert config.emotion_decay_time == 30.0
        assert config.decay_function is DecayFunction.EXPONENTIAL
        assert config.mood_change_time == 300.0
        assert config.mood_return_time == 1200.0  # untouched default

    def test_pad_map_merged_over_table2(self):
        config = config_from_dict(CONFIG)
        assert config.emotion_pad_map[EmotionType.ANGER].as_tuple() == \
            pytest.approx((-0.6, 0.7, 0.3))
        assert config.emotion_pad_map[EmotionType.JOY].as_tuple() == \
            pytest.approx((0.4, 0.2, 0.1))  # default preserved

    def test_personality_maps(self):
        config = config_from_dict(CONFIG)
        assert config.personality_to_mood["pleasure"] == \
            {"extraversion": 0.5, "agreeableness": 0.5}
        assert config.personality_baselines[EmotionType.JOY] == \
            {"extraversion": 0.2}

    def test_unknown_key_rejected(self):
        with pytest.raises(ValueError):
            config_from_dict({"emotion_decay": 30.0})

    def test_invalid_value_rejected(self):
        with pytest.raises(ValueError):
            config_from_dict({"mood_return_mode": "sometimes"})


class TestCharacterFromDict:
    def test_profile(self):
        name, personality, rules = character_from_dict(VALERIE)
        assert name == "Valerie"
        assert personality.conscientiousness == 0.8
        assert rules.match_event("SunIsShining")[0].desirability == 0.7
        assert len(rules.match_act("Attack", "Sven", "direct")) == 2
        assert rules.match_act("Attack", "Ghost", "direct") == []
        assert rules.match_emotion_display(
            "ReproachDisplay", "Valerie", "self")[0].desirability == -0.3

    def test_unknown_rule_class_rejected(self):
        with pytest.raises(ValueError):
            character_from_dict({"appraisal": {"telepathy": []}})

    def test_runs_in_engine(self):
        engine = AffectEngine(load_config(CONFIG))
        engine.add_character(*load_character(VALERIE))
        engine.add_character("Sven")
        elicited = engine.perceive_act("Attack", performer="Sven",
                                       addressee="Valerie")
        assert {e.type for e in elicited["Valerie"]} >= \
            {EmotionType.DISTRESS, EmotionType.REPROACH, EmotionType.ANGER}


class TestFormats:
    def test_yaml_string(self):
        config = load_config(yaml.safe_dump(CONFIG))
        assert config.decay_function is DecayFunction.EXPONENTIAL

    def test_json_string_is_valid_yaml(self):
        config = load_config(json.dumps(CONFIG))
        assert config.emotion_decay_time == 30.0

    def test_yaml_flow_mapping(self):
        config = load_config("{emotion_decay_time: 5, "
                             "decay_function: linear}")
        assert config.emotion_decay_time == 5

    @pytest.mark.parametrize("suffix,dump", [
        ("json", json.dumps),
        ("yaml", lambda d: yaml.safe_dump(d)),
        ("yml", lambda d: yaml.safe_dump(d)),
    ])
    def test_file_loading(self, tmp_path, suffix, dump):
        path = tmp_path / f"valerie.{suffix}"
        path.write_text(dump(VALERIE))
        name, personality, rules = load_character(str(path))
        assert name == "Valerie"
        assert rules.match_event("SunIsShining")

    def test_example_files_load(self):
        load_config(str(EXAMPLES / "affect.yaml"))
        for stem in ("valerie", "sven"):
            name, _, rules = load_character(str(EXAMPLES / f"{stem}.yaml"))
            assert name.lower() == stem
        _, _, valerie = load_character(str(EXAMPLES / "valerie.yaml"))
        assert valerie.match_event("SunIsShining")

    def test_example_config_is_the_publication_default(self):
        from alma_affect_kit import AffectConfig
        loaded = load_config(str(EXAMPLES / "affect.yaml"))
        default = AffectConfig()
        for field in ("emotion_decay_time", "decay_function",
                      "dominant_emotion_threshold", "update_period",
                      "mood_change_time", "mood_return_time",
                      "mood_return_mode", "vec_intensity_weighted"):
            assert getattr(loaded, field) == getattr(default, field), field

    def test_non_mapping_rejected(self):
        with pytest.raises(ValueError):
            load_config("- just\n- a list\n")

    def test_unsupported_source_type_rejected(self):
        with pytest.raises(TypeError):
            load_config(42)

    def test_missing_file_raises_file_not_found(self):
        """A mistyped path must not be parsed as document content."""
        with pytest.raises(FileNotFoundError):
            load_config("no_such_file.yaml")
        with pytest.raises(FileNotFoundError):
            load_character("no_such_file.json")


class TestAffectMLParity:
    """Everything the paper's AffectML documents express is expressible
    in YAML with the same effect."""

    def test_fig3_global_parameters(self):
        config = load_config(PAPER_FIG3_YAML)
        assert config.emotion_decay_time == 20.0
        assert config.update_period == 0.5
        assert config.decay_function is DecayFunction.LINEAR
        assert config.dominant_emotion_threshold == 0.4
        assert config.mood_return_time == 600.0

    def test_fig3_mood_relations(self):
        config = load_config(PAPER_FIG3_YAML)
        assert config.emotion_pad_map[EmotionType.ANGER].as_tuple() == \
            pytest.approx((-0.51, 0.59, 0.25))
        assert config.emotion_pad_map[EmotionType.ADMIRATION].as_tuple() == \
            pytest.approx((0.5, 0.3, -0.2))

    def test_fig3_personality_relations(self):
        config = load_config(PAPER_FIG3_YAML)
        assert config.personality_to_mood["pleasure"]["agreeableness"] == 0.59
        assert config.personality_to_mood["arousal"]["neuroticism"] == -0.57
        assert config.personality_to_mood["dominance"]["extraversion"] == 0.60

    def test_fig4_character(self):
        name, personality, rules = load_character(PAPER_FIG4_YAML)
        assert name == "Valerie"
        assert personality.conscientiousness == 0.8
        # paper form: the basic appraisal input is the tag itself
        assert rules.match_event("GoodEvent")[0].desirability == 0.7
        calm = rules.match_act("Calm", "Valerie", "self")
        assert calm[0].agency == "self" and calm[0].praiseworthiness == 0.5
        assert len(rules.match_act("Attack", "Sven", "direct")) == 2
        assert rules.match_act("Attack", "Ghost", "direct") == []
        display = rules.match_emotion_display("ReproachDisplay", "Valerie",
                                              "self")
        assert display[0].desirability == -0.3

    def test_fig4_scenario(self):
        engine = AffectEngine(load_config(PAPER_FIG3_YAML))
        engine.add_character(*load_character(PAPER_FIG4_YAML))
        engine.add_character("Sven")
        elicited = engine.perceive_act("Attack", performer="Sven",
                                       addressee="Valerie")
        assert {e.type for e in elicited["Valerie"]} >= \
            {EmotionType.DISTRESS, EmotionType.REPROACH, EmotionType.ANGER}


class TestRobustness:
    def test_field_unsupported_by_tag_rejected(self):
        """A likelihood on GoodEvent must error, not silently elicit
        Joy instead of Hope."""
        with pytest.raises(ValueError, match="likelihood"):
            eec_from_dict({"tag": "GoodEvent", "desirability": 0.7,
                           "likelihood": 0.9})

    def test_redundant_consistent_field_accepted(self):
        eec = eec_from_dict({"tag": "GoodActSelf", "agency": "self",
                             "praiseworthiness": 0.5})
        assert eec.agency == "self"

    def test_contradicting_agency_rejected(self):
        with pytest.raises(ValueError, match="agency"):
            eec_from_dict({"tag": "GoodActSelf", "agency": "other",
                           "praiseworthiness": 0.5})

    def test_zero_update_period_rejected(self):
        """update_period 0 would make engine.run() loop forever."""
        with pytest.raises(ValueError, match="update_period"):
            config_from_dict({"update_period": 0})

    def test_trait_typo_rejected_at_load_time(self):
        with pytest.raises(ValueError, match="extroversion"):
            config_from_dict({"personality_to_mood": {
                "pleasure": {"extroversion": 0.2}}})
        with pytest.raises(ValueError, match="extrovert"):
            config_from_dict({"personality_baselines": {
                "Joy": {"extrovert": 0.15}}})
