from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_pgwatch', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION smart_notify(
                channel_name TEXT,
                payload_data JSONB DEFAULT '{}'::jsonb
            ) RETURNS BIGINT AS $$
            DECLARE
                notification_log_id BIGINT;
                notification_payload JSONB;
            BEGIN
                -- Insert into log table first
                INSERT INTO services.django_pgwatch_notificationlog (channel, payload, created_at, processed_by)
                VALUES (channel_name, payload_data, NOW(), '{}')
                RETURNING id INTO notification_log_id;

                -- Build notification with notification log ID
                notification_payload := jsonb_build_object(
                    'notification_log_id', notification_log_id,
                    'timestamp', extract(epoch from now()),
                    'data', payload_data
                );

                -- Send notification (truncate if too large)
                IF length(notification_payload::text) > 7500 THEN
                    -- Send minimal notification for large payloads
                    notification_payload := jsonb_build_object(
                        'notification_log_id', notification_log_id,
                        'timestamp', extract(epoch from now()),
                        'large_payload', true
                    );
                END IF;

                PERFORM pg_notify(channel_name, notification_payload::text);

                RETURN notification_log_id;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS smart_notify(TEXT, JSONB);",
        ),
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION notify_data_change()
            RETURNS trigger AS $$
            DECLARE
                payload_data JSONB;
                notification_log_id BIGINT;
            BEGIN
                -- Build complex payload
                payload_data := jsonb_build_object(
                    'table', TG_TABLE_NAME,
                    'action', TG_OP,
                    'id', COALESCE(NEW.id, OLD.id),
                    'old_data', CASE
                        WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD)
                        WHEN TG_OP = 'UPDATE' THEN to_jsonb(OLD)
                        ELSE NULL
                    END,
                    'new_data', CASE
                        WHEN TG_OP != 'DELETE' THEN to_jsonb(NEW)
                        ELSE NULL
                    END,
                    'metadata', jsonb_build_object(
                        'user_id', current_setting('app.user_id', true),
                        'session_id', current_setting('app.session_id', true),
                        'transaction_id', txid_current()
                    )
                );

                -- Use smart_notify function
                SELECT smart_notify('data_change', payload_data) INTO notification_log_id;

                RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS notify_data_change();",
        ),
    ]
