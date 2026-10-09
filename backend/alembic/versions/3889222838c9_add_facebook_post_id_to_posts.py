"""add facebook post id to posts

Revision ID: 3889222838c9
Revises: aaaa1111bbbb
Create Date: 2026-10-07 01:54:03.541061

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3889222838c9"
down_revision: Union[str, Sequence[str], None] = "aaaa1111bbbb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Facebook post ID column to posts table."""
    op.add_column(
        "posts",
        sa.Column(
            "facebook_post_id",
            sa.String(length=255),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove Facebook post ID column from posts table."""
    op.drop_column(
        "posts",
        "facebook_post_id",
    )