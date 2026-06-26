# Alarak Skillshot Work Packet

Build: `97039`
Branch: `codex/skillshot-alarak`
PR title: `[skillshots] Add Alarak landing rules`

## Summary

- Ability count: 15
- Implemented rules: 5
- Research backlog: 10
- No-rule likely: 0

## Implemented Rules

- `AlarakDeadlyChargeExecute2ndHeroic` / AlarakDeadlyChargeExecute2ndHeroic: `directional_position_overlap`, confidence `geometry_proxy_uncalibrated`
- `AlarakCounterStrikeTargeted` / Counter-Strike: `directional_position_overlap`, confidence `geometry_proxy_uncalibrated`
- `AlarakCounterStrikeTargeted2ndHeroic` / Counter-Strike: `directional_position_overlap`, confidence `geometry_proxy_uncalibrated`
- `AlarakDiscordStrike` / Discord Strike: `directional_position_overlap`, confidence `geometry_proxy_uncalibrated`
- `AlarakDeadlyChargeExecute` / Unleash Deadly Charge: `directional_position_overlap`, confidence `geometry_proxy_uncalibrated`

## Research Backlog

- `AlarakMightOfTheHighlordSetCounterStrikeAsHeroic` / AlarakMightOfTheHighlordSetCounterStrikeAsHeroic: needs_research
  - Search: Heroes of the Storm Alarak AlarakMightOfTheHighlordSetCounterStrikeAsHeroic mechanics
  - Search: Heroes of the Storm Alarak AlarakMightOfTheHighlordSetCounterStrikeAsHeroic radius delay hit
- `AlarakDeadlyChargeActivate` / Deadly Charge: needs_research
  - Search: Heroes of the Storm Alarak Deadly Charge mechanics
  - Search: Heroes of the Storm Alarak Deadly Charge radius delay hit
- `AlarakDeadlyChargeActivate2ndHeroic` / Deadly Charge: needs_research
  - Search: Heroes of the Storm Alarak Deadly Charge mechanics
  - Search: Heroes of the Storm Alarak Deadly Charge radius delay hit
- `AlarakHastyBargain` / Hasty Bargain: needs_triage
  - Search: Heroes of the Storm Alarak Hasty Bargain mechanics
  - Search: Heroes of the Storm Alarak Hasty Bargain radius delay hit
- `AlarakLastLaugh` / Last Laugh: needs_triage
  - Search: Heroes of the Storm Alarak Last Laugh mechanics
  - Search: Heroes of the Storm Alarak Last Laugh radius delay hit
- `AlarakLightningSurge` / Lightning Surge: needs_triage
  - Search: Heroes of the Storm Alarak Lightning Surge mechanics
  - Search: Heroes of the Storm Alarak Lightning Surge radius delay hit
- `AlarakLightningSurgeLightningBarrage` / Lightning Surge: needs_triage
  - Search: Heroes of the Storm Alarak Lightning Surge mechanics
  - Search: Heroes of the Storm Alarak Lightning Surge radius delay hit
- `AlarakMightOfTheHighlordSetDeadlyChargeAsHeroic` / Might of the Highlord: needs_research
  - Search: Heroes of the Storm Alarak Might of the Highlord mechanics
  - Search: Heroes of the Storm Alarak Might of the Highlord radius delay hit
- `AlarakRiteofRakShir` / Rite of Rak'Shir: needs_triage
  - Search: Heroes of the Storm Alarak Rite of Rak'Shir mechanics
  - Search: Heroes of the Storm Alarak Rite of Rak'Shir radius delay hit
- `AlarakTelekinesis` / Telekinesis: needs_triage
  - Search: Heroes of the Storm Alarak Telekinesis mechanics
  - Search: Heroes of the Storm Alarak Telekinesis radius delay hit

## Agent Workflow

- Coordinator: Create the branch, assign abilities, keep this packet current, and create one PR for the hero.
- Research: Browse current ability sources for each backlog ability and record mechanics, delays, radius, target type, and source URLs.
- Rule Designer: Choose detector type, evidence priority, confidence, gameloop windows, and docstring/evidence description.
- Implementer: Add versioned rules and detector support in data/replay modules without changing unrelated heroes.
- Validation: Parse at least two real replays for this hero and record generated skillshot stats in the PR body.
- Reviewer: Check plausibility, double counting, evidence strength, tests, and PR summary completeness.

## Validation Commands

- `.venv/bin/python -m pytest tests/test_skillshot_landing.py -q`
- `.venv/bin/python -m pytest`
- `.venv/bin/python -m ruff check .`

## PR Body Template

## Summary

- Hero: Alarak
- Build: 97039
- Implemented landing rules: TODO
- Omitted abilities: TODO
- Blocked abilities: TODO

## Research

- TODO: ability source URLs and mechanics notes

## Example Replay Stats

- TODO: paste output from `scripts/skillshot_rule_pipeline.py example-stats`

## Validation

- [ ] `.venv/bin/python -m pytest tests/test_skillshot_landing.py -q`
- [ ] `.venv/bin/python -m pytest`
- [ ] `.venv/bin/python -m ruff check .`
