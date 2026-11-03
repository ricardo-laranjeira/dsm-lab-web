from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base

if TYPE_CHECKING:
    from api.models.material import Material
    from api.models.orcamento import Orcamento


class OrcamentoMaterial(Base):
    __tablename__ = "orcamentos_materiais"

    orcamentos_id: Mapped[int] = mapped_column(
        ForeignKey("orcamentos.idorcamentos", ondelete="CASCADE"),
        primary_key=True,
    )
    materiais_id: Mapped[int] = mapped_column(
        ForeignKey("materiais.idmateriais", ondelete="RESTRICT"),
        primary_key=True,
    )
    quantidade: Mapped[int] = mapped_column(nullable=False)
    orcamento: Mapped["Orcamento"] = relationship(
        "Orcamento", back_populates="materiais"
    )
    material: Mapped["Material"] = relationship(
        "Material", back_populates="orcamentos"
    )
