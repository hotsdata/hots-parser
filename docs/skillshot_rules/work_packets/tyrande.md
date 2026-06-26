# Tyrande Skillshot Work Packet

Build: `97039`
Branch: `codex/skillshot-tyrande`
PR title: `[skillshots] Add Tyrande landing rules`

## Summary

- Ability count: 8
- Implemented rules: 2
- Research backlog: 6
- No-rule likely: 0

## Implemented Rules

- `TyrandeLunarFlare` / Lunar Flare: `area_position_overlap`, confidence `geometry_proxy_uncalibrated`
- `TyrandeSentinelShot` / Sentinel: `directional_position_overlap`, confidence `projectile_geometry_proxy_uncalibrated`

## Research Backlog

- `TyrandeElunesChosen` / Elune's Chosen: needs_triage
  - Search: Heroes of the Storm Tyrande Elune's Chosen mechanics
  - Search: Heroes of the Storm Tyrande Elune's Chosen radius delay hit
- `TyrandeHuntersMark` / Hunter's Mark: needs_triage
  - Search: Heroes of the Storm Tyrande Hunter's Mark mechanics
  - Search: Heroes of the Storm Tyrande Hunter's Mark radius delay hit
- `TyrandeLightofElune` / Light of Elune: needs_triage
  - Search: Heroes of the Storm Tyrande Light of Elune mechanics
  - Search: Heroes of the Storm Tyrande Light of Elune radius delay hit
- `TyrandeShadowstalk` / Shadowstalk: needs_triage
  - Search: Heroes of the Storm Tyrande Shadowstalk mechanics
  - Search: Heroes of the Storm Tyrande Shadowstalk radius delay hit
- `TyrandeStarfall` / Starfall: needs_triage
  - Search: Heroes of the Storm Tyrande Starfall mechanics
  - Search: Heroes of the Storm Tyrande Starfall radius delay hit
- `TyrandeTrueshotAura` / Trueshot Aura: needs_research
  - Search: Heroes of the Storm Tyrande Trueshot Aura mechanics
  - Search: Heroes of the Storm Tyrande Trueshot Aura radius delay hit

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

- Hero: Tyrande
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
