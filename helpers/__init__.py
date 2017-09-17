__author__ = 'Rodrigo Duenas, Cristian Orellana'

import datetime
from math import sqrt, sin, asin, degrees, hypot, radians
from types import UnicodeType


def win_timestamp_to_date(ts=None, date_format='%Y-%m-%d %H:%M:%S'):
    if ts:
        return datetime.datetime.fromtimestamp(int((ts / 10000000) - 11644473600)).strftime(date_format)
    else:
        return None


def get_seconds_from_event_gameloop(e):
    return int((e['_gameloop'] % 2 ** 32) / 16)


def get_seconds_from_int_gameloop(gameloop):
    return int((gameloop % 2 ** 32) / 16)


def get_gameloops(e):
    return (e['_gameloop'] % 2 ** 32)


def get_unit_tag(e):
    return (e['m_unitTagIndex'] << 18) + e['m_unitTagRecycle']


def get_ability_tag(e):
    if e.get('m_abilityTag'):
        return e['m_abilityTag']
    else:
        return e['m_abil']['m_abilLink'] << 5 | e['m_abil']['m_abilCmdIndex']


def calculate_distance(x1, y1, x2, y2):
    return sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))


def calculate_weighted_average(values, weights):
    if len(values) > len(weights) or len(values) == 0:
        return None
    result = 0
    for v in xrange(0, len(values)):
        result += values[v] * weights[v]
    return result


def get_unit_owners(e, unitsInGame, totalDuration):
    """
    Get the owner of the unit and the time the unit was owned
    """

    # This is for units where the ownership is not permanent, like Sky Temple towers, Ghost Ship and Dragon Statue
    # one common trait among these units is that ownership will alternate between teams (teams 11 and 12) and map (team 0)

    if e['_event'] == 'NNet.Replay.Tracker.SUnitOwnerChangeEvent':
        unitTag = get_unit_tag(e)
        unit = unitsInGame[unitTag]
        if unit.is_sky_temple_tower() \
                or unit.is_dragon_statue() \
                or unit.is_ghostship() \
                or unit.is_braxis_antenna():
            if e['m_upkeepPlayerId'] in (11, 12, 0):
                owner = e['m_upkeepPlayerId'] - 11
            elif e['m_upkeepPlayerId'] in xrange(1, 6):  # If the player is in the slots 1 to 5, then team 0
                owner = 0
            elif e['m_upkeepPlayerId'] in xrange(6, 11):  # If the player is in the slots 6 to 10, then team 1
                owner = 1
            ownerTuple = (owner, get_seconds_from_event_gameloop(e), None)  # owner, when, duration (None = forever)
            totalOwners = len(unit.ownerList)
            if len(unit.ownerList) > 0:  # update duration (in secs) for previous capture
                unit.ownerList[totalOwners - 1][2] = int(ownerTuple[1] - unit.ownerList[totalOwners - 1][1])
            unit.ownerList.append(list(ownerTuple))


            # This is for pickable units
        if e['_event'] == 'NNet.Replay.Tracker.SUnitOwnerChangeEvent' and e['m_upkeepPlayerId'] in xrange(0, 11):
            unitTag = get_unit_tag(e)

            # This is for vehicles (Dragon, Plant)

            if unit.is_plant_vehicle():
                owner = e['m_upkeepPlayerId'] - 1
                unit.bornAt = get_seconds_from_event_gameloop(e)
                unit.bornAtGameLoops = e['_gameloop']
                unit.positions[e['_gameloop']] = [unit.bornAtX, unitsInGame[unitTag].bornAtY]
                # ownerTuple = (owner, unit.bornAt, get_seconds_from_event_gameloop(e)-unit.bornAt)
                ownerTuple = (owner, unit.bornAt, 0)
                unit.ownerList.append(list(ownerTuple))


            elif not unit.is_sky_temple_tower() and not unit.is_plant_vehicle() \
                    and not unit.is_ghostship() and not unit.is_dragon_statue():
                owner = e['m_upkeepPlayerId'] - 1
                ownerTuple = (owner, get_seconds_from_event_gameloop(e), 0)
                unit.ownerList.append(list(ownerTuple))


def get_position_by_second(unit, total_time, start=None, end=None):
    pos = {}
    iter = 0
    dist_iter = 1
    start_game = get_seconds_from_int_gameloop(unit.bornAtGameLoops)
    end_game = total_time if unit.is_hero() else unit.get_death_time(total_time)
    positions = sorted(unit.positions)
    # try:
    if start > get_seconds_from_int_gameloop(unit.bornAtGameLoops):
        if start < end:
            start_game = start
    if end < unit.get_death_time(total_time):
        if end > start:
            end_game = end

    for second in xrange(start_game, end_game + 1):
        if second in positions:

            if second not in pos:
                # If the info for this second is not stored yet
                pos[second] = unit.positions[second]
                iter += 1
                dist_iter = 1

        # if we don't have information for the current second, we need to estimate it
        else:
            total_positions = len(positions)
            # estimate the last known position for the unit before this second
            previousPos = [val for val in positions if val < second]
            if len(previousPos) > 0:
                iter_sec = max(previousPos)
                iter = positions.index(iter_sec)
                # for p in positions:
                #     if p != iter_sec:
                #         iter += 1
                #     else:
                #         break
                if second not in pos and iter < total_positions - 1:
                    x_1 = unit.positions[positions[iter]][0]
                    y_1 = unit.positions[positions[iter]][1]
                    x_2 = unit.positions[positions[iter + 1]][0]
                    y_2 = unit.positions[positions[iter + 1]][1]

                    elapsed_seconds = positions[iter + 1] - positions[iter]
                    if elapsed_seconds > 0:
                        distance = hypot(x_2 - x_1, y_2 - y_1)
                        if distance > 0:
                            alpha = degrees(asin(abs(y_2 - y_1) / distance))
                        else:
                            alpha = 0
                        beta = 180 - 90 - alpha
                        distance_per_second = distance / elapsed_seconds
                        travel_distance = distance_per_second * dist_iter
                        distance_x = round(travel_distance * sin(radians(beta)))
                        distance_y = round(travel_distance * sin(radians(alpha)))
                        if y_1 < y_2:
                            multi_y = 1
                        else:
                            multi_y = -1
                        if x_1 < x_2:
                            multi_x = 1
                        else:
                            multi_x = -1
                        new_x = x_1 + distance_x * multi_x
                        new_y = y_1 + distance_y * multi_y
                        pos[second] = [new_x, new_y]
                        dist_iter += 1

    # except Exception, e:
    #     print "error here!!! %s" % e
    return pos


def get_unit_clicked(e, unitsInGame):
    """
    Gets information when a unit has been clicked by another one. i.e: When clicking tribute or returning souls
    """

    if e['_event'] == 'NNet.Game.SCmdUpdateTargetUnitEvent':
        unitTag = e['m_target']['m_tag']
        if unitTag in unitsInGame.keys():
            if unitsInGame[unitTag].is_tribute():
                playerId = e['_userid']['m_userId']
                clickTuple = (playerId, get_seconds_from_event_gameloop(e))
                unitsInGame[unitTag].clickerList.append(clickTuple)


def find_hero_key_from_tag(heroList=None, tag=None):
    if len(heroList) == 0 or not heroList:
        return None
    else:
        for k, v in heroList.iteritems():
            if v.unitTag == tag:
                return k
    return None


def find_hero_key_from_user_id(heroList=None, userId=None):
    if len(heroList) == 0 or not heroList:
        return None
    else:
        for k, v in heroList.iteritems():
            if v.id == userId:
                return k
    return None


def find_player_key_from_user_id(playerList=None, userId=None):
    if len(playerList) == 0 or not playerList:
        return None
    else:
        for k, v in playerList.iteritems():
            if v.userId == userId:
                return k
    return None
