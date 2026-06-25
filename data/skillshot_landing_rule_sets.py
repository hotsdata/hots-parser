from __future__ import annotations

from data.abilities import DEFAULT_ABILITY_BUILD
from data.skillshot_landing_rules import (
    AbilityKey,
    AreaPositionRule,
    QuestCounterRule,
    SkillshotLandingRule,
    SkillshotLandingRuleSet,
)


CURRENT_BUILD_RULE_SET = SkillshotLandingRuleSet(
    game_version=DEFAULT_ABILITY_BUILD,
    rules=(
        SkillshotLandingRule(
            hero_name="Kel'Thuzad",
            ability_catalog_name="KelThuzadChains",
            ability_name="Chains of Kel'Thuzad",
            attempt=AbilityKey(1111, 0),
            detector="same_user_followup",
            confidence="proxy",
            rule_version="97039.1",
            followup_abilities=(
                AbilityKey(1112, 0),
                AbilityKey(1109, 0),
            ),
            followup_window_gameloops=48,
            quest_counter=QuestCounterRule(
                event_names=(
                    "KelThuzadMasterOfTheColdDark",
                    "KelThuzadMasterOfTheColdDarkQuest",
                    "MasterOfTheColdDark",
                ),
                window_gameloops=48,
                value_keys=(
                    "QuestProgress",
                    "StackCount",
                    "Stacks",
                    "Value",
                    "Count",
                ),
                max_value=30,
            ),
            evidence_description=(
                "Counts the initial Chains cast as landed when the same user produces "
                "a Chains Link, Chains Pull, or Kel'Thuzad quest-progress event before "
                "the next Chains attempt and within the configured evidence window."
            ),
        ),
        SkillshotLandingRule(
            hero_name="Kel'Thuzad",
            ability_catalog_name="KelThuzadFrostNova",
            ability_name="Frost Nova",
            attempt=AbilityKey(1105, 0),
            detector="area_position_overlap",
            confidence="geometry_proxy_calibrated",
            rule_version="97039.1",
            area_position=AreaPositionRule(
                impact_delay_gameloops=16,
                radius=6.0,
                target="enemy_heroes",
                outcome_stat="rootedHeroUnits",
                attempt_dedupe_window_gameloops=48,
                mechanic_radius=1.5,
                target_point_strategy="first",
            ),
            evidence_description=(
                "Counts a Frost Nova cast as landed when one or more enemy Hero units "
                "overlap the calibrated replay-position radius at the configured impact "
                "delay. The mechanic center-root radius is recorded separately; the "
                "larger replay radius compensates for one-second unit-position samples. "
                "Repeated target-point updates inside the configured dedupe window are "
                "treated as one cast, using the first target point in that cast cluster."
            ),
        ),
    ),
)


SKILLSHOT_LANDING_RULE_SETS_BY_BUILD: dict[int, SkillshotLandingRuleSet] = {
    CURRENT_BUILD_RULE_SET.game_version: CURRENT_BUILD_RULE_SET,
}
