from dataclasses import dataclass
from uuid import UUID

from ..model.anuncio import Anuncio
from ..model.contexto import Pergunta
from ..model.repositorio import RepositorioCampanhas, RepositorioMetricas, RepositorioPerguntas
from ..model.strategies import EstrategiaSelecaoAnuncio
from ..service.seletor import SeletorDeEstrategia


class PerguntaNaoEncontrada(LookupError):
    pass


class FallbackSemAnuncio(RuntimeError):
    """A estratégia de fallback deve sempre devolver um anúncio quando configurada."""


@dataclass(frozen=True)
class EntregaAnuncio:
    pergunta: Pergunta
    anuncio: Anuncio
    politica: str
    usou_fallback: bool


class ControladorEntrega:
    """Context do Strategy: delega a seleção à política configurada.

    O fallback é responsabilidade do Context e só é executado quando a
    estratégia principal devolve None. Selecionar não registra eventos;
    visualizações e cliques são registrados explicitamente pelo chamador.
    """

    def __init__(
        self,
        seletor: SeletorDeEstrategia,
        politica: str,
        fallback: EstrategiaSelecaoAnuncio,
        perguntas: RepositorioPerguntas,
        campanhas: RepositorioCampanhas,
        metricas: RepositorioMetricas,
    ) -> None:
        if not isinstance(fallback, EstrategiaSelecaoAnuncio):
            raise TypeError("O fallback deve atender a EstrategiaSelecaoAnuncio.")
        self._seletor = seletor
        self._fallback = fallback
        self._perguntas = perguntas
        self._campanhas = campanhas
        self._metricas = metricas
        self.definir_estrategia(politica)

    @property
    def politica_atual(self) -> str:
        return self._estrategia.obter_nome()

    def definir_estrategia(self, politica: str) -> None:
        self._estrategia = self._seletor.escolher(politica)

    def entregar_anuncio(self, pergunta_id: UUID) -> EntregaAnuncio:
        pergunta = self._perguntas.obter(pergunta_id)
        if pergunta is None:
            raise PerguntaNaoEncontrada(f"Pergunta {pergunta_id} não encontrada.")

        campanhas = self._campanhas.listar_ativas()
        estrategia = self._estrategia
        anuncio = estrategia.selecionar_anuncio(pergunta, campanhas)
        if anuncio is None:
            estrategia = self._fallback
            anuncio = estrategia.selecionar_anuncio(pergunta, campanhas)
            if anuncio is None:
                raise FallbackSemAnuncio(
                    f"A estratégia de fallback '{estrategia.obter_nome()}' não devolveu anúncio."
                )

        return EntregaAnuncio(
            pergunta=pergunta,
            anuncio=anuncio,
            politica=estrategia.obter_nome(),
            usou_fallback=estrategia is self._fallback,
        )

    def registrar_visualizacao(self, anuncio_id: UUID) -> None:
        self._metricas.registrar_visualizacao(anuncio_id)

    def registrar_clique(self, anuncio_id: UUID) -> None:
        self._metricas.registrar_clique_atomico(anuncio_id)
