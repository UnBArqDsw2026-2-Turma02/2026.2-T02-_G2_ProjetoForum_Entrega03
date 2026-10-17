from collections.abc import Iterable

from ..model.strategies import EstrategiaSelecaoAnuncio


class PoliticaDesconhecida(LookupError):
    """A política configurada não corresponde a nenhuma estratégia registrada."""


class SeletorDeEstrategia:
    """Registro das políticas de seleção, indexadas pelo nome de cada estratégia.

    Acrescentar uma política exige apenas registrar a nova estratégia; o
    registro não inspeciona tags nem decide qual algoritmo usar.
    """

    def __init__(self, estrategias: Iterable[EstrategiaSelecaoAnuncio] = ()) -> None:
        self._estrategias: dict[str, EstrategiaSelecaoAnuncio] = {}
        for estrategia in estrategias:
            self.registrar(estrategia)

    def registrar(self, estrategia: EstrategiaSelecaoAnuncio) -> None:
        if not isinstance(estrategia, EstrategiaSelecaoAnuncio):
            raise TypeError("A estratégia deve atender a EstrategiaSelecaoAnuncio.")
        nome = estrategia.obter_nome()
        if not isinstance(nome, str) or not nome:
            raise ValueError("O nome da estratégia deve ser uma string não vazia.")
        if nome in self._estrategias:
            raise ValueError(f"A política '{nome}' já está registrada.")
        self._estrategias[nome] = estrategia

    def escolher(self, politica: str) -> EstrategiaSelecaoAnuncio:
        try:
            return self._estrategias[politica]
        except KeyError:
            disponiveis = ", ".join(self.politicas()) or "nenhuma"
            raise PoliticaDesconhecida(
                f"Política '{politica}' não registrada. Disponíveis: {disponiveis}."
            ) from None

    def politicas(self) -> tuple[str, ...]:
        return tuple(sorted(self._estrategias))
