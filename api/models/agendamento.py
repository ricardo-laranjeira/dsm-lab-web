from datetime import date, time

from sqlalchemy import Date, ForeignKey, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base
from api.models.mixins.auditoria import AuditoriaMixin


class Agendamento(Base, AuditoriaMixin):
    __tablename__ = "agendamentos"
    __table_args__ = (
        UniqueConstraint("orcamentos_id", name="uq_agendamentos_orcamentos_id"),
    )

    idagendamentos: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    hora: Mapped[time] = mapped_column(Time, nullable=False)

    orcamentos_id: Mapped[int] = mapped_column(
        ForeignKey("orcamentos.idorcamentos", ondelete="CASCADE"),
        nullable=False,
    )
    orcamento: Mapped["Orcamento"] = relationship(
        "Orcamento", back_populates="agendamento"
    )
