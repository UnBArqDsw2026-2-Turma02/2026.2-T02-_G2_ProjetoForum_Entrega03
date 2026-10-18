
from .anuncio import AnuncioGenerico
from .campanha import Campanha
from .contexto import Pergunta


class EstrategiaAnuncioGenerico:
    def __init__(self, anuncio_padrao: AnuncioGenerico) -> None:
        if not isinstance(anuncio_padrao, AnuncioGenerico):
            raise TypeError(
                "O anúncio padrão deve ser uma instância de AnuncioGenerico."
            )

        self._anuncio_padrao = anuncio_padrao

    def obter_nome(self) -> str:
        return "generico"

    def selecionar_anuncio(
        self,
        pergunta: Pergunta,
        campanhas: list[Campanha],
    ) -> AnuncioGenerico:
        return self._anuncio_padrao
