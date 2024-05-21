"""0023_order_item_variant_id_remove

Revision ID: e1bac47b20e1
Revises: a7210acf706b
Create Date: 2024-05-21 12:26:08.931157

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1bac47b20e1'
down_revision = 'a7210acf706b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('shop_order_items_variant_id_fkey', 'shop_order_items', type_='foreignkey')
    op.drop_column('shop_order_items', 'variant_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shop_order_items', sa.Column('variant_id', sa.BIGINT(), autoincrement=False, nullable=True))
    op.create_foreign_key('shop_order_items_variant_id_fkey', 'shop_order_items', 'shop_product_variants', ['variant_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###
