from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class ServicoCreate(BaseModel):
    descricao: str = Field(min_length=1, max_length=150)
    valor: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    categorias_id: int = Field(gt=0)


class ServicoUpdate(BaseModel):
    descricao: str | None = Field(default=None, min_length=1, max_length=150)
    valor: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    categorias_id: int | None = Field(default=None, gt=0)


class ServicoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    idservicos: int
    descricao: str
    valor: Decimal
    data_cadastro: datetime
    data_atualizacao: datetime | None = None
    categorias_id: int
