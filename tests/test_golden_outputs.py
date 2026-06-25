from pathlib import Path

import pytest

from tests.support.normalization import load_payloads, parse_replay_payloads


REPLAY = Path("tests/fixtures/replays/local/2026-06-24_15-49-48_Silver_City.StormReplay")
GOLDEN = Path("tests/golden/local/silver_city_2026-06-24")


@pytest.mark.skipif(not REPLAY.exists(), reason="local golden replay fixture is not present")
@pytest.mark.skipif(not GOLDEN.exists(), reason="local golden output has not been generated")
def test_silver_city_golden_outputs():
    expected = load_payloads(GOLDEN)
    actual = parse_replay_payloads(REPLAY)

    assert actual == expected
