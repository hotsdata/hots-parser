from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from data.ability_catalog_97039 import ABILITY_CATALOG_ROWS_97039


@dataclass(frozen=True)
class AbilityDefinition:
    catalog_name: str
    display_name: str
    hero_catalog_name: str | None = None
    hero_name: str | None = None


DEFAULT_ABILITY_BUILD = 97039


def _catalog_definitions(
    rows: tuple[tuple[str, str | None, str | None, str], ...],
) -> dict[str, AbilityDefinition]:
    return {
        catalog_name: AbilityDefinition(catalog_name, display_name, hero_catalog_name, hero_name)
        for catalog_name, hero_catalog_name, hero_name, display_name in rows
    }


def _hero_ability_catalog_names(
    rows: tuple[tuple[str, str | None, str | None, str], ...],
) -> dict[str, tuple[str, ...]]:
    hero_abilities: defaultdict[str, list[str]] = defaultdict(list)
    for catalog_name, hero_catalog_name, _, _ in rows:
        if hero_catalog_name is not None:
            hero_abilities[hero_catalog_name].append(catalog_name)
    return {hero_catalog_name: tuple(catalog_names) for hero_catalog_name, catalog_names in hero_abilities.items()}


ABILITY_CATALOG_DEFINITIONS_97039 = _catalog_definitions(ABILITY_CATALOG_ROWS_97039)

HERO_ABILITY_CATALOG_NAMES_97039 = _hero_ability_catalog_names(ABILITY_CATALOG_ROWS_97039)


# Build 97039 ability catalog links observed in the replay fixture and checked
# against local HeroesData catalog XML / localized GameStrings data.
ABILITY_DEFINITIONS_97039: dict[tuple[int, int], AbilityDefinition] = {
    # Generic replay command links observed in the fixture. These are not
    # localized hero spell catalog entries, but naming them keeps the ordered
    # dict readable while preserving link/cmd metadata for later refinement.
    (22, 3): AbilityDefinition("ReplayCommand22Cmd3", "Replay Command 22:3"),
    (22, 4): AbilityDefinition("ReplayCommand22Cmd4", "Replay Command 22:4"),
    (24, 0): AbilityDefinition("ReplayCommand24", "Replay Command 24"),
    (26, 0): AbilityDefinition("ReplayCommand26", "Replay Command 26"),
    (41, 0): AbilityDefinition("ReplayCommand41Cmd0", "Replay Command 41:0"),
    (41, 1): AbilityDefinition("ReplayCommand41Cmd1", "Replay Command 41:1"),
    (66, 0): AbilityDefinition("ReplayCommand66", "Replay Command 66"),
    (172, 0): AbilityDefinition("ReplayCommand172", "Replay Command 172"),
    (182, 0): AbilityDefinition("ReplayCommand182", "Replay Command 182"),
    (183, 0): AbilityDefinition("ReplayCommand183", "Replay Command 183"),
    (188, 0): AbilityDefinition("ReplayCommand188", "Replay Command 188"),
    (111, 0): AbilityDefinition("Mount", "Mount"),
    # Azmodan
    (244, 0): AbilityDefinition("AzmodanAllShallBurn", "All Shall Burn"),
    (247, 0): AbilityDefinition("AzmodanDemonLieutenant", "Demon Lieutenant"),
    (249, 0): AbilityDefinition("AzmodanDemonicInvasion", "Demonic Invasion"),
    (250, 0): AbilityDefinition("AzmodanGlobeOfAnnihilation", "Globe of Annihilation"),
    (251, 0): AbilityDefinition("AzmodanSummonDemonWarrior", "Summon Demon Warrior"),
    # Diablo
    (324, 0): AbilityDefinition("DiabloApocalypse", "Apocalypse"),
    (325, 0): AbilityDefinition("DiabloHellgate", "Hellgate"),
    (327, 0): AbilityDefinition("DiabloOverpower", "Overpower"),
    (328, 0): AbilityDefinition("DiabloShadowCharge", "Shadow Charge"),
    (330, 0): AbilityDefinition("DiabloFireStomp", "Fire Stomp"),
    (331, 0): AbilityDefinition("DiabloBlackSoulstoneSoulShield", "Soul Shield"),
    # Gazlowe / Tinker
    (625, 0): AbilityDefinition("TinkerFocusTurrets", "Focus Turrets!"),
    (627, 0): AbilityDefinition("TinkerXplodiumBomb", "Xplodium Charge"),
    (628, 0): AbilityDefinition("TinkerGravOBomb3000", "Grav-O-Bomb 3000"),
    (629, 0): AbilityDefinition("TinkerRockItTurret", "Rock-It! Turret"),
    (631, 0): AbilityDefinition("TinkerDethLazorCharged", "Deth Lazor"),
    # Hogger
    (1315, 0): AbilityDefinition("HoggerCancelHoggWild", "Cancel Hogg Wild"),
    (1316, 0): AbilityDefinition("HoggerStaggeringBlow", "Staggering Blow"),
    (1317, 0): AbilityDefinition("HoggerCancelLootHoard", "Cancel Loot Hoard"),
    (1318, 0): AbilityDefinition("HoggerEzThroDynamite", "Ez-Thro Dynamite"),
    (1321, 0): AbilityDefinition("HoggerHoggWild", "Hogg Wild"),
    (1324, 0): AbilityDefinition("HoggerLootHoard", "Loot Hoard"),
    (1325, 0): AbilityDefinition("HoggerShockwave", "Shockwave"),
    # Kel'Thuzad
    (1105, 0): AbilityDefinition("KelThuzadFrostNova", "Frost Nova"),
    (1106, 0): AbilityDefinition("KelThuzadShadowFissure", "Shadow Fissure"),
    (1107, 0): AbilityDefinition("KelThuzadPhylacteryItem", "Phylactery of Kel'Thuzad"),
    (1108, 0): AbilityDefinition("KelThuzadSpawnShade", "The Damned Return"),
    (1109, 0): AbilityDefinition("KelThuzadChainsPull", "Chains Pull"),
    (1110, 0): AbilityDefinition("KelThuzadShiftingMalice", "Shifting Malice"),
    (1111, 0): AbilityDefinition("KelThuzadChains", "Chains of Kel'Thuzad"),
    (1112, 0): AbilityDefinition("KelThuzadChainsLink", "Chains of Kel'Thuzad"),
    (1113, 0): AbilityDefinition("KelThuzadDeathAndDecay", "Death and Decay"),
    (1114, 0): AbilityDefinition("KelThuzadFrozenTomb", "Frost Blast"),
    (1115, 0): AbilityDefinition("KelThuzadArchlichArmor", "Armor of the Archlich"),
    (1116, 0): AbilityDefinition("KelThuzadGlacialSpike", "Glacial Spike"),
    (1117, 0): AbilityDefinition("KelThuzadDeathAndDecayShade", "Death and Decay"),
    # Maiev
    (1151, 0): AbilityDefinition("MaievSpiritOfVengeance", "Spirit of Vengeance"),
    (1152, 0): AbilityDefinition("MaievSpiritOfVengeanceBlink", "Blink"),
    (1153, 0): AbilityDefinition("MaievFanOfKnives", "Fan of Knives"),
    (1154, 0): AbilityDefinition("MaievUmbralBind", "Umbral Bind"),
    (1155, 0): AbilityDefinition("MaievContainmentDisc", "Containment Disc"),
    (1156, 0): AbilityDefinition("MaievContainmentDiscContain", "Contain"),
    (1157, 0): AbilityDefinition("MaievWardensCage", "Warden's Cage"),
    (1158, 0): AbilityDefinition("MaievVaultOfTheWardens", "Vault of the Wardens"),
    (1159, 0): AbilityDefinition("MaievFanOfKnivesNaishasMemento", "Naisha's Memento"),
    (1160, 0): AbilityDefinition("MaievSpiritOfVengeanceShadowOrbVengeance", "Shadow Orb: Vengeance"),
    (1161, 0): AbilityDefinition("MaievShadowOrbHuntress", "Shadow Orb: Huntress"),
    (1162, 0): AbilityDefinition("MaievShadowOrbShadowStrike", "Shadow Orb: Shadow Strike"),
    # Muradin
    (494, 0): AbilityDefinition("MuradinStormbolt", "Storm Bolt"),
    (496, 0): AbilityDefinition("MuradinDwarfToss", "Dwarf Toss"),
    (497, 0): AbilityDefinition("MuradinThunderclap", "Thunder Clap"),
    # Nova
    (521, 0): AbilityDefinition("NovaCovertMission", "Covert Mission"),
    (522, 0): AbilityDefinition("NovaHoloDecoy", "Holo Decoy"),
    (523, 0): AbilityDefinition("NovaTripleTap", "Triple Tap"),
    (524, 0): AbilityDefinition("NovaSnipeStorm", "Snipe"),
    # Stitches
    (573, 0): AbilityDefinition("StitchesDevour", "Devour"),
    (578, 0): AbilityDefinition("StitchesPutridBile", "Putrid Bile"),
    (579, 0): AbilityDefinition("StitchesSlam", "Slam"),
    (580, 0): AbilityDefinition("StitchesHook", "Hook"),
    # Zagara
    (712, 0): AbilityDefinition("ZagaraInfestedDrop", "Infested Drop"),
    (714, 0): AbilityDefinition("ZagaraBanelingBarrage", "Baneling Barrage"),
    (715, 0): AbilityDefinition("ZagaraSummonCreepTumor", "Creep Tumor"),
    (716, 0): AbilityDefinition("ZagaraSummonHydralisk", "Hunter Killer"),
    (718, 0): AbilityDefinition("ZagaraSummonNydusWorm", "Nydus Network"),
}

ABILITY_DEFINITIONS_BY_BUILD: dict[int, dict[tuple[int, int], AbilityDefinition]] = {
    DEFAULT_ABILITY_BUILD: ABILITY_DEFINITIONS_97039,
}

ABILITY_CATALOG_DEFINITIONS_BY_BUILD: dict[int, dict[str, AbilityDefinition]] = {
    DEFAULT_ABILITY_BUILD: ABILITY_CATALOG_DEFINITIONS_97039,
}

HERO_ABILITY_CATALOG_NAMES_BY_BUILD: dict[int, dict[str, tuple[str, ...]]] = {
    DEFAULT_ABILITY_BUILD: HERO_ABILITY_CATALOG_NAMES_97039,
}

SUPPORTED_ABILITY_BUILDS = tuple(sorted(ABILITY_DEFINITIONS_BY_BUILD))


def get_ability_definition(
    ability_link: int | None,
    ability_cmd_index: int | None,
    game_version: int | None = None,
) -> AbilityDefinition | None:
    if ability_link is None or ability_cmd_index is None:
        return None
    if game_version is None:
        return None
    definitions = ABILITY_DEFINITIONS_BY_BUILD.get(game_version)
    if definitions is None:
        return None
    return definitions.get((ability_link, ability_cmd_index))


def get_ability_catalog_definition(
    catalog_name: str | None,
    game_version: int | None = None,
) -> AbilityDefinition | None:
    if catalog_name is None:
        return None
    if game_version is None:
        return None
    definitions = ABILITY_CATALOG_DEFINITIONS_BY_BUILD.get(game_version)
    if definitions is None:
        return None
    return definitions.get(catalog_name)


def get_hero_ability_definitions(
    hero_catalog_name: str | None,
    game_version: int | None = None,
) -> tuple[AbilityDefinition, ...]:
    if hero_catalog_name is None:
        return ()
    if game_version is None:
        return ()
    catalog_names_by_hero = HERO_ABILITY_CATALOG_NAMES_BY_BUILD.get(game_version)
    definitions = ABILITY_CATALOG_DEFINITIONS_BY_BUILD.get(game_version)
    if catalog_names_by_hero is None or definitions is None:
        return ()
    catalog_names = catalog_names_by_hero.get(hero_catalog_name, ())
    return tuple(definitions[catalog_name] for catalog_name in catalog_names)
