"""0027_chatbot_telegram_bot_cascade

Revision ID: 3c562e41a1c5
Revises: e610dde7d7fe
Create Date: 2024-05-03 15:11:31.732688

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c562e41a1c5'
down_revision = 'e610dde7d7fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('chatbot_telegram_bots_chatbot_id_fkey', 'chatbot_telegram_bots', type_='foreignkey')
    op.drop_constraint('chatbot_telegram_bots_telegram_bot_id_fkey', 'chatbot_telegram_bots', type_='foreignkey')
    op.create_foreign_key(None, 'chatbot_telegram_bots', 'telegram_bots', ['telegram_bot_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'chatbot_telegram_bots', 'chatbots', ['chatbot_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'chatbot_telegram_bots', type_='foreignkey')
    op.drop_constraint(None, 'chatbot_telegram_bots', type_='foreignkey')
    op.create_foreign_key('chatbot_telegram_bots_telegram_bot_id_fkey', 'chatbot_telegram_bots', 'telegram_bots', ['telegram_bot_id'], ['id'])
    op.create_foreign_key('chatbot_telegram_bots_chatbot_id_fkey', 'chatbot_telegram_bots', 'chatbots', ['chatbot_id'], ['id'])
    # ### end Alembic commands ###
