# Alarak and Tyrande Skillshot Rule Test

Build: `97039`

## Implemented Rules

- `AlarakDiscordStrike`: directional triangle proxy for Discord Strike.
- `AlarakCounterStrikeTargeted`: directional triangle proxy for Counter-Strike.
- `AlarakCounterStrikeTargeted2ndHeroic`: directional triangle proxy for second-heroic Counter-Strike.
- `AlarakDeadlyChargeExecute`: directional line proxy for Deadly Charge.
- `AlarakDeadlyChargeExecute2ndHeroic`: directional line proxy for second-heroic Deadly Charge.
- `TyrandeSentinelShot`: projectile line proxy for Sentinel.
- `TyrandeLunarFlare`: delayed area-position proxy for Lunar Flare.

## Research Notes

- Alarak Discord Strike is a point-targeted triangular area after a 0.625 second cast delay.
- Alarak Counter-Strike is a point-targeted triangular shockwave after a one-second channel, but only fires if Alarak took enemy-Hero damage.
- Alarak Deadly Charge travels forward after channel release and damages enemies in Alarak's path.
- Tyrande Sentinel is a global point-targeted projectile that hits the first enemy Hero by default.
- Tyrande Lunar Flare is a delayed point-targeted circular area that stuns enemies.
- Tyrande Starfall was not implemented in this pass because it is a persistent area over time, not a single landing event.

## Example Replay Stats

### Alarak

Command:

```bash
.venv/bin/python scripts/skillshot_rule_pipeline.py example-stats Alarak --replay-dir "/media/crorella/44108A78108A70AA/Users/crore/OneDrive/Documents/Heroes of the Storm/Accounts/222876/1-Hero-1-1440382/Replays/Multiplayer" --limit 2 --random --seed 101
```

`2026-06-14 22.05.55 Lost Cavern.StormReplay`

- Discord Strike: attempts=58, landed=17, hitRate=29.31%, totalTargetsHit=19.
- Counter-Strike: attempts=0.
- Unleash Deadly Charge: attempts=8, landed=4, hitRate=50.00%, totalTargetsHit=5.

`2026-06-07 12.41.26 Braxis Holdout.StormReplay`

- Discord Strike: attempts=58, landed=17, hitRate=29.31%, totalTargetsHit=27.
- Counter-Strike: attempts=8, landed=4, hitRate=50.00%, totalTargetsHit=5.
- Unleash Deadly Charge: attempts=0.

### Tyrande

Command:

```bash
.venv/bin/python scripts/skillshot_rule_pipeline.py example-stats Tyrande --replay-dir "/media/crorella/44108A78108A70AA/Users/crore/OneDrive/Documents/Heroes of the Storm/Accounts/222876/1-Hero-1-1440382/Replays/Multiplayer" --limit 2 --random --seed 202
```

`2026-05-25 20.35.24 Braxis Outpost.StormReplay`

- Sentinel: attempts=48, landed=30, hitRate=62.50%, totalTargetsHit=30.
- Lunar Flare: attempts=75, landed=54, hitRate=72.00%, totalTargetsHit=94.

`2026-06-12 22.28.50 Towers of Doom.StormReplay`

- Sentinel: attempts=64, landed=22, hitRate=34.38%, totalTargetsHit=22.
- Lunar Flare: attempts=46, landed=15, hitRate=32.61%, totalTargetsHit=19.

## Follow-Up Calibration

- Discord Strike likely needs calibration against known talent quest progress or damage/stun/silence tracker signals if available; geometry alone looks conservative in the sampled replays.
- Counter-Strike needs a stronger trigger signal because geometry alone cannot prove that Alarak took enemy-Hero damage during the channel.
- Starfall needs a persistent-area detector that checks enemy Hero occupancy across the duration, not only at cast time.
