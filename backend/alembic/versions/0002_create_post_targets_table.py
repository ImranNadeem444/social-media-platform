"""create_post_targets_table

Revision ID: 0002_create_post_targets
Revises: 3889222838c9
Create Date: 2026-10-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002_create_post_targets'
down_revision: Union[str, Sequence[str], None] = '3889222838c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create post_targets table
    op.create_table(
        'post_targets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('social_account_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('platform_media_id', sa.String(length=255), nullable=True),
        sa.Column('platform_post_id', sa.String(length=255), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['social_account_id'], ['social_accounts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(op.f('ix_post_targets_post_id'), 'post_targets', ['post_id'], unique=False)
    op.create_index(op.f('ix_post_targets_social_account_id'), 'post_targets', ['social_account_id'], unique=False)
    op.create_index(op.f('ix_post_targets_status'), 'post_targets', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_post_targets_status'), table_name='post_targets')
    op.drop_index(op.f('ix_post_targets_social_account_id'), table_name='post_targets')
    op.drop_index(op.f('ix_post_targets_post_id'), table_name='post_targets')
    op.drop_table('post_targets')
