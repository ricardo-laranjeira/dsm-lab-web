from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base
from api.models.mixins.auditoria import AuditoriaMixin

if TYPE_CHECKING:
    from api.models.material import Material
    from api.models.servico import Servico


class Categoria(Base, AuditoriaMixin):
    __tablename__ = "categorias"

    idcategorias: Mapped[int] = mapped_column(primary_key=True, index=True)
    descricao: Mapped[str] = mapped_column(String(45), nullable=False)

    materiais: Mapped[list[Material]] = relationship(back_populates="categoria")
    servicos: Mapped[list[Servico]] = relationship(back_populates="categoria")
