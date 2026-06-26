# Automate Skillshot Landing Rule Coverage

This ExecPlan is a living document. Keep `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` current as work proceeds.

## Purpose / Big Picture

The goal is to make skillshot landing-rule coverage repeatable across all Heroes of the Storm heroes. A contributor or agent should be able to run one script, see which abilities are already covered, which abilities need research, and which hero-specific work packet should be assigned next. A later per-hero PR should include all landing rules for that hero plus example replay stats.

The observable first milestone is an instrumentation layer: a coverage JSON, a hero work packet, a PR summary template, and an example-stat sampler that can be run against the replay corpus. This milestone does not attempt to implement every hero's rules yet.

## Progress

- [x] 2026-06-26: Confirmed `master` includes the merged Kel'Thuzad rule infrastructure and is clean.
- [x] 2026-06-26: Drafted this repository-local ExecPlan.
- [x] 2026-06-26: Add `scripts/skillshot_rule_pipeline.py`.
- [x] 2026-06-26: Add tests for coverage classification and work packet generation.
- [x] 2026-06-26: Generate initial coverage and Kel'Thuzad work packet artifacts.
- [x] 2026-06-26: Run full pytest and ruff validation.
- [x] 2026-06-26: Prove the loop on Alarak and Tyrande with reusable directional geometry, updated packets, real replay stats, and a test report.
- [x] 2026-06-26: Run the first subagent batch pass over the remaining heroes and integrate safe candidate rules.

## Surprises & Discoveries

The current parser branch already has `data/skillshot_landing_rules.py`, `data/skillshot_landing_rule_sets.py`, and `replay/skillshot_landing.py` on `master`, so the automation can be additive and does not need to recreate detector infrastructure.

The initial coverage snapshot for build 97039 found 90 heroes and 1063 hero ability rows. The first-pass triage classified 2 abilities as already implemented, 163 as `needs_research`, 793 as `needs_triage`, and 105 as `no_rule_likely`.

After Kel'Thuzad, Alarak, and Tyrande, coverage was at 9 implemented rules. The all-hero subagent pass completed five batches recorded in `docs/skillshot_rules/subagent_batches.md`, and the first safe integration slice increased coverage to 89 implemented rules across 46 heroes.

Some researched abilities were intentionally not integrated because they need new detector semantics: persistent zones, persistent beams/channels, multi-projectile spreads, summon-origin attacks, trap/vector-wall geometry, self/no-target areas, and thrown-unit collision effects.

## Decision Log

Decision: Build a deterministic local coordinator script before spawning or coordinating agent work.

Rationale: The script gives every agent the same source of truth: current rules, catalog rows, first-pass classification, research checklist, and validation commands. That reduces duplicated manual state.

Date/Author: 2026-06-26 / Codex

Decision: Subagents produce specs before central rule-set edits.

Rationale: Most future rules would edit the same central files, especially `data/skillshot_landing_rule_sets.py`. Requiring subagents to produce candidate specs first avoids merge conflicts and lets the parent integrate only rules that fit existing detector semantics.

Date/Author: 2026-06-26 / Codex

Decision: Integrate only the first safe detector-compatible slice from the all-hero pass.

Rationale: The existing replay implementation supports follow-up evidence, area-position overlap, and directional-position overlap. Abilities that require persistent-zone, summon-origin, multi-projectile, trap, vector-wall, self-area, or throw-collision semantics are documented as blocked rather than approximated with an incompatible detector.

Date/Author: 2026-06-26 / Codex

Decision: Store generated operational artifacts under `docs/skillshot_rules/`.

Rationale: The artifacts are documentation and coordination state, not parser runtime data. Keeping them in `docs` avoids changing the parser payload surface.

Date/Author: 2026-06-26 / Codex

Decision: Treat classifier output as triage, not final truth.

Rationale: Ability names are not enough to prove whether a landing-rate rule is useful. The classifier should route work to research agents, while human or agent research makes final include/skip decisions.

Date/Author: 2026-06-26 / Codex

## Outcomes & Retrospective

The instrumentation milestone now has a coordinator CLI, tests, documentation, a generated build coverage file, and a Kel'Thuzad work packet. A first two-hero proof pass added versioned Alarak and Tyrande rules plus `docs/skillshot_rules/test_reports/alarak_tyrande_97039.md`.

The first all-hero subagent pass is consolidated in `docs/skillshot_rules/subagent_consolidation_97039.md`. It adds a first detector-compatible slice of uncalibrated geometry proxy rules, bringing build `97039` to 89 implemented skillshot rules. Every integrated rule's `ability_catalog_name` resolves against the build `97039` catalog.

## Context and Orientation

The relevant repository root is `/home/crorella/Documents/HotsData/hots-parser`.

Important files:

- `data/ability_catalog_97039.py` contains all current hero ability catalog rows for build 97039.
- `data/abilities.py` exposes helper lookups such as `get_hero_ability_definitions`.
- `data/skillshot_landing_rules.py` defines rule dataclasses such as `SkillshotLandingRule`.
- `data/skillshot_landing_rule_sets.py` contains the current build rule set. At the start of this plan it has Kel'Thuzad Chains and Frost Nova.
- `replay/skillshot_landing.py` applies rules to parsed replay heroes.
- `scripts/replay_ability_report.py` and `scripts/replay_corpus_report.py` are existing CLI patterns for replay/corpus reporting.

Terms:

`coverage JSON` means a generated file listing every hero ability for the build, its current rule status, and first-pass routing state.

`work packet` means a per-hero JSON/Markdown bundle that tells a future agent what to research, what to implement, what commands to run, and what PR summary to produce.

`landing rule` means a versioned rule that computes hit/landing stats from replay data.

## Plan of Work

First add `scripts/skillshot_rule_pipeline.py`. It will read the ability catalog and current skillshot rule set. It will produce build-level coverage and hero-level work packets. It will include an optional replay sampler that finds replays containing a hero and reports current `skillshotStats`.

Then add tests that validate first-pass classification, existing rule detection, and work packet shape. The tests should avoid the external replay corpus and should run quickly.

Then create documentation under `docs/skillshot_rules/README.md` explaining the loop and generate initial artifacts for build 97039. The initial generated artifacts should be small enough to review: coverage JSON for the whole build and a Kel'Thuzad packet that proves the already implemented rules are detected.

Finally run the focused tests, full pytest, and ruff.

## Concrete Steps

Run these commands from `/home/crorella/Documents/HotsData/hots-parser`:

    .venv/bin/python scripts/skillshot_rule_pipeline.py coverage --out docs/skillshot_rules/coverage_97039.json
    .venv/bin/python scripts/skillshot_rule_pipeline.py packet "Kel'Thuzad" --out-dir docs/skillshot_rules/work_packets
    .venv/bin/python -m pytest tests/test_skillshot_rule_pipeline.py -q
    .venv/bin/python -m pytest
    .venv/bin/python -m ruff check .

Expected observations:

- Coverage generation reports 90 heroes for build 97039.
- The Kel'Thuzad packet marks Chains and Frost Nova as implemented.
- Tests pass and ruff reports no issues.

## Validation and Acceptance

The instrumentation milestone is accepted when:

- The script can generate coverage JSON.
- The script can generate a per-hero JSON and Markdown work packet.
- The script can print an example-stats report for a hero when a replay corpus is supplied.
- Tests cover the triage classifier and packet shape.
- Full pytest and ruff pass.

## Idempotence and Recovery

Generated docs can be safely regenerated. If a command fails midway, rerun the same command after fixing the issue. The script should create directories as needed and overwrite only the requested output files. It should not mutate parser runtime behavior.

If external replay parsing fails for a replay, the example-stats command records the error and continues until it finds the requested number of usable examples or exhausts the corpus.

## Artifacts and Notes

Generated artifacts:

- `docs/skillshot_rules/coverage_97039.json`
- `docs/skillshot_rules/work_packets/kelthuzad.json`
- `docs/skillshot_rules/work_packets/kelthuzad.md`
- `docs/skillshot_rules/subagent_batches.md`
- `docs/skillshot_rules/subagent_consolidation_97039.md`
- `docs/skillshot_rules/test_reports/all_heroes_first_slice_97039.md`

Focused validation passed:

    .venv/bin/python -m pytest tests/test_skillshot_rule_pipeline.py -q
    4 passed

    .venv/bin/python -m ruff check scripts/skillshot_rule_pipeline.py tests/test_skillshot_rule_pipeline.py
    All checks passed

Example replay sampler smoke test:

    .venv/bin/python scripts/skillshot_rule_pipeline.py example-stats "Kel'Thuzad" --replay-dir "/media/crorella/44108A78108A70AA/Users/crore/OneDrive/Documents/Heroes of the Storm/Accounts/222876/1-Hero-1-1440382/Replays/Multiplayer" --limit 2 --random --seed 26

Observed two replay reports. Chains hit rates were 68.89% and 52.63%; Frost Nova hit rates were 58.82% and 54.17%.

Full validation passed:

    .venv/bin/python -m pytest
    40 passed, 1 skipped

    .venv/bin/python -m ruff check .
    All checks passed

All-hero first-slice validation passed:

    .venv/bin/python -m pytest
    40 passed, 1 skipped

    .venv/bin/python -m ruff check .
    All checks passed

Replay smoke tests from the external replay corpus produced Nova and Jaina
skillshot stats. The exact commands and observed rates are recorded in
`docs/skillshot_rules/test_reports/all_heroes_first_slice_97039.md`.

## Interfaces and Dependencies

The script depends only on existing repository modules and the standard library:

- `data.abilities`
- `data.skillshot_landing_rules`
- `data.skillshot_landing_rule_sets`
- `hotsparser.processEvents` for optional replay examples
- `protocol_loader` for replay metadata

It intentionally does not browse the internet. Research agents must browse when executing a work packet because ability mechanics can change and source attribution matters.
