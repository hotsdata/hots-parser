# hots-parser
A fast Heroes of the Storm's replay files parser written in Python.

## Python 3 quick start

This project now targets Python 3.10 or newer.

```bash
git submodule update --init --recursive
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
```

Parse a replay and dump legacy object JSON files:

```bash
.venv/bin/python main.py --dump-all --output-dir /tmp/hots-parser-output path/to/replay.StormReplay
```

Dump the cleaner standard JSON payload files used by persistence and golden tests:

```bash
.venv/bin/python main.py --dump-payloads --output-dir /tmp/hots-parser-payloads path/to/replay.StormReplay
```

Useful payload files include `teamgeneralstats.json`, `teammapstats.json`, `generalstats.json`, `mapstats.json`, `players.json`, and `timeline.json`.

The older `--dump-heroes`, `--dump-teams`, `--dump-timeline`, `--dump-units`, `--dump-players`, and `--dump-all` flags are kept for compatibility, but they write `jsonpickle` object dumps. Prefer `--dump-payloads` for stable JSON inspection and tests.

The package entry point is also available:

```bash
.venv/bin/python -m hots_parser --help
```

## Golden replay tests

Private replay fixtures stay out of Git. Put local fixtures under:

```text
tests/fixtures/replays/local/
```

The current local golden replay is:

```text
tests/fixtures/replays/local/2026-06-24_15-49-48_Silver_City.StormReplay
```

Generate or refresh its ignored golden JSON payloads with:

```bash
.venv/bin/python scripts/generate_golden.py --update
```

The golden test skips on machines without the local replay or generated local golden output.

## Database configuration

Parser-only usage and JSON dumping do not require database credentials. Database writes use `HOTSDATA_DATABASE_URL` or `DATABASE_URL` when set, with `credentials.json` retained as a legacy fallback.

Optional PostgreSQL integration tests use the same database URL and require the schema in `database/database_schema.sql` to already be loaded:

```bash
HOTSDATA_DATABASE_URL=postgresql://user:password@localhost:5432/hotsdata .venv/bin/python -m pytest tests/test_postgres_persistence.py -q
```


## How to run it:

There are two ways to run hots-parser:

1) Standalone: where the stats are save to different files, based on the flags you use.

2) Database: where the stats are inserted into a database. This is the default mode where you don't provide any flag or parameter besides the path to the replay file

```
usage: main.py [-h] [-o OUTPUT_DIR] [-r] [-t] [-l] [-u] [-p] [-a] replay_path

positional arguments:
  replay_path           Path to the .StormReplay file to process

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Path to the output directory
  -r, --dump-heroes     Legacy jsonpickle dump of hero objects
  -t, --dump-teams      Legacy jsonpickle dump of team objects
  -l, --dump-timeline   Legacy jsonpickle dump of timeline objects
  -u, --dump-units      Legacy jsonpickle dump of unit objects
  -p, --dump-players    Legacy jsonpickle dump of player objects
  -a, --dump-all        Legacy shortcut for --dump-heroes --dump-teams --dump-units
                        --dump-players --dump-timeline
  --dump-payloads       Dump standard JSON payload files used by persistence
                        and golden tests
```

# Configuration
The parser is tested with CPython 3.10 or newer. PyPy was used by the legacy Python 2 version, but it is no longer required for normal development.

## Loading submodules
The parser relies on Blizzard's heroprotocol project, which is included as a submodule in this repo, in order to pull the data for heroprotocol you need to run this command after cloning the repo:

```
git submodule init
git submodule update
```

alternatively, you can clone hots-parser recursively:

```
git clone --recursive git@github.com:crorella/hots-parser.git
```

## Loading the database schema
You will need a PostgreSQL server running at least the version 9.5, because we make extensive use of the JSONB datatype to store the metrics we extract from the replay.

- Create a database with the name "hotsdata"
- Create a user with the name "hotsdata" and grant ALL to the hotsdata database.

```
CREATE DATABASE hotsdata;
CREATE ROLE hotsdata WITH LOGIN PASSWORD 'hotsdata';
REVOKE CONNECT ON DATABASE hotsdata FROM PUBLIC;
GRANT ALL ON DATABASE hotsdata TO hotsdata;
```

- Set `HOTSDATA_DATABASE_URL` or `DATABASE_URL`, or update `credentials.json` with the appropriate password and server information for the legacy fallback path.
- Load the script in database/database_schema.sql into hotsdata. Please note this schema also contains the tables used by the API, data processing (ETL) and frontend that power www.hotsdata.com

## Installing python libraries
Install the project dependencies from `pyproject.toml`:

> python3 -m pip install -e '.[dev]'

## Testing all
To test if everything is working fine run the following command in the root folder of this project:
> python3 main.py --dump-all --output-dir /tmp/hots-parser-output Hanamura.StormReplay

You should see something like this in the console:
```
Processing: Hanamura.StormReplay
saving 18c0a432362fca4bb38ccf950ede92d562bb3a5b9e72a93beb4ce196c322650d to db
```

If you query the database you should see data in the following tables:
- replayinfo: This is the main table where general information about the replay is stored. Every table has a replayid as a foreign key to this table.
- players: stores the players present in the replay, you should see 10 entries here, one per player.
- teams: teams present in the replay, you should see 2 entries here.
- teamstats: this table store generic team metrics which are common across all maps. You should see 2 entries here, one per team.
- teammapstats: this table store map specific metrics at a team level. You should see 2 entries here, one per team.
- generalstats: this table store generic player stats which are common across all maps. You should see 10 entries here, one per player.
- mapstats: this table store map specific metrics for each player. You should see 10 entries here, one per player.
- battletag_toonhandle_lookup: this table creates a mapping between the battletags and the toonhandles of every player, you should see 10 entries here, one per player.

The others tables are mostly used by the processes that aggregate data and calculate more advanced metrics. This project is still not Open Source, but we are working on cleaning the code to release it in the next couple of days.
