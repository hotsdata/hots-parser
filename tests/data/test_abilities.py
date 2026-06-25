from data.abilities import (
    DEFAULT_ABILITY_BUILD,
    HERO_ABILITY_CATALOG_NAMES_BY_BUILD,
    get_ability_catalog_definition,
    get_ability_definition,
    get_hero_ability_definitions,
)
from helpers import get_ability_cmd_index, get_ability_link, get_ability_tag
from models import BaseAbility, TargetPointAbility


def _event(m_abil=None, m_ability_tag=None, m_data=None):
    event = {
        "_gameloop": 160,
        "_userid": {"m_userId": 1},
        "m_abil": m_abil,
        "m_data": m_data or {"None": None},
    }
    if m_ability_tag is not None:
        event["m_abilityTag"] = m_ability_tag
    return event


def test_ability_tag_splits_link_and_command_index_from_packed_tag():
    event = _event(m_ability_tag=3552)

    assert get_ability_tag(event) == 3552
    assert get_ability_link(event) == 111
    assert get_ability_cmd_index(event) == 0


def test_ability_definition_requires_game_version():
    assert get_ability_definition(1105, 0) is None


def test_ability_definition_resolves_localized_name_from_link_and_command_index():
    definition = get_ability_definition(1105, 0, DEFAULT_ABILITY_BUILD)

    assert definition is not None
    assert definition.catalog_name == "KelThuzadFrostNova"
    assert definition.display_name == "Frost Nova"


def test_ability_definition_resolves_localized_name_for_matching_build():
    definition = get_ability_definition(1105, 0, DEFAULT_ABILITY_BUILD)

    assert definition is not None
    assert definition.catalog_name == "KelThuzadFrostNova"
    assert definition.display_name == "Frost Nova"


def test_ability_definition_does_not_cross_builds():
    assert get_ability_definition(1105, 0, DEFAULT_ABILITY_BUILD + 1) is None


def test_current_build_catalog_contains_all_playable_heroes():
    hero_abilities = HERO_ABILITY_CATALOG_NAMES_BY_BUILD[DEFAULT_ABILITY_BUILD]

    assert len(hero_abilities) == 90
    assert "Cho" in hero_abilities
    assert "Gall" in hero_abilities
    assert "Hogger" in hero_abilities
    assert "ChoGallBundleProduct" not in hero_abilities


def test_ability_catalog_definition_resolves_current_hero_abilities():
    hogger_definition = get_ability_catalog_definition("HoggerEzThroDynamite", DEFAULT_ABILITY_BUILD)
    cho_definition = get_ability_catalog_definition("ChoUpheaval", DEFAULT_ABILITY_BUILD)
    gall_definition = get_ability_catalog_definition("GallShadowflame", DEFAULT_ABILITY_BUILD)
    deathwing_definition = get_ability_catalog_definition("DeathwingMoltenFlame", DEFAULT_ABILITY_BUILD)

    assert hogger_definition is not None
    assert hogger_definition.hero_catalog_name == "Hogger"
    assert hogger_definition.hero_name == "Hogger"
    assert hogger_definition.display_name == "Ez-Thro Dynamite"
    assert cho_definition is not None
    assert cho_definition.hero_catalog_name == "Cho"
    assert cho_definition.display_name == "Upheaval"
    assert gall_definition is not None
    assert gall_definition.hero_catalog_name == "Gall"
    assert gall_definition.display_name == "Shadowflame"
    assert deathwing_definition is not None
    assert deathwing_definition.hero_catalog_name == "Deathwing"
    assert deathwing_definition.display_name == "Molten Flame"


def test_hero_ability_definitions_returns_all_current_hero_catalog_rows():
    definitions = get_hero_ability_definitions("Azmodan", DEFAULT_ABILITY_BUILD)

    assert {definition.catalog_name for definition in definitions} >= {
        "AzmodanAllShallBurn",
        "AzmodanDemonicInvasion",
        "AzmodanGlobeOfAnnihilation",
        "AzmodanSummonDemonWarrior",
    }
    assert {definition.hero_name for definition in definitions} == {"Azmodan"}


def test_base_ability_assigns_name_from_packed_tag():
    ability = BaseAbility(_event(m_ability_tag=3552), DEFAULT_ABILITY_BUILD)

    assert ability.gameVersion == DEFAULT_ABILITY_BUILD
    assert ability.abilityTag == 3552
    assert ability.abilityLink == 111
    assert ability.abilityCmdIndex == 0
    assert ability.abilityCatalogName == "Mount"
    assert ability.abilityName == "Mount"


def test_target_point_ability_assigns_name_from_replay_ability_link():
    ability = TargetPointAbility(
        _event(
            m_abil={"m_abilLink": 1105, "m_abilCmdIndex": 0, "m_abilCmdData": None},
            m_data={"TargetPoint": {"x": 4096, "y": 8192, "z": 0}},
        ),
        DEFAULT_ABILITY_BUILD,
    )

    assert ability.gameVersion == DEFAULT_ABILITY_BUILD
    assert ability.abilityTag == 35360
    assert ability.abilityLink == 1105
    assert ability.abilityCmdIndex == 0
    assert ability.abilityCatalogName == "KelThuzadFrostNova"
    assert ability.abilityName == "Frost Nova"
