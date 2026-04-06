"""add REFUNDED to payment_status_enum

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-04-06

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE payment_status_enum ADD VALUE IF NOT EXISTS 'REFUNDED'")


def downgrade():
    # Postgres does not support DROP VALUE on an enum.
    # Recreate the type without REFUNDED and migrate any REFUNDED rows back to SUCCESS.
    op.execute("UPDATE payments SET status = 'SUCCESS' WHERE status = 'REFUNDED'")
    op.execute("ALTER TABLE payments ALTER COLUMN status TYPE TEXT")
    op.execute("DROP TYPE payment_status_enum")
    op.execute(
        "CREATE TYPE payment_status_enum AS ENUM ('PENDING', 'SUCCESS', 'FAILED', 'CANCELLED')"
    )
    op.execute(
        "ALTER TABLE payments ALTER COLUMN status TYPE payment_status_enum "
        "USING status::payment_status_enum"
    )
