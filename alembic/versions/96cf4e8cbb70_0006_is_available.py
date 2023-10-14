"""0009_is_available

Revision ID: 96cf4e8cbb70
Revises: 23432815e837
Create Date: 2023-10-14 13:56:18.339497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96cf4e8cbb70'
down_revision = '23432815e837'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('social_telegram_lead_messages', sa.Column('reply_to_id', sa.BigInteger(), nullable=True))
    op.create_index(op.f('ix_social_telegram_lead_messages_reply_to_id'), 'social_telegram_lead_messages', ['reply_to_id'], unique=False)
    
    op.add_column('social_telegram_leads', sa.Column('lead_number', sa.BigInteger(), nullable=True))
    op.create_index(op.f('ix_social_telegram_leads_lead_number'), 'social_telegram_leads', ['lead_number'], unique=False)
  
    op.add_column('shop_categories', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('shop_order_items', sa.Column('product_title', sa.String(length=256), nullable=True))
    op.drop_constraint('shop_order_items_product_id_fkey', 'shop_order_items', type_='foreignkey')
    op.create_foreign_key(None, 'shop_order_items', 'shop_products', ['product_id'], ['id'], ondelete='SET NULL')
    op.add_column('shop_payment_methods', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('shop_products', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.drop_constraint('shop_products_shop_id_fkey', 'shop_products', type_='foreignkey')
    op.drop_constraint('shop_products_category_id_fkey', 'shop_products', type_='foreignkey')
    op.create_foreign_key(None, 'shop_products', 'shop_shops', ['shop_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'shop_products', 'shop_categories', ['category_id'], ['id'], ondelete='SET NULL')
    op.add_column('shop_shipment_methods', sa.Column('is_active', sa.Boolean(), nullable=True))
    
    op.add_column('shop_products', sa.Column('is_available', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    op.drop_column('shop_products', 'is_available')
    op.drop_column('shop_shipment_methods', 'is_active')
    op.drop_constraint(None, 'shop_products', type_='foreignkey')
    op.drop_constraint(None, 'shop_products', type_='foreignkey')
    op.create_foreign_key('shop_products_category_id_fkey', 'shop_products', 'shop_categories', ['category_id'], ['id'])
    op.create_foreign_key('shop_products_shop_id_fkey', 'shop_products', 'shop_shops', ['shop_id'], ['id'])
    op.drop_column('shop_products', 'is_active')
    op.drop_column('shop_payment_methods', 'is_active')
    op.drop_constraint(None, 'shop_order_items', type_='foreignkey')
    op.create_foreign_key('shop_order_items_product_id_fkey', 'shop_order_items', 'shop_products', ['product_id'], ['id'])
    op.drop_column('shop_order_items', 'product_title')
    op.drop_column('shop_categories', 'is_active')
    op.drop_index(op.f('ix_social_telegram_leads_lead_number'), table_name='social_telegram_leads')
    op.drop_column('social_telegram_leads', 'lead_number')
    
    op.drop_index(op.f('ix_social_telegram_lead_messages_reply_to_id'), table_name='social_telegram_lead_messages')
    op.drop_column('social_telegram_lead_messages', 'reply_to_id')
    
   
    # ### end Alembic commands ###
