from typing import Protocol, runtime_checkable

from .anuncio import Anuncio
from .campanha import Campanha
from .contexto import Pergunta


@runtime_checkable
class EstrategiaSelecaoAnuncio(Protocol):
    def selecionar_anuncio(
        self, pergunta: Pergunta, campanhas: list[Campanha]
    ) -> Anuncio | None:
        ...

    def obter_nome(self) -> str:
        ...
