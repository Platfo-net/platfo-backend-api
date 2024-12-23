"""0017_total_amount_order

Revision ID: 0f0487d64919
Revises: 235590fd9073
Create Date: 2024-03-21 19:34:55.981364

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f0487d64919'
down_revision = '235590fd9073'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shop_orders', sa.Column('currency', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shop_orders', 'currency')
    # ### end Alembic commands ###
