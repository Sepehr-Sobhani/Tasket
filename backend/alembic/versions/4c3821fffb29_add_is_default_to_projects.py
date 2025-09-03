"""add_is_default_to_projects

Revision ID: 4c3821fffb29
Revises: 2f14a4022334
Create Date: 2025-08-25 23:08:46.112692

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4c3821fffb29"  # pragma: allowlist secret
down_revision: str | None = "2f14a4022334"  # pragma: allowlist secret
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add is_default column to projects table
    op.add_column(
        "projects",
        sa.Column("is_default", sa.Boolean(), nullable=True, server_default="false"),
    )


def downgrade() -> None:
    # Remove is_default column from projects table
    op.drop_column("projects", "is_default")
