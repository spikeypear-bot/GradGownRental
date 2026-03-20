-- notification-service/db/init.sql
-- Initialises the notification_logs table on first container startup.

CREATE TABLE IF NOT EXISTS notification_logs (
    id              SERIAL          PRIMARY KEY,
    order_id        VARCHAR(64)     NOT NULL,
    event_type      VARCHAR(32)     NOT NULL,   -- e.g. 'OrderConfirmed', 'pickup_reminder'
    channel         VARCHAR(8)      NOT NULL,   -- 'SMS' | 'EMAIL'
    recipient       VARCHAR(255)    NOT NULL,   -- phone number or email address
    message_body    TEXT            NOT NULL,
    status          VARCHAR(10)     NOT NULL DEFAULT 'PENDING',  -- PENDING | SENT | FAILED
    external_id     VARCHAR(128),               -- Twilio SID or SendGrid X-Message-Id
    error_message   TEXT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notification_logs_order_id ON notification_logs (order_id);
CREATE INDEX IF NOT EXISTS idx_notification_logs_status   ON notification_logs (status);
