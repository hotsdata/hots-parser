from pathlib import Path

from tests.support.normalization import load_payloads, parse_replay_payloads, redact_player_identities


REPLAY = Path("tests/fixtures/replays/ci/silver_city_2026-06-24.StormReplay")
GOLDEN = Path("tests/golden/ci/silver_city_2026-06-24")


def test_ci_silver_city_golden_outputs():
    expected = load_payloads(GOLDEN)
    actual = redact_player_identities(parse_replay_payloads(REPLAY))

    assert actual == expected
