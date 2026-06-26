# Skillshot Subagent Consolidation

Build: `97039`

This file consolidates the first all-hero subagent pass. Subagents researched
hero ability mechanics and produced candidate rule specs. The parent process
integrated only rules that fit the existing `area_position_overlap` or
`directional_position_overlap` detectors and had known ability-link evidence.

## Completed Batches

- Lovelace: completed.
- McClintock: completed.
- Anscombe: completed.
- Newton: completed.
- Herschel: completed.

## Integrated First Slice

Coverage after this pass:

- Heroes in catalog: `90`
- Hero ability rows: `1063`
- Implemented skillshot rules: `89`
- Remaining `needs_research`: `132`
- Remaining `needs_triage`: `737`
- `no_rule_likely`: `105`

Implemented rules are still conservative: most new rules use
`geometry_proxy_uncalibrated` because they are geometry-based landing estimates
and have not yet been tuned against hero-specific replay samples.

Integrated heroes and rule counts:

- Alarak: 5
- Ana: 3
- Anduin: 2
- Anub'arak: 1
- Artanis: 2
- Azmodan: 1
- Blaze: 2
- Cassia: 2
- Chen: 2
- Chromie: 2
- Deckard: 2
- Dehaka: 2
- E.T.C.: 1
- Falstad: 3
- Garrosh: 1
- Gazlowe: 3
- Genji: 1
- Greymane: 2
- Gul'dan: 1
- Imperius: 2
- Jaina: 3
- Kael'thas: 2
- Kel'Thuzad: 2
- Leoric: 1
- Maiev: 3
- Malfurion: 2
- Malthael: 1
- Medivh: 1
- Mephisto: 2
- Muradin: 1
- Nova: 2
- Orphea: 4
- Probius: 1
- Raynor: 1
- Sonya: 2
- Stitches: 2
- Stukov: 2
- Thrall: 2
- Tyrael: 2
- Tyrande: 2
- Uther: 1
- Valla: 3
- Varian: 1
- Xul: 1
- Zagara: 2
- Zul'jin: 3

## Representative Integrated Candidates

- Nova: `NovaSnipeStorm`, `NovaPrecisionStrike`.
- Ana: `AnaSleepDart`, `AnaBioticGrenade`, `AnaEyeOfHorusAttack`.
- Gazlowe: `GazloweDethLazor`, `TinkerXplodiumBomb`, `TinkerGravOBomb3000`.
- Jaina: `JainaFrostbolt`, `JainaConeOfCold`, `JainaBlizzard`.
- Kael'thas: `KaelthasFlamestrike`, `KaelthasGravityLapse`.
- Chromie: `ChromieSandBlast`, `ChromieDragonsBreath`.
- Stitches: `StitchesHook`, `StitchesSlam`.
- Orphea: `OrpheaShadowWaltz`, `OrpheaChomp`, `OrpheaDread`, `OrpheaCrushingJaws`.

## Blocked Detector Families

These ability groups were intentionally not integrated in this pass because
they need new detector semantics, not just new rule rows.

- Persistent areas over time: Psionic Storm, Starfall, Slowing Sands, Oil Spill,
  Earthbind Totem full-duration checks.
- Persistent beams/channels: Disintegrate, Planet Cracker, Plasma Cutter,
  Molten Flame.
- Multi-projectile patterns: Magic Missiles, Shuriken, Micro Missiles,
  Cleansing Flame, Angelic Armaments.
- Pet or summon origin: Misha Charge, Gargantuan Stomp, Bunker Flamethrower.
- Ring, trap, or vector wall: Zombie Wall, Time Trap, Force Wall, Null Gate.
- Self/no-target area: Seven-Sided Strike, Spin To Win, Combustion,
  Twilight Dream.
- Thrown-unit collision or displaced-target landing: Garrosh Wrecking Ball and
  similar throw interactions.

## Validation Notes

The first integrated slice passed catalog-row validation: every rule's
`ability_catalog_name` resolves against build `97039`.

Generated coverage file:

- `docs/skillshot_rules/coverage_97039.json`
