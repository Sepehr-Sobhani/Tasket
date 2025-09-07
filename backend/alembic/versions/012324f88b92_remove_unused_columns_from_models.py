"""remove unused columns from models

Revision ID: 012324f88b92
Revises: 4d001f6df8b8
Create Date: 2025-09-07 10:28:00.224850

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "012324f88b92"  # pragma: allowlist secret
down_revision: str | None = "4d001f6df8b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Remove unused columns from users table
    op.drop_column("users", "hashed_password")
    op.drop_column("users", "is_superuser")
    op.drop_column("users", "is_verified")
    op.drop_column("users", "bio")
    op.drop_column("users", "last_login")

    # Remove unused columns from projects table
    op.drop_column("projects", "visibility")
    op.drop_column("projects", "is_active")
    op.drop_column("projects", "github_repo_id")
    op.drop_column("projects", "github_repo_name")
    op.drop_column("projects", "github_repo_owner")
    op.drop_column("projects", "github_webhook_id")

    # Remove unused columns from project_members table
    op.drop_column("project_members", "is_active")
    op.drop_column("project_members", "joined_at")
    op.drop_column("project_members", "updated_at")

    # Drop unused enum types
    op.execute("DROP TYPE IF EXISTS projectvisibility CASCADE")


def downgrade() -> None:
    # Add back columns to users table
    op.add_column(
        "users", sa.Column("hashed_password", sa.VARCHAR(length=255), nullable=True)
    )
    op.add_column("users", sa.Column("is_superuser", sa.BOOLEAN(), nullable=True))
    op.add_column("users", sa.Column("is_verified", sa.BOOLEAN(), nullable=True))
    op.add_column("users", sa.Column("bio", sa.TEXT(), nullable=True))
    op.add_column(
        "users", sa.Column("last_login", sa.TIMESTAMP(timezone=True), nullable=True)
    )

    # Add back columns to projects table
    op.add_column(
        "projects",
        sa.Column(
            "visibility",
            sa.Enum("public", "private", name="projectvisibility"),
            nullable=True,
        ),
    )
    op.add_column("projects", sa.Column("is_active", sa.BOOLEAN(), nullable=True))
    op.add_column(
        "projects", sa.Column("github_repo_id", sa.VARCHAR(length=100), nullable=True)
    )
    op.add_column(
        "projects", sa.Column("github_repo_name", sa.VARCHAR(length=255), nullable=True)
    )
    op.add_column(
        "projects",
        sa.Column("github_repo_owner", sa.VARCHAR(length=100), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column("github_webhook_id", sa.VARCHAR(length=100), nullable=True),
    )

    # Add back columns to project_members table
    op.add_column(
        "project_members", sa.Column("is_active", sa.BOOLEAN(), nullable=True)
    )
    op.add_column(
        "project_members",
        sa.Column(
            "joined_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )
    op.add_column(
        "project_members",
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
