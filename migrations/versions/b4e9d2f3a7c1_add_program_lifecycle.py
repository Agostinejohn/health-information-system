"""iteration 4 program lifecycle

Revision ID: b4e9d2f3a7c1
Revises: a3f8c1d2e4b6
"""
from alembic import op
import sqlalchemy as sa

revision = 'b4e9d2f3a7c1'
down_revision = 'a3f8c1d2e4b6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('programs') as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(20), nullable=False, server_default='active'))
        batch_op.add_column(sa.Column('capacity', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('start_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('end_date', sa.Date(), nullable=True))

    op.create_table('program_enrollments',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('client_id', sa.String(36), nullable=False),
        sa.Column('program_id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('enrolled_by', sa.String(36), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('enrolled_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['enrolled_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('client_id', 'program_id', name='uq_client_program_enrollment'))
    op.create_index('ix_program_enrollments_client_id', 'program_enrollments', ['client_id'])
    op.create_index('ix_program_enrollments_program_id', 'program_enrollments', ['program_id'])
    op.create_index('ix_program_enrollments_organization_id', 'program_enrollments', ['organization_id'])


def downgrade():
    op.drop_table('program_enrollments')
    with op.batch_alter_table('programs') as batch_op:
        batch_op.drop_column('end_date')
        batch_op.drop_column('start_date')
        batch_op.drop_column('capacity')
        batch_op.drop_column('status')
        batch_op.drop_column('description')
