"""adiciona confirmação de e-mail para usuários

Revision ID: 7d3b2a1c9e10
Revises: c19ab4d0e712
Create Date: 2026-10-31 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7d3b2a1c9e10"
down_revision: Union[str, Sequence[str], None] = "c19ab4d0e712"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column(
            "email_verificado",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.alter_column(
            "email_verificado",
            server_default=None,
        )
    op.add_column(
        "usuarios",
        sa.Column("email_pendente", sa.String(length=100), nullable=True),
    )
    op.create_table(
        "email_verification_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuarios.idusuarios"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
        sa.UniqueConstraint("usuario_id"),
    )


def downgrade() -> None:
    op.drop_table("email_verification_tokens")
    op.drop_column("usuarios", "email_pendente")
    op.drop_column("usuarios", "email_verificado")
