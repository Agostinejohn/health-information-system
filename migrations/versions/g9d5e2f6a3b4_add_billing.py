"""iteration 9 billing subscriptions

Revision ID: g9d5e2f6a3b4
Revises: f8c4d1e5a2b3a
"""
from alembic import op
import sqlalchemy as sa

revision = 'g9d5e2f6a3b4'
down_revision = 'f8c4d1e5a2b3a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('subscription_plans',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('monthly_price', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('max_users', sa.Integer(), nullable=True),
        sa.Column('max_clients', sa.Integer(), nullable=True),
        sa.Column('entitlements', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('code'))

    op.create_table('organization_subscriptions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('plan_id', sa.String(36), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='trialing'),
        sa.Column('billing_provider', sa.String(50), nullable=True),
        sa.Column('provider_customer_id', sa.String(255), nullable=True),
        sa.Column('provider_subscription_id', sa.String(255), nullable=True),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('trial_end', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('suspended_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id']),
        sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('organization_id'))
    op.create_index('ix_organization_subscriptions_organization_id', 'organization_subscriptions', ['organization_id'])

    op.create_table('invoices',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('subscription_id', sa.String(36), nullable=False),
        sa.Column('provider_invoice_id', sa.String(255), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('issued_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('due_at', sa.DateTime(), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['organization_subscriptions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('provider_invoice_id'))
    op.create_index('ix_invoices_organization_id', 'invoices', ['organization_id'])

    op.create_table('usage_records',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('metric', sa.String(50), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_usage_records_organization_id', 'usage_records', ['organization_id'])
    op.create_index('ix_usage_records_metric', 'usage_records', ['metric'])

    op.create_table('billing_events',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('subscription_id', sa.String(36), nullable=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('details', sa.JSON(), nullable=False),
        sa.Column('actor_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['organization_subscriptions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_billing_events_organization_id', 'billing_events', ['organization_id'])
    op.create_index('ix_billing_events_event_type', 'billing_events', ['event_type'])


def downgrade():
    op.drop_table('billing_events')
    op.drop_table('usage_records')
    op.drop_table('invoices')
    op.drop_table('organization_subscriptions')
    op.drop_table('subscription_plans')
