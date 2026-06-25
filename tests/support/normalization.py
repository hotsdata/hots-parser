import json
from pathlib import Path

from hotsparser import processEvents
from protocol_loader import get_header_protocol, get_mpyq_archive_class
from utils.payloads import build_payloads


IDENTITY_FIELDS = ("name", "battleTag", "toonHandle")


def parse_replay_payloads(replay_path):
    MPQArchive = get_mpyq_archive_class()
    replay = MPQArchive(str(replay_path))
    replay_data = processEvents(get_header_protocol(), replay)
    return build_payloads(replay_data)


def write_payloads(payloads, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in sorted(payloads.items()):
        with (output_dir / f"{name}.json").open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")


def load_payloads(input_dir):
    input_dir = Path(input_dir)
    payloads = {}
    for path in sorted(input_dir.glob("*.json")):
        with path.open(encoding="utf-8") as handle:
            payloads[path.stem] = json.load(handle)
    return payloads


def redact_player_identities(payloads):
    replacements = {}
    players = sorted(payloads.get("players", []), key=lambda player: player.get("playerId", 0))

    for index, player in enumerate(players):
        redacted = {
            "name": "Player %d" % index,
            "battleTag": "Player%d#0000" % index,
            "toonHandle": "toon-handle-%d" % index,
        }
        for field, value in redacted.items():
            original = player.get(field)
            if original:
                replacements[original] = value

    return _replace_strings(payloads, replacements)


def _replace_strings(value, replacements):
    if isinstance(value, dict):
        return {key: _replace_strings(item, replacements) for key, item in value.items()}
    if isinstance(value, list):
        return [_replace_strings(item, replacements) for item in value]
    if isinstance(value, str):
        return replacements.get(value, value)
    return value
