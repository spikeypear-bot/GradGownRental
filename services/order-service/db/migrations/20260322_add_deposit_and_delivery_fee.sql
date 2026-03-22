-- Migration: Add deposit and delivery_fee columns to orders table
-- Date: 2026-03-22
-- Description: Add support for deposit tracking and delivery fees for order pricing

ALTER TABLE orders
ADD COLUMN IF NOT EXISTS deposit DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS delivery_fee DECIMAL(10, 2) NOT NULL DEFAULT 0.00;

-- Add comments explaining the new columns
COMMENT ON COLUMN orders.deposit IS 'Total deposit amount from all selected items, used for damage refund calculation';
COMMENT ON COLUMN orders.delivery_fee IS '$5 flat rate if fulfillment_method is DELIVERY, $0 if COLLECTION';
