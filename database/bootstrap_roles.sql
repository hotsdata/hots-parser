--
-- Development bootstrap roles required before loading database_schema.sql.
--
-- The schema dump assigns object ownership to `hotstats` and grants read/API
-- access to `hotsdata`, so both roles must exist before database_schema.sql is
-- applied to a fresh PostgreSQL cluster.
--
-- These passwords are local-development defaults. Use stronger credentials in
-- shared or production environments.
--

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'hotstats') THEN
        CREATE ROLE hotstats LOGIN PASSWORD 'hotstats';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'hotsdata') THEN
        CREATE ROLE hotsdata LOGIN PASSWORD 'hotsdata';
    END IF;
END
$$;

ALTER ROLE hotstats LOGIN;
ALTER ROLE hotsdata LOGIN;
