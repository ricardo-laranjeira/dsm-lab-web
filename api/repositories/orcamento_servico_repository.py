from api.models.orcamento_servico import OrcamentoServico
from api.repositories.associacao_repository import (
    AssociacaoRepository,
)


class OrcamentoServicoRepository(
    AssociacaoRepository[OrcamentoServico]
):
    def __init__(self):
        super().__init__(OrcamentoServico)

    def adicionar_servico(
        self,
        db,
        orcamentos_id: int,
        servicos_id: int,
        quantidade: int,
    ):
        item = OrcamentoServico(
            orcamentos_id=orcamentos_id,
            servicos_id=servicos_id,
            quantidade=quantidade,
        )

        return self._salvar(db, item)


orcamento_servico_repository = (
    OrcamentoServicoRepository()
)
