CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(36) UNIQUE NOT NULL,

    -- Student contact info (needed by Notification Service)
    student_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,

    -- Package & selected items
    -- package_id: which graduation package was selected
    -- selected_items: JSON array of {modelId, qty} — flexible for hat, hood, gown, etc.
    -- model_id encodes both STYLE and SIZE (e.g., "0100020" = M Blue Gown)
    package_id INT NOT NULL,
    selected_items JSONB NOT NULL,

    -- Rental period
    rental_start_date DATE NOT NULL,        -- fulfillment date (pickup/delivery)
    rental_end_date DATE NOT NULL,          -- return date

    -- Pricing
    total_amount DECIMAL(10, 2) NOT NULL,
    deposit DECIMAL(10, 2) NOT NULL DEFAULT 0.00,          -- Total deposit amount from all items

    -- Fulfillment method
    fulfillment_method VARCHAR(50) NOT NULL,    -- 'COLLECTION' | 'DELIVERY'

    -- Order lifecycle
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    -- Status flow: PENDING → CONFIRMED → ACTIVE → RETURNED_DAMAGED → COMPLETED
    -- PENDING: order created, awaiting successful payment
    -- CONFIRMED: payment processed and inventory reserved
    -- ACTIVE: handover completed and items are rented out
    -- RETURNED_DAMAGED: damaged return in repair / wash workflow
    -- COMPLETED: return workflow finalized and stock restored

    -- Status transition timestamps
    confirmed_at TIMESTAMP,
    activated_at TIMESTAMP,
    returned_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Optional: from saga context
    hold_id VARCHAR(255),
    payment_id VARCHAR(255),

    -- Damage tracking
    damaged BOOLEAN DEFAULT FALSE,
    damaged_items JSONB DEFAULT '[]'
);

CREATE INDEX idx_orders_order_id ON orders(order_id);
CREATE INDEX idx_orders_student_email ON orders(email);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_rental_start_date ON orders(rental_start_date);

-- Migration tracking table (also maintained by migrate.py at runtime).
-- Pre-seeding it here marks all migrations that are already reflected in this
-- init script as applied, so migrate.py skips them on a fresh deployment.
CREATE TABLE IF NOT EXISTS schema_migrations (
    filename   TEXT        PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO schema_migrations (filename) VALUES
    ('20260322_add_damaged_column.sql'),
    ('20260322_add_deposit_and_delivery_fee.sql'),
    ('20260407_drop_phone_column.sql'),
    ('20260407_change_order_id_to_uuid.sql')
ON CONFLICT DO NOTHING;