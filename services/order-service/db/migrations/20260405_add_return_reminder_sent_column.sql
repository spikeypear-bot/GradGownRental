-- Add return_reminder_sent column to track if return reminder has been sent
-- This prevents spamming multiple reminders for the same return date

ALTER TABLE orders
ADD COLUMN return_reminder_sent BOOLEAN DEFAULT FALSE;

-- Create index for efficient queries filtering by this flag
CREATE INDEX idx_orders_return_reminder_sent 
ON orders(return_reminder_sent, rental_end_date)
WHERE status IN ('ACTIVE', 'RETURNED_DAMAGED') AND return_reminder_sent = FALSE;
