from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class CategoriaMixin:
    categorias_id: Mapped[int] = mapped_column(
        ForeignKey(
            "categorias.idcategorias",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True,
    )
