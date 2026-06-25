from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class AbilityKey:
    ability_link: int
    ability_cmd_index: int


@dataclass(frozen=True)
class SkillshotLandingRule:
    hero_name: str
    ability_catalog_name: str
    ability_name: str
    attempt: AbilityKey
    detector: str
    confidence: str
    rule_version: str
    followup_abilities: tuple[AbilityKey, ...] = ()
    followup_window_gameloops: int = 0
    evidence_description: str = ""


@dataclass(frozen=True)
class SkillshotLandingRuleSet:
    game_version: int
    rules: tuple[SkillshotLandingRule, ...]


def get_skillshot_landing_rules(game_version: int | None) -> tuple[SkillshotLandingRule, ...]:
    if game_version is None:
        return ()

    from data.skillshot_landing_rule_sets import SKILLSHOT_LANDING_RULE_SETS_BY_BUILD

    rule_set = SKILLSHOT_LANDING_RULE_SETS_BY_BUILD.get(game_version)
    if rule_set is None:
        return ()
    return rule_set.rules
