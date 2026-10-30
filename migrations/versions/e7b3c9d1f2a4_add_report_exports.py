"""iteration 7 report exports

Revision ID: e7b3c9d1f2a4
Revises: d6a2b7c8e9f1
"""
from alembic import op
import sqlalchemy as sa

revision = 'e7b3c9d1f2a4'
down_revision = 'd6a2b7c8e9f1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('report_exports',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('requested_by', sa.String(36), nullable=True),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='ready'),
        sa.Column('filters', sa.JSON(), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=True),
        sa.Column('record_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('requested_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['requested_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_report_exports_organization_id', 'report_exports', ['organization_id'])
    op.create_index('ix_report_exports_requested_by', 'report_exports', ['requested_by'])


def downgrade():
    op.drop_table('report_exports')
