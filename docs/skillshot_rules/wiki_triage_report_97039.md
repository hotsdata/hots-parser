# Wiki Triage Report

Build: `97039`

Generated: `2026-06-26`

Source: current Heroes of the Storm Wiki `Data:<Hero>` pages, fetched through
the public Fandom MediaWiki API. The generated parsed source cache is
`docs/skillshot_rules/wiki_ability_sources_97039.json`.

## Summary

Before wiki triage, coverage had:

- `implemented`: `89`
- `needs_research`: `132`
- `needs_triage`: `737`
- `no_rule_likely`: `105`

After matching current wiki ability/talent descriptions:

- `implemented`: `89`
- `rule_candidate_existing_detector`: `104`
- `blocked_new_detector`: `228`
- `no_rule_likely`: `449`
- `needs_manual_review`: `89`
- `wiki_unmatched`: `104`

For the original `737` `needs_triage` abilities specifically:

- `360` are now `no_rule_likely`.
- `167` are now `blocked_new_detector`.
- `62` are now `rule_candidate_existing_detector`.
- `70` still need manual review after a wiki match.
- `78` were not matched to a wiki ability/talent entry.

That leaves `148` unresolved triage rows (`70` manual review + `78` unmatched),
down from `737`.

## Candidate Existing Detectors

The wiki pass found `62` original triage rows that appear implementable with
existing detector families:

- `31` `directional_position_overlap`
- `31` `area_position_overlap`

Examples:

- Abathur: `AbathurSymbioteStab` / Stab -> `directional_position_overlap`
- Alexstrasza: `AlexstraszaWingBuffet` / Wing Buffet -> `area_position_overlap`
- Ana: `AnaEyeOfHorusAttackDummy` / High Powered Round -> `area_position_overlap`
- The Butcher: `ButcherHamstring` / Hamstring -> `area_position_overlap`
- D.Va: `DVaPilotConcussivePulse` / Concussive Pulse -> `area_position_overlap`
- Deathwing: `DeathwingSkyfall` / Skyfall -> `area_position_overlap`

## Blocked Detector Families

The wiki pass found `167` original triage rows that look relevant but need
detectors we do not have yet:

- `54` `persistent_area`
- `37` `channel_or_beam`
- `31` `source_centered_area`
- `29` `summon_or_pet_origin`
- `15` `trap_trigger`
- `1` `multi_projectile`

Examples:

- Abathur: `AbathurToxicNest` / Toxic Nest -> `trap_trigger`
- Abathur: `AbathurSymbioteSpikeBurst` / Spike Burst -> `source_centered_area`
- Alexstrasza: `AlexstraszaCleansingFlame` / Cleansing Flame -> `persistent_area`
- Cassia: `AmazonValkyrie` / Valkyrie -> `summon_or_pet_origin`
- Artanis: `ArtanisBladeDash` / Blade Dash -> `persistent_area`
- Arthas: `ArthasFrozenTempest` / Frozen Tempest -> `source_centered_area`

## Remaining Manual Review

The wiki pass matched but did not confidently classify `70` original triage rows.
Common causes:

- vector targeting, such as Alarak Telekinesis or Deckard Lorenado
- mode/activation abilities, such as Ana Eye of Horus activation
- modifiers or secondary detonation commands
- unclear catalog rows where the display name maps to a broad wiki entry

Top heroes by remaining manual review:

- Sgt. Hammer: `4`
- Deckard: `3`
- Lunara: `3`
- Gall: `3`
- Junkrat: `3`
- Maiev: `3`

## Unmatched Rows

The wiki pass did not match `78` original triage rows to a wiki ability/talent
entry. These are often internal commands, dummy abilities, hero-specific mode
rows, or variant catalog rows.

Top heroes by unmatched original triage rows:

- Deathwing: `12`
- The Lost Vikings: `6`
- Rexxar: `5`
- Zagara: `5`
- Lúcio: `4`
- Tracer: `4`

## Generated Artifacts

- `docs/skillshot_rules/wiki_ability_sources_97039.json`
- `docs/skillshot_rules/wiki_triage_97039.json`

Regenerate with:

```bash
.venv/bin/python scripts/skillshot_rule_pipeline.py wiki-triage --refresh --source-cache docs/skillshot_rules/wiki_ability_sources_97039.json --out docs/skillshot_rules/wiki_triage_97039.json
```
