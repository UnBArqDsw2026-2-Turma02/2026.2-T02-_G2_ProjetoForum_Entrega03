from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from ..model.anuncio import FormatoAnuncio, validar_url_anuncio


class AnuncioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    titulo: str
    link_destino: str
    banner_url: str
    formato: FormatoAnuncio

    @field_validator("link_destino", "banner_url")
    @classmethod
    def validar_url(cls, valor: str) -> str:
        validar_url_anuncio(valor)
        return valor
