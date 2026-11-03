from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class OrcamentoCreate(BaseModel):
    validade: date
    status: bool = True
    clientes_id: int = Field(gt=0)


class OrcamentoUpdate(BaseModel):
    validade: date | None = None
    status: bool | None = None
    clientes_id: int | None = Field(default=None, gt=0)


class OrcamentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idorcamentos: int
    validade: date
    status: bool
    data_cadastro: datetime
    data_atualizacao: datetime | None = None
    usuarios_id: int
    clientes_id: int
