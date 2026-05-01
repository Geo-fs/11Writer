"""add discovered source auto-check fields

Revision ID: 5c0e5d7a6c3a
Revises: f5e35ec3725d
Create Date: 2026-03-14 22:35:00

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "5c0e5d7a6c3a"
down_revision: str | Sequence[str] | None = "f5e35ec3725d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("discoveredsource", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("consecutive_failures", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("auto_check_enabled", sa.Boolean(), nullable=False, server_default=sa.true())
        )
        batch_op.add_column(
            sa.Column(
                "check_interval_minutes",
                sa.Integer(),
                nullable=False,
                server_default="60",
            )
        )
        batch_op.add_column(sa.Column("next_check_at", sa.DateTime(), nullable=True))
        batch_op.create_index(
            batch_op.f("ix_discoveredsource_consecutive_failures"),
            ["consecutive_failures"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_discoveredsource_auto_check_enabled"),
            ["auto_check_enabled"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_discoveredsource_next_check_at"),
            ["next_check_at"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("discoveredsource", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_discoveredsource_next_check_at"))
        batch_op.drop_index(batch_op.f("ix_discoveredsource_auto_check_enabled"))
        batch_op.drop_index(batch_op.f("ix_discoveredsource_consecutive_failures"))
        batch_op.drop_column("next_check_at")
        batch_op.drop_column("check_interval_minutes")
        batch_op.drop_column("auto_check_enabled")
        batch_op.drop_column("consecutive_failures")
