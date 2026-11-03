from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from api.models.base import Base
from api.models.mixins.auditoria import AuditoriaMixin

if TYPE_CHECKING:
    from api.models.usuario import Usuario
    from api.models.cliente import Cliente
    from api.models.orcamento_servico import OrcamentoServico
    from api.models.orcamento_material import OrcamentoMaterial


class Orcamento(Base, AuditoriaMixin):
    __tablename__ = "orcamentos"

    idorcamentos: Mapped[int] = mapped_column(primary_key=True, index=True)
    validade: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1"
    )
    usuarios_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.idusuarios", ondelete="CASCADE"),
        nullable=False, index=True
    )
    clientes_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.idclientes", ondelete="CASCADE"),
        nullable=False, index=True
    )

    usuario: Mapped["Usuario"] = relationship("Usuario")
    cliente: Mapped["Cliente"] = relationship("Cliente")

    materiais: Mapped[list["OrcamentoMaterial"]] = relationship(
        "OrcamentoMaterial", back_populates="orcamento",
        cascade="all, delete-orphan", passive_deletes=True,
    )
    servicos: Mapped[list["OrcamentoServico"]] = relationship(
        "OrcamentoServico", back_populates="orcamento",
        cascade="all, delete-orphan", passive_deletes=True,
    )

    agendamento: Mapped["Agendamento | None"] = relationship(
        "Agendamento",
        back_populates="orcamento",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
