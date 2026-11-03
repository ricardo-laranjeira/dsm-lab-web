from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base

if TYPE_CHECKING:
    from api.models.orcamento import Orcamento
    from api.models.servico import Servico


class OrcamentoServico(Base):
    __tablename__ = "orcamentos_servicos"

    orcamentos_id: Mapped[int] = mapped_column(
        ForeignKey("orcamentos.idorcamentos", ondelete="CASCADE"),
        primary_key=True,
    )
    servicos_id: Mapped[int] = mapped_column(
        ForeignKey("servicos.idservicos", ondelete="RESTRICT"),
        primary_key=True,
    )
    quantidade: Mapped[int] = mapped_column(nullable=False)
    orcamento: Mapped["Orcamento"] = relationship(
        "Orcamento", back_populates="servicos"
    )
    servico: Mapped["Servico"] = relationship(
        "Servico", back_populates="orcamentos"
    )
