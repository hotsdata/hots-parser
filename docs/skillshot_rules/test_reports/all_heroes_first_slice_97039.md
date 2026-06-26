# All-Hero First Slice Skillshot Report

Build: `97039`

This report records validation for the first all-hero subagent integration
slice. The integrated rules are intentionally marked as uncalibrated geometry
proxies unless they had already been tuned in prior work.

## Coverage

Generated with:

```bash
.venv/bin/python scripts/skillshot_rule_pipeline.py coverage --out docs/skillshot_rules/coverage_97039.json
```

Observed:

- Heroes: `90`
- Hero ability rows: `1063`
- Implemented: `89`
- Needs research: `132`
- Needs triage: `737`
- No rule likely: `105`

## Replay Smoke Tests

Replay corpus:

```text
/media/crorella/44108A78108A70AA/Users/crore/OneDrive/Documents/Heroes of the Storm/Accounts/222876/1-Hero-1-1440382/Replays/Multiplayer
```

Corpus size: `909` replay files.

### Nova

Command:

```bash
.venv/bin/python scripts/skillshot_rule_pipeline.py example-stats Nova --replay-dir "/media/crorella/44108A78108A70AA/Users/crore/OneDrive/Documents/Heroes of the Storm/Accounts/222876/1-Hero-1-1440382/Replays/Multiplayer" --limit 1 --random --seed 303
```

Replay: `2026-06-13 21.19.01 Braxis Outpost.StormReplay`

- Snipe: `64` attempts, `15` landed, `49` missed, `23.44%` hit rate.
- Precision Strike: `0` attempts.

### Jaina

Command:

```bash
.venv/bin/python scripts/skillshot_rule_pipeline.py example-stats Jaina --replay-dir "/media/crorella/44108A78108A70AA/Users/crore/OneDrive/Documents/Heroes of the Storm/Accounts/222876/1-Hero-1-1440382/Replays/Multiplayer" --limit 1 --random --seed 404
```

Replay: `2026-06-21 17.45.05 Silver City.StormReplay`

- Frostbolt: `78` attempts, `12` landed, `66` missed, `15.38%` hit rate.
- Cone of Cold: `53` attempts, `13` landed, `40` missed, `24.53%` hit rate.
- Blizzard: `50` attempts, `19` landed, `31` missed, `38.00%` hit rate.

## Validation

```bash
.venv/bin/python -m pytest
```

Observed: `40 passed, 1 skipped`.

```bash
.venv/bin/python -m ruff check .
```

Observed: `All checks passed`.
