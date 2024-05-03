"""0027_chatbot_telegram_bot_cascade

Revision ID: 36fe8849a271
Revises: e610dde7d7fe
Create Date: 2024-05-03 15:00:49.654895

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36fe8849a271'
down_revision = 'e610dde7d7fe'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('chatbot_telegram_bots', 'chatbot_id',
                    sa.ForeignKey('chatbots.id', ondelete='CASCADE'))
    op.alter_column('chatbot_telegram_bots', 'telegram_bot_id',
                    sa.ForeignKey('telegram_bots.id', ondelete='CASCADE'))


def downgrade():
    op.alter_column('chatbot_telegram_bots', 'chatbot_id',
                    sa.ForeignKey('chatbots.id'))
    op.alter_column('chatbot_telegram_bots', 'telegram_bot_id',
                    sa.ForeignKey('telegram_bots.id'))
