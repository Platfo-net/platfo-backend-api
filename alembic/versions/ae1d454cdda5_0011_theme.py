"""0011_theme

Revision ID: ae1d454cdda5
Revises: 6a2d8e3603ed
Create Date: 2024-02-17 10:29:29.972033

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae1d454cdda5'
down_revision = '6a2d8e3603ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shop_themes',
    sa.Column('color_code', sa.String(length=255), nullable=True),
    sa.Column('shop_id', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['shop_id'], ['shop_shops.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('shop_id')
    )
    op.create_index(op.f('ix_shop_themes_id'), 'shop_themes', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_shop_themes_id'), table_name='shop_themes')
    op.drop_table('shop_themes')
    # ### end Alembic commands ###
