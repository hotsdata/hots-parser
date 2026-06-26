# Kel'Thuzad Skillshot Work Packet

Build: `97039`
Branch: `codex/skillshot-kelthuzad`
PR title: `[skillshots] Add Kel'Thuzad landing rules`

## Summary

- Ability count: 13
- Implemented rules: 2
- Research backlog: 11
- No-rule likely: 0

## Implemented Rules

- `KelThuzadChains` / Chains of Kel'Thuzad: `same_user_followup`, confidence `proxy`
- `KelThuzadFrostNova` / Frost Nova: `area_position_overlap`, confidence `geometry_proxy_calibrated`

## Research Backlog

- `KelThuzadArchlichArmor` / Armor of the Archlich: needs_triage
  - Search: Heroes of the Storm Kel'Thuzad Armor of the Archlich mechanics
  - Search: Heroes of the Storm Kel'Thuzad Armor of the Archlich radius delay hit
- `KelThuzadChainsPull` / Chains Pull: needs_research
  - Search: Heroes of the Storm Kel'Thuzad Chains Pull mechanics
  - Search: Heroes of the Storm Kel'Thuzad Chains Pull radius delay hit
- `KelThuzadChainsLink` / Chains of Kel'Thuzad: needs_research
  - Search: Heroes of the Storm Kel'Thuzad Chains of Kel'Thuzad mechanics
  - Search: Heroes of the Storm Kel'Thuzad Chains of Kel'Thuzad radius delay hit
- `KelThuzadDeathAndDecay` / Death and Decay: needs_triage
  - Search: Heroes of the Storm Kel'Thuzad Death and Decay mechanics
  - Search: Heroes of the Storm Kel'Thuzad Death and Decay radius delay hit
- `KelThuzadDeathAndDecayShade` / Death and Decay: needs_triage
  - Search: Heroes of the Storm Kel'Thuzad Death and Decay mechanics
  - Search: Heroes of the Storm Kel'Thuzad Death and Decay radius delay hit
- `KelThuzadFrozenTomb` / Frost Blast: needs_research
  - Search: Heroes of the Storm Kel'Thuzad Frost Blast mechanics
  - Search: Heroes of the Storm Kel'Thuzad Frost Blast radius delay hit
- `KelThuzadGlacialSpike` / Glacial Spike: needs_triage
  - Search: Heroes of the Storm Kel'Thuzad Glacial Spike mechanics
  - Search: Heroes of the Storm Kel'Thuzad Glacial Spike radius delay hit
- `KelThuzadPhylacteryItem` / Phylactery of Kel'Thuzad: needs_triage
  - Search: Heroes of the Storm Kel'Thuzad Phylactery of Kel'Thuzad mechanics
  - Search: Heroes of the Storm Kel'Thuzad Phylactery of Kel'Thuzad radius delay hit
- `KelThuzadShadowFissure` / Shadow Fissure: needs_research
  - Search: Heroes of the Storm Kel'Thuzad Shadow Fissure mechanics
  - Search: Heroes of the Storm Kel'Thuzad Shadow Fissure radius delay hit
- `KelThuzadShiftingMalice` / Shifting Malice: needs_triage
  - Search: Heroes of the Storm Kel'Thuzad Shifting Malice mechanics
  - Search: Heroes of the Storm Kel'Thuzad Shifting Malice radius delay hit
- `KelThuzadSpawnShade` / The Damned Return: needs_triage
  - Search: Heroes of the Storm Kel'Thuzad The Damned Return mechanics
  - Search: Heroes of the Storm Kel'Thuzad The Damned Return radius delay hit

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

- Hero: Kel'Thuzad
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
