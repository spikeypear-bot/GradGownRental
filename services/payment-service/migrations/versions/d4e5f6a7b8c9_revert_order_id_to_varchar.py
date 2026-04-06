"""revert order_id to VARCHAR(36) in payments table

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-04-07

"""
from alembic import op

revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP INDEX IF EXISTS ix_payments_order_id")
    op.execute("ALTER TABLE payments DROP CONSTRAINT IF EXISTS payments_order_id_key")
    op.execute("ALTER TABLE payments DROP CONSTRAINT IF EXISTS uq_payments_order_id")
    op.execute(
        "ALTER TABLE payments "
        "ALTER COLUMN order_id TYPE VARCHAR(36) USING order_id::TEXT"
    )
    op.execute("CREATE UNIQUE INDEX ix_payments_order_id ON payments (order_id)")


def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_payments_order_id")
    op.execute("ALTER TABLE payments DROP CONSTRAINT IF EXISTS payments_order_id_key")
    op.execute("ALTER TABLE payments DROP CONSTRAINT IF EXISTS uq_payments_order_id")
    op.execute(
        "ALTER TABLE payments "
        "ALTER COLUMN order_id TYPE UUID USING order_id::UUID"
    )
    op.execute("CREATE UNIQUE INDEX ix_payments_order_id ON payments (order_id)")
