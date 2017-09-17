__author__ = 'Rodrigo Duenas, Cristian Orellana'

from replay import *


def processEvents(protocol=None, replayFile=None, team1=None, team2=None, event=None, stage=None):
    """"
    This is the main loop, reads a replayFile and applies available decoders (trackerEvents, gameEvents, msgEvents, etc)
    Receives the protocol and the replayFile as an mpyq file object
    """
    if not protocol or not replayFile:
        print "Error - Protocol and replayFile are needed"
        return -1

    replay_data = Replay(protocol, replayFile, team1, team2, event, stage)

    replay_data.process_replay_details()
    replay_data.process_replay_initdata()
    replay_data.process_replay()
    replay_data.process_replay_attributes()
    replay_data.calculate_army_strength()
    replay_data.process_map_events()
    replay_data.process_generic_events()

    return replay_data
