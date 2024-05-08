"""0027_chatbot_telegram_bot

Revision ID: 4db5244a69e5
Revises: e610dde7d7fe
Create Date: 2024-05-05 12:02:33.077147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4db5244a69e5'
down_revision = 'e610dde7d7fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chatbot_telegram_bots', sa.Column('chatbot_id', sa.BigInteger(), nullable=False))
    op.add_column('chatbot_telegram_bots', sa.Column('telegram_bot_id', sa.BigInteger(), nullable=False))
    op.create_foreign_key(None, 'chatbot_telegram_bots', 'telegram_bots', ['telegram_bot_id'], ['id'])
    op.create_foreign_key(None, 'chatbot_telegram_bots', 'chatbots', ['chatbot_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'chatbot_telegram_bots', type_='foreignkey')
    op.drop_constraint(None, 'chatbot_telegram_bots', type_='foreignkey')
    op.drop_column('chatbot_telegram_bots', 'telegram_bot_id')
    op.drop_column('chatbot_telegram_bots', 'chatbot_id')
    # ### end Alembic commands ###