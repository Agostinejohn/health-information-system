"""add request hash to idempotency records

Revision ID: f8c4d1e5a2b3a
Revises: f8c4d1e5a2b3
"""
from alembic import op
import sqlalchemy as sa

revision = 'f8c4d1e5a2b3a'
down_revision = 'f8c4d1e5a2b3'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('idempotency_records') as batch_op:
        batch_op.add_column(sa.Column('request_hash', sa.String(64), nullable=True))
    op.execute("UPDATE idempotency_records SET request_hash = '' WHERE request_hash IS NULL")
    with op.batch_alter_table('idempotency_records') as batch_op:
        batch_op.alter_column('request_hash', existing_type=sa.String(64), nullable=False)


def downgrade():
    with op.batch_alter_table('idempotency_records') as batch_op:
        batch_op.drop_column('request_hash')
