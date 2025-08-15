DROP PROCEDURE IF EXISTS InsertMetaIfTableExists;

CREATE PROCEDURE InsertMetaIfTableExists()
BEGIN
    DECLARE table_exists INT;

    SELECT COUNT(*)
    INTO table_exists
    FROM information_schema.tables
    WHERE table_schema = DATABASE() AND table_name = 'dap_meta';

    IF table_exists > 0 THEN
        TRUNCATE TABLE instructure_dap__table_sync;

        INSERT IGNORE INTO instructure_dap__table_sync (
                source_namespace,
                source_table,
                timestamp,
                schema_version,
                target_schema,
                target_table,
                schema_description_format,
                schema_description
            )
        SELECT IF(
                source_table LIKE 'catalog~_~_%' ESCAPE '~',
                SUBSTRING_INDEX(source_table, '__', 1),
                IF(source_table <> 'web_logs', 'canvas', 'canvas_logs')
            ) AS source_namespace,
            IF(
                source_table LIKE 'catalog~_~_%' ESCAPE '~',
                SUBSTRING_INDEX(source_table, '__', -1),
                source_table
            ) AS source_table,
            timestamp,
            schema_version,
            IF(
                target_table LIKE 'catalog~_~_%' ESCAPE '~',
                SUBSTRING_INDEX(target_table, '__', 1),
                IF(source_table <> 'web_logs', 'canvas', 'canvas_logs')
            ) AS target_namespace,
            IF(
                target_table LIKE 'catalog~_~_%' ESCAPE '~',
                SUBSTRING_INDEX(target_table, '__', -1),
                target_table
            ) AS target_table,
            schema_description_format,
            schema_description
        FROM dap_meta;

        RENAME TABLE dap_meta TO dap_meta_backup;
    ELSE
        SELECT 'Table dap_meta does not exist.';
    END IF;
END;

CALL  InsertMetaIfTableExists();


DROP PROCEDURE IF EXISTS MigrateCanvasTables;

CREATE PROCEDURE MigrateCanvasTables()
BEGIN
    DECLARE tableCount INT DEFAULT 0;
    DECLARE tableName VARCHAR(255);
    DECLARE done INT DEFAULT FALSE;
    DECLARE metaTableExists INT;

    
    DECLARE tablesCursor CURSOR FOR
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
            AND table_name IN (
                'access_tokens', 'account_users', 'accounts', 'assessment_question_banks', 'assessment_questions',
                'assignment_groups', 'assignment_override_students', 'assignment_overrides', 'assignments',
                'attachment_associations', 'attachments', 'calendar_events', 'canvadocs_annotation_contexts',
                'comment_bank_items', 'communication_channels', 'content_migrations',
                'content_participation_counts', 'content_participations', 'content_shares', 'content_tags',
                'context_external_tools', 'context_module_progressions', 'context_modules',
                'conversation_message_participants', 'conversation_messages', 'conversation_participants',
                'conversations', 'course_account_associations', 'course_sections', 'courses',
                'custom_gradebook_column_data', 'custom_gradebook_columns', 'developer_key_account_bindings',
                'developer_keys', 'discussion_entries', 'discussion_entry_participants',
                'discussion_topic_participants', 'discussion_topics', 'enrollment_dates_overrides',
                'enrollment_states', 'enrollment_terms', 'enrollments', 'favorites', 'folders',
                'grading_period_groups', 'grading_periods', 'grading_standards', 'group_categories',
                'group_memberships', 'groups', 'late_policies', 'learning_outcome_groups',
                'learning_outcome_question_results', 'learning_outcome_results', 'learning_outcomes',
                'lti_line_items', 'lti_resource_links', 'lti_results', 'master_courses_child_content_tags',
                'master_courses_child_subscriptions', 'master_courses_master_content_tags',
                'master_courses_master_migrations', 'master_courses_master_templates',
                'master_courses_migration_results', 'originality_reports', 'outcome_proficiencies',
                'outcome_proficiency_ratings', 'post_policies', 'pseudonyms', 'quiz_groups', 'quiz_questions',
                'quiz_submissions', 'quizzes', 'role_overrides', 'roles', 'rubric_assessments',
                'rubric_associations', 'rubrics', 'score_statistics', 'scores', 'submission_comments',
                'submission_versions', 'submissions', 'user_account_associations', 'user_notes', 'users',
                'web_conference_participants', 'web_conferences', 'wiki_pages', 'wikis'
            );

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    SELECT COUNT(*)
    INTO metaTableExists
    FROM information_schema.tables
    WHERE table_schema = DATABASE() AND table_name = 'instructure_dap__table_sync';

    IF metaTableExists > 0 THEN
        SELECT COUNT(*)
        INTO tableCount
        FROM instructure_dap__table_sync;

        IF tableCount > 0 THEN
            SET SESSION group_concat_max_len = 16383;
            
            OPEN tablesCursor;

            tablesLoop: LOOP
                FETCH tablesCursor INTO tableName;

                IF done THEN
                    LEAVE tablesLoop;
                END IF;

                SET @sqlQuery = CONCAT('RENAME TABLE "', tableName, '" TO "canvas__', tableName, '"');
                -- Execute the dynamic SQL
                PREPARE stmt FROM @sqlQuery;
                EXECUTE stmt;
                DEALLOCATE PREPARE stmt;
            END LOOP;

            CLOSE tablesCursor;
        ELSE
            SELECT 'Table instructure_dap__table_sync is empty.';
        END IF;
    ELSE
        SELECT 'Table instructure_dap__table_sync does not exist.';
    END IF;
END;

CALL MigrateCanvasTables();

DROP PROCEDURE IF EXISTS MigrateCanvasLogsTables;

CREATE PROCEDURE MigrateCanvasLogsTables()
BEGIN
    DECLARE tableCount INT DEFAULT 0;
    DECLARE tableName VARCHAR(255);
    DECLARE done INT DEFAULT FALSE;
    DECLARE metaTableExists INT;

    DECLARE tablesCursor CURSOR FOR
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
            AND table_name IN (
                'web_logs'
            );

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    SELECT COUNT(*)
    INTO metaTableExists
    FROM information_schema.tables
    WHERE table_schema = DATABASE() AND table_name = 'instructure_dap__table_sync';

    IF metaTableExists > 0 THEN
        SELECT COUNT(*)
        INTO tableCount
        FROM instructure_dap__table_sync;

        IF tableCount > 0 THEN
            SET SESSION group_concat_max_len = 16383;
            
            OPEN tablesCursor;

            tablesLoop: LOOP
                FETCH tablesCursor INTO tableName;

                IF done THEN
                    LEAVE tablesLoop;
                END IF;

                SET @sqlQuery = CONCAT('RENAME TABLE "', tableName, '" TO "canvas_logs__', tableName, '"');
                -- Execute the dynamic SQL
                PREPARE stmt FROM @sqlQuery;
                EXECUTE stmt;
                DEALLOCATE PREPARE stmt;
            END LOOP;

            CLOSE tablesCursor;
        ELSE
            SELECT 'Table instructure_dap__table_sync is empty.';
        END IF;
    ELSE
        SELECT 'Table instructure_dap__table_sync does not exist.';
    END IF;
END;

CALL MigrateCanvasLogsTables();
