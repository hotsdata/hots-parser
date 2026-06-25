# Modernize hots-parser for Python 3 with compatibility tests

This ExecPlan is a living document. Keep `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` current as work proceeds.

## Purpose / Big Picture

The goal is to make `hots-parser` runnable, testable, and maintainable on a modern Python stack while preserving the replay data contract consumed by the HotsData API, ETL jobs, and frontend. After this work, a developer should be able to use Python 3.10 or newer to parse a `.StormReplay` file, dump structured JSON artifacts, and optionally persist the same replay data into PostgreSQL without relying on Python 2 or PyPy.

The primary observable result is behavioral compatibility: for representative replay fixtures, the modern parser produces the same normalized data as the legacy parser for `replayInfo`, `players`, `generalStats`, `mapStats`, `teamGeneralStats`, `teamMapStats`, `timeline`, `deathlist`, and `armystr`. The secondary observable result is operational usability: `pytest`, linting, and the parser CLI run from a clean checkout with documented setup.

## Progress

- [x] 2026-06-25: Cloned and inspected all public `hotsdata` repositories under `/home/crorella/Documents/HotsData`.
- [x] 2026-06-25: Inspected `hots-parser` files, dependencies, Python 2 syntax, test coverage, and PostgreSQL persistence code.
- [x] 2026-06-25: User approved the modernization sequence: golden-output safety net, Python 3 port, dependency/config modernization, parser/persistence separation, tooling, and CI.
- [x] 2026-06-25: Created this ExecPlan at `PARSER_MODERNIZATION_EXEC_PLAN.md`.
- [x] 2026-06-25: User selected `2026-06-24 15.49.48 Silver City.StormReplay` as the first golden replay; copied it to ignored local path `tests/fixtures/replays/local/2026-06-24_15-49-48_Silver_City.StormReplay`.
- [x] 2026-06-25: Confirmed the pinned 2017 `heroprotocol` cannot decode the selected build `97039`; advanced the submodule to upstream commit `9af3ea7`, whose latest generated protocol is `96477`.
- [x] 2026-06-25: Added Python 3 protocol loading with nearest-older protocol fallback for newer replay builds.
- [x] 2026-06-25: Added Python 3 golden-output harness and generated ignored local golden JSON for the selected Silver City replay.
- [x] 2026-06-25: Ported parser and supporting modules to Python 3 syntax and runtime behavior.
- [x] 2026-06-25: Modernized dependencies, packaging, CLI entry points, README setup, and Ruff/Pytest tooling.
- [x] 2026-06-25: Added `utils/payloads.py` so parser output generation is separated from PostgreSQL writes.
- [x] 2026-06-25: Replaced `psycopg2ct` with `psycopg` and added `HOTSDATA_DATABASE_URL` / `DATABASE_URL` support with `credentials.json` fallback.
- [ ] Remove or quarantine dead legacy MySQL/TrueSkill persistence code.
- [x] 2026-06-25: Added CI-ready validation commands and documentation; local validation passes.

## Surprises & Discoveries

The current repository is a 2017-era Python 2 project. It uses Python 2 constructs including `print` statements, `except Exception, e`, `xrange`, `iteritems`, `itervalues`, `file(...)`, `unicode(...)`, `<>`, and `sys.setdefaultencoding`.

The local environment has `python3` version 3.10.12, but no `python` command. The parser cannot run in this environment until it is ported or a Python 2/PyPy runtime is supplied.

The `heroprotocol` submodule directory exists but is empty. `git submodule status --recursive` reports the pinned commit as `1f5f4f6352c46ff497e03e494502843bf60fe156`, and `.gitmodules` points to the SSH URL `git@github.com:Blizzard/heroprotocol.git`. That URL will fail for contributors without GitHub SSH setup; the modernization should switch this to HTTPS or replace the submodule with a pinned package dependency.

Existing tests only cover hero and map translation behavior in `tests/data/test_data.py`. There are no replay fixture tests and no database integration tests.

`utils/db.py` appears to be legacy MySQL/TrueSkill persistence code. The active PostgreSQL path is `utils/pg_persistence.py`, imported from `main.py`.

`credentials.json` is committed and contains placeholder values. The modernization should not require editing committed credentials to run tests or parse replay files.

The selected first replay fixture is locally available at `tests/fixtures/replays/local/2026-06-24_15-49-48_Silver_City.StormReplay`. It is ignored by Git because replay files can contain player names and BattleTags. The original source path is `/media/crorella/44108A78108A70AA/Users/crore/OneDrive/Documents/Heroes of the Storm/Accounts/222876/1-Hero-1-1440382/Replays/Multiplayer/2026-06-24 15.49.48 Silver City.StormReplay`.

The selected replay has header base build `97039`. The original pinned `heroprotocol` only provides generated protocol modules through `57286`, so a true Python 2 legacy golden output for this specific replay is not possible from the original code. The current upstream `heroprotocol` submodule provides generated protocol modules through `96477`, and that nearest-older protocol successfully decodes details, init data, attributes, and tracker events for the selected replay.

The latest upstream `heroprotocol` package layout changed from root-level `heroprotocol.protocolNNNNN` modules to `heroprotocol.versions.protocolNNNNN`. The parser now uses `protocol_loader.py` to insert the submodule path explicitly, load `mpyq` from PyPI, load the header protocol, and choose an exact or nearest-older protocol for the replay build.

Decoded protocol objects on Python 3 contain byte strings in some fields that the legacy code compared against text constants. The parser now normalizes decoded protocol objects to text at the boundary before event handling.

Python 3 exposed two legacy semantic assumptions: integer division was needed for team/index values, and Python 2 allowed comparisons between `None` and integers. These were fixed in the port.

## Decision Log

Decision: Preserve downstream table names and JSON keys until API and ETL migrations are explicitly planned.

Rationale: The API and ETL query tables and JSON keys written by this parser, including `replayinfo`, `players`, `generalstats`, `mapstats`, `teamgeneralstats`, `teammapstats`, `timeline`, `deathlist`, `armystr`, `heroName`, `gameLoops`, `pickedTalents`, and `toonHandle`. Renaming these during parser modernization would create avoidable cross-repository breakage.

Date/Author: 2026-06-25 / Codex

Decision: Build golden-output tests before changing parser behavior.

Rationale: The parser has dense replay event logic and no replay-level test safety net. Golden outputs from the legacy parser provide the only practical guard against accidental semantic changes during the Python 3 port.

Date/Author: 2026-06-25 / Codex

Decision: Target Python 3.10 or newer first.

Rationale: The current local environment provides Python 3.10.12. Targeting Python 3.10+ keeps the migration pragmatic while allowing modern packaging, typing syntax where useful, and current tooling.

Date/Author: 2026-06-25 / Codex

Decision: Keep the old CLI command working while adding modern packaging.

Rationale: Existing operational usage likely invokes `main.py` directly. A new package entry point can coexist with a backward-compatible `python3 main.py ...` path during migration.

Date/Author: 2026-06-25 / Codex

Decision: Replace `psycopg2ct` with `psycopg` version 3 for PostgreSQL persistence unless compatibility testing reveals a blocker.

Rationale: `psycopg2ct` was chosen for PyPy/Python 2 compatibility. The modern parser should run on CPython 3, and `psycopg` is actively maintained.

Date/Author: 2026-06-25 / Codex

Decision: Prefer HTTPS for `heroprotocol` retrieval, pinned to the current submodule commit, unless a maintained PyPI release can be pinned to equivalent behavior.

Rationale: The current submodule is empty locally and uses an SSH URL. HTTPS plus a pinned commit makes clean checkout setup reproducible for more contributors.

Date/Author: 2026-06-25 / Codex

Decision: Use `2026-06-24 15.49.48 Silver City.StormReplay` as the first golden replay fixture, but keep the binary replay file in an ignored local fixture directory.

Rationale: The user explicitly selected this replay for the golden baseline. Keeping it ignored reduces the chance of accidentally committing personal replay data while still giving local implementation work a stable fixture path.

Date/Author: 2026-06-25 / Codex

Decision: Use latest upstream `heroprotocol` commit `9af3ea7150f1a8acb53464c92519a9bbcc7a3594` and select the nearest older generated protocol when the exact replay build is unavailable.

Rationale: The selected replay is build `97039`, which the original pinned protocol cannot decode. The latest upstream generated protocol is `96477` and decodes the selected replay successfully. Keeping a deterministic fallback is more useful than blocking modernization on a non-existent generated protocol for `97039`.

Date/Author: 2026-06-25 / Codex

Decision: Store golden JSON for the selected replay under ignored `tests/golden/local/`.

Rationale: Golden payloads include player-identifying replay data. Keeping both the binary fixture and generated payloads local avoids accidentally committing private replay contents while still allowing this machine to run regression tests.

Date/Author: 2026-06-25 / Codex

Decision: Introduce a migration-friendly Ruff baseline that excludes the generated `heroprotocol` submodule and ignores legacy star-import cleanup until a focused cleanup pass.

Rationale: The generated protocol files produce hundreds of style findings outside this repository's ownership. The parser still has legacy star-import structure; changing all imports now would create unnecessary risk after the behavior-preserving Python 3 port. Ruff still catches syntax, import, and serious Python errors in project-owned code.

Date/Author: 2026-06-25 / Codex

## Outcomes & Retrospective

Implementation pass completed on 2026-06-25. The parser now runs on Python 3.10, opens the selected Silver City replay, decodes it with protocol fallback `96477`, and produces stable local golden payloads. The fixture parse produced replay id `5a3c3a2c774d12eb271fe9ed14523b4850aa0c1d20d9924163af915764432df5`, map `Silver City`, build `97039`, 10 players, 10 heroes, 3890 units, and 176 timeline events.

The local golden generator wrote 10 payload files under `tests/golden/local/silver_city_2026-06-24`: `replayinfo`, `players`, `generalstats`, `mapstats`, `teamgeneralstats`, `teammapstats`, `timeline`, `deathlist`, `armystr`, and `battletag_toonhandle_lookup`.

Validation passed with `.venv/bin/python -m pytest -q`, `.venv/bin/python -m ruff check .`, `.venv/bin/python -m ruff format --check .`, `.venv/bin/python -m hots_parser --help`, and a `main.py --dump-all` smoke test against the local replay. Pytest emits one warning from upstream `heroprotocol` using deprecated `imp`, and the dump smoke test emits `jsonpickle` deprecation warnings; both are non-blocking follow-ups.

Remaining work: remove or quarantine `utils/db.py`, add optional PostgreSQL integration tests against `database/database_schema.sql`, decide whether to commit a public replay fixture, and eventually replace `jsonpickle` dump compatibility with explicit standard-JSON output once downstream consumers are checked.

## Context and Orientation

Work from the repository root:

    /home/crorella/Documents/HotsData/hots-parser

The parser entry point is `main.py`. It parses CLI arguments, opens a `.StormReplay` file through PyPI `mpyq.MPQArchive`, calls `hotsparser.processEvents`, and either dumps JSON files or saves data to PostgreSQL. The package wrapper `hots_parser/__main__.py` exposes the same CLI through `python3 -m hots_parser`.

`protocol_loader.py` makes the checked-out `heroprotocol` submodule importable under Python 3, loads the header protocol, and chooses either the exact generated protocol for the replay build or the nearest older generated protocol when the exact build is unavailable.

`hotsparser.py` is a small orchestration module. Its `processEvents` function creates a `Replay` object and runs replay processing in this order: details, init data, tracker events, attributes, army strength, map events, and generic events.

`replay/__init__.py` contains the core `Replay` class and most replay event handling. This is the highest-risk file because it maps raw replay protocol events into HotsData-specific metrics.

`models/__init__.py` contains domain objects such as `Team`, `Unit`, `HeroUnit`, `HeroReplay`, `Player`, `GameUnit`, and related metric storage.

`data/__init__.py` contains constants and translators for maps and heroes. The only existing tests focus here.

`helpers/__init__.py` contains utility functions for game loop conversion, unit tags, map positions, distances, and player/hero lookup.

`utils/payloads.py` converts a parsed `Replay` object into plain dictionaries for the persistence targets and golden tests. This layer avoids mutating live parser objects during database serialization.

`utils/pg_persistence.py` writes parser output into PostgreSQL. It uses `psycopg` version 3, reads `HOTSDATA_DATABASE_URL` or `DATABASE_URL` when set, falls back to `credentials.json`, and serializes payload dictionaries with `jsonpickle` for compatibility.

`database/database_schema.sql` defines the shared PostgreSQL schema used by the parser, API, ETL, and frontend.

Terms used in this plan:

Golden output means a checked-in or generated JSON snapshot produced by the legacy parser from a known replay fixture. Tests compare modern output to these snapshots.

Replay fixture means a `.StormReplay` file used only for tests. It must be safe to store in the repository or kept in an ignored local fixture directory with a documented retrieval path.

The first selected replay fixture is named `2026-06-24_15-49-48_Silver_City.StormReplay` in the local ignored fixture directory. The map name in the source filename is `Silver City`.

Normalized output means parser output transformed into stable JSON for comparison. It should exclude timestamps in generated filenames, local replay paths, and any ordering differences that do not affect data meaning.

## Plan of Work

Start by recovering a runnable legacy parser environment. Populate `heroprotocol` at the pinned commit or install an equivalent dependency, then run the old parser against one or more representative replay fixtures. Capture normalized outputs for the tables and dump artifacts that downstream repositories depend on. If no safe replay fixture is available in the repository, stop at this milestone and obtain a public or user-approved fixture before porting behavior.

Next, add a Python 3 test harness around the expected parser contract. The harness should be able to parse a fixture, convert the `Replay` object into plain dictionaries, and compare those dictionaries to golden JSON. This test may initially be marked as pending or documented as failing until the Python 3 port is complete, but the expected output and comparison rules must exist before modifying parser internals.

Then perform a mechanical Python 3 port. Convert syntax and standard library usage while preserving file layout and runtime flow as much as possible. Avoid refactoring event logic during the mechanical port. The safest order is to update imports and syntax first, make translator tests pass, then make fixture parsing pass.

After the Python 3 port passes compatibility tests, modernize project structure and dependencies. Add `pyproject.toml`, pin dependencies, add a console script, and keep `main.py` as a compatibility shim. Add `pytest` and `ruff` development dependencies. Add a `README.md` modernization section that documents setup, fixture tests, parsing, and persistence.

Next, separate parsing from persistence. Introduce a stable conversion layer that turns `Replay` objects into plain dictionaries representing each persistence target. Make PostgreSQL persistence consume those dictionaries rather than mutating and serializing the live `Replay` object directly. Keep SQL table names and field names compatible.

Then modernize PostgreSQL access and configuration. Replace `psycopg2ct` with `psycopg`, support `DATABASE_URL`, and retain a backward-compatible `credentials.json` fallback with deprecation notes. Add an integration test path that runs only when a test database URL is provided.

Finally, remove or quarantine unused legacy code. Confirm `utils/db.py` is not imported. If it is unused, delete it or move it under a clearly named legacy location only if preserving history is required. Do this after parser and persistence tests pass.

## Concrete Steps

Run all commands from `/home/crorella/Documents/HotsData/hots-parser` unless a step says otherwise.

Confirm the starting point:

    git status --short
    git log -1 --format='%h %ci %s'
    python3 --version
    git submodule status --recursive

Expected observations: clean worktree before implementation, commit `7fe2fc6` unless newer work has landed, Python 3.10 or newer available, and `heroprotocol` currently uninitialized at commit `1f5f4f6352c46ff497e03e494502843bf60fe156`.

Recover `heroprotocol` in a reproducible way:

    git config submodule.heroprotocol.url https://github.com/Blizzard/heroprotocol.git
    git submodule update --init --recursive
    git submodule status --recursive

Expected observation: `heroprotocol` is populated at the pinned commit. If network access is unavailable, document that blocker in `Surprises & Discoveries` and retry with network approval or with a local mirror.

Create fixture layout:

    mkdir -p tests/fixtures/replays tests/golden tests/support scripts

Use the selected local replay as the first fixture. The replay has already been copied locally to:

    tests/fixtures/replays/local/2026-06-24_15-49-48_Silver_City.StormReplay

If recreating the local fixture from the original source path, run:

    mkdir -p tests/fixtures/replays/local
    cp '/media/crorella/44108A78108A70AA/Users/crore/OneDrive/Documents/Heroes of the Storm/Accounts/222876/1-Hero-1-1440382/Replays/Multiplayer/2026-06-24 15.49.48 Silver City.StormReplay' 'tests/fixtures/replays/local/2026-06-24_15-49-48_Silver_City.StormReplay'
    sha256sum tests/fixtures/replays/local/2026-06-24_15-49-48_Silver_City.StormReplay

Expected SHA-256:

    9ddd0723b5608a9b8ef504197ae3018bc74c570088fdb641ff790521a5fba664

Do not commit files under `tests/fixtures/replays/local/`. `.gitignore` intentionally excludes that directory. If a replay fixture should become public and committed later, create a separate non-ignored fixture path and record that decision.

Add a legacy baseline generator under `scripts/`. It should run under Python 2/PyPy, call the existing parser flow, and write normalized JSON into `tests/golden/<fixture-name>/`. The normalized JSON should include one file per persistence target or dump entity, not one giant opaque blob.

Run the baseline generator in a controlled legacy environment. If Docker is available, use a throwaway image or Dockerfile. If not, use pyenv, system Python 2, or PyPy. Record the exact runtime and command in `Artifacts and Notes`.

Add Python 3 tooling:

    pyproject.toml
    tests/support/normalization.py
    tests/test_golden_outputs.py

Add dependencies for runtime and development. The first version should include `jsonpickle`, a pinned `heroprotocol` source or submodule note, `psycopg[binary]`, `pytest`, and `ruff`.

Port Python 2 syntax to Python 3 in focused passes:

    main.py
    hotsparser.py
    replay/__init__.py
    models/__init__.py
    helpers/__init__.py
    data/__init__.py
    utils/pg_persistence.py

Run translator tests after the first pass:

    python3 -m pytest tests/data/test_data.py -q

Expected observation: map and hero translation tests pass under Python 3.

Run golden parser tests:

    python3 -m pytest tests/test_golden_outputs.py -q

Expected observation: fixture output matches the legacy golden files. If output differs, inspect whether the difference is ordering, string/bytes normalization, or a real semantic regression. Only update golden files when the difference is intentionally accepted and recorded in the Decision Log.

Add and validate the modern CLI while preserving old usage:

    python3 main.py --help
    python3 -m hots_parser --help

Expected observation: both commands document equivalent parse and dump options, including `--output-dir`, `--dump-heroes`, `--dump-teams`, `--dump-timeline`, `--dump-units`, `--dump-players`, `--dump-all`, `--team1`, `--team2`, `--event`, and `--stage`.

Add linting and run it:

    python3 -m ruff check .
    python3 -m ruff format --check .

Expected observation: checks pass. If formatting is introduced after the port, do it in a separate commit or stopping point from semantic changes.

Modernize persistence and validate with an optional database:

    HOTSDATA_DATABASE_URL=postgresql://hotsdata:hotsdata@localhost:5432/hotsdata python3 -m pytest tests/test_postgres_persistence.py -q

Expected observation: when a compatible test database is available and `database/database_schema.sql` has been applied, the parser writes the expected rows for the fixture replay. When the environment variable is missing, integration tests should skip rather than fail.

## Validation and Acceptance

The modernization is accepted when these checks pass from a clean checkout:

    python3 -m pytest -q
    python3 -m ruff check .
    python3 -m ruff format --check .
    python3 main.py --help

At least one replay fixture must parse successfully under Python 3 and match its legacy golden output. The expected comparison is stable JSON after normalization, not raw object identity or timestamped output filenames.

The CLI must remain backward-compatible for existing direct `main.py` usage. New package entry points are additive.

PostgreSQL persistence must remain compatible with `database/database_schema.sql` and the downstream API/ETL expectations. Table names, primary keys, conflict behavior, and JSON field names must not change unless a separate cross-repository migration plan is created.

Configuration should allow parsing and JSON dumping without database credentials. Database credentials should come from `DATABASE_URL` or documented environment/config paths. Tests should not require editing committed `credentials.json`.

Documentation must explain setup, fixture expectations, parse/dump usage, database persistence usage, and the compatibility contract.

## Idempotence and Recovery

Run parser tests and golden-output generation against copies or read-only fixture files. The parser should not mutate fixture replay files.

Golden-output generation should either refuse to overwrite existing golden files by default or require an explicit update flag. When golden files change, the implementer must record why in `Decision Log` or `Outcomes & Retrospective`.

Database integration tests should use a disposable database or schema. They should clean rows inserted for fixture replay IDs, or use a fresh test database loaded from `database/database_schema.sql`.

If `heroprotocol` retrieval fails because of SSH authentication, retry with HTTPS. If the pinned commit is unavailable, stop and record the exact failure rather than silently using a different commit.

If Python 3 output differs from golden output, do not immediately update the golden files. First classify the difference as one of: harmless ordering/encoding/path normalization, accepted bug fix, or regression. Regressions must be fixed in code. Accepted bug fixes must be documented because they may affect downstream analytics.

Keep large replay fixtures out of the repository unless they are public and intentionally committed. If local-only fixtures are needed, add a clear `.gitignore` pattern and a README note describing where to place them.

Avoid broad refactors before golden tests pass. If a mechanical formatter creates a large diff, run it after behavior is already green so behavior changes and style changes are reviewable separately.

## Artifacts and Notes

Current inspection evidence from 2026-06-25:

    git log -1 --format='%h %ci %s'
    7fe2fc6 2017-09-18 11:04:12 -0300 Merge pull request #6 from CamDavidsonPilon/master

    python3 --version
    Python 3.10.12

    python --version
    /bin/bash: line 1: python: command not found

    git submodule status --recursive
    -1f5f4f6352c46ff497e03e494502843bf60fe156 heroprotocol

    requirements.txt
    jsonpickle
    psycopg2ct

The repository currently has 21 tracked files and no populated replay fixtures. `README.md` documents PyPy and PostgreSQL 9.5 assumptions.

The first selected replay fixture was copied locally on 2026-06-25:

    Original path:
    /media/crorella/44108A78108A70AA/Users/crore/OneDrive/Documents/Heroes of the Storm/Accounts/222876/1-Hero-1-1440382/Replays/Multiplayer/2026-06-24 15.49.48 Silver City.StormReplay

    Local ignored fixture path:
    tests/fixtures/replays/local/2026-06-24_15-49-48_Silver_City.StormReplay

    Size:
    1.2M

    SHA-256:
    9ddd0723b5608a9b8ef504197ae3018bc74c570088fdb641ff790521a5fba664

## Interfaces and Dependencies

`main.py` is the current CLI interface. Preserve its flags and behavior while adding a modern entry point.

`hotsparser.processEvents(protocol, replayFile, team1=None, team2=None, event=None, stage=None)` is the current programmatic parser interface. It returns a `Replay` object after processing replay details, init data, tracker events, attributes, army strength, map events, and generic events.

`Replay.get_replay_id()` computes the replay ID used as the primary identifier across persistence tables. Treat this as a stable downstream contract unless a separate migration is planned.

`utils/pg_persistence.save_data(replayData, path)` is the current database write entry point. It writes to `replayInfo`, `deathlist`, `armystr`, `teamGeneralStats`, `teamMapStats`, `timeline`, `generalStats`, `mapstats`, `players`, and `battletag_toonhandle_lookup`.

`database/database_schema.sql` is the authoritative schema snapshot for parser persistence. Any SQL changes must be coordinated with API and ETL users.

`heroprotocol` decodes Blizzard replay files. The modernized project must pin its source or commit so replay parsing remains reproducible.

`jsonpickle` currently serializes Python objects and dictionaries into JSONB strings. The modernization may retain it temporarily for compatibility, but the long-term direction is explicit plain dictionaries and standard `json` serialization.

`psycopg` version 3 is the target PostgreSQL client. It replaces `psycopg2ct` after compatibility tests exist.

The API repository queries parser output directly, especially replay details, player stats, map stats, hero info, win rates, and player lookup tables. The ETL repository aggregates parser output into staged and fact tables. These downstream dependencies make output compatibility the central acceptance criterion.
