from __future__ import annotations

from dataclasses import dataclass

from data.abilities import DEFAULT_ABILITY_BUILD


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


def get_skillshot_landing_rules(game_version: int | None) -> tuple[SkillshotLandingRule, ...]:
    if game_version != DEFAULT_ABILITY_BUILD:
        return ()

    from data.skillshot_landing_rules_97039 import SKILLSHOT_LANDING_RULES_97039

    return SKILLSHOT_LANDING_RULES_97039
