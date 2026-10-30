"""iteration 5 appointments follow-ups referrals

Revision ID: c5f1a8b2d4e7
Revises: b4e9d2f3a7c1
"""
from alembic import op
import sqlalchemy as sa

revision = 'c5f1a8b2d4e7'
down_revision = 'b4e9d2f3a7c1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('appointments',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('client_id', sa.String(36), nullable=False),
        sa.Column('program_id', sa.String(36), nullable=True),
        sa.Column('assigned_to', sa.String(36), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='UTC'),
        sa.Column('reason', sa.String(255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='scheduled'),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_appointments_organization_id', 'appointments', ['organization_id'])
    op.create_index('ix_appointments_client_id', 'appointments', ['client_id'])
    op.create_index('ix_appointments_program_id', 'appointments', ['program_id'])
    op.create_index('ix_appointments_assigned_to', 'appointments', ['assigned_to'])
    op.create_index('ix_appointments_status', 'appointments', ['status'])

    op.create_table('follow_ups',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('client_id', sa.String(36), nullable=False),
        sa.Column('program_id', sa.String(36), nullable=True),
        sa.Column('assigned_to', sa.String(36), nullable=True),
        sa.Column('due_at', sa.DateTime(), nullable=False),
        sa.Column('priority', sa.String(20), nullable=False, server_default='normal'),
        sa.Column('title', sa.String(150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_follow_ups_organization_id', 'follow_ups', ['organization_id'])
    op.create_index('ix_follow_ups_client_id', 'follow_ups', ['client_id'])
    op.create_index('ix_follow_ups_program_id', 'follow_ups', ['program_id'])
    op.create_index('ix_follow_ups_assigned_to', 'follow_ups', ['assigned_to'])
    op.create_index('ix_follow_ups_priority', 'follow_ups', ['priority'])
    op.create_index('ix_follow_ups_status', 'follow_ups', ['status'])

    op.create_table('referrals',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('client_id', sa.String(36), nullable=False),
        sa.Column('program_id', sa.String(36), nullable=True),
        sa.Column('destination', sa.String(255), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(20), nullable=False, server_default='normal'),
        sa.Column('status', sa.String(20), nullable=False, server_default='referred'),
        sa.Column('referred_by', sa.String(36), nullable=True),
        sa.Column('referred_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('outcome', sa.Text(), nullable=True),
        sa.Column('outcome_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['referred_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_referrals_organization_id', 'referrals', ['organization_id'])
    op.create_index('ix_referrals_client_id', 'referrals', ['client_id'])
    op.create_index('ix_referrals_program_id', 'referrals', ['program_id'])
    op.create_index('ix_referrals_status', 'referrals', ['status'])


def downgrade():
    op.drop_table('referrals')
    op.drop_table('follow_ups')
    op.drop_table('appointments')
