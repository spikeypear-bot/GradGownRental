-- Add damaged column to orders table
ALTER TABLE orders ADD COLUMN damaged BOOLEAN DEFAULT FALSE;