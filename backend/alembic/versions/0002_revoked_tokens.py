"""Add revoked_tokens: a jti blocklist so logout has a real server-side effect.

JWTs are stateless by default; this table lets POST /auth/logout immediately
invalidate the current token (NFR-004) with a single small table, which is
sufficient at the tens-to-low-hundreds-of-users scale this system targets
(NFR-016) -- no distributed session store needed.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-28
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "revoked_tokens",
        sa.Column("jti", sa.String(64), primary_key=True),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("revoked_tokens")
