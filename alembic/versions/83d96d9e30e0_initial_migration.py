"""Initial Migration

Revision ID: 83d96d9e30e0
Revises: 
Create Date: 2022-10-02 11:51:11.447164

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '83d96d9e30e0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('academy_categories',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['academy_categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('academy_labels',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('label_name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notifications',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_visible', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('persian_name', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('phone_number', sa.String(length=13), nullable=True),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_table('academy_contents',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('title', sa.String(length=1024), nullable=True),
    sa.Column('caption', sa.Text(), nullable=True),
    sa.Column('blocks', postgresql.ARRAY(sa.JSON()), nullable=True),
    sa.Column('slug', sa.String(length=300), nullable=True),
    sa.Column('is_published', sa.Boolean(), nullable=True),
    sa.Column('cover_image', sa.String(length=1024), nullable=True),
    sa.Column('time', sa.String(length=200), nullable=True),
    sa.Column('version', sa.String(length=200), nullable=True),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bot_builder_chatflows',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('connections',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('application_name', sa.String(length=255), nullable=True),
    sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('details', sa.ARRAY(sa.JSON()), nullable=True),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('instagram_pages',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('facebook_user_long_lived_token', sa.String(length=255), nullable=True),
    sa.Column('facebook_user_id', sa.String(length=255), nullable=True),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('facebook_page_id', sa.String(length=255), nullable=True),
    sa.Column('instagram_page_id', sa.String(length=255), nullable=True),
    sa.Column('facebook_page_token', sa.String(length=255), nullable=True),
    sa.Column('instagram_username', sa.String(length=255), nullable=True),
    sa.Column('instagram_profile_picture_url', sa.String(length=1024), nullable=True),
    sa.Column('information', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('live_chat_contacts',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('contact_igs_id', sa.String(length=64), nullable=True),
    sa.Column('user_page_id', sa.String(length=64), nullable=True),
    sa.Column('last_message', sa.String(length=1024), nullable=True),
    sa.Column('last_message_at', sa.DateTime(), nullable=True),
    sa.Column('information', sa.JSON(), nullable=True),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('live_chat_messages',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('from_page_id', sa.String(length=64), nullable=True),
    sa.Column('to_page_id', sa.String(length=64), nullable=True),
    sa.Column('content', sa.JSON(), nullable=True),
    sa.Column('mid', sa.String(length=256), nullable=True),
    sa.Column('send_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notification_users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('notification_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('academy_content_categories',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['academy_categories.id'], ),
    sa.ForeignKeyConstraint(['content_id'], ['academy_contents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('academy_content_labels',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('label_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['content_id'], ['academy_contents.id'], ),
    sa.ForeignKeyConstraint(['label_id'], ['academy_labels.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bot_builder_edges',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('from_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('to_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('from_port', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('to_port', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('from_widget', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('text', sa.String(length=255), nullable=True),
    sa.Column('chatflow_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['chatflow_id'], ['bot_builder_chatflows.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bot_builder_nodes',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('chatflow_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('from_widget', postgresql.ARRAY(postgresql.UUID()), nullable=True),
    sa.Column('widget', sa.JSON(), nullable=True),
    sa.Column('quick_replies', postgresql.ARRAY(sa.JSON()), nullable=True),
    sa.Column('is_head', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['chatflow_id'], ['bot_builder_chatflows.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bot_builder_nodeuies',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('text', sa.String(length=255), nullable=True),
    sa.Column('width', sa.Integer(), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('data', sa.JSON(), nullable=True),
    sa.Column('ports', postgresql.ARRAY(sa.JSON()), nullable=True),
    sa.Column('has_delete_action', sa.Boolean(), nullable=True),
    sa.Column('has_edit_action', sa.Boolean(), nullable=True),
    sa.Column('chatflow_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['chatflow_id'], ['bot_builder_chatflows.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bot_builder_nodeuies')
    op.drop_table('bot_builder_nodes')
    op.drop_table('bot_builder_edges')
    op.drop_table('academy_content_labels')
    op.drop_table('academy_content_categories')
    op.drop_table('notification_users')
    op.drop_table('live_chat_messages')
    op.drop_table('live_chat_contacts')
    op.drop_table('instagram_pages')
    op.drop_table('connections')
    op.drop_table('bot_builder_chatflows')
    op.drop_table('academy_contents')
    op.drop_table('users')
    op.drop_table('roles')
    op.drop_table('notifications')
    op.drop_table('academy_labels')
    op.drop_table('academy_categories')
    # ### end Alembic commands ###
