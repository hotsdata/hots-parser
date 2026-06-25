#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import HeroTranslator
from data.abilities import get_ability_definition, get_hero_ability_definitions
from helpers import get_ability_cmd_index, get_ability_link, get_ability_tag
from protocol_loader import get_header_protocol, get_mpyq_archive_class, get_protocol_for_build


ReplayEvent = dict[str, Any]
HeroByUserId = dict[int, dict[str, str | int | None]]


def _to_text(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return "" if value is None else str(value)


def _toon_handle(toon: dict[str, Any]) -> str:
    return "-".join(
        [
            str(toon["m_region"]),
            _to_text(toon["m_programId"]),
            str(toon["m_realm"]),
            str(toon["m_id"]),
        ]
    )


def _replay_files(corpus_dir: Path, recursive: bool, limit: int | None) -> list[Path]:
    pattern = "**/*.StormReplay" if recursive else "*.StormReplay"
    files = sorted(corpus_dir.glob(pattern))
    if limit is not None:
        return files[:limit]
    return files


def _hero_catalog_name(hero_name: str | None, game_version: int) -> str | None:
    if hero_name is None:
        return None
    for definition in get_hero_ability_definitions(hero_name, game_version):
        return definition.hero_catalog_name
    return None


def _hero_candidate_abilities(hero_catalog_name: str | None, game_version: int) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "catalogName": definition.catalog_name,
            "displayName": definition.display_name,
        }
        for definition in get_hero_ability_definitions(hero_catalog_name, game_version)
    )


def _hero_by_user_id(details: dict[str, Any], init_data: dict[str, Any], game_version: int) -> HeroByUserId:
    players_by_working_set: dict[int, dict[str, str | int | None]] = {}
    players_by_toon: dict[str, dict[str, str | int | None]] = {}

    for index, player in enumerate(details["m_playerList"]):
        raw_hero = _to_text(player["m_hero"])
        hero_name = HeroTranslator.get_base_hero_name(raw_hero) or raw_hero
        hero = {
            "playerIndex": index,
            "workingSetSlotId": player.get("m_workingSetSlotId"),
            "heroName": hero_name,
            "heroCatalogName": _hero_catalog_name(hero_name, game_version),
            "rawHeroName": raw_hero,
        }
        working_set_slot_id = player.get("m_workingSetSlotId")
        if working_set_slot_id is not None:
            players_by_working_set[int(working_set_slot_id)] = hero
        players_by_toon[_toon_handle(player["m_toon"])] = hero

    heroes_by_user_id: HeroByUserId = {}
    slots = init_data["m_syncLobbyState"]["m_lobbyState"]["m_slots"]
    for slot in slots:
        user_id = slot.get("m_userId")
        if user_id is None:
            continue
        toon_handle = _to_text(slot.get("m_toonHandle"))
        hero = players_by_toon.get(toon_handle)
        if hero is None and slot.get("m_workingSetSlotId") is not None:
            hero = players_by_working_set.get(int(slot["m_workingSetSlotId"]))
        if hero is not None:
            heroes_by_user_id[int(user_id)] = hero

    for working_set_slot_id, hero in players_by_working_set.items():
        heroes_by_user_id.setdefault(working_set_slot_id, hero)
    return heroes_by_user_id


def _target_type(event: ReplayEvent) -> str:
    data = event.get("m_data") or {}
    if not isinstance(data, dict):
        return type(data).__name__
    for key, value in data.items():
        if value is not None:
            return key
    return "None"


def _parse_replay(replay_path: Path) -> tuple[int, list[dict[str, Any]]]:
    archive = get_mpyq_archive_class()(str(replay_path))
    header = get_header_protocol().decode_replay_header(archive.header["user_data_header"]["content"])
    game_version = int(header["m_version"]["m_baseBuild"])
    protocol, _, _ = get_protocol_for_build(game_version)
    details = protocol.decode_replay_details(archive.read_file("replay.details"))
    init_data = protocol.decode_replay_initdata(archive.read_file("replay.initData"))
    heroes_by_user_id = _hero_by_user_id(details, init_data, game_version)

    rows = []
    for event in protocol.decode_replay_game_events(archive.read_file("replay.game.events")):
        if event["_event"] != "NNet.Game.SCmdEvent" or not event.get("m_abil"):
            continue
        ability_link = get_ability_link(event)
        ability_cmd_index = get_ability_cmd_index(event)
        if ability_link is None or ability_cmd_index is None:
            continue
        user_id = int(event["_userid"]["m_userId"])
        hero = heroes_by_user_id.get(user_id, {})
        definition = get_ability_definition(ability_link, ability_cmd_index, game_version)
        rows.append(
            {
                "gameVersion": game_version,
                "heroName": hero.get("heroName"),
                "heroCatalogName": hero.get("heroCatalogName"),
                "rawHeroName": hero.get("rawHeroName"),
                "playerIndex": hero.get("playerIndex"),
                "userId": user_id,
                "abilityLink": ability_link,
                "abilityCmdIndex": ability_cmd_index,
                "abilityTag": get_ability_tag(event),
                "targetType": _target_type(event),
                "gameloop": int(event["_gameloop"]),
                "abilityCatalogName": definition.catalog_name if definition else None,
                "abilityName": definition.display_name if definition else None,
                "replay": str(replay_path),
            }
        )
    return game_version, rows


def _record_example(examples: list[dict[str, Any]], row: dict[str, Any], max_examples: int) -> None:
    if len(examples) >= max_examples:
        return
    examples.append(
        {
            "replay": row["replay"],
            "gameloop": row["gameloop"],
            "userId": row["userId"],
            "targetType": row["targetType"],
        }
    )


def _build_report(
    files: list[Path],
    progress_every: int | None,
    max_examples: int,
    include_candidates: bool,
) -> dict[str, Any]:
    observations: dict[tuple[int, str | None, int, int], dict[str, Any]] = {}
    replays_by_observation: defaultdict[tuple[int, str | None, int, int], set[str]] = defaultdict(set)
    failures = []
    replay_builds: Counter[str] = Counter()

    for index, replay_path in enumerate(files, start=1):
        if progress_every and (index == 1 or index % progress_every == 0):
            print(f"Parsing {index}/{len(files)}: {replay_path.name}", file=sys.stderr, flush=True)

        parser_output = io.StringIO()
        try:
            with contextlib.redirect_stdout(parser_output):
                game_version, rows = _parse_replay(replay_path)
            replay_builds[str(game_version)] += 1
        except Exception as exc:
            failures.append(
                {
                    "file": str(replay_path),
                    "size": replay_path.stat().st_size,
                    "errorType": type(exc).__name__,
                    "error": str(exc) or parser_output.getvalue().strip(),
                }
            )
            continue

        for row in rows:
            key = (row["gameVersion"], row["heroName"], row["abilityLink"], row["abilityCmdIndex"])
            if key not in observations:
                observation = {
                    "gameVersion": row["gameVersion"],
                    "heroName": row["heroName"],
                    "heroCatalogName": row["heroCatalogName"],
                    "rawHeroName": row["rawHeroName"],
                    "abilityLink": row["abilityLink"],
                    "abilityCmdIndex": row["abilityCmdIndex"],
                    "abilityTag": row["abilityTag"],
                    "abilityCatalogName": row["abilityCatalogName"],
                    "abilityName": row["abilityName"],
                    "count": 0,
                    "replayCount": 0,
                    "targetTypes": Counter(),
                    "examples": [],
                }
                if include_candidates and row["abilityCatalogName"] is None:
                    observation["candidateAbilities"] = _hero_candidate_abilities(
                        row["heroCatalogName"], row["gameVersion"]
                    )
                observations[key] = observation

            observation = observations[key]
            observation["count"] += 1
            observation["targetTypes"][row["targetType"]] += 1
            replays_by_observation[key].add(row["replay"])
            _record_example(observation["examples"], row, max_examples)

    for key, observation in observations.items():
        observation["replayCount"] = len(replays_by_observation[key])
        observation["targetTypes"] = dict(sorted(observation["targetTypes"].items()))

    ordered_observations = sorted(
        observations.values(),
        key=lambda item: (
            item["gameVersion"],
            item["heroName"] or "",
            item["abilityLink"],
            item["abilityCmdIndex"],
        ),
    )
    heroes = Counter(
        f"{item['gameVersion']}:{item['heroName']}" for item in ordered_observations if item["heroName"] is not None
    )
    unmapped = [item for item in ordered_observations if item["abilityCatalogName"] is None]

    return {
        "total": len(files),
        "passed": sum(replay_builds.values()),
        "failed": len(failures),
        "builds": dict(sorted(replay_builds.items())),
        "heroes": dict(sorted(heroes.items())),
        "uniqueObservations": len(ordered_observations),
        "unmappedObservations": len(unmapped),
        "observations": ordered_observations,
        "failures": failures,
    }


def _print_text_report(report: dict[str, Any], max_unmapped: int) -> None:
    print(
        "Replay ability corpus: %d total, %d parsed, %d failed"
        % (report["total"], report["passed"], report["failed"])
    )
    print("Unique observed hero/link/cmd rows: %d" % report["uniqueObservations"])
    print("Unmapped observed rows: %d" % report["unmappedObservations"])

    print("\nBuilds:")
    for build, count in report["builds"].items():
        print("  %s: %d" % (build, count))

    print("\nHeroes:")
    for hero, count in report["heroes"].items():
        print("  %s: %d" % (hero, count))

    unmapped = [row for row in report["observations"] if row["abilityCatalogName"] is None]
    if unmapped:
        print("\nUnmapped observations:")
        for row in unmapped[:max_unmapped]:
            print(
                "  build=%s hero=%s link=%s cmd=%s tag=%s count=%s targets=%s"
                % (
                    row["gameVersion"],
                    row["heroName"],
                    row["abilityLink"],
                    row["abilityCmdIndex"],
                    row["abilityTag"],
                    row["count"],
                    row["targetTypes"],
                )
            )
        if len(unmapped) > max_unmapped:
            print("  ... %d more omitted" % (len(unmapped) - max_unmapped))

    if report["failures"]:
        print("\nFailures:")
        for row in report["failures"][:20]:
            print("  %s: %s: %s" % (row["file"], row["errorType"], row["error"]))
        if len(report["failures"]) > 20:
            print("  ... %d more failures omitted" % (len(report["failures"]) - 20))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus_dir", type=Path)
    parser.add_argument("--non-recursive", action="store_true", help="only read replay files directly in corpus_dir")
    parser.add_argument("--limit", type=int, default=None, help="only parse the first N replay files by filename")
    parser.add_argument("--progress-every", type=int, default=None, help="print progress to stderr every N files")
    parser.add_argument("--max-examples", type=int, default=3, help="examples to retain per observed ability row")
    parser.add_argument("--max-unmapped", type=int, default=50, help="unmapped rows to print in text mode")
    parser.add_argument("--include-candidates", action="store_true", help="include current hero catalog candidates in JSON")
    parser.add_argument("--json", action="store_true", help="print full report JSON")
    parser.add_argument("--out", type=Path, default=None, help="write full report JSON to this path")
    parser.add_argument("--fail-on-error", action="store_true", help="exit non-zero if any replay fails to parse")
    args = parser.parse_args(argv)

    if not args.corpus_dir.exists():
        raise SystemExit("Replay corpus directory not found: %s" % args.corpus_dir)

    files = _replay_files(args.corpus_dir, recursive=not args.non_recursive, limit=args.limit)
    report = _build_report(
        files,
        progress_every=args.progress_every,
        max_examples=args.max_examples,
        include_candidates=args.include_candidates,
    )

    if args.out:
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        _print_text_report(report, args.max_unmapped)

    if args.fail_on_error and report["failed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
