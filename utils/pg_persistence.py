import jsonpickle
import json
import psycopg2ct

from data import *


def save_data(replayData, path):
    # read credential file
    with open('credentials.json') as data_file:
        conf = json.load(data_file)
    try:
        rConn = psycopg2ct.connect(database=conf['database'], user=conf['user'], password=conf['password'],
        host=conf['host'], port=conf['port'])
        cursor = rConn.cursor()
        rConn.autocommit = True
    except Exception, e:
        print "Error while trying to establish connection with database %s" % e

    try:
        replayData.path = path
        exists = save_replay_info(replayData, cursor)
        if not exists:
            save_death_list(replayData, cursor)
            save_armystr(replayData, cursor)
            save_team_stats(replayData, cursor)
            save_time_line(replayData, cursor)
            save_player_stats(replayData, cursor)
            save_players(replayData, cursor)
    finally:
        rConn.close()


def save_death_list(replayData, cursor):
    id = replayData.get_replay_id()

    deaths = {}
    deathList = []
    row = None
    for h in replayData.heroList:
        hero = replayData.heroList[h]

        for d in hero.generalStats['deaths']:
            seconds = d['seconds']
            soloDeath = d['soloDeath']
            x = d['x']
            y = d['y']
            killers = [replayData.heroList[l - 1].name if l - 1 in replayData.heroList else OTHERKILLERS[l - 1] for l in
                       d['killers'] if l > 0]
            row = {'seconds': seconds, 'soloDeath': soloDeath, 'x': x, 'y': y, 'killers': killers, 'victim': hero.name,
                   'team': hero.team}
            deathList.append(row)
            if not deaths.get("team%s" % hero.team):
                deaths["team%s" % hero.team] = []
            deaths["team%s" % hero.team].append(row)
            row = {}
            row['deaths'] = deaths
            row['mapName'] = replayData.replayInfo.mapName

    row = jsonpickle.encode(row)
    if row:
        sql = "INSERT INTO deathlist (replayid, mapname, doc) VALUES (%s,%s,%s) " \
              "ON CONFLICT ON CONSTRAINT deathlist_pk DO UPDATE SET doc = excluded.doc;"
        cursor.execute(sql, [id, replayData.replayInfo.mapName, row])



def save_armystr(replayData, cursor):
    id = replayData.get_replay_id()
    row = {'id': id,
           'team0': None,
           'team1': None,
           'start': None
           }
    for t in replayData.teams:
        armyStr = []
        armyTeamId = 0 if t.generalStats['teamId'] == "Blue" else 1
        keys = sorted(t.generalStats['army_strength'])
        if len(keys) > 0:
            row['start'] = keys[0]
            for k in keys:
                armyStr.append(t.generalStats['army_strength'][k])
            row['team%s' % armyTeamId] = armyStr

    if row:
        row = jsonpickle.encode(row)
        sql = "INSERT INTO armystr (replayid, doc) VALUES (%s,%s) " \
              "ON CONFLICT ON CONSTRAINT armystr_pk DO UPDATE SET doc = excluded.doc;"
        cursor.execute(sql, [id, row])



def save_team_stats(replayData, cursor):
    id = replayData.get_replay_id()
    for t in replayData.teams:
        t.generalStats['replayId'] = id
        t.generalStats['team'] = 0 if t.generalStats['teamId'] == "Blue" else 1
        t.generalStats['id'] = '%s-%s' % (id, t.generalStats['teamId'])
        t.generalStats['army_strength'] = ""
        t.generalStats['merc_strength'] = ""
        t.mapStats['team'] = 0 if t.generalStats['teamId'] == "Blue" else 1
        t.mapStats['id'] = '%s-%s' % (id, t.generalStats['teamId'])

        if t.generalStats:
            doc = jsonpickle.encode(t.generalStats)
            sql = "INSERT INTO teamGeneralStats (replayid, team, doc) VALUES (%s, %s, %s) " \
                  "ON CONFLICT ON CONSTRAINT teamgeneralstats_pk DO UPDATE SET doc = excluded.doc;"
            cursor.execute(sql, [id, t.generalStats['team'], doc])

        if t.mapStats:
            doc = jsonpickle.encode(t.mapStats)
            sql = "INSERT INTO teamMapStats (replayid, team, doc) VALUES (%s, %s, %s) " \
                  "ON CONFLICT ON CONSTRAINT teammapstats_pk DO UPDATE SET doc = excluded.doc;"
            cursor.execute(sql, [id, t.mapStats['team'], doc])



def save_time_line(replayData, cursor):
    id = replayData.get_replay_id()
    tl = {}
    tl['id'] = id
    tl['tl'] = replayData.timeLine

    if tl:
        doc = jsonpickle.encode(tl)
        sql = "INSERT INTO timeline (replayid, doc) VALUES (%s, %s) " \
              "ON CONFLICT ON CONSTRAINT timeline_pk DO UPDATE SET doc = excluded.doc;"
        cursor.execute(sql, [id, doc])


def save_replay_info(replayData, cursor):
    id = replayData.get_replay_id()
    rep = replayData.replayInfo
    replay = {'startTime': rep.startTime,
              'gameLoops': rep.gameLoops,
              'speed': rep.speed,
              'gameType': rep.gameType,
              'gameVersion': rep.gameVersion,
              'mapSize': rep.mapSize,
              'startTime': rep.startTime,
              'mapName': rep.mapName,
              'id': id,
              'replayPath': replayData.path,
              'team1': replayData.team1,
              'team2': replayData.team2,
              'event': replayData.event,
              'stage': replayData.stage
              }

    if replay:
        doc = jsonpickle.encode(replay)


        sql = "INSERT INTO replayInfo (replayid, doc) VALUES (%s, %s) " \
              "ON CONFLICT ON CONSTRAINT replayinfo_pk DO UPDATE SET doc = excluded.doc;"


        if check_row(cursor, "replayInfo", [['replayId', id, '='],
                                            ["(doc->>'gameLoops')::integer", replay['gameLoops'], '>=']]) > 0:
            print "Replay already processed"
            return True
        else:
            cursor.execute(sql, [id, doc])
            return False



def save_player_stats(replayData, cursor):
    id = replayData.get_replay_id()
    for h in replayData.heroList:
        hero = replayData.heroList[h]
        deathList = []
        hero.name = hero.name

        for d in hero.generalStats['deaths']:
            seconds = d['seconds']
            soloDeath = d['soloDeath']
            x = d['x']
            y = d['y']
            killers = [replayData.heroList[l - 1].name if l - 1 in replayData.heroList else OTHERKILLERS[l - 1] for l in
                       d['killers'] if l > 0]
            row = {'seconds': seconds, 'soloDeath': soloDeath, 'x': x, 'y': y, 'killers': killers, 'victim': hero.name,
                   'team': hero.team, 'id': '%s-%s-%s' % (id, hero.team, hero.name)}
            deathList.append(row)

        hero.generalStats['castedAbilities'] = ""
        hero.generalStats['deaths'] = deathList
        hero.generalStats['team'] = hero.team
        hero.generalStats['playerId'] = hero.playerId
        replayData.heroList[h].mapStats['team'] = hero.team
        replayData.heroList[h].mapStats['playerId'] = hero.playerId
        replayData.heroList[h].mapStats['replayId'] = id
        replayData.heroList[h].mapStats['heroName'] = hero.name
        replayData.heroList[h].mapStats['id'] = '%s-%s-%s' % (id, hero.team, hero.name)
        replayData.heroList[h].generalStats['replayId'] = id
        replayData.heroList[h].generalStats['levelEvents'] = ""
        replayData.heroList[h].generalStats['heroName'] = hero.name
        replayData.heroList[h].generalStats['id'] = '%s-%s-%s' % (id, hero.team, hero.name)

        if hero.generalStats:
            doc = jsonpickle.encode(hero.generalStats)
            sql = "INSERT INTO generalStats (replayid, team, heroname, doc) VALUES (%s, %s, %s, %s) " \
              "ON CONFLICT ON CONSTRAINT generalstats_pk DO UPDATE SET doc = excluded.doc;"
            cursor.execute(sql, [id, hero.generalStats['team'], hero.name, doc])


        if hero.mapStats:
            doc = jsonpickle.encode(hero.mapStats)
            sql = "INSERT INTO mapstats (replayid, team, heroname, doc) VALUES (%s, %s, %s, %s) " \
                  "ON CONFLICT ON CONSTRAINT mapstats_pk DO UPDATE SET doc = excluded.doc;"
            cursor.execute(sql, [id, hero.mapStats['team'], hero.name, doc])



def save_players(replayData, cursor):
    id = replayData.get_replay_id()

    for p in replayData.players:
        player = replayData.players[p]
        player.hero = player.hero
        row = {'playerId': player.playerId,
               'heroLevel': int(player.heroLevel),
               'slotId': player.id,
               'team': player.team,
               'hero': player.hero,
               'name': unicode(player.name, "utf-8"),
               'isHuman': player.isHuman,
               'gameResult': player.gameResult,
               'toonHandle': player.toonHandle,
               'realm': player.realm,
               'region': player.region,
               'rank': player.rank,
               'battleTag': player.battleTag or -1,
               # 'replayId': id,
               'id': '%s-%s-%s' % (id, player.team, player.hero)
               }

        if row:
            doc = jsonpickle.encode(row)
            sql = """
                    INSERT INTO players (replayid, team, heroname, doc) VALUES (%s, %s, %s, %s)
                    ON CONFLICT ON CONSTRAINT players_pk DO UPDATE SET doc = excluded.doc;
                  """
            cursor.execute(sql, [id, player.team, player.hero, doc])
            sql = """
                    INSERT INTO battletag_toonhandle_lookup (battletag, toonhandle, region)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (battletag, toonhandle) DO NOTHING ;
                    """
            try:
                region_code = player.toonHandle.split('-')[0]
                if region_code == '98':
                    region = 'PTR'
                elif region_code == '1':
                    region = 'NA'
                elif region_code == '2':
                    region = 'EU'
                elif region_code == '3':
                    region = 'KR'
                elif region_code == '5':
                    region = 'CN'
                cursor.execute(sql, [player.battleTag, player.toonHandle, region])
            except Exception, e:
                print "Error: %s" % e.message



def check_row(cursor, table, verification):
    sql = "SELECT COUNT(*) FROM %s WHERE " % (table)
    where = []
    filter = []
    for val in verification:
        where.append("%s %s %%s" % (val[0], val[2]))
        filter.append(val[1])
    query = sql + ' AND '.join(where)
    cursor.execute(query, filter)
    result = cursor.fetchone()
    return result[0]
