__author__ = 'Rodrigo Duenas, Cristian Orellana'

import argparse
from heroprotocol import protocol29406 as protocol
from heroprotocol.mpyq import mpyq
from os import path
from hotsparser import processEvents
import json
import datetime
import jsonpickle
from utils import pg_persistence as p


def save_to_db(replayData, path):
    """
    The original intent of this function is to store all the metrics to a database
    but at this moment it's just printing basic stats directly from the variables
    just to give an idea of what is being calculated
    """
    p.save_data(replayData, path)


def dump_data(entities=None, replay_data=None, file_path=None):
    if not entities or not path or not replay_data:
        return None

    file_path = path.join(file_path, '%s_' % (datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")))

    if entities == 'all':
        dump_heroes(data=replay_data, output_path=file_path)
        dump_teams(data=replay_data, output_path=file_path)
        dump_units(data=replay_data, output_path=file_path)
        dump_players(data=replay_data, output_path=file_path)
        dump_timeline(data=replay_data, output_path=file_path)

    if entities == 'heroes':
        dump_heroes(data=replay_data, output_path=file_path)

    if entities == 'teams':
        dump_teams(data=replay_data, output_path=file_path)

    if entities == 'units':
        dump_units(data=replay_data, output_path=file_path)

    if entities == 'players':
        dump_players(data=replay_data, output_path=file_path)

    if entities == 'timeline':
        dump_timeline(data=replay_data, output_path=file_path)


def dump_heroes(data=None, output_path=None):
    if not data or not output_path:
        return None
    file_path = output_path + "heroes.json"
    print "dumping heroes data into %s" % (file_path)
    with file(file_path, 'w') as f:
        dump = jsonpickle.encode(data.heroList)
        f.write(dump)


def dump_units(data=None, output_path=None):
    if not data or not output_path:
        return None
    file_path = output_path + "units.json"
    print "dumping units data into %s" % (file_path)
    with file(file_path, 'w') as f:
        dump = jsonpickle.encode(data.unitsInGame)
        f.write(dump)


def dump_teams(data=None, output_path=None):
    if not data or not output_path:
        return None
    file_path = output_path + "teams.json"
    print "dumping teams data into %s" % (file_path)
    with file(file_path, 'w') as f:
        dump = "[" + jsonpickle.encode(data.teams[0])
        f.write(dump)

        dump = "," + jsonpickle.encode(data.teams[1]) + "]"
        f.write(dump)


def dump_players(data=None, output_path=None):
    if not data or not output_path:
        return None
    file_path = output_path + "players.json"
    print "dumping player data into %s" % (file_path)
    with file(file_path, 'w') as f:
        dump = jsonpickle.encode(data.players)
        f.write(dump)


def dump_timeline(data=None, output_path=None):
    if not data or not output_path:
        return None
    file_path = output_path + "timeline.json"
    print "dumping timeline into %s" % file_path
    with file(file_path, 'w') as f:
        dump = jsonpickle.encode(data.timeLine)
        f.write(dump)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output-dir', help='Path to the output directory')
    parser.add_argument('-r', '--dump-heroes', action='store_true', default=False,
                        help='Indicates you want to dump hero data')
    parser.add_argument('-t', '--dump-teams', action='store_true', default=False,
                        help='Indicates you want to dump teams data')
    parser.add_argument('-l', '--dump-timeline', action='store_true', default=False,
                        help='Indicates you want to dump timeline data')
    parser.add_argument('-u', '--dump-units', action='store_true', default=False,
                        help='Indicates you want to dump units data')
    parser.add_argument('-p', '--dump-players', action='store_true', default=False,
                        help='Indicates you want to dump player data')
    parser.add_argument('-a', '--dump-all', action='store_true', default=False,
                        help='Shortcut for --dump-heroes --dump-teams --dump-units --dump-players --dump-timeline')
    parser.add_argument('replay_path', help='Path to the .StormReplay file to process')
    parser.add_argument('-t1', '--team1', help='Name of the Team 1', default=None)
    parser.add_argument('-t2', '--team2', help='Name of the Team 2', default=None)
    parser.add_argument('-e', '--event', help='Name of the eSport event', default=None)
    parser.add_argument('-s', '--stage', help='Stage of the event', default=None)
    args = parser.parse_args()

    print "Processing: %s" % (args.replay_path)

    replayData = None
    replay = mpyq.MPQArchive(args.replay_path)
    replayData = processEvents(protocol, replay, args.team1, args.team2, args.event, args.stage)

    if (args.output_dir):
        if not path.exists(args.output_dir):  # check if the provided path exists
            print 'Error - Path %s does not exist' % (args.output_dir)
            exit(0)
        output_path = args.output_dir

    else:
        # If the parameter is not provided then assume the output is the same folder this script resides
        output_path = path.dirname(path.abspath(__file__))

    if (args.dump_all):
        dump_data(entities='all', file_path=output_path, replay_data=replayData)
    elif args.dump_heroes or args.dump_teams or args.dump_units or args.dump_players or args.dump_timeline:
        if (args.dump_heroes):
            dump_data(entities='heroes', file_path=output_path, replay_data=replayData)
        if (args.dump_teams):
            dump_data(entities='teams', file_path=output_path, replay_data=replayData)
        if (args.dump_units):
            dump_data(entities='units', file_path=output_path, replay_data=replayData)
        if (args.dump_players):
            dump_data(entities='players', file_path=output_path, replay_data=replayData)
        if (args.dump_timeline):
            dump_data(entities='timeline', file_path=output_path, replay_data=replayData)
    else:
        print 'saving %s to db' % replayData.get_replay_id()
        save_to_db(replayData, args.replay_path)
