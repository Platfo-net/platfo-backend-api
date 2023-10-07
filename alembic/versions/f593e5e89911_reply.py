"""reply

Revision ID: f593e5e89911
Revises: 23432815e837
Create Date: 2023-10-07 19:43:11.407261

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f593e5e89911'
down_revision = '23432815e837'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('social_telegram_lead_messages', sa.Column('reply_to_id', sa.BigInteger(), nullable=True))
    op.create_index(op.f('ix_social_telegram_lead_messages_reply_to_id'), 'social_telegram_lead_messages', ['reply_to_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_social_telegram_lead_messages_reply_to_id'), table_name='social_telegram_lead_messages')
    op.drop_column('social_telegram_lead_messages', 'reply_to_id')
    # ### end Alembic commands ###
