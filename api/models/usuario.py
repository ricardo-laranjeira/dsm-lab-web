from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base
from api.models.mixins.auditoria import AuditoriaMixin

if TYPE_CHECKING:
    from api.models.cliente import Cliente


class Usuario(Base, AuditoriaMixin):
    __tablename__ = "usuarios"

    idusuarios: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(45), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    senha: Mapped[str] = mapped_column(String(200), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    clientes: Mapped[list[Cliente]] = relationship(
        back_populates="usuario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
