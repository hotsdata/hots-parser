from collections import OrderedDict
from types import SimpleNamespace

from data.abilities import DEFAULT_ABILITY_BUILD
from models import BaseAbility, TargetPointAbility
from replay.skillshot_landing import SkillshotQuestEvent, apply_skillshot_landing_stats


def _ability(ability_link, gameloop, user_id=7):
    return BaseAbility(
        {
            "_event": "NNet.Game.SCmdEvent",
            "_gameloop": gameloop,
            "_userid": {"m_userId": user_id},
            "m_abil": {
                "m_abilLink": ability_link,
                "m_abilCmdIndex": 0,
                "m_abilCmdData": None,
            },
            "m_data": {"None": None},
        },
        DEFAULT_ABILITY_BUILD,
    )


def _target_point_ability(ability_link, gameloop, x, y, user_id=7):
    return TargetPointAbility(
        {
            "_event": "NNet.Game.SCmdEvent",
            "_gameloop": gameloop,
            "_userid": {"m_userId": user_id},
            "m_abil": {
                "m_abilLink": ability_link,
                "m_abilCmdIndex": 0,
                "m_abilCmdData": None,
            },
            "m_data": {"TargetPoint": {"x": x * 4096, "y": y * 4096, "z": 0}},
        },
        DEFAULT_ABILITY_BUILD,
    )


def _hero(casts, name="Kel'Thuzad", player_id=6, team=0, unit_tag=100):
    return SimpleNamespace(
        name=name,
        playerId=player_id,
        team=team,
        unitTag=unit_tag,
        generalStats={
            "castedAbilities": OrderedDict((cast.castedAtGameLoops, cast) for cast in casts),
            "skillshotStats": {},
        },
    )


def test_kelthuzad_chains_uses_followup_as_landing_proxy():
    hero = _hero(
        [
            _ability(1111, 100),
            _ability(1112, 112),
            _ability(1111, 300),
        ]
    )

    apply_skillshot_landing_stats({6: hero}, DEFAULT_ABILITY_BUILD)

    chains = hero.generalStats["skillshotStats"]["KelThuzadChains"]
    assert chains["totalAttempts"] == 2
    assert chains["landed"] == 1
    assert chains["missed"] == 1
    assert chains["hitRate"] == 0.5
    assert chains["confidence"] == "proxy"
    assert chains["landedByEvidence"] == {"followup_ability": 1}
    assert chains["sampleEvidence"] == [
        {
            "castGameLoop": 100,
            "evidenceType": "followup_ability",
            "evidenceGameLoop": 112,
            "deltaGameloops": 12,
            "evidenceAbilityLink": 1112,
            "evidenceAbilityCmdIndex": 0,
            "evidenceAbilityName": "Chains of Kel'Thuzad",
            "evidenceEventName": None,
            "evidenceValue": None,
        }
    ]


def test_kelthuzad_chains_uses_quest_counter_as_first_contact_proxy():
    hero = _hero([_ability(1111, 100), _ability(1111, 300)])
    quest_events = (
        SkillshotQuestEvent(
            event_name="KelThuzadMasterOfTheColdDark",
            gameloop=118,
            player_id=6,
            value=12,
        ),
    )

    apply_skillshot_landing_stats({6: hero}, DEFAULT_ABILITY_BUILD, quest_events)

    chains = hero.generalStats["skillshotStats"]["KelThuzadChains"]
    assert chains["totalAttempts"] == 2
    assert chains["landed"] == 1
    assert chains["missed"] == 1
    assert chains["landedByEvidence"] == {"quest_counter": 1}
    assert chains["sampleEvidence"] == [
        {
            "castGameLoop": 100,
            "evidenceType": "quest_counter",
            "evidenceGameLoop": 118,
            "deltaGameloops": 18,
            "evidenceAbilityLink": None,
            "evidenceAbilityCmdIndex": None,
            "evidenceAbilityName": None,
            "evidenceEventName": "KelThuzadMasterOfTheColdDark",
            "evidenceValue": 12,
        }
    ]


def test_kelthuzad_chains_does_not_match_followup_after_next_attempt():
    hero = _hero(
        [
            _ability(1111, 100),
            _ability(1111, 120),
            _ability(1112, 130),
        ]
    )

    apply_skillshot_landing_stats({6: hero}, DEFAULT_ABILITY_BUILD)

    chains = hero.generalStats["skillshotStats"]["KelThuzadChains"]
    assert chains["totalAttempts"] == 2
    assert chains["landed"] == 1
    assert chains["missed"] == 1


def test_skillshot_rules_are_versioned_by_build():
    hero = _hero([_ability(1111, 100), _ability(1112, 112)])

    apply_skillshot_landing_stats({6: hero}, DEFAULT_ABILITY_BUILD + 1)

    assert hero.generalStats["skillshotStats"] == {}


def test_kelthuzad_frost_nova_counts_enemy_heroes_inside_effective_radius():
    hero = _hero([_target_point_ability(1105, 100, 10, 10)], player_id=6, team=0, unit_tag=1)
    enemy_hit = _hero([], name="Enemy Hit", player_id=2, team=1, unit_tag=2)
    enemy_miss = _hero([], name="Enemy Miss", player_id=3, team=1, unit_tag=3)
    ally_inside_area = _hero([], name="Ally", player_id=4, team=0, unit_tag=4)
    units = {
        2: SimpleNamespace(positions={7: [11.0, 10.0]}),
        3: SimpleNamespace(positions={7: [17.0, 10.0]}),
        4: SimpleNamespace(positions={7: [10.0, 10.0]}),
    }

    apply_skillshot_landing_stats(
        {6: hero, 2: enemy_hit, 3: enemy_miss, 4: ally_inside_area},
        DEFAULT_ABILITY_BUILD,
        units_in_game=units,
    )

    frost_nova = hero.generalStats["skillshotStats"]["KelThuzadFrostNova"]
    assert frost_nova["totalAttempts"] == 1
    assert frost_nova["landed"] == 1
    assert frost_nova["missed"] == 0
    assert frost_nova["hitRate"] == 1.0
    assert frost_nova["totalTargetsHit"] == 1
    assert frost_nova["rootedHeroUnits"] == 1
    assert frost_nova["sampleEvidence"] == [
        {
            "castGameLoop": 100,
            "evidenceType": "area_position_overlap",
            "evidenceGameLoop": 116,
            "deltaGameloops": 16,
            "evidenceAbilityLink": None,
            "evidenceAbilityCmdIndex": None,
            "evidenceAbilityName": None,
            "evidenceEventName": None,
            "evidenceValue": None,
            "targetCount": 1,
            "targetHeroNames": ["Enemy Hit"],
            "targetPlayerIds": [2],
            "targetDistances": [1.0],
        }
    ]


def test_kelthuzad_frost_nova_misses_when_no_enemy_hero_is_inside_effective_radius():
    hero = _hero([_target_point_ability(1105, 100, 10, 10)], player_id=6, team=0, unit_tag=1)
    enemy = _hero([], name="Enemy", player_id=2, team=1, unit_tag=2)
    units = {2: SimpleNamespace(positions={7: [17.0, 10.0]})}

    apply_skillshot_landing_stats({6: hero, 2: enemy}, DEFAULT_ABILITY_BUILD, units_in_game=units)

    frost_nova = hero.generalStats["skillshotStats"]["KelThuzadFrostNova"]
    assert frost_nova["totalAttempts"] == 1
    assert frost_nova["landed"] == 0
    assert frost_nova["missed"] == 1
    assert frost_nova["hitRate"] == 0.0
    assert frost_nova["totalTargetsHit"] == 0
    assert frost_nova["rootedHeroUnits"] == 0
    assert frost_nova["sampleEvidence"] == []


def test_kelthuzad_frost_nova_uses_quest_counter_as_root_proxy():
    hero = _hero([_target_point_ability(1105, 100, 10, 10)], player_id=6, team=0, unit_tag=1)
    enemy = _hero([], name="Enemy", player_id=2, team=1, unit_tag=2)
    quest_events = (
        SkillshotQuestEvent(
            event_name="KelThuzadMasterOfTheColdDark",
            gameloop=118,
            player_id=6,
            value=12,
        ),
    )
    units = {2: SimpleNamespace(positions={7: [17.0, 10.0]})}

    apply_skillshot_landing_stats(
        {6: hero, 2: enemy},
        DEFAULT_ABILITY_BUILD,
        quest_events,
        units_in_game=units,
    )

    frost_nova = hero.generalStats["skillshotStats"]["KelThuzadFrostNova"]
    assert frost_nova["landed"] == 1
    assert frost_nova["landedByEvidence"] == {"quest_counter": 1}
    assert frost_nova["rootedHeroUnits"] == 1
    assert frost_nova["sampleEvidence"] == [
        {
            "castGameLoop": 100,
            "evidenceType": "quest_counter",
            "evidenceGameLoop": 118,
            "deltaGameloops": 18,
            "evidenceAbilityLink": None,
            "evidenceAbilityCmdIndex": None,
            "evidenceAbilityName": None,
            "evidenceEventName": "KelThuzadMasterOfTheColdDark",
            "evidenceValue": 12,
            "targetCount": 1,
            "targetHeroNames": [],
            "targetPlayerIds": [],
            "targetDistances": [],
        }
    ]


def test_kelthuzad_frost_nova_deduplicates_target_point_updates():
    hero = _hero(
        [
            _target_point_ability(1105, 100, 10, 10),
            _target_point_ability(1105, 102, 30, 30),
        ],
        player_id=6,
        team=0,
        unit_tag=1,
    )
    enemy = _hero([], name="Enemy", player_id=2, team=1, unit_tag=2)
    units = {2: SimpleNamespace(positions={7: [10.5, 10.0]})}

    apply_skillshot_landing_stats({6: hero, 2: enemy}, DEFAULT_ABILITY_BUILD, units_in_game=units)

    frost_nova = hero.generalStats["skillshotStats"]["KelThuzadFrostNova"]
    assert frost_nova["totalAttempts"] == 1
    assert frost_nova["landed"] == 1
    assert frost_nova["rootedHeroUnits"] == 1
    assert frost_nova["sampleEvidence"][0]["castGameLoop"] == 100


def test_alarak_discord_strike_counts_enemy_heroes_inside_triangle():
    hero = _hero([_target_point_ability(926, 100, 20, 10)], name="Alarak", player_id=6, team=0, unit_tag=1)
    enemy_hit = _hero([], name="Enemy Hit", player_id=2, team=1, unit_tag=2)
    enemy_miss = _hero([], name="Enemy Miss", player_id=3, team=1, unit_tag=3)
    units = {
        1: SimpleNamespace(positions={6: [10.0, 10.0]}),
        2: SimpleNamespace(positions={6: [13.0, 10.0]}),
        3: SimpleNamespace(positions={6: [13.0, 15.0]}),
    }

    apply_skillshot_landing_stats({6: hero, 2: enemy_hit, 3: enemy_miss}, DEFAULT_ABILITY_BUILD, units_in_game=units)

    discord_strike = hero.generalStats["skillshotStats"]["AlarakDiscordStrike"]
    assert discord_strike["totalAttempts"] == 1
    assert discord_strike["landed"] == 1
    assert discord_strike["hitRate"] == 1.0
    assert discord_strike["totalTargetsHit"] == 1
    assert discord_strike["silencedHeroUnits"] == 1
    assert discord_strike["sampleEvidence"][0]["targetHeroNames"] == ["Enemy Hit"]


def test_alarak_deadly_charge_counts_enemy_heroes_along_charge_line():
    hero = _hero([_target_point_ability(927, 100, 28, 10)], name="Alarak", player_id=6, team=0, unit_tag=1)
    enemy_hit = _hero([], name="Enemy Hit", player_id=2, team=1, unit_tag=2)
    enemy_miss = _hero([], name="Enemy Miss", player_id=3, team=1, unit_tag=3)
    units = {
        1: SimpleNamespace(positions={6: [10.0, 10.0]}),
        2: SimpleNamespace(positions={6: [15.0, 11.0]}),
        3: SimpleNamespace(positions={6: [15.0, 13.0]}),
    }

    apply_skillshot_landing_stats({6: hero, 2: enemy_hit, 3: enemy_miss}, DEFAULT_ABILITY_BUILD, units_in_game=units)

    deadly_charge = hero.generalStats["skillshotStats"]["AlarakDeadlyChargeExecute"]
    assert deadly_charge["totalAttempts"] == 1
    assert deadly_charge["landed"] == 1
    assert deadly_charge["totalTargetsHit"] == 1
    assert deadly_charge["deadlyChargeHeroUnits"] == 1
    assert deadly_charge["sampleEvidence"][0]["targetHeroNames"] == ["Enemy Hit"]


def test_tyrande_sentinel_counts_first_enemy_hero_on_projectile_line():
    hero = _hero([_target_point_ability(170, 100, 100, 10)], name="Tyrande", player_id=6, team=0, unit_tag=1)
    enemy_first = _hero([], name="Enemy First", player_id=2, team=1, unit_tag=2)
    enemy_second = _hero([], name="Enemy Second", player_id=3, team=1, unit_tag=3)
    units = {
        1: SimpleNamespace(positions={6: [10.0, 10.0]}),
        2: SimpleNamespace(positions={6: [20.0, 10.5], 7: [20.0, 10.5]}),
        3: SimpleNamespace(positions={6: [30.0, 10.0], 7: [30.0, 10.0]}),
    }

    apply_skillshot_landing_stats(
        {6: hero, 2: enemy_first, 3: enemy_second},
        DEFAULT_ABILITY_BUILD,
        units_in_game=units,
    )

    sentinel = hero.generalStats["skillshotStats"]["TyrandeSentinelShot"]
    assert sentinel["totalAttempts"] == 1
    assert sentinel["landed"] == 1
    assert sentinel["totalTargetsHit"] == 1
    assert sentinel["sentinelHeroUnits"] == 1
    assert sentinel["sampleEvidence"][0]["targetHeroNames"] == ["Enemy First"]


def test_tyrande_lunar_flare_counts_enemy_heroes_inside_delayed_area():
    hero = _hero([_target_point_ability(674, 100, 20, 20)], name="Tyrande", player_id=6, team=0, unit_tag=1)
    enemy_hit = _hero([], name="Enemy Hit", player_id=2, team=1, unit_tag=2)
    enemy_miss = _hero([], name="Enemy Miss", player_id=3, team=1, unit_tag=3)
    units = {
        2: SimpleNamespace(positions={7: [21.0, 20.0]}),
        3: SimpleNamespace(positions={7: [30.0, 20.0]}),
    }

    apply_skillshot_landing_stats({6: hero, 2: enemy_hit, 3: enemy_miss}, DEFAULT_ABILITY_BUILD, units_in_game=units)

    lunar_flare = hero.generalStats["skillshotStats"]["TyrandeLunarFlare"]
    assert lunar_flare["totalAttempts"] == 1
    assert lunar_flare["landed"] == 1
    assert lunar_flare["totalTargetsHit"] == 1
    assert lunar_flare["stunnedHeroUnits"] == 1
    assert lunar_flare["sampleEvidence"][0]["targetHeroNames"] == ["Enemy Hit"]
