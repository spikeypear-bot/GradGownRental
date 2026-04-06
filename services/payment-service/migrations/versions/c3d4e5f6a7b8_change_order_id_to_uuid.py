"""ensure order_id is VARCHAR(36) in payments table

Revision ID: c3d4e5f6a7b8
Revises: a1b2c3d4e5f6
Create Date: 2026-04-07

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # If order_id was previously migrated to UUID, convert it back to VARCHAR(36).
    # On fresh deployments the column is already VARCHAR(36) so this is a no-op.
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'payments'
                  AND column_name = 'order_id'
                  AND data_type = 'uuid'
            ) THEN
                DROP INDEX IF EXISTS ix_payments_order_id;
                ALTER TABLE payments DROP CONSTRAINT IF EXISTS payments_order_id_key;
                ALTER TABLE payments DROP CONSTRAINT IF EXISTS uq_payments_order_id;
                ALTER TABLE payments
                    ALTER COLUMN order_id TYPE VARCHAR(36) USING order_id::TEXT;
                CREATE UNIQUE INDEX ix_payments_order_id ON payments (order_id);
            END IF;
        END$$;
    """)


def downgrade():
    pass
