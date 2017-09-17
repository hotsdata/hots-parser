__author__ = 'Rodrigo Duenas, Cristian Orellana'

from collections import OrderedDict

from data import *
from helpers import *


class Team():
    def __init__(self):


        # General team attributes
        self.generalStats = {

            "teamId": None,
            "level": 0,
            "memberList": list(),
            "isWinner": None,
            "isLoser": None,
            "periodicXPBreakdown": [],
            "totalXP": 0,
            "totalMinionXP": 0,
            "totalCreepXP": 0,
            "totalStructureXP": 0,
            "totalHeroXP": 0,
            "totalTrickleXP": 0,
            "army_strength": {},
            "merc_strength": {},
            "missedRegenGlobes": 0,  # regen globes no one took
            "watchTowersTaken": 0,
            "bossTaken": 0,
            "mercsTaken": 0,
            "siegeCampTaken": 0,
            "levelEvents": [],
            "totalEnemyHeroesTakenDown": 0,  # How many enemy heroes this team killed?
            'totalHeroesKilledByEnemy': 0,  # how many times the heroes of this team were killed by the enemy?
            'banned': [] # Banned heroes, if any

        }
        self.mapStats = {}

    def set_map_stats(self, map):
        # Tomb of the spider queen map
        tombOfSpiderStats = {
            "pickedSoulGems": 0,
            "wastedSoulGems": 0,
            "summonedSpiderBosses": 0,
            "spiderBossesNorthTotalAliveTime": 0,
            "spiderBossesCenterTotalAliveTime": 0,
            "spiderBossesSouthTotalAliveTime": 0,
            "spiderBossesTotalAliveTime": 0,
            "totalBuildingsKilledDuringSpiders": 0,
            "totalUnitsKilledDuringSpiders": 0,
            "totalBuildingsKilledDuringNorthSpider": 0,
            "totalUnitsKilledDuringNorthSpider": 0,
            "totalBuildingsKilledDuringCenterSpider": 0,
            "totalUnitsKilledDuringCenterSpider": 0,
            "totalBuildingsKilledDuringSouthSpider": 0,
            "totalUnitsKilledDuringSouthSpider": 0
        }

        # Braxis Holdout Map specific stats
        braxisHoldoutStats = {
            "ZergWaveStrength": 0
        }

        # Sky Temple map
        skyTempleStats = {
            "luxoriaTemplesCaptured": 0,
            "luxoriaTemplesCapturedSeconds": 0,
            "luxoriaTempleNorthCapturedSeconds": 0,
            "luxoriaTempleNorthCaptured": 0,
            "luxoriaTempleCenterCapturedSeconds": 0,
            "luxoriaTempleCenterCaptured": 0,
            "luxoriaTempleSouthCapturedSeconds": 0,
            "luxoriaTempleSouthCaptured": 0,
            "luxoriaTempleDmg": [],
            "luxoriaTempleShots": [],
            "luxoriaTemplesPct": 0,
            "luxoriaTempleNorthPct": 0,
            "luxoriaTempleCenterPct": 0,
            "luxoriaTempleSouthPct": 0,
            "luxoriaTempleNorthShots": [],
            "luxoriaTempleCenterShots": [],
            "luxoriaTempleSouthShots": [],
            "luxoriaTempleNorthDmg": [],
            "luxoriaTempleCenterDmg": [],
            "luxoriaTempleSouthDmg": [],
        }

        # Garden of Terror Map
        gardenStats = {
            "plantSummonedAt": [],
            "totalPlantsSummoned": 0,
            "totalWastedPlants": 0,
            "totalPlantsDuration": 0,
            "plantDuration": [],
            "plantPotDuration": [],
            "totalPlantPotDuration": 0,
            "totalUnitsKilledByPlants": [],
            "totalBuildingsKilledByPlants": [],
            "totalBuildingsKilledDuringPlant": [],
            "totalUnitsKilledDuringPlant": [],
            "totalPlantPotsPlaced": 0,
            "plantEffectiveness": [],
            "totalPlantPotsKilled": 0,
            "plantController": []
        }

        # Warhead Junction
        warheadJunctionStats = {
            "droppedNukes": 0,
            "launchedNukes": 0
        }

        # Dragon Shire
        dragonShireStats = {
            "dragonCaptureTimes": [],  # in seconds
            "totalDragonsDuration": 0,
            "dragonDuration": [],
            "totalUnitsKilledBydragons": [],
            "totalBuildingsKilledBydragons": [],
            "dragonEffectiveness": [],
            "totalBuildingsKilledDuringdragon": [],
            "totalUnitsKilledDuringdragon": [],
            "wastedDragonTime": [],
            "totalDragonsSummoned": 0,
        }  # How many seconds the dragon was available to be controlled but no one used it.

        # Haunted Mines Map
        hauntedMinesStats = {
            "totalGolemsSummoned": 0,
            "totalGolemDistanceTraveled": 0,
            "golemDistanceTraveled": [],
            "golemEffectiveness": [],
            "golemDuration": [],
            "totalUnitsKilledByGolem": 0,
            "unitsKilledByGolem": [],
            "totalBuildingsKilledByGolem": 0,
            "buildingsKilledByGolem": [],
            "totalUnitsKilledDuringGolem": 0,
            "unitsKilledDuringGolem": [],
            "totalBuildingsKilledDuringGolem": 0,
            "buildingsKilledDuringGolem": [],
            "totalGolemDuration": 0
        }

        # Blackheart's Bay Map
        blackheartsBayStats = {
            "totalShipsControlled": 0,
            "totalUnitsKilledDuringShip": [],
            "shipDurations": [],
            "totalBuildingsDestroyedDuringShip": [],
            "ghostShipScore": [],
            "shipEffectiveness": []
        }

        # Infernal Shrine Map
        infernalShrinesStats = {
            "summonedPunishers": 0,
            "punisherSummonedAt": [],
            "punisherTotalAliveTime": [],
            "totalBuildingsKilledDuringPunisher": [],
            "totalUnitsKilledDuringPunisher": [],
            "punisherEfectiveness": [],
            "punisherHeroDmg": [],
            "punisherBuildingDmg": [],
            "punisherType": [],
            "shrineScore": []
        }

        # Cursed Hollow Map
        cursedHollowStats = {
            "tributesCapturedAt": [],  # When the tribute was captured
            "curseCaptures": [],  # How many tributes the team captured for each curse. 3": team won the curse
            "curseActivatedAt": [],
            "totalCursesWon": 0
        }

        # Towers of Doom Map
        towersOfDoomStats = {
            "totalTowersCaptured": 0,  # for Towers of Doom Maps
            "towersCapturedAtFire": [],
            "towersCapturedAt": [],
            "altarsCapturedAt": [],  # When was the altar captured by the team?
            "totalAltarsCaptured": 0,
        }

        # Battlefield of Eternity Map
        battlefieldEternityStats = {
            "totalImmortalsSummoned": 0,
            "immortalSummonedAt": [],
            "immortalFightDuration": [],
            "immortalDuration": [],
            "immortalPower": [],
            "immortalEffectiveness": [],
            "unitsKilledDuringImmortal": [],
            "totalUnitsKilledDuringImmortal": 0,
            "buildingsDestroyedDuringImmortal": [],
            "totalBuildingsDestroyedDuringImmortal": 0
        }

        if map == 'Cursed Hollow':
            self.mapStats = cursedHollowStats
        elif map == 'Tomb of the Spider Queen':
            self.mapStats = tombOfSpiderStats
        elif map == 'Sky Temple':
            self.mapStats = skyTempleStats
        elif map == 'Battlefield of Eternity':
            self.mapStats = battlefieldEternityStats
        elif map == 'Garden of Terror':
            self.mapStats = gardenStats
        elif map == 'Dragon Shire':
            self.mapStats = dragonShireStats
        elif map == 'Blackheart\'s Bay':
            self.mapStats = blackheartsBayStats
        elif map == 'Towers of Doom':
            self.mapStats = towersOfDoomStats
        elif map == 'Infernal Shrines':
            self.mapStats = infernalShrinesStats
        elif map == 'Haunted Mines':
            self.mapStats = hauntedMinesStats
        elif map == 'Warhead Junction':
            self.mapStats = warheadJunctionStats
        elif map == 'Braxis Holdout':
            self.mapStats = braxisHoldoutStats

    def add_member(self, hero, player):
        if hero.playerId is not None:
            self.generalStats['memberList'].append(hero.playerId)
            if self.generalStats['isWinner'] is None:
                self.generalStats['teamId'] = "Blue" if player.team == 0 else "Red"
                self.generalStats['isWinner'] = player.is_winner()
                self.generalStats['isLoser'] = player.is_loser()

    def get_total_members(self):
        return len(self.generalStats['memberList'])

    def __str__(self):
        return "%15s\t%15s\t%15s\t%15s" % (self.generalStats['teamId'],
                                           self.generalStats['level'],
                                           self.generalStats['isWinner'],
                                           self.generalStats['isLoser'])


class Unit:
    def __init__(self):
        self.bornAtX = -1
        self.bornAtY = -1

    def unit_tag(self):
        try:
            return (self.unitTagIndex << 18) + self.unitTagRecycle
        except Exception, e:
            print "Error: %s" % e.message

def unit_tag_index(self):
    return (self.unitTag >> 18) & 0x00003fff


def unit_tag_recycle(self):
    return (self.unitTag) & 0x0003ffff


def is_hero(self):
    return False


class HeroUnit(Unit):
    def __init__(self, player):

        # General data
        self.isHuman = False

        self.mapStats = {}
        self.playerId = player.playerId

        self.name = get_base_hero_name(player.hero, HERO_TRANSLATIONS) or player.hero
        self.team = player.team
        self.id = player.id
        # self.userId = self.playerId
        self.unitTagIndex = None  # Set at unit born event
        self.unitTagRecycle = None  # Set at unit born event
        self.internalName = None  # Set at unit born event
        # self.unitTag = self.unit_tag()
        # General Metrics
        self.generalStats = {
            "pickedTalents": [],  # list of dicts
            "deathCount": 0,
            "deaths": [],  # At what point in game (in seconds) the hero died, who killed them and was solo death?
            "soloDeathsCount": 0,  # how many times this hero died while away from team mates
            "killCountNeutral": 0,  # How many neutral npc units this hero killed?
            "killCountBuildings": 0,  # How many buildings this hero destroyed?
            "killCountMinions": 0,  # How many minions this hero killed?
            "killCount": 0,  # How many units this hero killed (normal minions + heroes + buildings + neutral npcs)
            "regenGlobesTaken": 0,
            "fortsDestroyed": 0,
            "levelEvents": [],
            "totalOutDmg": 0,
            "votesReceivedBy": [],
            "castedAbilities": OrderedDict()  # key" : gameloops when the ability was casted, value" : ability instance
        }
        self.set_hero_stats()

    def set_total_out_damage(self):
        self.generalStats['totalOutDmg'] = self.generalStats['totalStructureDmg'] + \
                                           self.generalStats['totalMinionDmg'] + \
                                           self.generalStats['totalHeroDmg'] + \
                                           self.generalStats['totalCreepDmg'] + \
                                           self.generalStats['totalSummonDmg']

    def set_hero_stats(self):
        if self.name == 'Gazlowe':
            self.generalStats['scrapTaken'] = 0
            self.generalStats['scrapMissed'] = 0
        elif self.name in ('Butcher', 'The Butcher'):
            self.generalStats['freshMeatTaken'] = 0
            self.generalStats['freshMeatMissed'] = 0
        elif self.name == 'Lunara':
            self.generalStats['wispsPlaced'] = 0

    def set_total_out_damage(self):
        self.generalStats['totalOutDmg'] = self.generalStats['SiegeDamage'] + \
                                           self.generalStats['StructureDamage'] + \
                                           self.generalStats['MinionDamage'] + \
                                           self.generalStats['HeroDamage'] + \
                                           self.generalStats['CreepDamage'] + \
                                           self.generalStats['SummonDamage']

    def set_map_stats(self, map):
        cursedHollowStats = {
            "capturedTributes": 0,  # Number of tributes captured by this hero in the Curse map
            "clickedTributes": 0,  # How many times the hero clicked a tribute in the Curse map
        }

        mineStats = {
            "skullsCollected": 0
        }

        # Garden map
        gardenStats = {
            "gardensSeedsCollected": 0,
            "totalPlantsControlled": 0,
            "unitsKilledAsPlant": [],
            "totalUnitsKilledAsPlant": 0,
            "buildingsKilledAsPlant": [],
            "totalBuildingsKilledAsPlant": 0,
            "polymorphedUnits": [],
            "totalPolymorphedUnits": 0,
            "plantDuration": [],
            "totalPlantPotsPlaced": 0,
            "totalPlantPotsKilled": 0,
            "plantEffectiveness": []
        }

        # Warhead junction
        warheadJunctionStats = {
            "droppedNukes": 0,
            "launchedNukes": 0
        }

        # Punisher map
        infernalShrinesStats = {
            "totalShrineMinionDmg": 0,  # Damage inflicted to minions in punisher map
            "totalMinionsKilled": 0
        }

        # Spider map
        tombOfSpiderStats = {
            "totalSoulsTaken": 0,  # How many times the hero collected soul shards on the tomb of the spider queen map
            "totalGemsTurnedIn": 0,
        }

        # Sky temple map
        skyTempleStats = {
            "totaltimeInTemples": 0,  # How many seconds was the hero holding the temples
        }

        # Dragon map
        dragonShireStats = {
            "totalDragonsControlled": 0,
            "totalShrinesCaptured": 0,
            "totalBuildingsKilledAsDragon": [],
            "totalUnitsKilledAsDragon": [],
            "dragonEffectiveness": [],
            "dragonCaptureTimes": [],
        }

        # Pirate map
        blackheartsBayStats = {
            "coinsTurnedIn": 0,
            "coinsCollected": 0,
            "coinsEffectiveness": 0,
        }

        battlefieldEternityStats = {
            "totalImmortalDmg": 0,  # Total damage done to the immortals
        }

        if map == 'Cursed Hollow':
            self.mapStats = cursedHollowStats
        elif map == 'Tomb of the Spider Queen':
            self.mapStats = tombOfSpiderStats
        elif map == 'Sky Temple':
            self.mapStats = skyTempleStats
        elif map == 'Battlefield of Eternity':
            self.mapStats = battlefieldEternityStats
        elif map == 'Garden of Terror':
            self.mapStats = gardenStats
        elif map == 'Dragon Shire':
            self.mapStats = dragonShireStats
        elif map == 'Blackheart\'s Bay':
            self.mapStats = blackheartsBayStats
        # elif map == 'Towers of Doom':
        #      self.mapStats = towersOfDoomStats
        elif map == 'Infernal Shrines':
            self.mapStats = infernalShrinesStats
        elif map == 'Haunted Mines':
            self.mapStats = mineStats
        elif map == 'Warhead Junction':
            self.mapStats = warheadJunctionStats

    def get_total_damage(self):
        return self.generalStats['totalSiegeDmg'] + \
               self.generalStats['totalStructureDmg'] + \
               self.generalStats['totalMinionDmg'] + \
               self.generalStats['totalHeroDmg'] + \
               self.generalStats['totalCreepDmg']

    def __str__(self):
        return "%15s\t%15s\t%15s\t%15s\t%15s\t%15s\t%15s\t%15s" % (self.name, self.internalName, self.isHuman,
                                                                         self.playerId, self.id, self.team,
                                                                         self.generalStats['deathCount'],
                                                                         self.get_total_casted_abilities())

    def get_total_casted_abilities(self):
        return len(self.generalStats['castedAbilities'])

    def get_total_picked_talents(self):
        return len(self.pickedTalents)

    def is_hero(self):
        return True


class HeroReplay:
    def __init__(self, details):
        # General Data
        self.startTime = None  # UTC
        self.gameLoops = None  # duration of the game in gameloops
        self.speed = 0
        self.gameType = None
        self.gameVersion = None
        self.randomVal = None
        self.mapName = get_base_map_name(details['m_title'], MAP_TRANSLATIONS)
        self.mapSize = {}
        self.startTime = win_timestamp_to_date(details['m_timeUTC'])
        self.gatesOpenedAt = None  # seconds into the game when the gates open

    def duration_in_secs(self):
        if self.gameLoops:
            return self.gameLoops / 16
        else:
            return 0

    def is_allowed_game_type(self):
        return self.gameType not in BANNED_GAME_TYPES

    def __str__(self):
        return "Title: %s\nStarted at: %s\nDuration (min/gl): %d/%d\nSpeed: %s\nGame Type: %s" % (self.mapName,
                                                                                                  self.startTime,
                                                                                                  self.duration_in_secs() / 60,
                                                                                                  self.gameLoops,
                                                                                                  self.speed,
                                                                                                  self.gameType
                                                                                                  )


class Player():
    def __init__(self, player):
        self.playerId = None  # Set at process_player_init
        self.heroLevel = 1
        self.id = player['m_workingSetSlotId']
        self.team = player['m_teamId']
        self.hero = get_base_hero_name(player['m_hero'], HERO_TRANSLATIONS) or player['m_hero']
        self.name = player['m_name']
        self.isHuman = (player['m_toon']['m_region'] != 0)
        self.gameResult = int(player['m_result'])
        self.toonHandle = self.get_toon_handle(player)
        self.battleTag = None
        self.realm = player['m_toon']['m_realm']
        self.region = player['m_toon']['m_region']
        self.rank = None

    def get_toon_handle(self, player):
        return '-'.join(
            [str(player['m_toon']['m_region']), player['m_toon']['m_programId'], str(player['m_toon']['m_realm']),
             str(player['m_toon']['m_id'])])

    def __str__(self):
        return "%10s\t%10s\t%10s\t%12s\t%10s\t%15s\t%15s\t%15s" % (self.id,
                                                             self.team,
                                                             self.hero,
                                                             self.name,
                                                             self.heroLevel,
                                                             self.is_winner(),
                                                             self.toonHandle,
                                                             self.battleTag
                                                             )

    def is_winner(self):
        return self.gameResult == 1

    def is_loser(self):
        return self.gameResult == 2


class GameUnit(Unit):
    def __init__(self, e):
        # General Data

        self.isDead = False
        self.diedAt = -1  # Seconds into the game when it was destroyed (-1 means never died)
        self.diedAtX = None
        self.diedAtY = None
        self.diedAtGameLoops = None
        self.gameLoopsAlive = -1  # -1 means never died.
        self.controlPlayerId = e['m_controlPlayerId']
        self.killerTeam = None
        self.killerTag = None
        self.killerTagIndex = None
        self.killerTagRecycle = None
        self.killerPlayerId = None
        self.ownerList = list()  # owner, when, duration (None = forever)
        self.clickerList = OrderedDict()  # key = gameloop , value = player id
        self.isHero = False
        self.unitsKilled = 0
        self.buildingsKilled = 0
        self.unitTagIndex = e['m_unitTagIndex']
        self.unitTagRecycle = e['m_unitTagRecycle']
        self.unitTag = self.unit_tag()
        self.bornAt = get_seconds_from_event_gameloop(e)  # Seconds into the game when it was created
        self.bornAtGameLoops = get_gameloops(e)
        self.internalName = e['m_unitTypeName']  # Internal unit name
        self.team = e['m_upkeepPlayerId'] - 11 if e['m_upkeepPlayerId'] > 10 else e[
                                                                                      'm_upkeepPlayerId'] - 1  # Team this unit belongs to, or Hero controlling it at born time (if it's <= 10)
        self.bornAtX = e['m_x']
        self.bornAtY = e['m_y']
        self.positions = {self.bornAt: [self.bornAtX, self.bornAtY]}  # key seconds, val = dict {'x','y'}
        self.distanceFromKiller = -1;
        if not self.is_plant_vehicle():
            self.positions[get_seconds_from_int_gameloop(self.bornAtGameLoops)] = [self.bornAtX, self.bornAtY]

    def is_map_resource(self):
        return self.internalName in PICKUNITS

    def is_warhead_dropped_nuke(self):
        return self.internalName in WARHEAD_DROPPED_NUKE

    def is_warhead_launched(self):
        return self.internalName in WARHEAD_LAUNCHED_NUKE

    def is_braxis_antenna(self):
        return self.internalName in BRAXIS_ANTENNA

    def is_braxis_zerg_unit(self):
        return self.internalName in BRAXIS_ZERG_WAVE_UNIT

    def was_picked(self):
        if self.internalName in PICKUNITS:
            return self.gameLoopsAlive < PICKUNITS[self.internalName]
        else:
            return False

    def is_building(self):
        return self.internalName in BUILDINGS

    def is_regen_globe(self):
        return self.internalName in REGEN_GLOBES_PICKABLE

    def is_regen_globe_neutral(self):
        return self.internalName == 'RegenGlobeNeutral'

    def is_spider_summon(self):
        return self.internalName == 'SoulEater'

    def is_plant_pot(self):
        return self.internalName == 'PlantHorrorOvergrowthPlant'

    def is_mercenary(self):
        return self.internalName in MERCUNITSNPC or self.internalName in MERCUNITSTEAM

    def is_hired_mercenary(self):
        return self.internalName in MERCUNITSTEAM

    def is_army_unit(self):
        return self.internalName in NORMALUNIT and self.internalName not in PICKUNITS

    def is_pickable_unit(self):
        return self.internalName in PICKUNITS

    def is_tomb_of_the_spider_pickable(self):
        return self.internalName in TOMB_OF_THE_SPIDER_PICKABLE

    def is_seed_pickable(self):
        return self.internalName == 'ItemSeedPickup'

    def is_sky_temple_tower(self):
        return self.internalName in SKY_TEMPLE_TOWER

    def is_beacon(self):
        return self.internalName in BEACONUNIT

    def is_tribute(self):
        return self.internalName in TRIBUTEUNIT

    def is_advanced_unit(self):
        return self.internalName in ADVANCEDUNIT

    def get_death_time(self, total_time):
        return self.diedAt if (self.diedAt >= 0) else total_time

    def is_plant_vehicle(self):
        return self.internalName in PLANT_CONTROLLABLE

    def is_dragon_statue(self):
        return self.internalName in DRAGON_STATUE

    def is_golem(self):
        return self.internalName in GOLEM_UNIT

    def is_golem_body(self):
        return self.internalName in GOLEM_BODY

    def is_ghostship(self):
        return self.internalName in GHOST_SHIP

    def is_punisher(self):
        return self.internalName in PUNISHER_UNIT

    def is_shrine_minion(self):
        return self.internalName in SHRINE_MINION

    def is_hero(self):
        return self.isHero

    def get_strength(self):
        if self.is_hired_mercenary():
            return MERCUNITSTEAM[self.internalName]
        elif self.is_advanced_unit():
            return ADVANCEDUNIT[self.internalName]
        elif self.is_army_unit():
            return NORMALUNIT[self.internalName]
        elif self.is_building():
            return BUILDINGS[self.internalName]
        else:
            return 0

    def __str__(self):
        val = "%s\t%s\t(%s)\tcreated: %d s (%d,%d) \tdied: %s s\tlifespan: %s gls\tpicked? (%s)\tkilledby: %s" \
              % (self.unitTag, self.internalName, self.team, self.bornAt, self.bornAtX, self.bornAtY, self.diedAt,
                 self.gameLoopsAlive, self.was_picked(), self.killerPlayerId)
        if len(self.ownerList) > 0:
            val += "\tOwners: %s" % self.ownerList
        if len(self.clickerList) > 0:
            val += "\tTaken by: %s" % (self.get_tribute_controller())
        return val


class BaseAbility():
    """
    Base class for all abilities, has all the common attributes
    """

    def __init__(self, event):
        self.abilityName = None
        self.abilityTag = get_ability_tag(event)
        self.castedAtGameLoops = event['_gameloop']
        self.castedAt = get_seconds_from_event_gameloop(event)
        self.userId = event['_userid']['m_userId']

    def __str__(self):
        return "%s" % self.abilityTag

    def __repr__(self):
        return "BaseAbility(%r)" % (self.abilityTag)


class TargetPointAbility(BaseAbility):
    def __init__(self, event):

        self.abilityTag = get_ability_tag(event)
        self.castedAt = get_seconds_from_event_gameloop(event)
        self.userId = event['_userid']['m_userId']
        self.castedAtGameLoops = event['_gameloop']
        if event.get('m_data'):
            self.x = event['m_data']['TargetPoint']['x'] / 4096.0
            self.y = event['m_data']['TargetPoint']['y'] / 4096.0
            self.z = event['m_data']['TargetPoint']['z'] / 4096.0
        elif event.get('m_target'):
            self.x = event['m_target']['x'] / 4096.0
            self.y = event['m_target']['y'] / 4096.0
            self.z = event['m_target']['z'] / 4096.0

    def __repr__(self):
        return "TargetPointAbility(%r, (%r, %r, %r))" % (self.abilityTag, self.x, self.y, self.z)

    def __str__(self):
        return "Skill: %s\tCoords: (%s,%s,%s)" % (self.abilityTag, self.x, self.y, self.z)


class UnitUpgrade():
    def __init__(self, event):
        self.gameloops = event['_gameloop']
        self.upgradedPlayerId = event['m_playerId'] - 1
        self.internalName = event['m_upgradeTypeName']

    def is_dragon_upgrade(self):
        return self.internalName in DRAGON_CONTROLLABLE


class TargetUnitAbility(BaseAbility):
    def __init__(self, event):
        self.abilityTag = get_ability_tag(event)
        self.castedAt = get_seconds_from_event_gameloop(event)
        self.userId = event['_userid']['m_userId']
        self.castedAtGameLoops = event['_gameloop']
        if event.get('m_data'):
            self.x = event['m_data']['TargetUnit']['m_snapshotPoint']['x'] / 4096.0
            self.y = event['m_data']['TargetUnit']['m_snapshotPoint']['y'] / 4096.0
            self.z = event['m_data']['TargetUnit']['m_snapshotPoint']['z'] / 4096.0
            self.targetPlayerId = event['m_data']['TargetUnit']['m_snapshotControlPlayerId']
            self.targetTeamId = event['m_data']['TargetUnit']['m_snapshotUpkeepPlayerId']
            self.targetUnitTag = event['m_data']['TargetUnit']['m_tag']
        elif event.get('m_target'):
            self.x = event['m_target']['m_snapshotPoint']['x'] / 4096.0
            self.y = event['m_target']['m_snapshotPoint']['y'] / 4096.0
            self.z = event['m_target']['m_snapshotPoint']['z'] / 4096.0
            self.targetPlayerId = event['m_target']['m_snapshotControlPlayerId']
            self.targetTeamId = event['m_target']['m_snapshotUpkeepPlayerId']
            self.targetUnitTag = event['m_target']['m_tag']

    def __repr__(self):
        return "TargetUnitAbility(%r, %r, (%r, %r, %r))" % (
            self.abilityTag, self.targetPlayerId, self.x, self.y, self.z)

    def __str__(self):
        return "Skill: %s\tCoords: (%s,%s,%s)\tTarget: %s" % (
            self.abilityTag, self.x, self.y, self.z, self.targetUnitTag)
