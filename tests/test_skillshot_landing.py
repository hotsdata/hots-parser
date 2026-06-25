from collections import OrderedDict
from types import SimpleNamespace

from data.abilities import DEFAULT_ABILITY_BUILD
from models import BaseAbility
from replay.skillshot_landing import apply_skillshot_landing_stats


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


def _hero(casts):
    return SimpleNamespace(
        name="Kel'Thuzad",
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
    assert chains["sampleEvidence"] == [
        {
            "castGameLoop": 100,
            "evidenceGameLoop": 112,
            "deltaGameloops": 12,
            "evidenceAbilityLink": 1112,
            "evidenceAbilityCmdIndex": 0,
            "evidenceAbilityName": "Chains of Kel'Thuzad",
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
