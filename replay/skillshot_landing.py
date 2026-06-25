from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data.skillshot_landing_rules import AbilityKey, SkillshotLandingRule, get_skillshot_landing_rules
from models import BaseAbility


@dataclass(frozen=True)
class SkillshotLandingResult:
    status: str
    cast_gameloop: int
    evidence_gameloop: int | None = None
    evidence_ability_link: int | None = None
    evidence_ability_cmd_index: int | None = None
    evidence_ability_name: str | None = None

    @property
    def delta_gameloops(self) -> int | None:
        if self.evidence_gameloop is None:
            return None
        return self.evidence_gameloop - self.cast_gameloop


def apply_skillshot_landing_stats(hero_list: dict[int, Any], game_version: int | None) -> None:
    rules = get_skillshot_landing_rules(game_version)
    if not rules:
        return

    for hero in hero_list.values():
        hero_rules = [rule for rule in rules if rule.hero_name == hero.name]
        if not hero_rules:
            hero.generalStats.setdefault("skillshotStats", {})
            continue

        stats = {}
        for rule in hero_rules:
            if rule.detector != "same_user_followup":
                continue
            results = _process_same_user_followup(hero.generalStats["castedAbilities"], rule)
            stats[rule.ability_catalog_name] = _aggregate_results(rule, game_version, results)
        hero.generalStats["skillshotStats"] = stats


def _process_same_user_followup(
    casted_abilities: dict[int, BaseAbility],
    rule: SkillshotLandingRule,
) -> list[SkillshotLandingResult]:
    casts = sorted(casted_abilities.values(), key=lambda ability: ability.castedAtGameLoops)
    attempts = [ability for ability in casts if _ability_matches(ability, rule.attempt)]
    followups = [ability for ability in casts if _ability_key(ability) in rule.followup_abilities]
    results = []

    for index, attempt in enumerate(attempts):
        next_attempt_loop = attempts[index + 1].castedAtGameLoops if index + 1 < len(attempts) else None
        followup = _first_followup_for_attempt(attempt, followups, next_attempt_loop, rule.followup_window_gameloops)
        if followup is None:
            results.append(SkillshotLandingResult(status="missed", cast_gameloop=attempt.castedAtGameLoops))
            continue
        results.append(
            SkillshotLandingResult(
                status="landed",
                cast_gameloop=attempt.castedAtGameLoops,
                evidence_gameloop=followup.castedAtGameLoops,
                evidence_ability_link=followup.abilityLink,
                evidence_ability_cmd_index=followup.abilityCmdIndex,
                evidence_ability_name=followup.abilityName,
            )
        )

    return results


def _first_followup_for_attempt(
    attempt: BaseAbility,
    followups: list[BaseAbility],
    next_attempt_loop: int | None,
    window_gameloops: int,
) -> BaseAbility | None:
    upper_bound = attempt.castedAtGameLoops + window_gameloops
    if next_attempt_loop is not None:
        upper_bound = min(upper_bound, next_attempt_loop)

    for followup in followups:
        if followup.userId != attempt.userId:
            continue
        if attempt.castedAtGameLoops < followup.castedAtGameLoops < upper_bound:
            return followup
    return None


def _aggregate_results(
    rule: SkillshotLandingRule,
    game_version: int | None,
    results: list[SkillshotLandingResult],
) -> dict[str, Any]:
    attempts = len(results)
    landed = sum(1 for result in results if result.status == "landed")
    missed = sum(1 for result in results if result.status == "missed")
    unknown = sum(1 for result in results if result.status == "unknown")
    hit_rate = round(landed / attempts, 4) if attempts else None
    sample_evidence = [_result_evidence(result) for result in results if result.status == "landed"][:5]

    return {
        "abilityCatalogName": rule.ability_catalog_name,
        "abilityName": rule.ability_name,
        "attemptAbilityLink": rule.attempt.ability_link,
        "attemptAbilityCmdIndex": rule.attempt.ability_cmd_index,
        "confidence": rule.confidence,
        "detector": rule.detector,
        "evidenceDescription": rule.evidence_description,
        "followupWindowGameloops": rule.followup_window_gameloops,
        "gameVersion": game_version,
        "hitRate": hit_rate,
        "landed": landed,
        "missed": missed,
        "sampleEvidence": sample_evidence,
        "totalAttempts": attempts,
        "unknown": unknown,
        "ruleVersion": rule.rule_version,
    }


def _result_evidence(result: SkillshotLandingResult) -> dict[str, Any]:
    return {
        "castGameLoop": result.cast_gameloop,
        "evidenceGameLoop": result.evidence_gameloop,
        "deltaGameloops": result.delta_gameloops,
        "evidenceAbilityLink": result.evidence_ability_link,
        "evidenceAbilityCmdIndex": result.evidence_ability_cmd_index,
        "evidenceAbilityName": result.evidence_ability_name,
    }


def _ability_matches(ability: BaseAbility, key: AbilityKey) -> bool:
    return ability.abilityLink == key.ability_link and ability.abilityCmdIndex == key.ability_cmd_index


def _ability_key(ability: BaseAbility) -> AbilityKey:
    ability_link = -1 if ability.abilityLink is None else ability.abilityLink
    ability_cmd_index = -1 if ability.abilityCmdIndex is None else ability.abilityCmdIndex
    return AbilityKey(ability_link, ability_cmd_index)
