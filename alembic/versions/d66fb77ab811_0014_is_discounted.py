"""0014_is_discounted

Revision ID: d66fb77ab811
Revises: 9fcafa2ccff1
Create Date: 2023-10-29 07:12:03.619718

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd66fb77ab811'
down_revision = '9fcafa2ccff1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('credit_plans', 'is_discounted')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('credit_plans', sa.Column('is_discounted', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
    # ### end Alembic commands ###