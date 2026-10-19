from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PerguntaIn(BaseModel):
    titulo: str = Field(min_length=1)
    corpo: str = Field(min_length=1)
    autor: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)


class RespostaIn(BaseModel):
    corpo: str = Field(min_length=1)
    autor: str = Field(min_length=1)


class ComentarioIn(BaseModel):
    corpo: str = Field(min_length=1)
    autor: str = Field(min_length=1)


class RespostaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pergunta_id: UUID
    corpo: str
    autor: str
    aceita: bool
    data_criacao: datetime


class ComentarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pergunta_id: UUID
    corpo: str
    autor: str
    data_criacao: datetime


class PerguntaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    titulo: str
    corpo: str
    autor: str
    tags: list[str]
    status: str
    data_criacao: datetime
    respostas: list[RespostaOut] = []
    comentarios: list[ComentarioOut] = []
