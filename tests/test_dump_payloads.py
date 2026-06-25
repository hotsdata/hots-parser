import json

import main


def test_dump_payloads_writes_standard_json_files(tmp_path, monkeypatch):
    payloads = {
        "teamgeneralstats": [{"team": 0, "level": 20}],
        "teammapstats": [{"team": 0, "map": "Silver City"}],
    }
    monkeypatch.setattr(main, "build_payloads", lambda data, replay_path=None: payloads)

    main.dump_payloads(data=object(), output_path=tmp_path, replay_path="replay.StormReplay")

    assert json.loads((tmp_path / "teamgeneralstats.json").read_text()) == payloads["teamgeneralstats"]
    assert json.loads((tmp_path / "teammapstats.json").read_text()) == payloads["teammapstats"]
