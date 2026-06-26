# Skillshot Rule Automation

This directory contains coordination artifacts for expanding skillshot landing-rate coverage.

The current loop is intentionally staged:

1. Generate build coverage from the ability catalog and current rule set.
2. Generate one work packet per hero.
3. Assign each hero packet to agents for research, rule design, implementation, validation, and review.
4. Open one PR per hero.

The coordinator script is:

    .venv/bin/python scripts/skillshot_rule_pipeline.py

Current detector families:

- `same_user_followup`: counts a cast as landed when a follow-up ability appears in the configured window.
- `area_position_overlap`: counts enemy Hero overlap against a delayed point-targeted area.
- `directional_position_overlap`: counts enemy Hero overlap against a line or triangular area projected from the caster through the target point.

## Coverage

Generate the build-level coverage file:

    .venv/bin/python scripts/skillshot_rule_pipeline.py coverage --out docs/skillshot_rules/coverage_97039.json

The coverage file contains every hero ability catalog row for build 97039 and a first-pass decision:

- `implemented`: a versioned skillshot landing rule already exists.
- `needs_research`: name-based triage suggests this may need a landing-rate rule.
- `needs_triage`: the ability needs manual or agent classification.
- `no_rule_likely`: name-based triage suggests no landing-rate rule is needed.

The first-pass decision is routing metadata, not a final decision.

## Wiki Triage

Run a current-source triage pass against Heroes of the Storm Wiki `Data:<Hero>`
pages:

    .venv/bin/python scripts/skillshot_rule_pipeline.py wiki-triage --refresh --source-cache docs/skillshot_rules/wiki_ability_sources_97039.json --out docs/skillshot_rules/wiki_triage_97039.json

The wiki triage uses ability and talent descriptions, targeting metadata,
properties such as `Skillshot` / `Area of Effect`, and fields such as radius,
hitbox, missile speed, and target type. It classifies rows into:

- `rule_candidate_existing_detector`: likely implementable with an existing detector.
- `blocked_new_detector`: relevant, but needs a detector family that does not exist yet.
- `no_rule_likely`: not a useful landing-rate check.
- `needs_manual_review`: matched, but not safely classifiable.
- `wiki_unmatched`: no matching wiki ability or talent entry was found.

The build `97039` report is
`docs/skillshot_rules/wiki_triage_report_97039.md`.

Generate the candidate status table from wiki triage:

    .venv/bin/python scripts/skillshot_rule_pipeline.py candidate-table --wiki-triage docs/skillshot_rules/wiki_triage_97039.json --csv-out docs/skillshot_rules/skillshot_candidate_status_97039.csv --markdown-out docs/skillshot_rules/skillshot_candidate_status_97039.md

Generated status artifacts:

- `docs/skillshot_rules/skillshot_candidate_status_97039.md`
- `docs/skillshot_rules/skillshot_candidate_status_97039.csv`

## Work Packets

Generate a work packet for one hero:

    .venv/bin/python scripts/skillshot_rule_pipeline.py packet "Kel'Thuzad" --out-dir docs/skillshot_rules/work_packets

Each packet contains:

- hero identity and recommended branch name
- existing implemented rules
- research backlog
- likely no-rule abilities
- agent workflow
- validation commands
- PR body template

## Example Stats

Generate example stats from real replays:

    .venv/bin/python scripts/skillshot_rule_pipeline.py example-stats "Kel'Thuzad" --replay-dir "$HOTSDATA_REPLAY_CORPUS_DIR" --limit 2 --random

The command scans replay metadata first, then fully parses matching replays until it has enough examples with `skillshotStats`.

## Test Reports

Generated proof reports live under `docs/skillshot_rules/test_reports/`. The first two-hero pass is `alarak_tyrande_97039.md`.

## Agent Contract

The Coordinator agent owns the hero packet. It creates the branch, keeps the packet current, and ensures one PR covers one hero.

The Research agent must browse current sources for every backlog ability before a rule is implemented. It should capture source URLs, target type, delay, radius, projectile behavior, effect signals, quest counters, and talent interactions.

The Rule Designer agent converts research into a detector spec. It chooses evidence priority, detector type, confidence, windows in gameloops, target scope, and the `evidenceDescription` that will appear in parser output.

The Implementer agent edits the versioned rule set and detector code. It should keep changes scoped to the hero PR.

The Validation agent parses at least two real replays for the hero, records stats, and checks whether rates are plausible.

The Reviewer agent checks for double counting, weak evidence, missing tests, and an incomplete PR summary.

## Per-Hero PR Summary

Every hero PR should include:

- hero and build
- abilities implemented
- abilities reviewed but omitted
- blocked abilities with reason
- source URLs used for mechanics
- example replay stats
- validation commands and results

Use the PR body template embedded in the hero work packet as the starting point.
