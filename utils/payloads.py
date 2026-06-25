"""Plain-dictionary parser outputs shared by tests and persistence."""

from __future__ import annotations

import copy
from collections import OrderedDict

from data import OTHERKILLERS


def to_plain(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (list, tuple, set)):
        return [to_plain(item) for item in value]
    if isinstance(value, (dict, OrderedDict)):
        return {str(to_plain(key)): to_plain(item) for key, item in value.items()}
    if hasattr(value, "__dict__"):
        return to_plain(vars(value))
    return str(value)


def _team_number(team):
    return 0 if team.generalStats.get("teamId") == "Blue" else 1


def _death_rows(replay_data, hero):
    rows = []
    for death in hero.generalStats["deaths"]:
        killers = [
            replay_data.heroList[killer - 1].name if killer - 1 in replay_data.heroList else OTHERKILLERS[killer - 1]
            for killer in death["killers"]
            if killer > 0
        ]
        rows.append(
            {
                "seconds": death["seconds"],
                "soloDeath": death["soloDeath"],
                "x": death["x"],
                "y": death["y"],
                "killers": killers,
                "victim": hero.name,
                "team": hero.team,
            }
        )
    return rows


def replay_info_payload(replay_data, replay_path=None):
    replay_id = replay_data.get_replay_id()
    replay = replay_data.replayInfo
    return to_plain(
        {
            "startTime": replay.startTime,
            "gameLoops": replay.gameLoops,
            "speed": replay.speed,
            "gameType": replay.gameType,
            "gameVersion": replay.gameVersion,
            "protocolBuild": getattr(replay, "protocolBuild", None),
            "protocolFallback": getattr(replay, "protocolFallback", False),
            "mapSize": replay.mapSize,
            "mapName": replay.mapName,
            "id": replay_id,
            "replayPath": replay_path,
            "team1": replay_data.team1,
            "team2": replay_data.team2,
            "event": replay_data.event,
            "stage": replay_data.stage,
        }
    )


def deathlist_payload(replay_data):
    deaths = {}
    for hero_key in replay_data.heroList:
        hero = replay_data.heroList[hero_key]
        for row in _death_rows(replay_data, hero):
            deaths.setdefault("team%s" % hero.team, []).append(row)
    return to_plain({"deaths": deaths, "mapName": replay_data.replayInfo.mapName})


def armystr_payload(replay_data):
    replay_id = replay_data.get_replay_id()
    row = {"id": replay_id, "team0": None, "team1": None, "start": None}
    for team in replay_data.teams:
        army_strength = []
        team_id = _team_number(team)
        keys = sorted(team.generalStats["army_strength"])
        if keys:
            row["start"] = keys[0] if row["start"] is None else min(row["start"], keys[0])
            for key in keys:
                army_strength.append(team.generalStats["army_strength"][key])
            row["team%s" % team_id] = army_strength
    return to_plain(row)


def team_general_stats_payloads(replay_data):
    replay_id = replay_data.get_replay_id()
    rows = []
    for team in replay_data.teams:
        stats = copy.deepcopy(team.generalStats)
        team_number = _team_number(team)
        stats["replayId"] = replay_id
        stats["team"] = team_number
        stats["id"] = "%s-%s" % (replay_id, stats.get("teamId"))
        stats["army_strength"] = ""
        stats["merc_strength"] = ""
        rows.append(to_plain(stats))
    return rows


def team_map_stats_payloads(replay_data):
    replay_id = replay_data.get_replay_id()
    rows = []
    for team in replay_data.teams:
        if not team.mapStats:
            continue
        stats = copy.deepcopy(team.mapStats)
        team_number = _team_number(team)
        stats["team"] = team_number
        stats["id"] = "%s-%s" % (replay_id, team.generalStats.get("teamId"))
        rows.append(to_plain(stats))
    return rows


def timeline_payload(replay_data):
    return to_plain({"id": replay_data.get_replay_id(), "tl": replay_data.timeLine})


def hero_general_stats_payloads(replay_data):
    replay_id = replay_data.get_replay_id()
    rows = []
    for hero_key in replay_data.heroList:
        hero = replay_data.heroList[hero_key]
        stats = copy.deepcopy(hero.generalStats)
        stats["castedAbilities"] = ""
        stats["deaths"] = _death_rows(replay_data, hero)
        stats["team"] = hero.team
        stats["playerId"] = hero.playerId
        stats["replayId"] = replay_id
        stats["levelEvents"] = ""
        stats["heroName"] = hero.name
        stats["id"] = "%s-%s-%s" % (replay_id, hero.team, hero.name)
        rows.append(to_plain(stats))
    return rows


def hero_map_stats_payloads(replay_data):
    replay_id = replay_data.get_replay_id()
    rows = []
    for hero_key in replay_data.heroList:
        hero = replay_data.heroList[hero_key]
        if not hero.mapStats:
            continue
        stats = copy.deepcopy(hero.mapStats)
        stats["team"] = hero.team
        stats["playerId"] = hero.playerId
        stats["replayId"] = replay_id
        stats["heroName"] = hero.name
        stats["id"] = "%s-%s-%s" % (replay_id, hero.team, hero.name)
        rows.append(to_plain(stats))
    return rows


def players_payloads(replay_data):
    replay_id = replay_data.get_replay_id()
    rows = []
    for player_key in replay_data.players:
        player = replay_data.players[player_key]
        rows.append(
            to_plain(
                {
                    "playerId": player.playerId,
                    "heroLevel": int(player.heroLevel),
                    "slotId": player.id,
                    "team": player.team,
                    "hero": player.hero,
                    "name": player.name,
                    "isHuman": player.isHuman,
                    "gameResult": player.gameResult,
                    "toonHandle": player.toonHandle,
                    "realm": player.realm,
                    "region": player.region,
                    "rank": player.rank,
                    "battleTag": player.battleTag or -1,
                    "id": "%s-%s-%s" % (replay_id, player.team, player.hero),
                }
            )
        )
    return rows


def battletag_lookup_payloads(replay_data):
    rows = []
    regions = {"98": "PTR", "1": "NA", "2": "EU", "3": "KR", "5": "CN"}
    for player_key in replay_data.players:
        player = replay_data.players[player_key]
        region_code = player.toonHandle.split("-")[0]
        rows.append(
            to_plain(
                {
                    "battleTag": player.battleTag,
                    "toonHandle": player.toonHandle,
                    "region": regions.get(region_code),
                }
            )
        )
    return rows


def build_payloads(replay_data, replay_path=None):
    return {
        "replayinfo": replay_info_payload(replay_data, replay_path),
        "deathlist": deathlist_payload(replay_data),
        "armystr": armystr_payload(replay_data),
        "teamgeneralstats": team_general_stats_payloads(replay_data),
        "teammapstats": team_map_stats_payloads(replay_data),
        "timeline": timeline_payload(replay_data),
        "generalstats": hero_general_stats_payloads(replay_data),
        "mapstats": hero_map_stats_payloads(replay_data),
        "players": players_payloads(replay_data),
        "battletag_toonhandle_lookup": battletag_lookup_payloads(replay_data),
    }
