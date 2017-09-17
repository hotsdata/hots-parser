--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.8
-- Dumped by pg_dump version 9.5.8

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner:
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: user_status; Type: DOMAIN; Schema: public; Owner: hotstats
--

CREATE DOMAIN user_status AS text
	CONSTRAINT user_status_check CHECK ((VALUE = ANY (ARRAY['active'::text, 'inactive'::text, 'deleted'::text])));


ALTER DOMAIN user_status OWNER TO hotstats;

--
-- Name: user_type; Type: DOMAIN; Schema: public; Owner: hotstats
--

CREATE DOMAIN user_type AS text
	CONSTRAINT user_type_check CHECK ((VALUE = ANY (ARRAY['basic'::text, 'admin'::text, 'premium'::text])));


ALTER DOMAIN user_type OWNER TO hotstats;

--
-- Name: insert_battletag_toonhandle_current(); Type: FUNCTION; Schema: public; Owner: hotstats
--

CREATE FUNCTION insert_battletag_toonhandle_current() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        -- insert into battletag_toonhandle_current, if there is an entry for a given
				-- battletag then update the toonhandle
				INSERT INTO battletag_toonhandle_current
					(battletag, toonhandle)
					VALUES (NEW.battletag, NEW.toonhandle)
					ON CONFLICT ON CONSTRAINT battletag_toonhandle_current_pk
					DO
          UPDATE SET toonhandle = excluded.toonhandle;
			RETURN NEW;
    END;
$$;


ALTER FUNCTION public.insert_battletag_toonhandle_current() OWNER TO hotstats;

--
-- Name: set_updated_at(); Type: FUNCTION; Schema: public; Owner: hotstats
--

CREATE FUNCTION set_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.set_updated_at() OWNER TO hotstats;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: armystr; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE armystr (
    replayid character varying(64) NOT NULL,
    doc jsonb
);


ALTER TABLE armystr OWNER TO hotstats;

--
-- Name: battlefield_eternity_stats; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE battlefield_eternity_stats (
    replayid character varying(64) NOT NULL,
    handle character varying(32),
    player character varying(20),
    hero character varying(20) NOT NULL,
    team smallint NOT NULL,
    gametype character varying(20),
    mapname character varying(32),
    gameversion integer,
    totalimmortaldmg bigint
);


ALTER TABLE battlefield_eternity_stats OWNER TO hotstats;

--
-- Name: battletag_toonhandle_current; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE battletag_toonhandle_current (
    battletag character varying(25) NOT NULL,
    toonhandle character varying(25) NOT NULL
);


ALTER TABLE battletag_toonhandle_current OWNER TO hotstats;

--
-- Name: battletag_toonhandle_lookup; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE battletag_toonhandle_lookup (
    player_id integer NOT NULL,
    battletag character varying(25) NOT NULL,
    toonhandle character varying(25) NOT NULL,
    region character varying(10)
);


ALTER TABLE battletag_toonhandle_lookup OWNER TO hotstats;

--
-- Name: battletag_toonhandle_lookup_player_id_seq; Type: SEQUENCE; Schema: public; Owner: hotstats
--

CREATE SEQUENCE battletag_toonhandle_lookup_player_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE battletag_toonhandle_lookup_player_id_seq OWNER TO hotstats;

--
-- Name: battletag_toonhandle_lookup_player_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: hotstats
--

ALTER SEQUENCE battletag_toonhandle_lookup_player_id_seq OWNED BY battletag_toonhandle_lookup.player_id;


--
-- Name: cursed_stats; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE cursed_stats (
    replayid character varying(64) NOT NULL,
    handle character varying(32),
    player character varying(20),
    hero character varying(20) NOT NULL,
    team smallint NOT NULL,
    gametype character varying(20),
    mapname character varying(32),
    gameversion integer,
    clickedtributes bigint,
    capturedtributes bigint
);


ALTER TABLE cursed_stats OWNER TO hotstats;

--
-- Name: deathlist; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE deathlist (
    replayid character varying(64) NOT NULL,
    mapname character varying(64) NOT NULL,
    doc jsonb
);


ALTER TABLE deathlist OWNER TO hotstats;

--
-- Name: dragon_shire_stats; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE dragon_shire_stats (
    replayid character varying(64) NOT NULL,
    handle character varying(32),
    player character varying(20),
    gametype character varying(20),
    hero character varying(20) NOT NULL,
    team smallint NOT NULL,
    mapname character varying(32),
    gameversion integer,
    dragoneffectiveness double precision,
    totalunitskilledasdragon bigint,
    totalbuildingskilledasdragon bigint,
    avgunitskilledasdragon numeric,
    avgbuildingskilledasdragon numeric,
    games bigint
);


ALTER TABLE dragon_shire_stats OWNER TO hotstats;

--
-- Name: fct_player_stats_agg; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE fct_player_stats_agg (
    player_id integer NOT NULL,
    toonhandle character varying(64) NOT NULL,
    battletag character varying(64),
    name character varying(50) NOT NULL,
    mapname character varying(64) NOT NULL,
    gameversion integer NOT NULL,
    match_date timestamp without time zone NOT NULL,
    process_date timestamp without time zone NOT NULL,
    heroname character varying(30) NOT NULL,
    stats jsonb,
    games bigint,
    gametype character varying(25) NOT NULL
);


ALTER TABLE fct_player_stats_agg OWNER TO hotstats;

--
-- Name: garden_stats; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE garden_stats (
    replayid character varying(64) NOT NULL,
    handle character varying(32),
    player character varying(20),
    hero character varying(20) NOT NULL,
    team smallint NOT NULL,
    gametype character varying(20),
    mapname character varying(32),
    gameversion integer,
    totalplantpotskilled integer,
    totalplantpotsplaced integer,
    gardensseedscollected integer,
    totalplantscontrolled integer,
    totalunitskilledasplant integer,
    totalbuildingskilledasplant integer,
    planteffectiveness double precision,
    avgtotalunitskilledasplant numeric,
    avgtotalbuildingskilledasplant numeric,
    avgplantduration numeric,
    plantduration bigint,
    games bigint
);


ALTER TABLE garden_stats OWNER TO hotstats;

--
-- Name: generalstats; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE generalstats (
    replayid character varying(64) NOT NULL,
    team smallint NOT NULL,
    heroname character varying(64) NOT NULL,
    doc jsonb,
    updated_at timestamp without time zone DEFAULT clock_timestamp() NOT NULL
);


ALTER TABLE generalstats OWNER TO hotstats;

--
-- Name: generalstats_test; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE generalstats_test (
    replayid character varying(64),
    team smallint,
    heroname character varying(64),
    doc jsonb,
    updated_at timestamp without time zone
);


ALTER TABLE generalstats_test OWNER TO hotstats;

--
-- Name: hero_data; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE hero_data (
    hero_id character varying(25) NOT NULL,
    hero_info jsonb,
    hero_talents jsonb
);


ALTER TABLE hero_data OWNER TO hotstats;

--
-- Name: hero_info; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE hero_info (
    build integer NOT NULL,
    hero_name character varying(64) NOT NULL,
    talent_tier smallint NOT NULL,
    talent_choice smallint NOT NULL,
    talent_internal_name character varying(255),
    talent_name character varying(255),
    talent_icon character varying(255),
    description text
);


ALTER TABLE hero_info OWNER TO hotstats;

--
-- Name: heroes; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE heroes (
    id character varying(64) NOT NULL,
    patch integer NOT NULL,
    name character varying(64),
    role character varying(64),
    universe character varying(64),
    alignment character varying(64),
    rarity character varying(64),
    portrait_icon character varying(128),
    gender character varying(64),
    difficulty character varying(64),
    damage smallint,
    utility smallint,
    complexity smallint,
    survivability smallint,
    attrib_name character varying(10)
);


ALTER TABLE heroes OWNER TO hotstats;

--
-- Name: hotsdata_user; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE hotsdata_user (
    user_id integer NOT NULL,
    email character varying(255) NOT NULL,
    password character varying(64),
    verified boolean,
    battletag character varying(64),
    toonhandle character varying(64),
    user_tz character varying(9) DEFAULT 'UTC'::character varying,
    updated_at timestamp without time zone DEFAULT now(),
    user_type user_type DEFAULT 'basic'::character varying,
    status user_status DEFAULT 'active'::character varying
);


ALTER TABLE hotsdata_user OWNER TO hotstats;

--
-- Name: hotsdata_user_user_id_seq; Type: SEQUENCE; Schema: public; Owner: hotstats
--

CREATE SEQUENCE hotsdata_user_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE hotsdata_user_user_id_seq OWNER TO hotstats;

--
-- Name: hotsdata_user_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: hotstats
--

ALTER SEQUENCE hotsdata_user_user_id_seq OWNED BY hotsdata_user.user_id;


--
-- Name: infernal_shrines_stats; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE infernal_shrines_stats (
    replayid character varying(64) NOT NULL,
    handle character varying(32),
    player character varying(20),
    hero character varying(20) NOT NULL,
    team smallint NOT NULL,
    gametype character varying(20),
    mapname character varying(32),
    gameversion integer,
    totalminionskilled integer,
    totalshrineminiondmg integer
);


ALTER TABLE infernal_shrines_stats OWNER TO hotstats;

--
-- Name: mapstats; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE mapstats (
    replayid character varying(64) NOT NULL,
    team smallint NOT NULL,
    heroname character varying(64) NOT NULL,
    doc jsonb,
    updated_at timestamp without time zone DEFAULT clock_timestamp() NOT NULL
);


ALTER TABLE mapstats OWNER TO hotstats;

--
-- Name: patches; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE patches (
    gameversion integer[]
);


ALTER TABLE patches OWNER TO hotstats;

--
-- Name: pirate_stats; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE pirate_stats (
    replayid character varying(64) NOT NULL,
    handle character varying(32),
    player character varying(20),
    hero character varying(20) NOT NULL,
    team smallint NOT NULL,
    gametype character varying(20),
    mapname character varying(32),
    gameversion integer,
    coinsturnedin bigint,
    coinscollected bigint,
    coinseffectiveness double precision
);


ALTER TABLE pirate_stats OWNER TO hotstats;

--
-- Name: player_hero_map_stats_daily; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE player_hero_map_stats_daily (
    toonhandle character varying(25) NOT NULL,
    name character varying(25) NOT NULL,
    mapname character varying(50) NOT NULL,
    heroname character varying(50) NOT NULL,
    starttime character varying(15) NOT NULL,
    games integer,
    stats jsonb
);


ALTER TABLE player_hero_map_stats_daily OWNER TO hotstats;

--
-- Name: player_stats; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE player_stats (
    handle character varying NOT NULL,
    player character varying NOT NULL,
    hero character varying NOT NULL,
    mapname character varying NOT NULL,
    gametype character varying NOT NULL,
    gameversion integer NOT NULL,
    average_length_sec integer,
    assists bigint,
    avg_assists_per_game numeric,
    total_kills bigint,
    avg_kills_per_game numeric,
    totalxp bigint,
    avg_xp_per_game numeric,
    avg_solokills_per_game numeric,
    avg_takedowns_per_game numeric,
    avg_deaths_per_game numeric,
    avg_secondsdead_per_game numeric,
    avg_totaloutdmg_per_game numeric,
    avg_totalherodmg_per_game numeric,
    avg_totalsummondmg_per_game numeric,
    avg_totaloutheal_per_game numeric,
    avg_totalcreepdmg_per_game numeric,
    avg_totalselfheal_per_game numeric,
    avg_totalsiegedmg_per_game numeric,
    avg_fortsdestroyed_per_game numeric,
    avg_totalincdamage_per_game numeric,
    avg_totalminiondmg_per_game numeric,
    avg_solodeathscount_per_game numeric,
    avg_killcountminions_per_game numeric,
    avg_killcountneutral_per_game numeric,
    avg_regenglobestaken_per_game numeric,
    avg_capturedmerccamps_per_game numeric,
    avg_totalstructuredmg_per_game numeric,
    avg_killcountbuildings_per_game numeric,
    avg_secondscconenemies_per_game numeric,
    avg_capturedbeacontowers_per_game numeric,
    max_xp_per_game integer,
    max_solokills_per_game integer,
    max_takedowns_per_game integer,
    max_deaths_per_game integer,
    max_secondsdead_per_game integer,
    max_totaloutdmg_per_game integer,
    max_totalherodmg_per_game integer,
    max_totaloutheal_per_game integer,
    max_totalcreepdmg_per_game integer,
    max_totalselfheal_per_game integer,
    max_totalsiegedmg_per_game integer,
    max_fortsdestroyed_per_game integer,
    max_totalincdamage_per_game integer,
    max_totalsummondmg_per_game integer,
    max_totalminiondmg_per_game integer,
    max_solodeathscount_per_game integer,
    max_killcountminions_per_game integer,
    max_killcountneutral_per_game integer,
    max_regenglobestaken_per_game integer,
    max_capturedmerccamps_per_game integer,
    max_totalstructuredmg_per_game integer,
    max_killcountbuildings_per_game integer,
    max_secondscconenemies_per_game integer,
    max_capturedbeacontowers_per_game integer,
    avg_immortaldmg_per_game numeric,
    totalimmortaldmg numeric,
    totalclickedtributes numeric,
    avg_clickedtributes_per_game numeric,
    totalcapturedtributes numeric,
    avg_capturedtributes_per_game numeric,
    most_captured_tributes bigint,
    avg_dragonefectiveness_per_game double precision,
    most_effective_dragon double precision,
    avg_unitskilledasdragon_per_game numeric,
    totalunitskilledasdragon numeric,
    most_unitskilledasdragon bigint,
    avg_buildingskilledasdragon_per_game numeric,
    totalbuildingskilledasdragon numeric,
    most_buildingskilledasdragon bigint,
    totalplantpotskilled bigint,
    avg_plantpotskilled_per_game numeric,
    most_totalplantpotskilled integer,
    totalplantpotsplaced bigint,
    avg_plantpotsplaced_per_game numeric,
    most_totalplantpotsplaced integer,
    gardensseedscollected bigint,
    avg_gardensseedscollected_per_game numeric,
    most_gardensseedscollected integer,
    totalplantscontrolled bigint,
    avg_plantscontrolled_per_game numeric,
    most_plantscontrolled integer,
    totalunitskilledasplant bigint,
    avg_unitskilledasplant_per_game numeric,
    most_unitskilledasplant integer,
    totalbuildingskilledasplant bigint,
    avg_buildingskilledasplant_per_game numeric,
    most_buildingskilledasplant integer,
    avg_planteffectiveness_per_game double precision,
    most_planteffectiveness double precision,
    plantduration numeric,
    avg_plantduration_per_game numeric,
    most_plantduration bigint,
    totalminionskilled bigint,
    avg_minionskilled_per_game numeric,
    most_minionskilled integer,
    totalshrineminiondmg bigint,
    avg_shrineminiondmg_per_game numeric,
    most_shrineminiondmg integer,
    coinsturnedin numeric,
    avg_coinsturnedin_per_game numeric,
    most_coinsturnedin bigint,
    coinscollected numeric,
    avg_coinscollected_per_game numeric,
    most_coinscollected bigint,
    avg_coinseffectiveness_per_game double precision,
    most_coinseffectiveness double precision,
    totaltimeintemples numeric,
    avg_timeintemples_per_game numeric,
    most_timeintemples bigint,
    totalgemsturnedin bigint,
    avg_gemsturnedin_per_game numeric,
    most_gemsturnedin integer,
    times bigint
);


ALTER TABLE player_stats OWNER TO hotstats;

--
-- Name: players; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE players (
    replayid character varying(64) NOT NULL,
    team smallint NOT NULL,
    heroname character varying(64) NOT NULL,
    doc jsonb,
    updated_at timestamp without time zone DEFAULT clock_timestamp() NOT NULL
);


ALTER TABLE players OWNER TO hotstats;

--
-- Name: players_process; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE players_process (
    replayid character varying(64) NOT NULL,
    team smallint NOT NULL,
    heroname character varying(64) NOT NULL,
    doc jsonb,
    updated_at timestamp without time zone DEFAULT clock_timestamp() NOT NULL
);


ALTER TABLE players_process OWNER TO hotstats;

--
-- Name: replayinfo; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE replayinfo (
    replayid character varying(64) NOT NULL,
    doc jsonb,
    updated_at timestamp without time zone DEFAULT clock_timestamp() NOT NULL
);


ALTER TABLE replayinfo OWNER TO hotstats;

--
-- Name: reset_password_requests; Type: TABLE; Schema: public; Owner: hotsdata
--

CREATE TABLE reset_password_requests (
    id integer NOT NULL,
    email text NOT NULL,
    hashkey text NOT NULL,
    expiration_date numeric NOT NULL,
    resolved boolean DEFAULT false
);


ALTER TABLE reset_password_requests OWNER TO hotsdata;

--
-- Name: reset_password_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: hotsdata
--

CREATE SEQUENCE reset_password_requests_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE reset_password_requests_id_seq OWNER TO hotsdata;

--
-- Name: reset_password_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: hotsdata
--

ALTER SEQUENCE reset_password_requests_id_seq OWNED BY reset_password_requests.id;


--
-- Name: sky_temple_stats; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE sky_temple_stats (
    replayid character varying(64) NOT NULL,
    handle character varying(32),
    player character varying(20),
    hero character varying(20) NOT NULL,
    team smallint NOT NULL,
    gametype character varying(20),
    mapname character varying(32),
    gameversion integer,
    totaltimeintemples bigint
);


ALTER TABLE sky_temple_stats OWNER TO hotstats;

--
-- Name: spider_stats; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE spider_stats (
    replayid character varying(64) NOT NULL,
    handle character varying(32),
    player character varying(20),
    hero character varying(20) NOT NULL,
    team smallint NOT NULL,
    gametype character varying(20),
    mapname character varying(32),
    gameversion integer,
    totalgemstaken integer,
    totalgemsturnedin integer
);


ALTER TABLE spider_stats OWNER TO hotstats;

--
-- Name: stats_hero_bans; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE stats_hero_bans (
    heroname character varying(64) NOT NULL,
    mapname character varying(64) NOT NULL,
    game_type character varying(25) NOT NULL,
    gameversion integer NOT NULL,
    banned_games integer
);


ALTER TABLE stats_hero_bans OWNER TO hotstats;

--
-- Name: stats_historical_metrics; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE stats_historical_metrics (
    heroname character varying(30) NOT NULL,
    mapname character varying(64) NOT NULL,
    metric text NOT NULL,
    mpg_l30 numeric,
    mpg_l60 numeric,
    mpg_l90 numeric,
    mpg_l180 numeric,
    games_l30 bigint,
    games_l60 bigint,
    games_l90 bigint,
    games_l180 bigint,
    metric_l30 numeric,
    metric_l60 numeric,
    metric_l90 numeric,
    metric_l180 numeric
);


ALTER TABLE stats_historical_metrics OWNER TO hotstats;

--
-- Name: stats_historical_winrates; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE stats_historical_winrates (
    toonhandle character varying(64) NOT NULL,
    heroname character varying(64) NOT NULL,
    mapname character varying(64) NOT NULL,
    game_type character varying(25) NOT NULL,
    gameversion integer NOT NULL,
    winrate_l30 numeric,
    winrate_l60 numeric,
    winrate_l90 numeric,
    winrate_l180 numeric,
    games_l30 bigint,
    games_l60 bigint,
    games_l90 bigint,
    games_l180 bigint,
    wins_l30 numeric,
    wins_l60 numeric,
    wins_l90 numeric,
    wins_l180 numeric
);


ALTER TABLE stats_historical_winrates OWNER TO hotstats;

--
-- Name: stg_player_stats; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE stg_player_stats (
    player_id integer,
    toonhandle character varying(64),
    battletag character varying(64),
    name character varying(50),
    mapname character varying(64),
    gameversion integer,
    match_date timestamp without time zone,
    process_date timestamp without time zone,
    heroname character varying(30),
    stats jsonb,
    games bigint,
    gametype character varying(25)
);


ALTER TABLE stg_player_stats OWNER TO hotstats;

--
-- Name: stg_player_stats_0; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE stg_player_stats_0 (
    heroname character varying(50) NOT NULL,
    replayid character varying(64) NOT NULL,
    team smallint NOT NULL,
    metric text NOT NULL,
    value bigint,
    process_date timestamp without time zone NOT NULL
);


ALTER TABLE stg_player_stats_0 OWNER TO hotstats;

--
-- Name: stg_player_stats_1; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE stg_player_stats_1 (
    replayid character varying(64),
    team smallint,
    heroname character varying(50),
    value bigint,
    metric text,
    mapname text,
    gametype text,
    gameloops integer,
    gameversion integer,
    match_date timestamp without time zone,
    toonhandle character varying(64),
    playername character varying(64),
    battletag character varying(64),
    process_date date
);


ALTER TABLE stg_player_stats_1 OWNER TO hotstats;

--
-- Name: stg_player_stats_2; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE stg_player_stats_2 (
    heroname character varying(50),
    team smallint,
    replayid character varying(64),
    value bigint,
    metric text,
    process_date date
);


ALTER TABLE stg_player_stats_2 OWNER TO hotstats;

--
-- Name: stg_player_stats_3; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE stg_player_stats_3 (
    heroname character varying(50),
    mapname text,
    gameversion integer,
    gametype text,
    gameloops integer,
    value bigint,
    metric text,
    toonhandle text,
    battletag text,
    player_id integer,
    playername text,
    match_date timestamp without time zone,
    process_date date
);


ALTER TABLE stg_player_stats_3 OWNER TO hotstats;

--
-- Name: stg_player_stats_agg; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE stg_player_stats_agg (
    player_id integer NOT NULL,
    toonhandle character varying(64) NOT NULL,
    battletag character varying(64),
    name character varying(50) NOT NULL,
    mapname character varying(64) NOT NULL,
    gameversion integer NOT NULL,
    match_date timestamp without time zone NOT NULL,
    process_date timestamp without time zone,
    heroname character varying(30) NOT NULL,
    metric text NOT NULL,
    value bigint,
    games bigint,
    gametype character varying(25)
);


ALTER TABLE stg_player_stats_agg OWNER TO hotstats;

--
-- Name: stg_player_stats_agg_backup; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE stg_player_stats_agg_backup (
    player_id integer,
    toonhandle character varying(64),
    battletag character varying(64),
    name character varying(50),
    mapname character varying(64),
    gameversion integer,
    match_date timestamp without time zone,
    process_date timestamp without time zone,
    heroname character varying(30),
    metric text,
    value bigint,
    games bigint,
    gametype character varying(25)
);


ALTER TABLE stg_player_stats_agg_backup OWNER TO hotstats;

--
-- Name: talents; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE talents (
    id character varying(64) NOT NULL,
    patch integer NOT NULL,
    name character varying(64),
    hero character varying(64) NOT NULL,
    tier smallint,
    "position" smallint,
    icon character varying(64)
);


ALTER TABLE talents OWNER TO hotstats;

--
-- Name: teamgeneralstats; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE teamgeneralstats (
    replayid character varying(64) NOT NULL,
    team smallint NOT NULL,
    doc jsonb,
    updated_at timestamp without time zone DEFAULT clock_timestamp() NOT NULL
);


ALTER TABLE teamgeneralstats OWNER TO hotstats;

--
-- Name: teammapstats; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE teammapstats (
    replayid character varying(64) NOT NULL,
    team smallint NOT NULL,
    doc jsonb,
    updated_at timestamp without time zone DEFAULT clock_timestamp() NOT NULL
);


ALTER TABLE teammapstats OWNER TO hotstats;

--
-- Name: teammates; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE teammates (
    toonhandle_1 character varying(25) NOT NULL,
    toonhandle_2 character varying(25) NOT NULL,
    games bigint
);


ALTER TABLE teammates OWNER TO hotstats;

--
-- Name: timeline; Type: TABLE; Schema: public; Owner: hotstats
--

CREATE TABLE timeline (
    replayid character varying(64) NOT NULL,
    doc jsonb
);


ALTER TABLE timeline OWNER TO hotstats;

--
-- Name: player_id; Type: DEFAULT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY battletag_toonhandle_lookup ALTER COLUMN player_id SET DEFAULT nextval('battletag_toonhandle_lookup_player_id_seq'::regclass);


--
-- Name: user_id; Type: DEFAULT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY hotsdata_user ALTER COLUMN user_id SET DEFAULT nextval('hotsdata_user_user_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: hotsdata
--

ALTER TABLE ONLY reset_password_requests ALTER COLUMN id SET DEFAULT nextval('reset_password_requests_id_seq'::regclass);


--
-- Name: armystr_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY armystr
    ADD CONSTRAINT armystr_pk PRIMARY KEY (replayid);


--
-- Name: battlefield_eternity_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY battlefield_eternity_stats
    ADD CONSTRAINT battlefield_eternity_stats_pkey PRIMARY KEY (hero, team, replayid);


--
-- Name: battletag_toonhandle_current_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY battletag_toonhandle_current
    ADD CONSTRAINT battletag_toonhandle_current_pk PRIMARY KEY (battletag, toonhandle);


--
-- Name: battletag_toonhandle_lookup_pkey; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY battletag_toonhandle_lookup
    ADD CONSTRAINT battletag_toonhandle_lookup_pkey PRIMARY KEY (battletag, toonhandle);


--
-- Name: cursed_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY cursed_stats
    ADD CONSTRAINT cursed_stats_pkey PRIMARY KEY (hero, team, replayid);


--
-- Name: deathlist_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY deathlist
    ADD CONSTRAINT deathlist_pk PRIMARY KEY (replayid, mapname);


--
-- Name: dragon_shire_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY dragon_shire_stats
    ADD CONSTRAINT dragon_shire_stats_pkey PRIMARY KEY (hero, team, replayid);


--
-- Name: fct_player_stats_agg_pkey; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY fct_player_stats_agg
    ADD CONSTRAINT fct_player_stats_agg_pkey PRIMARY KEY (toonhandle, match_date, gameversion, gametype, mapname, heroname, process_date, name, player_id);


--
-- Name: garden_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY garden_stats
    ADD CONSTRAINT garden_stats_pkey PRIMARY KEY (hero, team, replayid);


--
-- Name: generalstats_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY generalstats
    ADD CONSTRAINT generalstats_pk PRIMARY KEY (replayid, team, heroname);


--
-- Name: hero_data_pkey; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY hero_data
    ADD CONSTRAINT hero_data_pkey PRIMARY KEY (hero_id);


--
-- Name: hero_info_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY hero_info
    ADD CONSTRAINT hero_info_pk PRIMARY KEY (build, hero_name, talent_tier, talent_choice);


--
-- Name: hero_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY heroes
    ADD CONSTRAINT hero_pk PRIMARY KEY (id, patch);


--
-- Name: hu_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY hotsdata_user
    ADD CONSTRAINT hu_pk PRIMARY KEY (email);


--
-- Name: infernal_shrines_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY infernal_shrines_stats
    ADD CONSTRAINT infernal_shrines_stats_pkey PRIMARY KEY (hero, team, replayid);


--
-- Name: mapstats_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY mapstats
    ADD CONSTRAINT mapstats_pk PRIMARY KEY (replayid, team, heroname);


--
-- Name: phmsd_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY player_hero_map_stats_daily
    ADD CONSTRAINT phmsd_pk PRIMARY KEY (toonhandle, name, mapname, heroname, starttime);


--
-- Name: pirate_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY pirate_stats
    ADD CONSTRAINT pirate_stats_pkey PRIMARY KEY (hero, team, replayid);


--
-- Name: player_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY player_stats
    ADD CONSTRAINT player_stats_pkey PRIMARY KEY (handle, player, mapname, hero, gametype, gameversion);


--
-- Name: players_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY players
    ADD CONSTRAINT players_pk PRIMARY KEY (replayid, team, heroname);


--
-- Name: players_pk_; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY players_process
    ADD CONSTRAINT players_pk_ PRIMARY KEY (replayid, team, heroname);


--
-- Name: replayinfo_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY replayinfo
    ADD CONSTRAINT replayinfo_pk PRIMARY KEY (replayid);


--
-- Name: reset_password_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: hotsdata
--

ALTER TABLE ONLY reset_password_requests
    ADD CONSTRAINT reset_password_requests_pkey PRIMARY KEY (id);


--
-- Name: sky_temple_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY sky_temple_stats
    ADD CONSTRAINT sky_temple_stats_pkey PRIMARY KEY (hero, team, replayid);


--
-- Name: spider_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY spider_stats
    ADD CONSTRAINT spider_stats_pkey PRIMARY KEY (hero, team, replayid);


--
-- Name: stats_hero_bans_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY stats_hero_bans
    ADD CONSTRAINT stats_hero_bans_pk PRIMARY KEY (heroname, mapname, game_type, gameversion);


--
-- Name: stats_historical_metrics_heroname_mapname_metric_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY stats_historical_metrics
    ADD CONSTRAINT stats_historical_metrics_heroname_mapname_metric_pk PRIMARY KEY (heroname, mapname, metric);


--
-- Name: stats_historical_winrates_toonhandle_mapname_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY stats_historical_winrates
    ADD CONSTRAINT stats_historical_winrates_toonhandle_mapname_pk PRIMARY KEY (toonhandle, heroname, mapname, game_type, gameversion);


--
-- Name: stg_player_stats_0_pkey; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY stg_player_stats_0
    ADD CONSTRAINT stg_player_stats_0_pkey PRIMARY KEY (process_date, replayid, heroname, team, metric);


--
-- Name: stg_player_stats_agg_pkey; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY stg_player_stats_agg
    ADD CONSTRAINT stg_player_stats_agg_pkey PRIMARY KEY (match_date, player_id, toonhandle, name, mapname, gameversion, heroname, metric);


--
-- Name: talents_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY talents
    ADD CONSTRAINT talents_pk PRIMARY KEY (id, patch, hero);


--
-- Name: teamgeneralstats_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY teamgeneralstats
    ADD CONSTRAINT teamgeneralstats_pk PRIMARY KEY (replayid, team);


--
-- Name: teammapstats_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY teammapstats
    ADD CONSTRAINT teammapstats_pk PRIMARY KEY (replayid, team);


--
-- Name: teammates_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY teammates
    ADD CONSTRAINT teammates_pk PRIMARY KEY (toonhandle_1, toonhandle_2);


--
-- Name: timeline_pk; Type: CONSTRAINT; Schema: public; Owner: hotstats
--

ALTER TABLE ONLY timeline
    ADD CONSTRAINT timeline_pk PRIMARY KEY (replayid);


--
-- Name: battletag_toonhandle_lookup_toonhandle_index; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX battletag_toonhandle_lookup_toonhandle_index ON battletag_toonhandle_lookup USING btree (toonhandle);


--
-- Name: btag_idx; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX btag_idx ON players USING gin (doc);


--
-- Name: btl; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX btl ON battletag_toonhandle_lookup USING btree (player_id);


--
-- Name: hero_info_internal_name; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX hero_info_internal_name ON hero_info USING btree (talent_internal_name);


--
-- Name: idx_players_updated_at; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX idx_players_updated_at ON players_process USING btree (updated_at);


--
-- Name: idx_stats; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX idx_stats ON fct_player_stats_agg USING gin (stats);


--
-- Name: match_date_stg_agg; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX match_date_stg_agg ON stg_player_stats_agg USING btree (match_date);


--
-- Name: process_date_stg; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX process_date_stg ON stg_player_stats_0 USING btree (process_date);


--
-- Name: process_date_stg_1; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX process_date_stg_1 ON stg_player_stats_1 USING btree (process_date);


--
-- Name: process_date_stg_3; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX process_date_stg_3 ON stg_player_stats_3 USING btree (process_date);


--
-- Name: stg_player_stats_1_replayid_team_heroname_index; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX stg_player_stats_1_replayid_team_heroname_index ON stg_player_stats_1 USING btree (replayid, team, heroname);


--
-- Name: stg_player_stats_agg_heroname_mapname_toonhandle_index; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX stg_player_stats_agg_heroname_mapname_toonhandle_index ON stg_player_stats_agg USING btree (heroname, mapname, toonhandle);


--
-- Name: stg_player_stats_agg_match_date_metric_player_id_index; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX stg_player_stats_agg_match_date_metric_player_id_index ON stg_player_stats_agg USING btree (match_date, metric, player_id);


--
-- Name: stg_player_stats_agg_toonhandle_match_date_metric_index; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX stg_player_stats_agg_toonhandle_match_date_metric_index ON stg_player_stats_agg USING btree (toonhandle, match_date, metric);


--
-- Name: stg_ps_1; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX stg_ps_1 ON stg_player_stats_1 USING btree (replayid, team, heroname, gameversion);


--
-- Name: teammates_th2; Type: INDEX; Schema: public; Owner: hotstats
--

CREATE INDEX teammates_th2 ON teammates USING btree (toonhandle_2);


--
-- Name: update_battletag_toonhandle_current; Type: TRIGGER; Schema: public; Owner: hotstats
--

CREATE TRIGGER update_battletag_toonhandle_current AFTER INSERT OR UPDATE ON battletag_toonhandle_lookup FOR EACH ROW EXECUTE PROCEDURE insert_battletag_toonhandle_current();


--
-- Name: update_generalstats; Type: TRIGGER; Schema: public; Owner: hotstats
--

CREATE TRIGGER update_generalstats BEFORE UPDATE ON generalstats FOR EACH ROW EXECUTE PROCEDURE set_updated_at();


--
-- Name: update_hotsdata_users; Type: TRIGGER; Schema: public; Owner: hotstats
--

CREATE TRIGGER update_hotsdata_users BEFORE UPDATE ON hotsdata_user FOR EACH ROW EXECUTE PROCEDURE set_updated_at();


--
-- Name: reset_password_requests_hotsdata_user_email_fk; Type: FK CONSTRAINT; Schema: public; Owner: hotsdata
--

ALTER TABLE ONLY reset_password_requests
    ADD CONSTRAINT reset_password_requests_hotsdata_user_email_fk FOREIGN KEY (email) REFERENCES hotsdata_user(email);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: armystr; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE armystr FROM PUBLIC;
REVOKE ALL ON TABLE armystr FROM hotstats;
GRANT ALL ON TABLE armystr TO hotstats;
GRANT SELECT ON TABLE armystr TO hotsdata;


--
-- Name: battlefield_eternity_stats; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE battlefield_eternity_stats FROM PUBLIC;
REVOKE ALL ON TABLE battlefield_eternity_stats FROM hotstats;
GRANT ALL ON TABLE battlefield_eternity_stats TO hotstats;
GRANT SELECT ON TABLE battlefield_eternity_stats TO hotsdata;


--
-- Name: battletag_toonhandle_lookup; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE battletag_toonhandle_lookup FROM PUBLIC;
REVOKE ALL ON TABLE battletag_toonhandle_lookup FROM hotstats;
GRANT ALL ON TABLE battletag_toonhandle_lookup TO hotstats;
GRANT SELECT ON TABLE battletag_toonhandle_lookup TO hotsdata;


--
-- Name: cursed_stats; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE cursed_stats FROM PUBLIC;
REVOKE ALL ON TABLE cursed_stats FROM hotstats;
GRANT ALL ON TABLE cursed_stats TO hotstats;
GRANT SELECT ON TABLE cursed_stats TO hotsdata;


--
-- Name: deathlist; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE deathlist FROM PUBLIC;
REVOKE ALL ON TABLE deathlist FROM hotstats;
GRANT ALL ON TABLE deathlist TO hotstats;
GRANT SELECT ON TABLE deathlist TO hotsdata;


--
-- Name: dragon_shire_stats; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE dragon_shire_stats FROM PUBLIC;
REVOKE ALL ON TABLE dragon_shire_stats FROM hotstats;
GRANT ALL ON TABLE dragon_shire_stats TO hotstats;
GRANT SELECT ON TABLE dragon_shire_stats TO hotsdata;


--
-- Name: garden_stats; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE garden_stats FROM PUBLIC;
REVOKE ALL ON TABLE garden_stats FROM hotstats;
GRANT ALL ON TABLE garden_stats TO hotstats;
GRANT SELECT ON TABLE garden_stats TO hotsdata;


--
-- Name: generalstats; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE generalstats FROM PUBLIC;
REVOKE ALL ON TABLE generalstats FROM hotstats;
GRANT ALL ON TABLE generalstats TO hotstats;
GRANT SELECT ON TABLE generalstats TO hotsdata;


--
-- Name: hero_info; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE hero_info FROM PUBLIC;
REVOKE ALL ON TABLE hero_info FROM hotstats;
GRANT ALL ON TABLE hero_info TO hotstats;
GRANT SELECT ON TABLE hero_info TO hotsdata;


--
-- Name: hotsdata_user; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE hotsdata_user FROM PUBLIC;
REVOKE ALL ON TABLE hotsdata_user FROM hotstats;
GRANT ALL ON TABLE hotsdata_user TO hotstats;
GRANT SELECT,INSERT,UPDATE ON TABLE hotsdata_user TO hotsdata;


--
-- Name: hotsdata_user_user_id_seq; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON SEQUENCE hotsdata_user_user_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE hotsdata_user_user_id_seq FROM hotstats;
GRANT ALL ON SEQUENCE hotsdata_user_user_id_seq TO hotstats;
GRANT SELECT,UPDATE ON SEQUENCE hotsdata_user_user_id_seq TO hotsdata;


--
-- Name: infernal_shrines_stats; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE infernal_shrines_stats FROM PUBLIC;
REVOKE ALL ON TABLE infernal_shrines_stats FROM hotstats;
GRANT ALL ON TABLE infernal_shrines_stats TO hotstats;
GRANT SELECT ON TABLE infernal_shrines_stats TO hotsdata;


--
-- Name: mapstats; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE mapstats FROM PUBLIC;
REVOKE ALL ON TABLE mapstats FROM hotstats;
GRANT ALL ON TABLE mapstats TO hotstats;
GRANT SELECT ON TABLE mapstats TO hotsdata;


--
-- Name: pirate_stats; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE pirate_stats FROM PUBLIC;
REVOKE ALL ON TABLE pirate_stats FROM hotstats;
GRANT ALL ON TABLE pirate_stats TO hotstats;
GRANT SELECT ON TABLE pirate_stats TO hotsdata;


--
-- Name: player_hero_map_stats_daily; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE player_hero_map_stats_daily FROM PUBLIC;
REVOKE ALL ON TABLE player_hero_map_stats_daily FROM hotstats;
GRANT ALL ON TABLE player_hero_map_stats_daily TO hotstats;
GRANT SELECT ON TABLE player_hero_map_stats_daily TO hotsdata;


--
-- Name: player_stats; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE player_stats FROM PUBLIC;
REVOKE ALL ON TABLE player_stats FROM hotstats;
GRANT ALL ON TABLE player_stats TO hotstats;
GRANT SELECT ON TABLE player_stats TO hotsdata;


--
-- Name: players; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE players FROM PUBLIC;
REVOKE ALL ON TABLE players FROM hotstats;
GRANT ALL ON TABLE players TO hotstats;
GRANT SELECT ON TABLE players TO hotsdata;


--
-- Name: replayinfo; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE replayinfo FROM PUBLIC;
REVOKE ALL ON TABLE replayinfo FROM hotstats;
GRANT ALL ON TABLE replayinfo TO hotstats;
GRANT SELECT ON TABLE replayinfo TO hotsdata;


--
-- Name: reset_password_requests; Type: ACL; Schema: public; Owner: hotsdata
--

REVOKE ALL ON TABLE reset_password_requests FROM PUBLIC;
REVOKE ALL ON TABLE reset_password_requests FROM hotsdata;
GRANT ALL ON TABLE reset_password_requests TO hotsdata;
GRANT ALL ON TABLE reset_password_requests TO hotstats;


--
-- Name: reset_password_requests_id_seq; Type: ACL; Schema: public; Owner: hotsdata
--

REVOKE ALL ON SEQUENCE reset_password_requests_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE reset_password_requests_id_seq FROM hotsdata;
GRANT ALL ON SEQUENCE reset_password_requests_id_seq TO hotsdata;
GRANT ALL ON SEQUENCE reset_password_requests_id_seq TO hotstats;


--
-- Name: sky_temple_stats; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE sky_temple_stats FROM PUBLIC;
REVOKE ALL ON TABLE sky_temple_stats FROM hotstats;
GRANT ALL ON TABLE sky_temple_stats TO hotstats;
GRANT SELECT ON TABLE sky_temple_stats TO hotsdata;


--
-- Name: spider_stats; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE spider_stats FROM PUBLIC;
REVOKE ALL ON TABLE spider_stats FROM hotstats;
GRANT ALL ON TABLE spider_stats TO hotstats;
GRANT SELECT ON TABLE spider_stats TO hotsdata;


--
-- Name: stats_historical_metrics; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE stats_historical_metrics FROM PUBLIC;
REVOKE ALL ON TABLE stats_historical_metrics FROM hotstats;
GRANT ALL ON TABLE stats_historical_metrics TO hotstats;
GRANT SELECT ON TABLE stats_historical_metrics TO hotsdata;


--
-- Name: teamgeneralstats; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE teamgeneralstats FROM PUBLIC;
REVOKE ALL ON TABLE teamgeneralstats FROM hotstats;
GRANT ALL ON TABLE teamgeneralstats TO hotstats;
GRANT SELECT ON TABLE teamgeneralstats TO hotsdata;


--
-- Name: teammapstats; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE teammapstats FROM PUBLIC;
REVOKE ALL ON TABLE teammapstats FROM hotstats;
GRANT ALL ON TABLE teammapstats TO hotstats;
GRANT SELECT ON TABLE teammapstats TO hotsdata;


--
-- Name: timeline; Type: ACL; Schema: public; Owner: hotstats
--

REVOKE ALL ON TABLE timeline FROM PUBLIC;
REVOKE ALL ON TABLE timeline FROM hotstats;
GRANT ALL ON TABLE timeline TO hotstats;
GRANT SELECT ON TABLE timeline TO hotsdata;


--
-- PostgreSQL database dump complete
--
