"""0004_credit

Revision ID: 40a207bc26e2
Revises: 47008826c604
Create Date: 2023-09-30 16:56:29.347019

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '40a207bc26e2'
down_revision = '47008826c604'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('credit_shop_credits',
    sa.Column('shop_id', sa.BigInteger(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['shop_id'], ['shop_shops.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_credit_shop_credits_id'), 'credit_shop_credits', ['id'], unique=False)
    op.create_index(op.f('ix_credit_shop_credits_shop_id'), 'credit_shop_credits', ['shop_id'], unique=True)
    op.drop_index('ix_credit_credit_logs_id', table_name='credit_credit_logs')
    op.drop_table('credit_credit_logs')
    op.drop_index('ix_credit_credits_id', table_name='credit_credits')
    op.drop_index('ix_credit_credits_user_id', table_name='credit_credits')
    op.drop_table('credit_credits')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('credit_credits',
    sa.Column('module', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('expires_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('uuid', sa.UUID(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='credit_credits_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='credit_credits_pkey')
    )
    op.create_index('ix_credit_credits_user_id', 'credit_credits', ['user_id'], unique=False)
    op.create_index('ix_credit_credits_id', 'credit_credits', ['id'], unique=False)
    op.create_table('credit_credit_logs',
    sa.Column('module', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('days_added', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('plan_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('invoice_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('uuid', sa.UUID(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['invoice_id'], ['credit_invoices.id'], name='credit_credit_logs_invoice_id_fkey'),
    sa.ForeignKeyConstraint(['plan_id'], ['credit_plans.id'], name='credit_credit_logs_plan_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='credit_credit_logs_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='credit_credit_logs_pkey')
    )
    op.create_index('ix_credit_credit_logs_id', 'credit_credit_logs', ['id'], unique=False)
    op.drop_index(op.f('ix_credit_shop_credits_shop_id'), table_name='credit_shop_credits')
    op.drop_index(op.f('ix_credit_shop_credits_id'), table_name='credit_shop_credits')
    op.drop_table('credit_shop_credits')
    # ### end Alembic commands ###