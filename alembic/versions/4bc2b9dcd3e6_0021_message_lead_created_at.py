"""0021_message_lead_created_at

Revision ID: 4bc2b9dcd3e6
Revises: 61b9249d6773
Create Date: 2024-05-17 08:43:33.777130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4bc2b9dcd3e6'
down_revision = '61b9249d6773'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('social_telegram_lead_messages', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('social_telegram_leads', sa.Column('created_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('social_telegram_leads', 'created_at')
    op.drop_column('social_telegram_lead_messages', 'created_at')
    # ### end Alembic commands ###
