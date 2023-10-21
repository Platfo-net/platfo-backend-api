"""0009_payment

Revision ID: 7a490ebb8538
Revises: bcb991e88719
Create Date: 2023-10-20 07:50:48.736054

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7a490ebb8538'
down_revision = 'bcb991e88719'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shop_shop_payment_methods',
    sa.Column('shop_id', sa.BigInteger(), nullable=True),
    sa.Column('payment_method_id', sa.BigInteger(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['payment_method_id'], ['shop_payment_methods.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['shop_id'], ['shop_shops.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shop_shop_payment_methods_id'), 'shop_shop_payment_methods', ['id'], unique=False)
    op.drop_column('shop_orders', 'payment_receipt_image')
    op.drop_column('shop_orders', 'payment_card_last_four_number')
    op.drop_column('shop_orders', 'payment_reference_number')
    op.drop_column('shop_orders', 'payment_datetime')
    op.add_column('shop_payment_methods', sa.Column('information_fields', sa.JSON(), nullable=True))
    op.add_column('shop_payment_methods', sa.Column('payment_fields', sa.JSON(), nullable=True))
    op.drop_constraint('shop_payment_methods_shop_id_fkey', 'shop_payment_methods', type_='foreignkey')
    op.drop_column('shop_payment_methods', 'is_active')
    op.drop_column('shop_payment_methods', 'shop_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shop_payment_methods', sa.Column('shop_id', sa.BIGINT(), autoincrement=False, nullable=True))
    op.add_column('shop_payment_methods', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.create_foreign_key('shop_payment_methods_shop_id_fkey', 'shop_payment_methods', 'shop_shops', ['shop_id'], ['id'])
    op.drop_column('shop_payment_methods', 'payment_fields')
    op.drop_column('shop_payment_methods', 'information_fields')
    op.add_column('shop_orders', sa.Column('payment_datetime', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('shop_orders', sa.Column('payment_reference_number', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('shop_orders', sa.Column('payment_card_last_four_number', sa.VARCHAR(length=16), autoincrement=False, nullable=True))
    op.add_column('shop_orders', sa.Column('payment_receipt_image', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_shop_shop_payment_methods_id'), table_name='shop_shop_payment_methods')
    op.drop_table('shop_shop_payment_methods')
    # ### end Alembic commands ###
