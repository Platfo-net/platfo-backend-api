"""Connection

Revision ID: fe4da0823905
Revises: 0435032113a7
Create Date: 2022-07-27 13:29:50.785138

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fe4da0823905'
down_revision = '0435032113a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('triggers',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('persian_name', sa.String(length=255), nullable=True),
    sa.Column('platform', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('connections',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('application_name', sa.String(length=255), nullable=True),
    sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('account_id', 'application_name')
    )
    op.create_table('connection_chatflows',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('trigger_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('chatflow_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['connection_id'], ['connections.id'], ),
    sa.ForeignKeyConstraint(['trigger_id'], ['triggers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('instagram_pages', sa.Column('instagram_username', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('instagram_pages', 'instagram_username')
    op.drop_table('connection_chatflows')
    op.drop_table('connections')
    op.drop_table('triggers')
    # ### end Alembic commands ###
