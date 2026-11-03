from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class MaterialCreate(BaseModel):
    descricao: str = Field(min_length=1, max_length=150)
    valor: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    unidade_medida: str = Field(min_length=1, max_length=45)
    categorias_id: int = Field(gt=0)


class MaterialUpdate(BaseModel):
    descricao: str | None = Field(default=None, min_length=1, max_length=150)
    valor: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    unidade_medida: str | None = Field(default=None, min_length=1, max_length=45)
    categorias_id: int | None = Field(default=None, gt=0)


class MaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    idmateriais: int
    descricao: str
    valor: Decimal
    unidade_medida: str
    data_cadastro: datetime
    data_atualizacao: datetime | None = None
    categorias_id: int
