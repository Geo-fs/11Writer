"""add domain trust profiles

Revision ID: 8a6b0c9d4e2f
Revises: 5c0e5d7a6c3a
Create Date: 2026-03-14 23:10:00

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8a6b0c9d4e2f"
down_revision: str | Sequence[str] | None = "5c0e5d7a6c3a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "domaintrustprofile",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("trust_level", sa.String(length=7), nullable=False),
        sa.Column("approval_policy", sa.String(length=19), nullable=False),
        sa.Column("notes", sa.String(length=2000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_domain_trust_domain_unique",
        "domaintrustprofile",
        ["domain"],
        unique=True,
    )
    op.create_index(
        "ix_domain_trust_level_policy",
        "domaintrustprofile",
        ["trust_level", "approval_policy"],
        unique=False,
    )
    op.create_index(
        op.f("ix_domaintrustprofile_approval_policy"),
        "domaintrustprofile",
        ["approval_policy"],
        unique=False,
    )
    op.create_index(
        op.f("ix_domaintrustprofile_domain"),
        "domaintrustprofile",
        ["domain"],
        unique=False,
    )
    op.create_index(
        op.f("ix_domaintrustprofile_trust_level"),
        "domaintrustprofile",
        ["trust_level"],
        unique=False,
    )
    op.create_index(
        op.f("ix_domaintrustprofile_updated_at"),
        "domaintrustprofile",
        ["updated_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_domaintrustprofile_updated_at"), table_name="domaintrustprofile")
    op.drop_index(op.f("ix_domaintrustprofile_trust_level"), table_name="domaintrustprofile")
    op.drop_index(op.f("ix_domaintrustprofile_domain"), table_name="domaintrustprofile")
    op.drop_index(
        op.f("ix_domaintrustprofile_approval_policy"),
        table_name="domaintrustprofile",
    )
    op.drop_index("ix_domain_trust_level_policy", table_name="domaintrustprofile")
    op.drop_index("ix_domain_trust_domain_unique", table_name="domaintrustprofile")
    op.drop_table("domaintrustprofile")
