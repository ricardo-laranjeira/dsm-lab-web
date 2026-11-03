from pydantic import BaseModel, ConfigDict, Field


class OrcamentoServicoCreate(BaseModel):
    servicos_id: int = Field(gt=0)
    quantidade: int = Field(gt=0)


class OrcamentoServicoUpdate(BaseModel):
    quantidade: int = Field(gt=0)


class OrcamentoServicoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    orcamentos_id: int
    servicos_id: int
    quantidade: int
