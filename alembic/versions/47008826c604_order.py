"""order

Revision ID: 47008826c604
Revises: 3279eb357e14
Create Date: 2023-09-21 19:03:48.431187

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '47008826c604'
down_revision = '3279eb357e14'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shop_payment_methods',
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('shop_id', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['shop_id'], ['shop_shops.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shop_payment_methods_id'), 'shop_payment_methods', ['id'], unique=False)
    op.create_table('shop_shipment_methods',
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('price', sa.String(length=255), nullable=True),
    sa.Column('currency', sa.String(length=255), nullable=True),
    sa.Column('shop_id', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['shop_id'], ['shop_shops.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shop_shipment_methods_id'), 'shop_shipment_methods', ['id'], unique=False)
    op.drop_constraint('shop_categories_user_id_fkey', 'shop_categories', type_='foreignkey')
    op.drop_column('shop_categories', 'user_id')
    op.add_column('shop_order_items', sa.Column('count', sa.Integer(), nullable=True))
    op.add_column('shop_order_items', sa.Column('price', sa.Float(), nullable=True))
    op.add_column('shop_order_items', sa.Column('currency', sa.String(length=32), nullable=True))
    op.add_column('shop_orders', sa.Column('payment_reference_number', sa.String(length=255), nullable=True))
    op.add_column('shop_orders', sa.Column('payment_card_last_four_number', sa.String(length=16), nullable=True))
    op.add_column('shop_orders', sa.Column('payment_datetime', sa.DateTime(), nullable=True))
    op.add_column('shop_orders', sa.Column('payment_receipt_image', sa.String(length=255), nullable=True))
    op.add_column('shop_orders', sa.Column('shipment_method_id', sa.BigInteger(), nullable=True))
    op.add_column('shop_orders', sa.Column('payment_method_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key(None, 'shop_orders', 'shop_shipment_methods', ['shipment_method_id'], ['id'])
    op.create_foreign_key(None, 'shop_orders', 'shop_payment_methods', ['payment_method_id'], ['id'])
    op.drop_constraint('shop_products_user_id_fkey', 'shop_products', type_='foreignkey')
    op.drop_column('shop_products', 'user_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shop_products', sa.Column('user_id', sa.BIGINT(), autoincrement=False, nullable=True))
    op.create_foreign_key('shop_products_user_id_fkey', 'shop_products', 'users', ['user_id'], ['id'])
    op.drop_constraint(None, 'shop_orders', type_='foreignkey')
    op.drop_constraint(None, 'shop_orders', type_='foreignkey')
    op.drop_column('shop_orders', 'payment_method_id')
    op.drop_column('shop_orders', 'shipment_method_id')
    op.drop_column('shop_orders', 'payment_receipt_image')
    op.drop_column('shop_orders', 'payment_datetime')
    op.drop_column('shop_orders', 'payment_card_last_four_number')
    op.drop_column('shop_orders', 'payment_reference_number')
    op.drop_column('shop_order_items', 'currency')
    op.drop_column('shop_order_items', 'price')
    op.drop_column('shop_order_items', 'count')
    op.add_column('shop_categories', sa.Column('user_id', sa.BIGINT(), autoincrement=False, nullable=True))
    op.create_foreign_key('shop_categories_user_id_fkey', 'shop_categories', 'users', ['user_id'], ['id'])
    op.drop_index(op.f('ix_shop_shipment_methods_id'), table_name='shop_shipment_methods')
    op.drop_table('shop_shipment_methods')
    op.drop_index(op.f('ix_shop_payment_methods_id'), table_name='shop_payment_methods')
    op.drop_table('shop_payment_methods')
    # ### end Alembic commands ###
