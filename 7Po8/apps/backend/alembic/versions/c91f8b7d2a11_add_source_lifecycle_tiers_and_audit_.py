"""add source lifecycle tiers and audit fields

Revision ID: c91f8b7d2a11
Revises: bbe62dbec5e4
Create Date: 2026-03-26 17:50:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c91f8b7d2a11"
down_revision: str | Sequence[str] | None = "bbe62dbec5e4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("discoveredsource", schema=None) as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.String(length=8),
            type_=sa.String(length=16),
        )
        batch_op.add_column(
            sa.Column("trust_tier", sa.String(length=6), nullable=False, server_default="TIER_4")
        )
        batch_op.add_column(sa.Column("degradation_reason", sa.String(length=500), nullable=True))
        batch_op.create_index(
            batch_op.f("ix_discoveredsource_trust_tier"),
            ["trust_tier"],
            unique=False,
        )

    op.execute(
        sa.text(
            "UPDATE discoveredsource "
            "SET status = 'CANDIDATE' "
            "WHERE status IN ('NEW', 'new')"
        )
    )
    op.execute(
        sa.text(
            "UPDATE discoveredsource "
            "SET trust_tier = CASE "
            "WHEN status IN ('APPROVED', 'DEGRADED') THEN 'TIER_3' "
            "WHEN status IN ('REJECTED', 'ARCHIVED', 'IGNORED') THEN 'TIER_5' "
            "ELSE 'TIER_4' END"
        )
    )

    with op.batch_alter_table("policyactionlog", schema=None) as batch_op:
        batch_op.alter_column(
            "previous_status",
            existing_type=sa.String(length=8),
            type_=sa.String(length=16),
        )
        batch_op.alter_column(
            "new_status",
            existing_type=sa.String(length=8),
            type_=sa.String(length=16),
        )
        batch_op.add_column(
            sa.Column(
                "previous_lifecycle_state",
                sa.String(length=9),
                nullable=False,
                server_default="CANDIDATE",
            )
        )
        batch_op.add_column(
            sa.Column(
                "new_lifecycle_state",
                sa.String(length=9),
                nullable=False,
                server_default="CANDIDATE",
            )
        )
        batch_op.add_column(
            sa.Column(
                "previous_trust_tier",
                sa.String(length=6),
                nullable=False,
                server_default="TIER_4",
            )
        )
        batch_op.add_column(
            sa.Column(
                "new_trust_tier",
                sa.String(length=6),
                nullable=False,
                server_default="TIER_4",
            )
        )
        batch_op.create_index(
            batch_op.f("ix_policyactionlog_previous_lifecycle_state"),
            ["previous_lifecycle_state"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_policyactionlog_new_lifecycle_state"),
            ["new_lifecycle_state"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_policyactionlog_previous_trust_tier"),
            ["previous_trust_tier"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_policyactionlog_new_trust_tier"),
            ["new_trust_tier"],
            unique=False,
        )

    op.execute(
        sa.text(
            "UPDATE policyactionlog "
            "SET previous_lifecycle_state = CASE "
            "WHEN previous_status IN ('NEW', 'new') THEN 'CANDIDATE' "
            "ELSE previous_status END, "
            "new_lifecycle_state = CASE "
            "WHEN new_status IN ('NEW', 'new') THEN 'CANDIDATE' "
            "ELSE new_status END, "
            "previous_trust_tier = CASE "
            "WHEN previous_status IN ('APPROVED', 'DEGRADED') THEN 'TIER_3' "
            "WHEN previous_status IN ('REJECTED', 'ARCHIVED', 'IGNORED') THEN 'TIER_5' "
            "ELSE 'TIER_4' END, "
            "new_trust_tier = CASE "
            "WHEN new_status IN ('APPROVED', 'DEGRADED') THEN 'TIER_3' "
            "WHEN new_status IN ('REJECTED', 'ARCHIVED', 'IGNORED') THEN 'TIER_5' "
            "ELSE 'TIER_4' END"
        )
    )


def downgrade() -> None:
    with op.batch_alter_table("policyactionlog", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_policyactionlog_new_trust_tier"))
        batch_op.drop_index(batch_op.f("ix_policyactionlog_previous_trust_tier"))
        batch_op.drop_index(batch_op.f("ix_policyactionlog_new_lifecycle_state"))
        batch_op.drop_index(batch_op.f("ix_policyactionlog_previous_lifecycle_state"))
        batch_op.drop_column("new_trust_tier")
        batch_op.drop_column("previous_trust_tier")
        batch_op.drop_column("new_lifecycle_state")
        batch_op.drop_column("previous_lifecycle_state")
        batch_op.alter_column(
            "new_status",
            existing_type=sa.String(length=16),
            type_=sa.String(length=8),
        )
        batch_op.alter_column(
            "previous_status",
            existing_type=sa.String(length=16),
            type_=sa.String(length=8),
        )

    with op.batch_alter_table("discoveredsource", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_discoveredsource_trust_tier"))
        batch_op.drop_column("degradation_reason")
        batch_op.drop_column("trust_tier")
        batch_op.alter_column(
            "status",
            existing_type=sa.String(length=16),
            type_=sa.String(length=8),
        )
