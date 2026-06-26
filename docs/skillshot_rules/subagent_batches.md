# Skillshot Subagent Batches

Build: `97039`

This file tracks the distributed pass over heroes that do not yet have complete
landing-rate coverage. Subagents produce candidate rule specs first. The parent
integrates only rules that fit an existing detector and have a clear observed
ability link. Risky or detector-missing abilities stay blocked until the detector
exists.

## Integration Criteria

- Existing detector only: `same_user_followup`, `area_position_overlap`, or `directional_position_overlap`.
- Observed `abilityLink` and `abilityCmdIndex` must be known from replay candidates or current ability mapping.
- Rule confidence must be marked as calibrated only after replay stats are checked. Otherwise use an uncalibrated proxy confidence.
- Persistent-area, chained multi-event, summon-minion, damage-over-time, or buff-triggered skills are blocked unless a detector already supports that behavior.
- No central rule-set changes should be made directly by subagents in this pass.

## Batches

- Lovelace: completed. Nova, Sylvanas, Ana, Gazlowe, Qhira, Ragnaros, Gall, Hanzo, Jaina, Lt. Morales, Sgt. Hammer, Tychus, Xul.
- McClintock: completed. Artanis, Kael'thas, Li-Ming, Maiev, Rexxar, Sonya, Stitches, Valeera, Varian, Chromie, D.Va, Deathwing, Fenix, Genji, Imperius, Malfurion.
- Anscombe: completed. Medivh, Mephisto, Samuro, The Butcher, Thrall, Valla, Abathur, Anduin, Anub'arak, Arthas, Auriel, Brightwing, Cho, Diablo, Falstad, Hogger, Illidan, Johanna.
- Newton: completed. Kerrigan, Kharazim, Lunara, Lúcio, Malthael, Muradin, Nazeebo, Probius, Raynor, Rehgar, Tassadar, The Lost Vikings, Tracer, Zarya, Zeratul, Alexstrasza, Azmodan, Blaze.
- Herschel: completed. Cassia, Chen, Deckard, Dehaka, E.T.C., Garrosh, Greymane, Gul'dan, Junkrat, Leoric, Li Li, Mal'Ganis, Mei, Murky, Orphea, Stukov, Tyrael, Uther, Whitemane, Yrel, Zagara, Zul'jin.

## Consolidation

The first integrated slice is recorded in
`docs/skillshot_rules/subagent_consolidation_97039.md`. It includes 89 total
implemented rules for build `97039`; remaining candidates are blocked on either
hero-specific calibration or new detector families.
