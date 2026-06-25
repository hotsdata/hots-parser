from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Any

from data.skillshot_landing_rules import AbilityKey, SkillshotLandingRule, get_skillshot_landing_rules
from helpers import get_seconds_from_int_gameloop
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
    target_count: int = 0
    target_hero_names: tuple[str, ...] = ()
    target_player_ids: tuple[int, ...] = ()
    target_distances: tuple[float, ...] = ()

    @property
    def delta_gameloops(self) -> int | None:
        if self.evidence_gameloop is None:
            return None
        return self.evidence_gameloop - self.cast_gameloop


def apply_skillshot_landing_stats(
    hero_list: dict[int, Any],
    game_version: int | None,
    quest_events: tuple[SkillshotQuestEvent, ...] = (),
    units_in_game: dict[int | None, Any] | None = None,
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
            if rule.detector == "same_user_followup":
                results = _process_same_user_followup(hero, rule, quest_events)
            elif rule.detector == "area_position_overlap":
                results = _process_area_position_overlap(hero, hero_list, units_in_game or {}, rule)
            else:
                continue
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


def _process_area_position_overlap(
    hero: Any,
    hero_list: dict[int, Any],
    units_in_game: dict[int | None, Any],
    rule: SkillshotLandingRule,
) -> list[SkillshotLandingResult]:
    if rule.area_position is None:
        return []

    casted_abilities = hero.generalStats["castedAbilities"]
    casts = sorted(casted_abilities.values(), key=lambda ability: ability.castedAtGameLoops)
    attempts = [ability for ability in casts if _ability_matches(ability, rule.attempt)]
    attempts = _dedupe_area_attempts(attempts, rule.area_position.attempt_dedupe_window_gameloops)
    results = []

    for attempt in attempts:
        target_x = getattr(attempt, "x", None)
        target_y = getattr(attempt, "y", None)
        impact_gameloop = attempt.castedAtGameLoops + rule.area_position.impact_delay_gameloops

        if target_x is None or target_y is None:
            results.append(
                SkillshotLandingResult(
                    status="unknown",
                    cast_gameloop=attempt.castedAtGameLoops,
                    evidence_type="missing_target_point",
                    evidence_gameloop=impact_gameloop,
                )
            )
            continue

        hits = _enemy_hero_area_hits(
            hero,
            hero_list,
            units_in_game,
            impact_gameloop,
            float(target_x),
            float(target_y),
            rule.area_position.radius,
        )
        target_count = len(hits)
        results.append(
            SkillshotLandingResult(
                status="landed" if target_count else "missed",
                cast_gameloop=attempt.castedAtGameLoops,
                evidence_type="area_position_overlap" if target_count else None,
                evidence_gameloop=impact_gameloop,
                target_count=target_count,
                target_hero_names=tuple(hit["hero_name"] for hit in hits),
                target_player_ids=tuple(hit["player_id"] for hit in hits if hit["player_id"] is not None),
                target_distances=tuple(hit["distance"] for hit in hits),
            )
        )

    return results


def _dedupe_area_attempts(attempts: list[BaseAbility], window_gameloops: int) -> list[BaseAbility]:
    if window_gameloops <= 0:
        return attempts

    deduped_attempts = []
    current_cluster: list[BaseAbility] = []
    for attempt in attempts:
        if not current_cluster:
            current_cluster.append(attempt)
            continue

        previous_attempt = current_cluster[-1]
        if attempt.castedAtGameLoops - previous_attempt.castedAtGameLoops <= window_gameloops:
            current_cluster.append(attempt)
            continue

        deduped_attempts.append(_select_area_attempt(current_cluster))
        current_cluster = [attempt]

    if current_cluster:
        deduped_attempts.append(_select_area_attempt(current_cluster))
    return deduped_attempts


def _select_area_attempt(attempts: list[BaseAbility]) -> BaseAbility:
    target_point_attempts = [
        attempt
        for attempt in attempts
        if getattr(attempt, "x", None) is not None and getattr(attempt, "y", None) is not None
    ]
    if target_point_attempts:
        return target_point_attempts[-1]
    return attempts[-1]


def _enemy_hero_area_hits(
    caster: Any,
    hero_list: dict[int, Any],
    units_in_game: dict[int | None, Any],
    impact_gameloop: int,
    target_x: float,
    target_y: float,
    radius: float,
) -> list[dict[str, Any]]:
    impact_second = get_seconds_from_int_gameloop(impact_gameloop)
    caster_team = getattr(caster, "team", None)
    hits = []

    for enemy in hero_list.values():
        if enemy is caster:
            continue
        if caster_team is not None and getattr(enemy, "team", None) == caster_team:
            continue

        unit_tag = _hero_unit_tag(enemy)
        unit = units_in_game.get(unit_tag)
        position = _position_at_second(unit, impact_second)
        if position is None:
            continue

        distance = hypot(float(position[0]) - target_x, float(position[1]) - target_y)
        if distance <= radius:
            hits.append(
                {
                    "hero_name": getattr(enemy, "name", "Unknown"),
                    "player_id": getattr(enemy, "playerId", None),
                    "distance": round(distance, 4),
                }
            )

    return sorted(hits, key=lambda hit: (hit["distance"], hit["hero_name"]))


def _hero_unit_tag(hero: Any) -> int | None:
    unit_tag = getattr(hero, "unitTag", None)
    if unit_tag is not None:
        return unit_tag

    unit_tag_method = getattr(hero, "unit_tag", None)
    if callable(unit_tag_method):
        return unit_tag_method()
    return None


def _position_at_second(unit: Any, second: int) -> list[Any] | None:
    if unit is None:
        return None

    positions = getattr(unit, "positions", None)
    if not positions:
        return None

    if second in positions:
        return positions[second]

    lower_second = max((position_second for position_second in positions if position_second < second), default=None)
    upper_second = min((position_second for position_second in positions if position_second > second), default=None)

    if lower_second is None:
        return None
    if upper_second is None:
        return positions[lower_second]

    elapsed = upper_second - lower_second
    if elapsed <= 0:
        return positions[lower_second]

    lower_position = positions[lower_second]
    upper_position = positions[upper_second]
    ratio = (second - lower_second) / elapsed
    x = float(lower_position[0]) + (float(upper_position[0]) - float(lower_position[0])) * ratio
    y = float(lower_position[1]) + (float(upper_position[1]) - float(lower_position[1])) * ratio
    return [x, y]


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
    total_targets_hit = sum(result.target_count for result in results)

    stats = {
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

    if rule.area_position is not None:
        stats.update(
            {
                "areaImpactDelayGameloops": rule.area_position.impact_delay_gameloops,
                "areaRadius": rule.area_position.radius,
                "areaTarget": rule.area_position.target,
                "attemptDedupeWindowGameloops": rule.area_position.attempt_dedupe_window_gameloops,
                "averageTargetsHit": round(total_targets_hit / attempts, 4) if attempts else None,
                "totalTargetsHit": total_targets_hit,
                rule.area_position.outcome_stat: total_targets_hit,
            }
        )

    return stats


def _result_evidence(result: SkillshotLandingResult) -> dict[str, Any]:
    evidence = {
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
    if result.target_count:
        evidence.update(
            {
                "targetCount": result.target_count,
                "targetHeroNames": list(result.target_hero_names),
                "targetPlayerIds": list(result.target_player_ids),
                "targetDistances": list(result.target_distances),
            }
        )
    return evidence


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
