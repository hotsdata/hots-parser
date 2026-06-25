from __future__ import annotations

from data.abilities import DEFAULT_ABILITY_BUILD
from data.skillshot_landing_rules import AbilityKey, SkillshotLandingRule, SkillshotLandingRuleSet


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
            evidence_description=(
                "Counts the initial Chains cast as landed when the same user produces "
                "a Chains Link or Chains Pull command before the next Chains attempt "
                "and within 48 gameloops."
            ),
        ),
    ),
)


SKILLSHOT_LANDING_RULE_SETS_BY_BUILD: dict[int, SkillshotLandingRuleSet] = {
    CURRENT_BUILD_RULE_SET.game_version: CURRENT_BUILD_RULE_SET,
}
