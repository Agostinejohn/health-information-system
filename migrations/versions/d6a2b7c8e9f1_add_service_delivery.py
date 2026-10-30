"""iteration 6 service delivery

Revision ID: d6a2b7c8e9f1
Revises: c5f1a8b2d4e7
"""
from alembic import op
import sqlalchemy as sa

revision = 'd6a2b7c8e9f1'
down_revision = 'c5f1a8b2d4e7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('assessment_templates',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('program_id', sa.String(36), nullable=True),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_assessment_templates_organization_id', 'assessment_templates', ['organization_id'])

    op.create_table('assessment_template_versions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('template_id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('definition', sa.JSON(), nullable=False),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['template_id'], ['assessment_templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('template_id', 'version_number', name='uq_template_version'))
    op.create_index('ix_assessment_template_versions_template_id', 'assessment_template_versions', ['template_id'])

    op.create_table('service_deliveries',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('client_id', sa.String(36), nullable=False),
        sa.Column('program_id', sa.String(36), nullable=True),
        sa.Column('appointment_id', sa.String(36), nullable=True),
        sa.Column('template_version_id', sa.String(36), nullable=True),
        sa.Column('service_type', sa.String(100), nullable=False),
        sa.Column('outcome', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('answers', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='recorded'),
        sa.Column('provided_by', sa.String(36), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('corrected_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['template_version_id'], ['assessment_template_versions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['provided_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_service_deliveries_organization_id', 'service_deliveries', ['organization_id'])
    op.create_index('ix_service_deliveries_client_id', 'service_deliveries', ['client_id'])

    op.create_table('service_delivery_corrections',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('service_delivery_id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('corrected_by', sa.String(36), nullable=True),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('previous_answers', sa.JSON(), nullable=False),
        sa.Column('previous_notes', sa.Text(), nullable=True),
        sa.Column('corrected_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['service_delivery_id'], ['service_deliveries.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['corrected_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_service_delivery_corrections_service_delivery_id', 'service_delivery_corrections', ['service_delivery_id'])


def downgrade():
    op.drop_table('service_delivery_corrections')
    op.drop_table('service_deliveries')
    op.drop_table('assessment_template_versions')
    op.drop_table('assessment_templates')
