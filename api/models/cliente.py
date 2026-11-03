from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base
from api.models.mixins.auditoria import AuditoriaMixin

if TYPE_CHECKING:
    from api.models.endereco import Endereco
    from api.models.usuario import Usuario


class Cliente(Base, AuditoriaMixin):
    __tablename__ = "clientes"

    idclientes: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(45), nullable=False)
    telefone: Mapped[str] = mapped_column(
        String(16), nullable=False)
    ativo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1")
    usuarios_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.idusuarios", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    usuario: Mapped[Usuario] = relationship(back_populates="clientes")
    enderecos: Mapped[list[Endereco]] = relationship(
        back_populates="cliente",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
