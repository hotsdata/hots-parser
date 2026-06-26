#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import contextlib
import io
import json
import random
import re
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import HeroTranslator
from data.abilities import (
    DEFAULT_ABILITY_BUILD,
    HERO_ABILITY_CATALOG_NAMES_BY_BUILD,
    get_hero_ability_definitions,
)
from data.skillshot_landing_rule_sets import SKILLSHOT_LANDING_RULE_SETS_BY_BUILD
from hotsparser import processEvents
from protocol_loader import get_header_protocol, get_mpyq_archive_class, get_protocol_for_build
from replay import _normalize_protocol_value


SCRIPT_VERSION = 1
WIKI_API_URL = "https://heroesofthestorm.fandom.com/api.php"
WIKI_SOURCE_URL = "https://heroesofthestorm.fandom.com/wiki/Data:%s"

LIKELY_NO_RULE_TERMS = (
    "cancel",
    "mount",
    "hearth",
    "trait",
    "passive",
    "quest",
    "activatable",
    "toggle",
    "vehicle",
    "interact",
    "spray",
    "voice line",
    "dance",
    "taunt",
    "self",
    "shield",
    "cleanse",
    "ice block",
    "fountain",
)

LIKELY_SKILLSHOT_TERMS = (
    "arrow",
    "beam",
    "blast",
    "bomb",
    "bolt",
    "charge",
    "chain",
    "cone",
    "dart",
    "explosion",
    "fissure",
    "flare",
    "grenade",
    "hook",
    "lance",
    "laser",
    "lazor",
    "meteor",
    "missile",
    "nova",
    "orb",
    "pull",
    "root",
    "shot",
    "slam",
    "spear",
    "strike",
    "stun",
    "wave",
)

WIKI_NO_RULE_TARGETS = (
    "automatic",
    "direct control",
    "passive",
    "self",
)

WIKI_NO_RULE_TYPES = (
    "bonus",
    "cleanse",
    "defensive damage modifier",
    "debuff removal",
    "healing",
    "mana",
    "movement",
    "shield",
    "status effect",
    "transformation",
)

WIKI_BLOCKED_TERMS_BY_FAMILY = (
    ("trap_trigger", ("arming delay", "becomes active", "mine", "trap")),
    ("persistent_area", ("damage over time", "every ", "lasts ", "periodic", "tickrate")),
    ("channel_or_beam", ("beam", "channel", "channeled", "stationary channel")),
    ("summon_or_pet_origin", ("beetle", "clone", "locust", "misha", "monstrosity", "summon", "totem", "turret")),
    ("multi_projectile", ("each missile", "multiple", "several", "split")),
)


def _to_text(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return "" if value is None else str(value)


def _slug(value: str) -> str:
    normalized = value.replace("'", "")
    normalized = re.sub(r"[^A-Za-z0-9]+", "-", normalized).strip("-")
    return normalized.lower() or "unknown"


def _term_match(text: str, terms: tuple[str, ...]) -> str | None:
    lowered = text.lower()
    for term in terms:
        if term in lowered:
            return term
    return None


def _implemented_rules(build: int) -> dict[str, Any]:
    rule_set = SKILLSHOT_LANDING_RULE_SETS_BY_BUILD.get(build)
    if rule_set is None:
        return {}
    return {rule.ability_catalog_name: rule for rule in rule_set.rules}


def _rule_summary(rule: Any) -> dict[str, Any]:
    summary = {
        "abilityCatalogName": rule.ability_catalog_name,
        "abilityName": rule.ability_name,
        "attempt": {
            "abilityLink": rule.attempt.ability_link,
            "abilityCmdIndex": rule.attempt.ability_cmd_index,
        },
        "confidence": rule.confidence,
        "detector": rule.detector,
        "evidenceDescription": rule.evidence_description,
        "ruleVersion": rule.rule_version,
    }
    if rule.followup_abilities:
        summary["followupAbilities"] = [
            {"abilityLink": ability.ability_link, "abilityCmdIndex": ability.ability_cmd_index}
            for ability in rule.followup_abilities
        ]
        summary["followupWindowGameloops"] = rule.followup_window_gameloops
    if rule.quest_counter is not None:
        summary["questCounter"] = asdict(rule.quest_counter)
    if rule.area_position is not None:
        summary["areaPosition"] = asdict(rule.area_position)
    if rule.directional_position is not None:
        summary["directionalPosition"] = asdict(rule.directional_position)
    return summary


def _research_queries(hero_name: str, ability_name: str) -> list[str]:
    return [
        f"Heroes of the Storm {hero_name} {ability_name} mechanics",
        f"Heroes of the Storm {hero_name} {ability_name} radius delay hit",
        f"Heroes of the Storm {hero_name} {ability_name} quest talent interaction",
    ]


def _normalize_ability_name(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\[\[([^|\]]*\|)?([^\]]+)\]\]", r"\2", value)
    value = re.sub(r"[^a-z0-9]+", " ", value.lower())
    return re.sub(r"\s+", " ", value).strip()


def _strip_wiki_markup(value: str) -> str:
    value = re.sub(r"<!--.*?-->", " ", value, flags=re.DOTALL)
    value = re.sub(r"\{\{undoc-x\|.*?\}\}", " ", value, flags=re.DOTALL)
    value = re.sub(r"\{\{[^{}]*\}\}", " ", value)
    value = re.sub(r"\[\[([^|\]]*\|)?([^\]]+)\]\]", r"\2", value)
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"</?[^>]+>", " ", value)
    value = value.replace("'''", "").replace("''", "")
    value = value.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", value).strip()


def _extract_field(wikitext: str, field_name: str, next_fields: tuple[str, ...]) -> str:
    match = re.search(r"(?m)^\| %s = ?(.*)$" % re.escape(field_name), wikitext)
    if match is None:
        return ""
    value_start = match.start(1)

    end_candidates = []
    for next_field in next_fields:
        next_match = re.search(r"(?m)^\| %s = ?" % re.escape(next_field), wikitext[value_start:])
        if next_match is not None:
            end_candidates.append(value_start + next_match.start())
    end = min(end_candidates) if end_candidates else len(wikitext)
    return wikitext[value_start:end].strip()


def _entry_start_positions(block: str) -> list[re.Match[str]]:
    return list(re.finditer(r"(?m)^(?!<!--)(?!-)(?!\s)([^;\n{}|<][^;\n]*);", block))


def _extract_undoc_fields(raw_description: str) -> dict[str, str]:
    values: dict[str, list[str]] = {}
    for template in re.findall(r"\{\{undoc-x\|(.*?)\}\}", raw_description, flags=re.DOTALL):
        for part in template.split("|"):
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            key = key.strip().lower()
            value = _strip_wiki_markup(value)
            if not key or not value:
                continue
            values.setdefault(key, []).append(value)
    return {key: " / ".join(items) for key, items in sorted(values.items())}


def _parse_wiki_entries_block(block: str, section: str) -> list[dict[str, Any]]:
    matches = _entry_start_positions(block)
    entries = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(block)
        raw_entry = block[start:end].strip()
        parts = raw_entry.split(";", 4)
        if section == "skills":
            if len(parts) < 4:
                continue
            name, slot, icon, raw_description = parts[:4]
            metadata = {"slot": slot.strip(), "icon": icon.strip()}
        else:
            if len(parts) < 4:
                continue
            name, tier, column, raw_description = parts[:4]
            metadata = {"talentTier": tier.strip(), "talentColumn": column.strip()}
        undoc_fields = _extract_undoc_fields(raw_description)
        entries.append(
            {
                "name": _strip_wiki_markup(name),
                "normalizedName": _normalize_ability_name(name),
                "section": section,
                "description": _strip_wiki_markup(raw_description),
                "undoc": undoc_fields,
                **metadata,
            }
        )
    return entries


def parse_wiki_hero_data(hero_name: str, wikitext: str) -> dict[str, Any]:
    skills = _extract_field(wikitext, "skills", ("talents", "skins"))
    talents = _extract_field(wikitext, "talents", ("skins", "mounts", "voice"))
    entries = _parse_wiki_entries_block(skills, "skills")
    entries.extend(_parse_wiki_entries_block(talents, "talents"))
    source_url_name = hero_name.replace(" ", "_")
    return {
        "heroName": hero_name,
        "sourceUrl": WIKI_SOURCE_URL % source_url_name,
        "entryCount": len(entries),
        "entries": entries,
    }


def _fetch_wiki_wikitext(page_title: str) -> str:
    params = urlencode(
        {
            "action": "parse",
            "page": page_title,
            "prop": "wikitext",
            "format": "json",
            "formatversion": "2",
        }
    )
    request = Request(
        "%s?%s" % (WIKI_API_URL, params),
        headers={
            "Accept": "application/json,text/plain,*/*",
            "User-Agent": "Mozilla/5.0 skillshot-triage",
        },
    )
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if "error" in payload:
        raise RuntimeError(payload["error"].get("info") or str(payload["error"]))
    return payload["parse"]["wikitext"]


def fetch_wiki_hero_sources(hero_names: list[str]) -> dict[str, Any]:
    heroes = []
    failures = []
    for hero_name in hero_names:
        try:
            wikitext = _fetch_wiki_wikitext("Data:%s" % hero_name)
            heroes.append(parse_wiki_hero_data(hero_name, wikitext))
        except Exception as exc:
            failures.append({"heroName": hero_name, "errorType": type(exc).__name__, "error": str(exc)})
    return {
        "schemaVersion": SCRIPT_VERSION,
        "source": "Heroes of the Storm Wiki Data pages",
        "apiUrl": WIKI_API_URL,
        "heroCount": len(heroes),
        "failures": failures,
        "heroes": heroes,
    }


def _entry_matches_ability(entry: dict[str, Any], ability_name: str) -> bool:
    ability_normalized = _normalize_ability_name(ability_name)
    entry_normalized = entry["normalizedName"]
    if not ability_normalized or not entry_normalized:
        return False
    if ability_normalized == entry_normalized:
        return True
    return ability_normalized in entry_normalized or entry_normalized in ability_normalized


def _match_wiki_entry(hero_source: dict[str, Any] | None, ability: dict[str, Any]) -> dict[str, Any] | None:
    if hero_source is None:
        return None
    matches = [
        entry
        for entry in hero_source["entries"]
        if _entry_matches_ability(entry, ability["abilityName"])
    ]
    if not matches:
        return None
    ability_normalized = _normalize_ability_name(ability["abilityName"])
    return sorted(
        matches,
        key=lambda entry: (
            entry["normalizedName"] != ability_normalized,
            entry["section"] != "skills",
            len(entry["normalizedName"]),
        ),
    )[0]


def _wiki_text_blob(entry: dict[str, Any]) -> str:
    values = [entry["name"], entry["description"]]
    values.extend(entry.get("undoc", {}).values())
    return " ".join(values).lower()


def classify_wiki_entry(entry: dict[str, Any]) -> dict[str, Any]:
    fields = entry.get("undoc", {})
    target = fields.get("target", "").lower()
    entry_type = fields.get("type", "").lower()
    affects = fields.get("affects", "").lower()
    props = fields.get("props", "").lower()
    radius = fields.get("radius", "")
    hitbox = fields.get("hitbox", "")
    missile = fields.get("missile", "")
    blob = _wiki_text_blob(entry)
    is_enemy_effect = (
        "enemies" in affects
        or "enemy" in affects
        or "damage" in entry_type
        or "crowd control" in entry_type
    )

    if "unit target" in target:
        return {
            "decision": "no_rule_likely",
            "detectorFamily": "unit_target_guaranteed",
            "reason": "Wiki marks this as unit-targeted, so landing is not an aiming check.",
        }

    if "transformation" in entry_type and "skillshot" not in props and "point target" not in target:
        return {
            "decision": "no_rule_likely",
            "detectorFamily": "transformation_or_form_swap",
            "reason": "Wiki type metadata indicates a transformation or form swap rather than a landing check.",
        }

    if any(term in target for term in WIKI_NO_RULE_TARGETS) and not is_enemy_effect:
        return {
            "decision": "no_rule_likely",
            "detectorFamily": "non_aimed_targeting",
            "reason": "Wiki target metadata is not an aimed enemy landing check.",
        }

    if any(term in entry_type for term in WIKI_NO_RULE_TYPES) and not is_enemy_effect:
        return {
            "decision": "no_rule_likely",
            "detectorFamily": "buff_heal_movement_or_form",
            "reason": "Wiki type metadata indicates healing, shield, movement, form, or stat-modifier behavior.",
        }

    for family, terms in WIKI_BLOCKED_TERMS_BY_FAMILY:
        if any(term in blob for term in terms):
            if family in {"trap_trigger", "summon_or_pet_origin"} and "point target" in target:
                return {
                    "decision": "blocked_new_detector",
                    "detectorFamily": family,
                    "reason": "Wiki mechanics matched the blocked %s family." % family,
                }
            if is_enemy_effect and ("area of effect" in props or "skillshot" in props or "point target" in target):
                return {
                    "decision": "blocked_new_detector",
                    "detectorFamily": family,
                    "reason": "Wiki mechanics matched the blocked %s family." % family,
                }

    if "point target" in target and (
        "skillshot" in props
        or hitbox
        or missile
        or "first enemy" in blob
        or "toward target" in blob
        or "target area" in blob and "contacts" in blob
    ) and is_enemy_effect:
        return {
            "decision": "rule_candidate_existing_detector",
            "detectorFamily": "directional_position_overlap",
            "reason": "Wiki marks this as a point-target skillshot or projectile-style ability.",
        }

    if "point target" in target and is_enemy_effect and ("area of effect" in props or radius or "radius" in blob):
        return {
            "decision": "rule_candidate_existing_detector",
            "detectorFamily": "area_position_overlap",
            "reason": "Wiki marks this as a point-target area ability.",
        }

    if "no target" in target and "area of effect" in props and is_enemy_effect:
        return {
            "decision": "blocked_new_detector",
            "detectorFamily": "source_centered_area",
            "reason": "Wiki marks this as a no-target area effect around the caster or hosted source.",
        }

    if any(term in target for term in WIKI_NO_RULE_TARGETS):
        return {
            "decision": "no_rule_likely",
            "detectorFamily": "non_aimed_targeting",
            "reason": "Wiki target metadata is not an aimed enemy landing check.",
        }

    if any(term in entry_type for term in WIKI_NO_RULE_TYPES):
        return {
            "decision": "no_rule_likely",
            "detectorFamily": "buff_heal_movement_or_form",
            "reason": "Wiki type metadata indicates healing, shield, movement, form, or stat-modifier behavior.",
        }

    if entry["section"] == "talents" and not any(term in blob for term in ("activate", "point target", "skillshot", "enemy")):
        return {
            "decision": "no_rule_likely",
            "detectorFamily": "passive_talent_modifier",
            "reason": "Wiki talent text looks like a passive modifier rather than a cast landing check.",
        }

    return {
        "decision": "needs_manual_review",
        "detectorFamily": None,
        "reason": "Wiki metadata was matched, but it did not clearly map to a no-rule, candidate, or blocked family.",
    }


def build_wiki_triage(coverage: dict[str, Any], wiki_sources: dict[str, Any]) -> dict[str, Any]:
    sources_by_hero = {hero["heroName"]: hero for hero in wiki_sources["heroes"]}
    heroes = []
    decision_counts: Counter[str] = Counter()
    original_needs_triage_counts: Counter[str] = Counter()
    match_counts: Counter[str] = Counter()

    for hero in coverage["heroes"]:
        source = sources_by_hero.get(hero["heroName"])
        abilities = []
        for ability in hero["abilities"]:
            if ability["decision"] == "implemented":
                triage = {
                    "decision": "implemented",
                    "detectorFamily": ability["rule"]["detector"],
                    "reason": "A versioned skillshot landing rule already exists.",
                }
                matched_entry = None
            else:
                matched_entry = _match_wiki_entry(source, ability)
                if matched_entry is None:
                    triage = {
                        "decision": "wiki_unmatched",
                        "detectorFamily": None,
                        "reason": "No matching ability or talent entry was found in the hero wiki data page.",
                    }
                else:
                    triage = classify_wiki_entry(matched_entry)

            decision_counts[triage["decision"]] += 1
            if matched_entry is None:
                match_counts["unmatched"] += 1
            else:
                match_counts["matched"] += 1
            if ability["decision"] == "needs_triage":
                original_needs_triage_counts[triage["decision"]] += 1

            ability_row = {
                "abilityCatalogName": ability["abilityCatalogName"],
                "abilityName": ability["abilityName"],
                "originalDecision": ability["decision"],
                "wikiDecision": triage["decision"],
                "detectorFamily": triage.get("detectorFamily"),
                "reason": triage["reason"],
            }
            if matched_entry is not None:
                ability_row["wikiEntry"] = {
                    "name": matched_entry["name"],
                    "section": matched_entry["section"],
                    "description": matched_entry["description"],
                    "target": matched_entry.get("undoc", {}).get("target"),
                    "type": matched_entry.get("undoc", {}).get("type"),
                    "affects": matched_entry.get("undoc", {}).get("affects"),
                    "props": matched_entry.get("undoc", {}).get("props"),
                    "radius": matched_entry.get("undoc", {}).get("radius"),
                    "hitbox": matched_entry.get("undoc", {}).get("hitbox"),
                    "missile": matched_entry.get("undoc", {}).get("missile"),
                    "sourceUrl": source["sourceUrl"] if source is not None else None,
                }
            abilities.append(ability_row)

        hero_counts = Counter(ability["wikiDecision"] for ability in abilities)
        heroes.append(
            {
                "heroCatalogName": hero["heroCatalogName"],
                "heroName": hero["heroName"],
                "heroSlug": hero["heroSlug"],
                "decisionCounts": dict(sorted(hero_counts.items())),
                "abilities": abilities,
            }
        )

    return {
        "schemaVersion": SCRIPT_VERSION,
        "build": coverage["build"],
        "source": wiki_sources["source"],
        "sourceApiUrl": wiki_sources["apiUrl"],
        "heroCount": coverage["heroCount"],
        "abilityCount": coverage["abilityCount"],
        "decisionCounts": dict(sorted(decision_counts.items())),
        "originalNeedsTriageDecisionCounts": dict(sorted(original_needs_triage_counts.items())),
        "matchCounts": dict(sorted(match_counts.items())),
        "sourceFailures": wiki_sources["failures"],
        "heroes": heroes,
    }


def build_candidate_status_table(triage: dict[str, Any]) -> dict[str, Any]:
    rows = []
    hero_summaries = []
    for hero in triage["heroes"]:
        hero_rows = []
        for ability in hero["abilities"]:
            decision = ability["wikiDecision"]
            if decision not in {"implemented", "rule_candidate_existing_detector"}:
                continue
            created = decision == "implemented"
            status = "created" if created else "candidate_not_created"
            wiki_entry = ability.get("wikiEntry", {})
            row = {
                "heroName": hero["heroName"],
                "abilityName": ability["abilityName"],
                "abilityCatalogName": ability["abilityCatalogName"],
                "created": "yes" if created else "no",
                "status": status,
                "detectorFamily": ability.get("detectorFamily") or "",
                "sourceDecision": decision,
                "originalDecision": ability["originalDecision"],
                "wikiMatchedName": wiki_entry.get("name", ""),
                "wikiTarget": wiki_entry.get("target") or "",
                "wikiType": wiki_entry.get("type") or "",
                "wikiProps": wiki_entry.get("props") or "",
                "wikiSourceUrl": wiki_entry.get("sourceUrl") or "",
                "reason": ability["reason"],
            }
            rows.append(row)
            hero_rows.append(row)

        if hero_rows:
            status_counts = Counter(row["status"] for row in hero_rows)
            hero_summaries.append(
                {
                    "heroName": hero["heroName"],
                    "totalCandidateSkills": len(hero_rows),
                    "created": status_counts.get("created", 0),
                    "candidateNotCreated": status_counts.get("candidate_not_created", 0),
                    "detectorFamilies": ", ".join(sorted({row["detectorFamily"] for row in hero_rows if row["detectorFamily"]})),
                }
            )

    total_status_counts = Counter(row["status"] for row in rows)
    return {
        "schemaVersion": SCRIPT_VERSION,
        "build": triage["build"],
        "source": triage["source"],
        "totalCandidateSkills": len(rows),
        "created": total_status_counts.get("created", 0),
        "candidateNotCreated": total_status_counts.get("candidate_not_created", 0),
        "heroCount": len(hero_summaries),
        "heroSummaries": sorted(hero_summaries, key=lambda row: row["heroName"]),
        "rows": sorted(rows, key=lambda row: (row["heroName"], row["created"] != "yes", row["abilityName"])),
    }


def classify_ability(hero_name: str, ability_catalog_name: str, ability_name: str, implemented_rule: Any | None) -> dict[str, Any]:
    if implemented_rule is not None:
        return {
            "decision": "implemented",
            "reason": "A versioned skillshot landing rule already exists for this ability.",
            "rule": _rule_summary(implemented_rule),
        }

    combined = f"{ability_catalog_name} {ability_name}"
    no_rule_term = _term_match(combined, LIKELY_NO_RULE_TERMS)
    if no_rule_term is not None:
        return {
            "decision": "no_rule_likely",
            "reason": "First-pass name triage matched a non-landing term: %s." % no_rule_term,
        }

    candidate_term = _term_match(combined, LIKELY_SKILLSHOT_TERMS)
    if candidate_term is not None:
        return {
            "decision": "needs_research",
            "reason": "First-pass name triage matched a likely skillshot term: %s." % candidate_term,
            "researchQueries": _research_queries(hero_name, ability_name),
        }

    return {
        "decision": "needs_triage",
        "reason": "No first-pass rule matched. A classifier or research agent should inspect the mechanics.",
        "researchQueries": _research_queries(hero_name, ability_name),
    }


def build_coverage(build: int = DEFAULT_ABILITY_BUILD) -> dict[str, Any]:
    hero_catalog_names = HERO_ABILITY_CATALOG_NAMES_BY_BUILD.get(build)
    if hero_catalog_names is None:
        raise SystemExit("Unsupported ability build: %s" % build)

    implemented_rules = _implemented_rules(build)
    heroes = []

    for hero_catalog_name in sorted(hero_catalog_names):
        definitions = sorted(
            get_hero_ability_definitions(hero_catalog_name, build),
            key=lambda definition: (definition.display_name, definition.catalog_name),
        )
        hero_name = definitions[0].hero_name if definitions else hero_catalog_name
        abilities = []
        for definition in definitions:
            classification = classify_ability(
                hero_name or hero_catalog_name,
                definition.catalog_name,
                definition.display_name,
                implemented_rules.get(definition.catalog_name),
            )
            abilities.append(
                {
                    "abilityCatalogName": definition.catalog_name,
                    "abilityName": definition.display_name,
                    "decision": classification["decision"],
                    "reason": classification["reason"],
                    **{key: value for key, value in classification.items() if key not in {"decision", "reason"}},
                }
            )

        decision_counts = Counter(ability["decision"] for ability in abilities)
        heroes.append(
            {
                "heroCatalogName": hero_catalog_name,
                "heroName": hero_name,
                "heroSlug": _slug(hero_name or hero_catalog_name),
                "abilityCount": len(abilities),
                "decisionCounts": dict(sorted(decision_counts.items())),
                "abilities": abilities,
            }
        )

    total_decisions = Counter()
    for hero in heroes:
        total_decisions.update(hero["decisionCounts"])

    return {
        "schemaVersion": SCRIPT_VERSION,
        "build": build,
        "heroCount": len(heroes),
        "abilityCount": sum(hero["abilityCount"] for hero in heroes),
        "decisionCounts": dict(sorted(total_decisions.items())),
        "heroes": heroes,
    }


def _find_hero(coverage: dict[str, Any], hero_query: str) -> dict[str, Any]:
    query = hero_query.lower()
    query_slug = _slug(hero_query)
    matches = [
        hero
        for hero in coverage["heroes"]
        if query
        in {
            str(hero["heroName"]).lower(),
            str(hero["heroCatalogName"]).lower(),
            str(hero["heroSlug"]).lower(),
        }
        or query_slug == hero["heroSlug"]
    ]
    if not matches:
        raise SystemExit("Hero not found in coverage for build %s: %s" % (coverage["build"], hero_query))
    if len(matches) > 1:
        raise SystemExit("Hero query is ambiguous: %s" % hero_query)
    return matches[0]


def build_work_packet(hero_query: str, build: int = DEFAULT_ABILITY_BUILD) -> dict[str, Any]:
    coverage = build_coverage(build)
    hero = _find_hero(coverage, hero_query)
    implemented = [ability for ability in hero["abilities"] if ability["decision"] == "implemented"]
    research_backlog = [
        ability
        for ability in hero["abilities"]
        if ability["decision"] in {"needs_research", "needs_triage"}
    ]
    no_rule_likely = [ability for ability in hero["abilities"] if ability["decision"] == "no_rule_likely"]
    hero_name = hero["heroName"]

    return {
        "schemaVersion": SCRIPT_VERSION,
        "build": build,
        "hero": {
            "heroCatalogName": hero["heroCatalogName"],
            "heroName": hero_name,
            "heroSlug": hero["heroSlug"],
        },
        "branchName": "codex/skillshot-%s" % hero["heroSlug"],
        "prTitle": "[skillshots] Add %s landing rules" % hero_name,
        "summary": {
            "abilityCount": hero["abilityCount"],
            "decisionCounts": hero["decisionCounts"],
            "implementedCount": len(implemented),
            "researchBacklogCount": len(research_backlog),
            "noRuleLikelyCount": len(no_rule_likely),
        },
        "implementedRules": implemented,
        "researchBacklog": research_backlog,
        "noRuleLikely": no_rule_likely,
        "agentWorkflow": [
            {
                "agent": "Coordinator",
                "task": "Create the branch, assign abilities, keep this packet current, and create one PR for the hero.",
            },
            {
                "agent": "Research",
                "task": "Browse current ability sources for each backlog ability and record mechanics, delays, radius, target type, and source URLs.",
            },
            {
                "agent": "Rule Designer",
                "task": "Choose detector type, evidence priority, confidence, gameloop windows, and docstring/evidence description.",
            },
            {
                "agent": "Implementer",
                "task": "Add versioned rules and detector support in data/replay modules without changing unrelated heroes.",
            },
            {
                "agent": "Validation",
                "task": "Parse at least two real replays for this hero and record generated skillshot stats in the PR body.",
            },
            {
                "agent": "Reviewer",
                "task": "Check plausibility, double counting, evidence strength, tests, and PR summary completeness.",
            },
        ],
        "validationCommands": [
            ".venv/bin/python -m pytest tests/test_skillshot_landing.py -q",
            ".venv/bin/python -m pytest",
            ".venv/bin/python -m ruff check .",
        ],
        "exampleStatsCommand": (
            ".venv/bin/python scripts/skillshot_rule_pipeline.py example-stats "
            "\"%s\" --replay-dir \"$HOTSDATA_REPLAY_CORPUS_DIR\" --limit 2"
        )
        % hero_name,
        "prBodyTemplate": _pr_body_template(hero_name, build),
    }


def _pr_body_template(hero_name: str, build: int) -> str:
    return "\n".join(
        [
            "## Summary",
            "",
            "- Hero: %s" % hero_name,
            "- Build: %s" % build,
            "- Implemented landing rules: TODO",
            "- Omitted abilities: TODO",
            "- Blocked abilities: TODO",
            "",
            "## Research",
            "",
            "- TODO: ability source URLs and mechanics notes",
            "",
            "## Example Replay Stats",
            "",
            "- TODO: paste output from `scripts/skillshot_rule_pipeline.py example-stats`",
            "",
            "## Validation",
            "",
            "- [ ] `.venv/bin/python -m pytest tests/test_skillshot_landing.py -q`",
            "- [ ] `.venv/bin/python -m pytest`",
            "- [ ] `.venv/bin/python -m ruff check .`",
        ]
    )


def _packet_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# %s Skillshot Work Packet" % packet["hero"]["heroName"],
        "",
        "Build: `%s`" % packet["build"],
        "Branch: `%s`" % packet["branchName"],
        "PR title: `%s`" % packet["prTitle"],
        "",
        "## Summary",
        "",
        "- Ability count: %s" % packet["summary"]["abilityCount"],
        "- Implemented rules: %s" % packet["summary"]["implementedCount"],
        "- Research backlog: %s" % packet["summary"]["researchBacklogCount"],
        "- No-rule likely: %s" % packet["summary"]["noRuleLikelyCount"],
        "",
        "## Implemented Rules",
        "",
    ]
    if packet["implementedRules"]:
        for ability in packet["implementedRules"]:
            rule = ability["rule"]
            lines.append("- `%s` / %s: `%s`, confidence `%s`" % (
                ability["abilityCatalogName"],
                ability["abilityName"],
                rule["detector"],
                rule["confidence"],
            ))
    else:
        lines.append("- None yet.")

    lines.extend(["", "## Research Backlog", ""])
    if packet["researchBacklog"]:
        for ability in packet["researchBacklog"]:
            lines.append("- `%s` / %s: %s" % (
                ability["abilityCatalogName"],
                ability["abilityName"],
                ability["decision"],
            ))
            for query in ability.get("researchQueries", [])[:2]:
                lines.append("  - Search: %s" % query)
    else:
        lines.append("- None.")

    lines.extend(["", "## Agent Workflow", ""])
    for step in packet["agentWorkflow"]:
        lines.append("- %s: %s" % (step["agent"], step["task"]))

    lines.extend(
        [
            "",
            "## Validation Commands",
            "",
            *(("- `%s`" % command) for command in packet["validationCommands"]),
            "",
            "## PR Body Template",
            "",
            packet["prBodyTemplate"],
            "",
        ]
    )
    return "\n".join(lines)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_candidate_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "heroName",
        "abilityName",
        "abilityCatalogName",
        "created",
        "status",
        "detectorFamily",
        "sourceDecision",
        "originalDecision",
        "wikiMatchedName",
        "wikiTarget",
        "wikiType",
        "wikiProps",
        "wikiSourceUrl",
        "reason",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _markdown_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def _candidate_table_markdown(candidate_table: dict[str, Any]) -> str:
    lines = [
        "# Skillshot Candidate Status Table",
        "",
        "Build: `%s`" % candidate_table["build"],
        "",
        "This table includes abilities that either already have a skillshot landing rule or were classified by wiki triage as implementable with an existing detector.",
        "",
        "## Summary",
        "",
        "- Heroes with candidate skills: `%s`" % candidate_table["heroCount"],
        "- Total candidate skills: `%s`" % candidate_table["totalCandidateSkills"],
        "- Created: `%s`" % candidate_table["created"],
        "- Candidate, not created: `%s`" % candidate_table["candidateNotCreated"],
        "",
        "## Hero Summary",
        "",
        "| Hero | Total | Created | Candidate Not Created | Detector Families |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for hero in candidate_table["heroSummaries"]:
        lines.append(
            "| %s | %s | %s | %s | %s |"
            % (
                _markdown_escape(hero["heroName"]),
                hero["totalCandidateSkills"],
                hero["created"],
                hero["candidateNotCreated"],
                _markdown_escape(hero["detectorFamilies"]),
            )
        )

    lines.extend(
        [
            "",
            "## Skill Status",
            "",
            "| Hero | Skill | Catalog Name | Created | Status | Detector | Wiki Target | Wiki Type | Wiki Props |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in candidate_table["rows"]:
        lines.append(
            "| %s | %s | `%s` | %s | `%s` | `%s` | %s | %s | %s |"
            % (
                _markdown_escape(row["heroName"]),
                _markdown_escape(row["abilityName"]),
                _markdown_escape(row["abilityCatalogName"]),
                row["created"],
                row["status"],
                _markdown_escape(row["detectorFamily"]),
                _markdown_escape(row["wikiTarget"]),
                _markdown_escape(row["wikiType"]),
                _markdown_escape(row["wikiProps"]),
            )
        )
    lines.append("")
    return "\n".join(lines)


def _write_candidate_markdown(path: Path, candidate_table: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_candidate_table_markdown(candidate_table), encoding="utf-8")


def _write_packet(packet: dict[str, Any], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = packet["hero"]["heroSlug"]
    json_path = out_dir / ("%s.json" % slug)
    markdown_path = out_dir / ("%s.md" % slug)
    _write_json(json_path, packet)
    markdown_path.write_text(_packet_markdown(packet), encoding="utf-8")
    return json_path, markdown_path


def _metadata_heroes(replay_path: Path, archive_class: Any, header_protocol: Any) -> tuple[int, list[str]]:
    archive = archive_class(str(replay_path))
    header = header_protocol.decode_replay_header(archive.header["user_data_header"]["content"])
    game_version = int(header["m_version"]["m_baseBuild"])
    protocol, _, _ = get_protocol_for_build(game_version)
    details = _normalize_protocol_value(protocol.decode_replay_details(archive.read_file("replay.details")))
    heroes = []
    for player in details["m_playerList"]:
        raw_hero = _to_text(player["m_hero"])
        heroes.append(HeroTranslator.get_base_hero_name(raw_hero) or raw_hero)
    return game_version, heroes


def _example_stats(
    hero_query: str,
    replay_dir: Path,
    build: int,
    limit: int,
    randomize: bool,
    seed: int | None,
    max_scan: int | None,
) -> dict[str, Any]:
    archive_class = get_mpyq_archive_class()
    header_protocol = get_header_protocol()
    files = sorted(replay_dir.glob("*.StormReplay"))
    if randomize:
        rng = random.Random(seed) if seed is not None else random.SystemRandom()
        rng.shuffle(files)
    if max_scan is not None:
        files = files[:max_scan]

    target = hero_query.lower()
    reports = []
    failures = []
    metadata_matches = 0
    for replay_path in files:
        try:
            game_version, heroes = _metadata_heroes(replay_path, archive_class, header_protocol)
        except Exception as exc:
            failures.append({"file": str(replay_path), "errorType": type(exc).__name__, "error": str(exc)})
            continue
        if game_version != build or not any(hero.lower() == target for hero in heroes):
            continue
        metadata_matches += 1

        parser_output = io.StringIO()
        try:
            with contextlib.redirect_stdout(parser_output):
                replay_data = processEvents(get_header_protocol(), archive_class(str(replay_path)))
        except Exception as exc:
            failures.append({"file": str(replay_path), "errorType": type(exc).__name__, "error": str(exc)})
            continue

        hero = next((candidate for candidate in replay_data.heroList.values() if candidate.name.lower() == target), None)
        if hero is None:
            failures.append({"file": str(replay_path), "errorType": "MissingHero", "error": "Hero absent after parse"})
            continue
        stats = hero.generalStats.get("skillshotStats", {})
        if not stats:
            failures.append({"file": str(replay_path), "errorType": "NoSkillshotStats", "error": "No stats for hero"})
            continue

        teams = {}
        for team in sorted({candidate.team for candidate in replay_data.heroList.values()}):
            teams[str(team)] = [
                candidate.name
                for candidate in sorted(replay_data.heroList.values(), key=lambda item: item.playerId or -1)
                if candidate.team == team
            ]
        reports.append(
            {
                "file": replay_path.name,
                "path": str(replay_path),
                "map": replay_data.replayInfo.mapName,
                "startTimeUTC": replay_data.replayInfo.startTime,
                "durationSeconds": replay_data.replayInfo.duration_in_secs(),
                "gameVersion": replay_data.replayInfo.gameVersion,
                "protocolBuild": replay_data.replayInfo.protocolBuild,
                "protocolFallback": replay_data.replayInfo.protocolFallback,
                "heroTeam": hero.team,
                "heroesByTeam": teams,
                "skillshotStats": stats,
            }
        )
        if len(reports) >= limit:
            break

    return {
        "hero": hero_query,
        "build": build,
        "replayDir": str(replay_dir),
        "totalReplayFiles": len(files),
        "metadataMatches": metadata_matches,
        "reports": reports,
        "failures": failures[:20],
    }


def _print_coverage_summary(coverage: dict[str, Any]) -> None:
    print("Skillshot coverage build %s" % coverage["build"])
    print("Heroes: %d" % coverage["heroCount"])
    print("Abilities: %d" % coverage["abilityCount"])
    print("Decisions:")
    for decision, count in coverage["decisionCounts"].items():
        print("  %s: %d" % (decision, count))


def _print_wiki_triage_summary(triage: dict[str, Any]) -> None:
    print("Wiki skillshot triage build %s" % triage["build"])
    print("Heroes: %d" % triage["heroCount"])
    print("Abilities: %d" % triage["abilityCount"])
    print("Wiki matches:")
    for status, count in triage["matchCounts"].items():
        print("  %s: %d" % (status, count))
    print("Decisions:")
    for decision, count in triage["decisionCounts"].items():
        print("  %s: %d" % (decision, count))
    print("Original needs_triage after wiki pass:")
    for decision, count in triage["originalNeedsTriageDecisionCounts"].items():
        print("  %s: %d" % (decision, count))
    if triage["sourceFailures"]:
        print("Source failures: %d" % len(triage["sourceFailures"]))


def _print_candidate_table_summary(candidate_table: dict[str, Any]) -> None:
    print("Skillshot candidate status build %s" % candidate_table["build"])
    print("Heroes with candidates: %d" % candidate_table["heroCount"])
    print("Total candidate skills: %d" % candidate_table["totalCandidateSkills"])
    print("Created: %d" % candidate_table["created"])
    print("Candidate, not created: %d" % candidate_table["candidateNotCreated"])


def _print_example_stats(report: dict[str, Any]) -> None:
    print("Example skillshot stats for %s, build %s" % (report["hero"], report["build"]))
    print("Replay files scanned: %d" % report["totalReplayFiles"])
    print("Metadata matches: %d" % report["metadataMatches"])
    for replay in report["reports"]:
        print("\n%s" % replay["file"])
        print("  Map: %s" % replay["map"])
        print("  Duration: %ds" % replay["durationSeconds"])
        print("  Hero team: %s" % replay["heroTeam"])
        for ability_name, stats in replay["skillshotStats"].items():
            hit_rate = stats["hitRate"]
            percent = "n/a" if hit_rate is None else "%.2f%%" % (hit_rate * 100)
            print(
                "  %s: attempts=%s landed=%s missed=%s hitRate=%s evidence=%s"
                % (
                    stats["abilityName"],
                    stats["totalAttempts"],
                    stats["landed"],
                    stats["missed"],
                    percent,
                    stats["landedByEvidence"],
                )
            )
            if "totalTargetsHit" in stats:
                print("    totalTargetsHit=%s averageTargetsHit=%s" % (
                    stats["totalTargetsHit"],
                    stats["averageTargetsHit"],
                ))
    if report["failures"]:
        print("\nFailures retained: %d" % len(report["failures"]))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coordinate skillshot landing-rule coverage work.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    coverage_parser = subparsers.add_parser("coverage", help="build skillshot rule coverage JSON")
    coverage_parser.add_argument("--build", type=int, default=DEFAULT_ABILITY_BUILD)
    coverage_parser.add_argument("--out", type=Path, default=None)
    coverage_parser.add_argument("--json", action="store_true", help="print full JSON instead of a text summary")

    packet_parser = subparsers.add_parser("packet", help="build a hero work packet")
    packet_parser.add_argument("hero")
    packet_parser.add_argument("--build", type=int, default=DEFAULT_ABILITY_BUILD)
    packet_parser.add_argument("--out-dir", type=Path, default=Path("docs/skillshot_rules/work_packets"))
    packet_parser.add_argument("--json", action="store_true", help="print full packet JSON")

    wiki_parser = subparsers.add_parser("wiki-triage", help="classify coverage rows using current wiki ability data")
    wiki_parser.add_argument("--build", type=int, default=DEFAULT_ABILITY_BUILD)
    wiki_parser.add_argument("--out", type=Path, default=None)
    wiki_parser.add_argument(
        "--source-cache",
        type=Path,
        default=Path("docs/skillshot_rules/wiki_ability_sources_97039.json"),
        help="read/write parsed wiki ability data",
    )
    wiki_parser.add_argument("--refresh", action="store_true", help="download fresh wiki data instead of reusing cache")
    wiki_parser.add_argument("--json", action="store_true", help="print full triage JSON")

    candidate_table_parser = subparsers.add_parser(
        "candidate-table",
        help="build a skillshot candidate status table from wiki triage",
    )
    candidate_table_parser.add_argument(
        "--wiki-triage",
        type=Path,
        default=Path("docs/skillshot_rules/wiki_triage_97039.json"),
    )
    candidate_table_parser.add_argument(
        "--csv-out",
        type=Path,
        default=Path("docs/skillshot_rules/skillshot_candidate_status_97039.csv"),
    )
    candidate_table_parser.add_argument(
        "--markdown-out",
        type=Path,
        default=Path("docs/skillshot_rules/skillshot_candidate_status_97039.md"),
    )
    candidate_table_parser.add_argument("--json", action="store_true", help="print full table JSON")

    stats_parser = subparsers.add_parser("example-stats", help="sample current skillshot stats from real replays")
    stats_parser.add_argument("hero")
    stats_parser.add_argument("--build", type=int, default=DEFAULT_ABILITY_BUILD)
    stats_parser.add_argument("--replay-dir", type=Path, required=True)
    stats_parser.add_argument("--limit", type=int, default=2)
    stats_parser.add_argument("--max-scan", type=int, default=None)
    stats_parser.add_argument("--random", action="store_true", help="shuffle replay order before scanning")
    stats_parser.add_argument("--seed", type=int, default=None)
    stats_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "coverage":
        coverage = build_coverage(args.build)
        if args.out is not None:
            _write_json(args.out, coverage)
        if args.json:
            print(json.dumps(coverage, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            _print_coverage_summary(coverage)
        return 0

    if args.command == "packet":
        packet = build_work_packet(args.hero, args.build)
        json_path, markdown_path = _write_packet(packet, args.out_dir)
        if args.json:
            print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print("Wrote %s" % json_path)
            print("Wrote %s" % markdown_path)
        return 0

    if args.command == "wiki-triage":
        coverage = build_coverage(args.build)
        if args.refresh or not args.source_cache.exists():
            hero_names = [hero["heroName"] for hero in coverage["heroes"]]
            wiki_sources = fetch_wiki_hero_sources(hero_names)
            _write_json(args.source_cache, wiki_sources)
        else:
            wiki_sources = json.loads(args.source_cache.read_text(encoding="utf-8"))
        triage = build_wiki_triage(coverage, wiki_sources)
        if args.out is not None:
            _write_json(args.out, triage)
        if args.json:
            print(json.dumps(triage, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            _print_wiki_triage_summary(triage)
        return 0

    if args.command == "candidate-table":
        if not args.wiki_triage.exists():
            raise SystemExit("Wiki triage file not found: %s" % args.wiki_triage)
        triage = json.loads(args.wiki_triage.read_text(encoding="utf-8"))
        candidate_table = build_candidate_status_table(triage)
        _write_candidate_csv(args.csv_out, candidate_table["rows"])
        _write_candidate_markdown(args.markdown_out, candidate_table)
        if args.json:
            print(json.dumps(candidate_table, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            _print_candidate_table_summary(candidate_table)
            print("Wrote %s" % args.csv_out)
            print("Wrote %s" % args.markdown_out)
        return 0

    if args.command == "example-stats":
        if not args.replay_dir.exists():
            raise SystemExit("Replay directory not found: %s" % args.replay_dir)
        report = _example_stats(
            args.hero,
            args.replay_dir,
            args.build,
            args.limit,
            args.random,
            args.seed,
            args.max_scan,
        )
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            _print_example_stats(report)
        return 0

    raise SystemExit("Unknown command: %s" % args.command)


if __name__ == "__main__":
    raise SystemExit(main())
