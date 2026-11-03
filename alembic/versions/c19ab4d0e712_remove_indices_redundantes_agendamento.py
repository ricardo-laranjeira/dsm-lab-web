"""remove índices redundantes de agendamentos

Revision ID: c19ab4d0e712
Revises: f454c230e4bc
Create Date: 2026-10-22 14:41:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "c19ab4d0e712"
down_revision: Union[str, Sequence[str], None] = "f454c230e4bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(
        op.f("ix_agendamentos_orcamentos_id"),
        table_name="agendamentos",
    )
    op.drop_index(
        op.f("ix_agendamentos_idagendamentos"),
        table_name="agendamentos",
    )


def downgrade() -> None:
    op.create_index(
        op.f("ix_agendamentos_idagendamentos"),
        "agendamentos",
        ["idagendamentos"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agendamentos_orcamentos_id"),
        "agendamentos",
        ["orcamentos_id"],
        unique=False,
    )
