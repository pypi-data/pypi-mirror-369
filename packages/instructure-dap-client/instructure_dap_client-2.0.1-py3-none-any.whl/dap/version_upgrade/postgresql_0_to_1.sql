DO
$$
    DECLARE
        ns VARCHAR[];
    BEGIN
        ns := ARRAY ['canvas', 'catalog', 'canvas_logs'];

        EXECUTE ('TRUNCATE TABLE instructure_dap.table_sync');

        FOR i IN 1..ARRAY_LENGTH(ns, 1)
            LOOP
                IF EXISTS (SELECT 1
                           FROM information_schema.tables
                           WHERE table_schema = ns[i]
                             AND table_name = 'dap_meta') THEN
                    EXECUTE FORMAT('
                INSERT INTO instructure_dap.table_sync
                    (
                        source_namespace,
                        source_table,
                        timestamp,
                        schema_version,
                        target_schema,
                        target_table,
                        schema_description_format,
                        schema_description
                    )
                SELECT namespace,
                       source_table,
                       timestamp,
                       schema_version,
                       target_schema,
                       target_table,
                       schema_description_format,
                       schema_description
                FROM %I.dap_meta', ns[i]);
                EXECUTE FORMAT('ALTER TABLE %I.dap_meta RENAME TO dap_meta_backup', ns[i]);
                ELSE
                    RAISE NOTICE 'Table %.dap_meta does not exist.', ns[i];
                END IF;
            END LOOP;
    END
$$;
