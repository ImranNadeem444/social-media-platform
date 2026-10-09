"""Create facebook_oauth_sessions table

Revision ID: aaaa1111bbbb
Revises: dd5dc6ccb5ee
Create Date: 2026-10-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aaaa1111bbbb'
down_revision = 'dd5dc6ccb5ee'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'facebook_oauth_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('selection_token_hash', sa.String(length=255), nullable=False),
        sa.Column('page_candidates', sa.Text(), nullable=False),
        sa.Column('user_access_token_encrypted', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('selection_token_hash'),
    )
    op.create_index(op.f('ix_facebook_oauth_sessions_selection_token_hash'), 'facebook_oauth_sessions', ['selection_token_hash'], unique=False)
    op.create_index(op.f('ix_facebook_oauth_sessions_user_id'), 'facebook_oauth_sessions', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_facebook_oauth_sessions_user_id'), table_name='facebook_oauth_sessions')
    op.drop_index(op.f('ix_facebook_oauth_sessions_selection_token_hash'), table_name='facebook_oauth_sessions')
    op.drop_table('facebook_oauth_sessions')
