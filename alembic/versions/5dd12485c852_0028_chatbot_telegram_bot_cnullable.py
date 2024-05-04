"""0028_chatbot_telegram_bot_cnullable

Revision ID: 5dd12485c852
Revises: 3c562e41a1c5
Create Date: 2024-05-03 15:21:34.305151

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5dd12485c852'
down_revision = '3c562e41a1c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('chatbot_telegram_bots', 'chatbot_id',
               existing_type=sa.BIGINT(),
               nullable=False)
    op.alter_column('chatbot_telegram_bots', 'telegram_bot_id',
               existing_type=sa.BIGINT(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('chatbot_telegram_bots', 'telegram_bot_id',
               existing_type=sa.BIGINT(),
               nullable=True)
    op.alter_column('chatbot_telegram_bots', 'chatbot_id',
               existing_type=sa.BIGINT(),
               nullable=True)
    # ### end Alembic commands ###