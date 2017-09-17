# hots-parser
A fast Heroes of the Storm's replay files parser written in Python.


## How to run it:

There are two ways to run hots-parser:

1) Standalone: where the stats are save to different files, based on the flags you use.

2) Database: where the stats are inserted into a database. This is the default mode where you don't provide any flag or parameter besides the path to the replay file

```
usage: main.py [-h] [-o OUTPUT_DIR] [-r] [-t] [-l] [-u] [-p] [-a] replay_path

positional arguments:
  replay_path           Path to the .StormReplay file to process

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Path to the output directory
  -r, --dump-heroes     Indicates you want to dump hero data
  -t, --dump-teams      Indicates you want to dump teams data
  -l, --dump-timeline   Indicates you want to dump timeline data
  -u, --dump-units      Indicates you want to dump units data
  -p, --dump-players    Indicates you want to dump player data
  -a, --dump-all        Shortcut for --dump-heroes --dump-teams --dump-units
                        --dump-players --dump-timeline
```

# Configuration
This parser tries to run as fast as possible, in order to do that we use PyPy which perform better than the default interpreter, so the first thing you need to do is to install PyPy. Please note that the default interpreter will still work, but a lot slower (about 1 second per replay on a mac with i7@2.8Ghz with 16GB of RAM)

## Loading submodules
The parser relies on Blizzard's heroprotocol project, which is included as a submodule in this repo, in order to pull the data for heroprotocol you need to run this command after cloning the repo:

```
git submodule init
git submodule update
```

alternativelly, you can clone hots-parser recursively:

```
git clone --recursive git@github.com:crorella/hots-parser.git
```

## Loading the database schema
You will need a PostgreSQL server running at least the version 9.5, because we make extensive use of the JSONB datatype to store the metrics we extract from the replay.

- Create a database with the name "hotsdata"
- Create a user with the name "hotsdata" and grant ALL to the hotsdata database.

```
CREATE DATABASE hotsdata;
CREATE ROLE hotsdata WITH LOGIN PASSWORD 'hotsdata';
REVOKE CONNECT ON DATABASE hotsdata FROM PUBLIC;
GRANT ALL ON DATABASE hotsdata TO hotsdata;
```

- Update credentials.json with the appropriate password and server information.
- Load the script in database/database_schema.sql into hotsdata. Please note this schema also contains the tables used by the API, data processing (ETL) and frontend that power www.hotsdata.com

## Installing python libraries
For now we just use jsonpickle and psycopg2ct. You can use pip to install them.

> pip install jsonpickle

> pip install psycopg2ct

## Testing all
To test if everything is working fine run the following command in the root folder of this project:
> pypy main.py Hanamura.HotsReplay

You should see something like this in the console:
```
Processing: Hanamura.StormReplay
saving 18c0a432362fca4bb38ccf950ede92d562bb3a5b9e72a93beb4ce196c322650d to db
```

If you query the database you should see data in the following tables:
- replayinfo: This is the main table where general information about the replay is stored. Every table has a replayid as a foreign key to this table.
- players: stores the players present in the replay, you should see 10 entries here, one per player.
- teams: teams present in the replay, you should see 2 entries here.
- teamstats: this table store generic team metrics which are common across all maps. You should see 2 entries here, one per team.
- teammapstats: this table store map specific metrics at a team level. You should see 2 entries here, one per team.
- generalstats: this table store generic player stats which are common across all maps. You should see 10 entries here, one per player.
- mapstats: this table store map specific metrics for each player. You should see 10 entries here, one per player.
- battletag_toonhandle_lookup: this table creates a mapping between the battletags and the toonhandles of every player, you should see 10 entries here, one per player.

The others tables are mostly used by the processes that aggregate data and calculate more advanced metrics. This project is still not Open Source, but we are working on cleaning the code to release it in the next couple of days.
