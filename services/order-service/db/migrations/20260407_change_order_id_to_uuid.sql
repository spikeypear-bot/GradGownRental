-- Migration: Ensure order_id is VARCHAR(36)
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
        WHERE table_name = 'orders'
          AND column_name = 'order_id'
          AND data_type = 'uuid'
    ) THEN
        DROP INDEX IF EXISTS idx_orders_order_id;
        ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_order_id_key;

        ALTER TABLE orders
            ALTER COLUMN order_id TYPE VARCHAR(36) USING order_id::TEXT;

        ALTER TABLE orders ADD CONSTRAINT orders_order_id_key UNIQUE (order_id);
        CREATE INDEX idx_orders_order_id ON orders (order_id);
    END IF;
END$$;
