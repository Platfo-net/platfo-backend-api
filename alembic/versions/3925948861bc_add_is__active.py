"""add_is__active

Revision ID: 3925948861bc
Revises: 2c2aecd78c39
Create Date: 2022-10-25 07:50:55.387856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3925948861bc'
down_revision = '2c2aecd78c39'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('postman_campaigns', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.drop_column('postman_campaigns', 'contact_count')
    op.drop_column('postman_campaigns', 'sent_count')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('postman_campaigns', sa.Column('sent_count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('postman_campaigns', sa.Column('contact_count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('postman_campaigns', 'is_active')
    # ### end Alembic commands ###
