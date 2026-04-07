-- Migration: Ensure order_id is VARCHAR(36) in notification_logs
-- Date: 2026-04-07
-- Description: order_id is generated as a UUID string by the service layer
--              and stored as VARCHAR(36). This migration ensures the column
--              is the correct type on existing deployments.

-- If the column is currently UUID (from a previous version of this migration),
-- convert it back to VARCHAR(36).
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'notification_logs'
          AND column_name = 'order_id'
          AND data_type = 'uuid'
    ) THEN
        DROP INDEX IF EXISTS idx_notification_logs_order_id;

        ALTER TABLE notification_logs
            ALTER COLUMN order_id TYPE VARCHAR(36) USING order_id::TEXT;

        CREATE INDEX idx_notification_logs_order_id ON notification_logs (order_id);
    END IF;
END$$;
