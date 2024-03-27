"""0018_currency_dashboard

Revision ID: 68dfcb63db3b
Revises: 0f0487d64919
Create Date: 2024-03-23 10:17:00.770882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68dfcb63db3b'
down_revision = '0f0487d64919'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shop_daily_reports', sa.Column('currency', sa.String(length=16), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shop_daily_reports', 'currency')
    # ### end Alembic commands ###