"""add wave trust overrides and policy action logs

Revision ID: bbe62dbec5e4
Revises: 8a6b0c9d4e2f
Create Date: 2026-03-19 14:27:15.955805

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bbe62dbec5e4"
down_revision: str | Sequence[str] | None = "8a6b0c9d4e2f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "wavedomaintrustoverride",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("wave_id", sa.Integer(), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("trust_level", sa.String(length=7), nullable=True),
        sa.Column("approval_policy", sa.String(length=19), nullable=True),
        sa.Column("notes", sa.String(length=2000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["wave_id"], ["wave.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("wavedomaintrustoverride", schema=None) as batch_op:
        batch_op.create_index(
            "ix_wave_trust_override_wave_domain_unique",
            ["wave_id", "domain"],
            unique=True,
        )
        batch_op.create_index(
            "ix_wave_trust_override_wave_updated",
            ["wave_id", "updated_at"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_wavedomaintrustoverride_approval_policy"),
            ["approval_policy"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_wavedomaintrustoverride_domain"),
            ["domain"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_wavedomaintrustoverride_trust_level"),
            ["trust_level"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_wavedomaintrustoverride_updated_at"),
            ["updated_at"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_wavedomaintrustoverride_wave_id"),
            ["wave_id"],
            unique=False,
        )

    op.create_table(
        "policyactionlog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("wave_id", sa.Integer(), nullable=False),
        sa.Column("discovered_source_id", sa.Integer(), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=True),
        sa.Column("action_type", sa.String(length=80), nullable=False),
        sa.Column("previous_status", sa.String(length=8), nullable=False),
        sa.Column("new_status", sa.String(length=8), nullable=False),
        sa.Column("previous_policy_context", sa.JSON(), nullable=True),
        sa.Column("new_policy_context", sa.JSON(), nullable=True),
        sa.Column("reason", sa.String(length=2000), nullable=False),
        sa.Column("triggered_by", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["discovered_source_id"], ["discoveredsource.id"]),
        sa.ForeignKeyConstraint(["wave_id"], ["wave.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("policyactionlog", schema=None) as batch_op:
        batch_op.create_index(
            "ix_policy_action_log_source_created",
            ["discovered_source_id", "created_at"],
            unique=False,
        )
        batch_op.create_index(
            "ix_policy_action_log_wave_created",
            ["wave_id", "created_at"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_policyactionlog_action_type"),
            ["action_type"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_policyactionlog_created_at"),
            ["created_at"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_policyactionlog_discovered_source_id"),
            ["discovered_source_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_policyactionlog_domain"),
            ["domain"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_policyactionlog_new_status"),
            ["new_status"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_policyactionlog_previous_status"),
            ["previous_status"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_policyactionlog_triggered_by"),
            ["triggered_by"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_policyactionlog_wave_id"),
            ["wave_id"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("policyactionlog", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_policyactionlog_wave_id"))
        batch_op.drop_index(batch_op.f("ix_policyactionlog_triggered_by"))
        batch_op.drop_index(batch_op.f("ix_policyactionlog_previous_status"))
        batch_op.drop_index(batch_op.f("ix_policyactionlog_new_status"))
        batch_op.drop_index(batch_op.f("ix_policyactionlog_domain"))
        batch_op.drop_index(batch_op.f("ix_policyactionlog_discovered_source_id"))
        batch_op.drop_index(batch_op.f("ix_policyactionlog_created_at"))
        batch_op.drop_index(batch_op.f("ix_policyactionlog_action_type"))
        batch_op.drop_index("ix_policy_action_log_wave_created")
        batch_op.drop_index("ix_policy_action_log_source_created")

    op.drop_table("policyactionlog")

    with op.batch_alter_table("wavedomaintrustoverride", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_wavedomaintrustoverride_wave_id"))
        batch_op.drop_index(batch_op.f("ix_wavedomaintrustoverride_updated_at"))
        batch_op.drop_index(batch_op.f("ix_wavedomaintrustoverride_trust_level"))
        batch_op.drop_index(batch_op.f("ix_wavedomaintrustoverride_domain"))
        batch_op.drop_index(batch_op.f("ix_wavedomaintrustoverride_approval_policy"))
        batch_op.drop_index("ix_wave_trust_override_wave_updated")
        batch_op.drop_index("ix_wave_trust_override_wave_domain_unique")

    op.drop_table("wavedomaintrustoverride")
