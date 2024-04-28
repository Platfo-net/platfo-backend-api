"""0023_embedding_cost

Revision ID: ac973dc6c7ef
Revises: b08fc6200530
Create Date: 2024-04-22 21:57:59.459069

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac973dc6c7ef'
down_revision = 'b08fc6200530'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('embedding_costs',
    sa.Column('cost_usd', sa.Float(), nullable=True),
    sa.Column('total_tokens', sa.BigInteger(), nullable=True),
    sa.Column('knowledgebase_id', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['knowledgebase_id'], ['knowledgebase.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_embedding_costs_id'), 'embedding_costs', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_embedding_costs_id'), table_name='embedding_costs')
    op.drop_table('embedding_costs')
    # ### end Alembic commands ###