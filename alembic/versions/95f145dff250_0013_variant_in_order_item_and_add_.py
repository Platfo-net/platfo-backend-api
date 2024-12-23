"""0013_variant_in_order_item_and_add_fields_to_order

Revision ID: 95f145dff250
Revises: c28de2156d76
Create Date: 2024-03-05 20:32:25.778470

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '95f145dff250'
down_revision = 'c28de2156d76'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shop_order_items', sa.Column('variant_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key(None, 'shop_order_items', 'shop_product_variants', ['variant_id'], ['id'], ondelete='SET NULL')
    op.add_column('shop_orders', sa.Column('shipment_cost_currency', sa.String(length=32), nullable=True))
    op.add_column('shop_orders', sa.Column('shipment_cost_amount', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shop_orders', 'shipment_cost_amount')
    op.drop_column('shop_orders', 'shipment_cost_currency')
    op.drop_constraint(None, 'shop_order_items', type_='foreignkey')
    op.drop_column('shop_order_items', 'variant_id')
    # ### end Alembic commands ###
