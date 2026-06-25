from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data.skillshot_landing_rules import AbilityKey, SkillshotLandingRule, get_skillshot_landing_rules
from models import BaseAbility


@dataclass(frozen=True)
class SkillshotQuestEvent:
    event_name: str
    gameloop: int
    player_id: int | None = None
    value: int | None = None


@dataclass(frozen=True)
class SkillshotLandingResult:
    status: str
    cast_gameloop: int
    evidence_type: str | None = None
    evidence_gameloop: int | None = None
    evidence_ability_link: int | None = None
    evidence_ability_cmd_index: int | None = None
    evidence_ability_name: str | None = None
    evidence_event_name: str | None = None
    evidence_value: int | None = None

    @property
    def delta_gameloops(self) -> int | None:
        if self.evidence_gameloop is None:
            return None
        return self.evidence_gameloop - self.cast_gameloop


def apply_skillshot_landing_stats(
    hero_list: dict[int, Any],
    game_version: int | None,
    quest_events: tuple[SkillshotQuestEvent, ...] = (),
) -> None:
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
            results = _process_same_user_followup(hero, rule, quest_events)
            stats[rule.ability_catalog_name] = _aggregate_results(rule, game_version, results)
        hero.generalStats["skillshotStats"] = stats


def skillshot_quest_event_names(game_version: int | None) -> set[str]:
    return {
        event_name
        for rule in get_skillshot_landing_rules(game_version)
        if rule.quest_counter is not None
        for event_name in rule.quest_counter.event_names
    }


def skillshot_quest_value_keys(game_version: int | None, event_name: str) -> tuple[str, ...]:
    for rule in get_skillshot_landing_rules(game_version):
        if rule.quest_counter is None:
            continue
        if event_name in rule.quest_counter.event_names:
            return rule.quest_counter.value_keys
    return ()


def skillshot_quest_player_id_key(game_version: int | None, event_name: str) -> str:
    for rule in get_skillshot_landing_rules(game_version):
        if rule.quest_counter is None:
            continue
        if event_name in rule.quest_counter.event_names:
            return rule.quest_counter.player_id_key
    return "PlayerID"


def _process_same_user_followup(
    hero: Any,
    rule: SkillshotLandingRule,
    quest_events: tuple[SkillshotQuestEvent, ...],
) -> list[SkillshotLandingResult]:
    casted_abilities = hero.generalStats["castedAbilities"]
    casts = sorted(casted_abilities.values(), key=lambda ability: ability.castedAtGameLoops)
    attempts = [ability for ability in casts if _ability_matches(ability, rule.attempt)]
    followups = [ability for ability in casts if _ability_key(ability) in rule.followup_abilities]
    results = []

    for index, attempt in enumerate(attempts):
        next_attempt_loop = attempts[index + 1].castedAtGameLoops if index + 1 < len(attempts) else None
        quest_event = _first_quest_event_for_attempt(attempt, hero, quest_events, next_attempt_loop, rule)
        if quest_event is not None:
            results.append(
                SkillshotLandingResult(
                    status="landed",
                    cast_gameloop=attempt.castedAtGameLoops,
                    evidence_type="quest_counter",
                    evidence_gameloop=quest_event.gameloop,
                    evidence_event_name=quest_event.event_name,
                    evidence_value=quest_event.value,
                )
            )
            continue

        followup = _first_followup_for_attempt(attempt, followups, next_attempt_loop, rule.followup_window_gameloops)
        if followup is None:
            results.append(SkillshotLandingResult(status="missed", cast_gameloop=attempt.castedAtGameLoops))
            continue
        results.append(
            SkillshotLandingResult(
                status="landed",
                cast_gameloop=attempt.castedAtGameLoops,
                evidence_type="followup_ability",
                evidence_gameloop=followup.castedAtGameLoops,
                evidence_ability_link=followup.abilityLink,
                evidence_ability_cmd_index=followup.abilityCmdIndex,
                evidence_ability_name=followup.abilityName,
            )
        )

    return results


def _first_quest_event_for_attempt(
    attempt: BaseAbility,
    hero: Any,
    quest_events: tuple[SkillshotQuestEvent, ...],
    next_attempt_loop: int | None,
    rule: SkillshotLandingRule,
) -> SkillshotQuestEvent | None:
    if rule.quest_counter is None:
        return None

    upper_bound = attempt.castedAtGameLoops + rule.quest_counter.window_gameloops
    if next_attempt_loop is not None:
        upper_bound = min(upper_bound, next_attempt_loop)
    hero_player_id = getattr(hero, "playerId", None)

    for quest_event in quest_events:
        if quest_event.event_name not in rule.quest_counter.event_names:
            continue
        if quest_event.player_id is not None and hero_player_id is not None and quest_event.player_id != hero_player_id:
            continue
        if rule.quest_counter.max_value is not None and quest_event.value is not None:
            if quest_event.value > rule.quest_counter.max_value:
                continue
        if attempt.castedAtGameLoops < quest_event.gameloop < upper_bound:
            return quest_event
    return None


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
    landed_by_evidence = _landed_by_evidence(results)

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
        "landedByEvidence": landed_by_evidence,
        "missed": missed,
        "questCounterEventNames": list(rule.quest_counter.event_names) if rule.quest_counter else [],
        "questCounterWindowGameloops": rule.quest_counter.window_gameloops if rule.quest_counter else None,
        "sampleEvidence": sample_evidence,
        "totalAttempts": attempts,
        "unknown": unknown,
        "ruleVersion": rule.rule_version,
    }


def _result_evidence(result: SkillshotLandingResult) -> dict[str, Any]:
    return {
        "castGameLoop": result.cast_gameloop,
        "evidenceType": result.evidence_type,
        "evidenceGameLoop": result.evidence_gameloop,
        "deltaGameloops": result.delta_gameloops,
        "evidenceAbilityLink": result.evidence_ability_link,
        "evidenceAbilityCmdIndex": result.evidence_ability_cmd_index,
        "evidenceAbilityName": result.evidence_ability_name,
        "evidenceEventName": result.evidence_event_name,
        "evidenceValue": result.evidence_value,
    }


def _landed_by_evidence(results: list[SkillshotLandingResult]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for result in results:
        if result.status != "landed":
            continue
        evidence_type = result.evidence_type or "unknown"
        counts[evidence_type] = counts.get(evidence_type, 0) + 1
    return dict(sorted(counts.items()))


def _ability_matches(ability: BaseAbility, key: AbilityKey) -> bool:
    return ability.abilityLink == key.ability_link and ability.abilityCmdIndex == key.ability_cmd_index


def _ability_key(ability: BaseAbility) -> AbilityKey:
    ability_link = -1 if ability.abilityLink is None else ability.abilityLink
    ability_cmd_index = -1 if ability.abilityCmdIndex is None else ability.abilityCmdIndex
    return AbilityKey(ability_link, ability_cmd_index)
