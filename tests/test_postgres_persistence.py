import os
from pathlib import Path

import psycopg
import pytest

from hotsparser import processEvents
from protocol_loader import get_header_protocol, get_mpyq_archive_class
from utils import pg_persistence
from utils.payloads import build_payloads


REPLAY = Path("tests/fixtures/replays/local/2026-06-24_15-49-48_Silver_City.StormReplay")


def _database_url():
    return os.environ.get("HOTSDATA_DATABASE_URL") or os.environ.get("DATABASE_URL")


def _parse_replay():
    MPQArchive = get_mpyq_archive_class()
    replay = MPQArchive(str(REPLAY))
    return processEvents(get_header_protocol(), replay)


def _cleanup(conn, replay_id, battletag_rows):
    with conn.cursor() as cursor:
        for table in (
            "deathlist",
            "armystr",
            "teamgeneralstats",
            "teammapstats",
            "timeline",
            "generalstats",
            "mapstats",
            "players",
            "replayinfo",
        ):
            cursor.execute("DELETE FROM %s WHERE replayid = %%s" % table, [replay_id])

        for row in battletag_rows:
            cursor.execute(
                "DELETE FROM battletag_toonhandle_lookup WHERE battletag = %s AND toonhandle = %s",
                [row["battleTag"], row["toonHandle"]],
            )
            cursor.execute(
                "DELETE FROM battletag_toonhandle_current WHERE battletag = %s AND toonhandle = %s",
                [row["battleTag"], row["toonHandle"]],
            )
    conn.commit()


@pytest.mark.skipif(not _database_url(), reason="HOTSDATA_DATABASE_URL or DATABASE_URL is not set")
@pytest.mark.skipif(not REPLAY.exists(), reason="local replay fixture is not present")
def test_save_data_writes_fixture_payloads_to_postgres(monkeypatch):
    database_url = _database_url()
    monkeypatch.setenv("HOTSDATA_DATABASE_URL", database_url)

    replay_data = _parse_replay()
    payloads = build_payloads(replay_data, replay_path=str(REPLAY))
    replay_id = payloads["replayinfo"]["id"]
    battletag_rows = payloads["battletag_toonhandle_lookup"]

    with psycopg.connect(database_url) as conn:
        _cleanup(conn, replay_id, battletag_rows)
        try:
            pg_persistence.save_data(replay_data, str(REPLAY))

            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM replayinfo WHERE replayid = %s", [replay_id])
                assert cursor.fetchone()[0] == 1

                cursor.execute("SELECT COUNT(*) FROM teamgeneralstats WHERE replayid = %s", [replay_id])
                assert cursor.fetchone()[0] == 2

                cursor.execute("SELECT COUNT(*) FROM players WHERE replayid = %s", [replay_id])
                assert cursor.fetchone()[0] == 10

                cursor.execute("SELECT COUNT(*) FROM generalstats WHERE replayid = %s", [replay_id])
                assert cursor.fetchone()[0] == 10

                cursor.execute("SELECT COUNT(*) FROM timeline WHERE replayid = %s", [replay_id])
                assert cursor.fetchone()[0] == 1
        finally:
            _cleanup(conn, replay_id, battletag_rows)
