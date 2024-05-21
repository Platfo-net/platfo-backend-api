"""0015_remove_academy_module

Revision ID: 0e50f60e6ab5
Revises: 501051f74878
Create Date: 2024-03-16 14:07:38.865426

"""
from alembic import op

revision = '0e50f60e6ab5'
down_revision = '501051f74878'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('academy_content_labels')
    op.drop_table('academy_labels')
    op.drop_table('academy_content_categories')
    op.drop_table('academy_contents')
    op.drop_table('academy_categories')


def downgrade():
    pass
