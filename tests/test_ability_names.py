from pathlib import Path

from data.abilities import SUPPORTED_ABILITY_BUILDS, get_ability_definition
from protocol_loader import get_header_protocol, get_mpyq_archive_class, get_protocol_for_build


REPLAY = Path(__file__).parent / "fixtures" / "replays" / "ci" / "silver_city_2026-06-24.StormReplay"


def test_ci_replay_ability_links_have_display_names():
    MPQArchive = get_mpyq_archive_class()
    replay = MPQArchive(str(REPLAY))
    header = get_header_protocol().decode_replay_header(replay.header["user_data_header"]["content"])
    game_version = header["m_version"]["m_baseBuild"]
    protocol, _, _ = get_protocol_for_build(game_version)

    assert game_version in SUPPORTED_ABILITY_BUILDS
    missing = set()
    for event in protocol.decode_replay_game_events(replay.read_file("replay.game.events")):
        if event["_event"] != "NNet.Game.SCmdEvent" or not event.get("m_abil"):
            continue
        ability_link = event["m_abil"]["m_abilLink"]
        ability_cmd_index = event["m_abil"]["m_abilCmdIndex"]
        if get_ability_definition(ability_link, ability_cmd_index, game_version) is None:
            missing.add((ability_link, ability_cmd_index))

    assert missing == set()
