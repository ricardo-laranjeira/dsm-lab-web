from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base
from api.models.mixins.auditoria import AuditoriaMixin
from api.models.mixins.categoria import CategoriaMixin

if TYPE_CHECKING:
    from api.models.categoria import Categoria
    from api.models.orcamento_servico import OrcamentoServico


class Servico(Base, AuditoriaMixin, CategoriaMixin):
    __tablename__ = "servicos"

    idservicos: Mapped[int] = mapped_column(primary_key=True, index=True)
    descricao: Mapped[str] = mapped_column(String(150), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    categoria: Mapped[Categoria] = relationship(back_populates="servicos")

    orcamentos: Mapped[list["OrcamentoServico"]] = relationship(
        "OrcamentoServico", back_populates="servico"
    )
