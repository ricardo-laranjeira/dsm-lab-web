from api.repositories.categoria_repository import categoria_repository
from api.repositories.cliente_repository import cliente_repository
from api.repositories.endereco_repository import endereco_repository
from api.repositories.material_repository import material_repository
from api.repositories.orcamento_material_repository import (
    orcamento_material_repository,
)
from api.repositories.orcamento_repository import orcamento_repository
from api.repositories.orcamento_servico_repository import (
    orcamento_servico_repository,
)
from api.repositories.servico_repository import servico_repository
from api.repositories.usuario_repository import usuario_repository
from api.repositories.agendamento_repository import agendamento_repository

__all__ = [
    "categoria_repository",
    "cliente_repository",
    "endereco_repository",
    "material_repository",
    "orcamento_material_repository",
    "orcamento_repository",
    "orcamento_servico_repository",
    "servico_repository",
    "usuario_repository",
    "agendamento_repository",
]
