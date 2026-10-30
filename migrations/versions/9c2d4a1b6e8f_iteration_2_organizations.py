"""iteration 2 organizations and tenant ownership

Revision ID: 9c2d4a1b6e8f
Revises: f780ba1f0a0c
"""
from alembic import op
import sqlalchemy as sa

revision = '9c2d4a1b6e8f'
down_revision = 'f780ba1f0a0c'
branch_labels = None
depends_on = None


def _program_name_unique_constraint():
    connection = op.get_bind()
    constraints = sa.inspect(connection).get_unique_constraints('programs')
    for constraint in constraints:
        if constraint.get('column_names') == ['name']:
            return constraint.get('name')
    return None


def upgrade():
    op.create_table('organizations',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('slug', sa.String(120), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'))

    op.create_table('organization_memberships',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'user_id', name='uq_membership_organization_user'))

    op.create_table('organization_invitations',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('email', sa.String(120), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('token_hash', sa.String(64), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('invited_by', sa.String(36), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash'))

    old_name_constraint = _program_name_unique_constraint()
    with op.batch_alter_table('clients') as batch_op:
        batch_op.add_column(sa.Column('organization_id', sa.String(36), nullable=True))
        batch_op.create_index('ix_clients_organization_id', ['organization_id'])
        batch_op.create_foreign_key('fk_clients_organization_id', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('programs') as batch_op:
        batch_op.add_column(sa.Column('organization_id', sa.String(36), nullable=True))
        batch_op.create_index('ix_programs_organization_id', ['organization_id'])
        batch_op.create_foreign_key('fk_programs_organization_id', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')
        if old_name_constraint:
            batch_op.drop_constraint(old_name_constraint, type_='unique')
        batch_op.create_unique_constraint('uq_program_organization_name', ['organization_id', 'name'])


def downgrade():
    with op.batch_alter_table('programs') as batch_op:
        batch_op.drop_constraint('uq_program_organization_name', type_='unique')
        batch_op.create_unique_constraint('programs_name_key', ['name'])
        batch_op.drop_constraint('fk_programs_organization_id', type_='foreignkey')
        batch_op.drop_index('ix_programs_organization_id')
        batch_op.drop_column('organization_id')
    with op.batch_alter_table('clients') as batch_op:
        batch_op.drop_constraint('fk_clients_organization_id', type_='foreignkey')
        batch_op.drop_index('ix_clients_organization_id')
        batch_op.drop_column('organization_id')
    op.drop_table('organization_invitations')
    op.drop_table('organization_memberships')
    op.drop_table('organizations')
