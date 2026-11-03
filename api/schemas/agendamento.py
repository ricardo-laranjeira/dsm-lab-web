from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field


class AgendamentoBase(BaseModel):
    data: date
    hora: time
    orcamentos_id: int = Field(gt=0)


class AgendamentoCreate(AgendamentoBase):
    pass


class AgendamentoUpdate(BaseModel):
    data: date | None = None
    hora: time | None = None


class AgendamentoResponse(AgendamentoBase):
    idagendamentos: int
    data_cadastro: datetime
    data_atualizacao: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
