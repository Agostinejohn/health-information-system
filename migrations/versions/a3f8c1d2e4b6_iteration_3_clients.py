"""iteration 3 client records

Revision ID: a3f8c1d2e4b6
Revises: 9c2d4a1b6e8f
"""
from alembic import op
import sqlalchemy as sa

revision = 'a3f8c1d2e4b6'
down_revision = '9c2d4a1b6e8f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('clients') as batch_op:
        batch_op.add_column(sa.Column('external_reference', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('email', sa.String(120), nullable=True))
        batch_op.add_column(sa.Column('phone', sa.String(30), nullable=True))
        batch_op.add_column(sa.Column('address', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(20), nullable=False, server_default='active'))
        batch_op.create_index('ix_clients_external_reference', ['external_reference'])
        batch_op.create_index('ix_clients_email', ['email'])
        batch_op.create_index('ix_clients_phone', ['phone'])

    op.create_table('client_consents',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('client_id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('consent_type', sa.String(100), nullable=False),
        sa.Column('granted', sa.Boolean(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('recorded_by', sa.String(36), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recorded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_client_consents_client_id', 'client_consents', ['client_id'])
    op.create_index('ix_client_consents_organization_id', 'client_consents', ['organization_id'])

    op.create_table('client_documents',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('client_id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('title', sa.String(150), nullable=False),
        sa.Column('category', sa.String(80), nullable=False, server_default='general'),
        sa.Column('storage_key', sa.String(500), nullable=False),
        sa.Column('content_type', sa.String(100), nullable=True),
        sa.Column('uploaded_by', sa.String(36), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_client_documents_client_id', 'client_documents', ['client_id'])
    op.create_index('ix_client_documents_organization_id', 'client_documents', ['organization_id'])

    op.create_table('client_timeline_events',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('client_id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('event_type', sa.String(80), nullable=False),
        sa.Column('title', sa.String(150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('actor_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_client_timeline_events_client_id', 'client_timeline_events', ['client_id'])
    op.create_index('ix_client_timeline_events_organization_id', 'client_timeline_events', ['organization_id'])
    op.create_index('ix_client_timeline_events_event_type', 'client_timeline_events', ['event_type'])


def downgrade():
    op.drop_table('client_timeline_events')
    op.drop_table('client_documents')
    op.drop_table('client_consents')
    with op.batch_alter_table('clients') as batch_op:
        batch_op.drop_index('ix_clients_phone')
        batch_op.drop_index('ix_clients_email')
        batch_op.drop_index('ix_clients_external_reference')
        batch_op.drop_column('status')
        batch_op.drop_column('address')
        batch_op.drop_column('phone')
        batch_op.drop_column('email')
        batch_op.drop_column('external_reference')
