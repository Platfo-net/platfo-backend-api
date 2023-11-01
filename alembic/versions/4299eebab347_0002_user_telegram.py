"""0002_user_telegram

Revision ID: 4299eebab347
Revises: dde3b6e472c2
Create Date: 2023-11-01 19:41:48.973816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4299eebab347'
down_revision = 'dde3b6e472c2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('telegram_admin_bot_chat_id', sa.BigInteger(), nullable=True))
    op.create_index(op.f('ix_users_telegram_admin_bot_chat_id'), 'users', ['telegram_admin_bot_chat_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_telegram_admin_bot_chat_id'), table_name='users')
    op.drop_column('users', 'telegram_admin_bot_chat_id')
    # ### end Alembic commands ###
