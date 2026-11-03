from api.models.orcamento_material import OrcamentoMaterial
from api.repositories.associacao_repository import (
    AssociacaoRepository,
)


class OrcamentoMaterialRepository(
    AssociacaoRepository[OrcamentoMaterial]
):
    def __init__(self):
        super().__init__(OrcamentoMaterial)

    def adicionar_material(
        self,
        db,
        orcamentos_id: int,
        materiais_id: int,
        quantidade: int,
    ):
        item = OrcamentoMaterial(
            orcamentos_id=orcamentos_id,
            materiais_id=materiais_id,
            quantidade=quantidade,
        )

        return self._salvar(db, item)


orcamento_material_repository = (
    OrcamentoMaterialRepository()
)
