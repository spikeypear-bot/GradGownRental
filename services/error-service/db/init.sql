CREATE TABLE IF NOT EXISTS error_log (
    error_id      VARCHAR(36) PRIMARY KEY,
    saga_name     VARCHAR(100) NOT NULL,
    step          VARCHAR(100) NOT NULL,
    order_id      VARCHAR(100),
    error_message TEXT NOT NULL,
    status_code   INT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_error_log_order_id ON error_log (order_id);
CREATE INDEX IF NOT EXISTS idx_error_log_created_at ON error_log (created_at DESC);
