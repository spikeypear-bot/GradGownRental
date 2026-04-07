-- Migration: Drop phone column from orders table
-- Date: 2026-04-07
-- Description: Phone number is no longer stored on orders.
--              The INSERT no longer supplies this value, so the NOT NULL constraint
--              causes every order creation to fail with a 500 error.

ALTER TABLE orders DROP COLUMN IF EXISTS phone;
