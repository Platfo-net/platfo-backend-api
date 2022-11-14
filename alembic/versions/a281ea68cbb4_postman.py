"""postman

Revision ID: a281ea68cbb4
Revises: 83d96d9e30e0
Create Date: 2022-11-14 12:22:12.986946

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a281ea68cbb4'
down_revision = '83d96d9e30e0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('live_chat_chatrooms',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('room_name', sa.String(length=255), nullable=True),
    sa.Column('chat_members', postgresql.ARRAY(sa.JSON()), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('postman_campaigns',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('group_name', sa.String(length=255), nullable=True),
    sa.Column('is_draft', sa.Boolean(), nullable=True),
    sa.Column('facebook_page_id', sa.String(length=100), nullable=True),
    sa.Column('status', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('content', sa.JSON(), nullable=True),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('postman_groups',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('facebook_page_id', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('postman_campaign_contacts',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('contact_igs_id', sa.String(length=100), nullable=True),
    sa.Column('is_sent', sa.Boolean(), nullable=True),
    sa.Column('is_seen', sa.Boolean(), nullable=True),
    sa.Column('mid', sa.String(length=255), nullable=True),
    sa.Column('reaction', sa.String(length=100), nullable=True),
    sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['postman_campaigns.id'], ),
    sa.ForeignKeyConstraint(['contact_id'], ['live_chat_contacts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('postman_group_contacts',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('contact_igs_id', sa.String(length=100), nullable=True),
    sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['contact_id'], ['live_chat_contacts.id'], ),
    sa.ForeignKeyConstraint(['group_id'], ['postman_groups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('academy_labels', sa.Column('name', sa.String(length=255), nullable=True))
    op.drop_column('academy_labels', 'label_name')
    op.add_column('instagram_pages', sa.Column('username', sa.String(length=255), nullable=True))
    op.add_column('instagram_pages', sa.Column('profile_picture_url', sa.String(length=1024), nullable=True))
    op.drop_column('instagram_pages', 'instagram_profile_picture_url')
    op.drop_column('instagram_pages', 'instagram_username')
    op.add_column('live_chat_contacts', sa.Column('message_count', sa.Integer(), nullable=True))
    op.add_column('live_chat_contacts', sa.Column('comment_count', sa.Integer(), nullable=True))
    op.add_column('live_chat_contacts', sa.Column('live_comment_count', sa.Integer(), nullable=True))
    op.add_column('live_chat_contacts', sa.Column('first_impression', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    op.drop_column('live_chat_contacts', 'first_impression')
    op.drop_column('live_chat_contacts', 'live_comment_count')
    op.drop_column('live_chat_contacts', 'comment_count')
    op.drop_column('live_chat_contacts', 'message_count')
    op.add_column('instagram_pages', sa.Column('instagram_username', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('instagram_pages', sa.Column('instagram_profile_picture_url', sa.VARCHAR(length=1024), autoincrement=False, nullable=True))
    op.drop_column('instagram_pages', 'profile_picture_url')
    op.drop_column('instagram_pages', 'username')
    op.add_column('academy_labels', sa.Column('label_name', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.drop_column('academy_labels', 'name')
    op.drop_table('postman_group_contacts')
    op.drop_table('postman_campaign_contacts')
    op.drop_table('postman_groups')
    op.drop_table('postman_campaigns')
    op.drop_table('live_chat_chatrooms')
