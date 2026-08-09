-- Transactional script to drop unused Supabase schemas from local DB
-- Usage: psql "postgresql://postgres:0728@localhost:5432/personal_portfolio" -f cleanup_unused_schemas.sql

\echo '=== Pre-drop inventory ==='
SELECT nspname, count(*) as table_count
FROM pg_class c JOIN pg_namespace n ON c.relnamespace = n.oid
WHERE n.nspname IN ('auth', 'realtime', 'storage') AND c.relkind = 'r'
GROUP BY nspname ORDER BY nspname;

\echo ''
\echo '=== Starting transaction ==='
BEGIN;

\echo 'Dropping schema: auth'
DROP SCHEMA IF EXISTS auth CASCADE;

\echo 'Dropping schema: realtime'
DROP SCHEMA IF EXISTS realtime CASCADE;

\echo 'Dropping schema: storage'
DROP SCHEMA IF EXISTS storage CASCADE;

\echo ''
\echo '=== Post-drop verification ==='
DO $$
DECLARE
    remaining_schemas TEXT;
    bad_schemas TEXT;
BEGIN
    -- Check no auth/realtime/storage schemas remain
    SELECT string_agg(nspname, ', ') INTO bad_schemas
    FROM pg_namespace
    WHERE nspname IN ('auth', 'realtime', 'storage');

    IF bad_schemas IS NOT NULL THEN
        RAISE EXCEPTION 'Schemas still exist after DROP: %', bad_schemas;
    END IF;

    -- List remaining non-system schemas
    SELECT string_agg(s.nspname, ', ') INTO remaining_schemas
    FROM (SELECT nspname FROM pg_namespace
          WHERE nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
          ORDER BY nspname) s;

    RAISE NOTICE 'Remaining schemas: %', remaining_schemas;
END $$;

\echo ''
\echo '=== All checks passed. Committing ==='
COMMIT;

\echo ''
\echo '=== Done. Verifying final state ==='
SELECT nspname FROM pg_namespace
WHERE nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
ORDER BY nspname;
