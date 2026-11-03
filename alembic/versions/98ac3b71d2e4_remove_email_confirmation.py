"""remove confirmação de e-mail

Revision ID: 98ac3b71d2e4
Revises: 7d3b2a1c9e10
Create Date: 2026-10-31 15:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "98ac3b71d2e4"
down_revision: Union[str, Sequence[str], None] = "7d3b2a1c9e10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("email_verification_tokens")
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.drop_column("email_pendente")
        batch_op.drop_column("email_verificado")


def downgrade() -> None:
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.add_column(
            sa.Column("email_verificado", sa.Boolean(), nullable=False,
                      server_default=sa.true())
        )
        batch_op.add_column(
            sa.Column("email_pendente", sa.String(length=100), nullable=True)
        )
        batch_op.alter_column("email_verificado", server_default=None)

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
