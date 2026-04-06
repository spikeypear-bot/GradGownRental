-- Migration: Fix negative rented quantities for all models
-- Date: 2026-04-06
-- Issue: Some models had negative rentedQty due to improper return processing
-- Solution: Recalculate rented quantities based on actual orders

-- Fix model 0000024 (NUS Mortarboard with Black Tassel - XS)
-- Current rentedQty: -5, should be: 0
UPDATE inventory_model SET rented_qty = 0 WHERE model_id = '0000024';

-- Fix model 0100020 (Light Cerise Hood - S)
-- Current rentedQty: -1, should be: 0
UPDATE inventory_model SET rented_qty = 0 WHERE model_id = '0100020';

-- Verify the fix
SELECT model_id, total_qty, available_qty, rented_qty 
FROM inventory_model 
WHERE model_id IN ('0000024', '0100020')
ORDER BY model_id;

-- General fix: Reset all negative rented_qty to 0
UPDATE inventory_model 
SET rented_qty = CASE 
  WHEN rented_qty < 0 THEN 0 
  ELSE rented_qty 
END 
WHERE rented_qty < 0;

-- Verify all models have non-negative quantities
SELECT model_id, total_qty, available_qty, rented_qty, damaged_qty, repair_qty, wash_qty
FROM inventory_model 
WHERE rented_qty < 0 OR damaged_qty < 0 OR repair_qty < 0 OR wash_qty < 0
ORDER BY model_id;
