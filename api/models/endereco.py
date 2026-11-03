from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base
from api.models.mixins.auditoria import AuditoriaMixin

if TYPE_CHECKING:
    from api.models.cliente import Cliente


class Endereco(Base, AuditoriaMixin):
    __tablename__ = "enderecos"

    idenderecos: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    cep: Mapped[str] = mapped_column(String(10), nullable=False)
    endereco: Mapped[str] = mapped_column(String(100), nullable=False)
    numero: Mapped[str] = mapped_column(String(5), nullable=False)
    complemento: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bairro: Mapped[str] = mapped_column(String(100), nullable=False)
    cidade: Mapped[str] = mapped_column(String(45), nullable=False)
    estado: Mapped[str] = mapped_column(String(45), nullable=False)

    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.idclientes", ondelete="CASCADE"),
        nullable=False, index=True
    )

    cliente: Mapped[Cliente] = relationship(back_populates="enderecos")
