from collections.abc import Iterable
from decimal import Decimal
from threading import RLock
from typing import Protocol, runtime_checkable
from uuid import UUID

from .anuncio import Anuncio, AnuncioContextual, AnuncioGenerico
from .campanha import Campanha, StatusCampanha, Tag
from .contexto import Pergunta


@runtime_checkable
class RepositorioPerguntas(Protocol):
    def obter(self, pergunta_id: UUID) -> Pergunta | None:
        ...


@runtime_checkable
class RepositorioCampanhas(Protocol):
    def listar_ativas(self) -> list[Campanha]:
        ...


@runtime_checkable
class RepositorioMetricas(Protocol):
    def registrar_visualizacao(self, anuncio_id: UUID) -> None:
        ...

    def registrar_clique_atomico(self, anuncio_id: UUID) -> None:
        ...


class AnuncioNaoEncontrado(LookupError):
    pass


class CampanhaInelegivel(ValueError):
    pass


class RepositorioAds:
    """Adaptador em memória compartilhado pelas três portas de repositório.

    O inventário é configurado na construção. Atualizações concorrentes de saldo
    e métricas devem passar por esta instância, compartilhada no mesmo processo.
    """

    def __init__(
        self,
        campanhas: Iterable[Campanha] = (),
        perguntas: Iterable[Pergunta] = (),
        anuncio_padrao: AnuncioGenerico | None = None,
    ) -> None:
        self._lock = RLock()
        self._campanhas: dict[UUID, Campanha] = {}
        self._perguntas: dict[UUID, Pergunta] = {}
        self._anuncios: dict[UUID, tuple[Anuncio, Campanha | None]] = {}
        self._anuncio_padrao = anuncio_padrao

        for pergunta in perguntas:
            if pergunta.id in self._perguntas:
                raise ValueError("ID de pergunta duplicado.")
            self._perguntas[pergunta.id] = pergunta
        for campanha in campanhas:
            if campanha.id in self._campanhas:
                raise ValueError("ID de campanha duplicado.")
            self._campanhas[campanha.id] = campanha
            for anuncio in campanha.anuncios:
                self._indexar_anuncio(anuncio, campanha)
        if anuncio_padrao is not None:
            if not isinstance(anuncio_padrao, AnuncioGenerico):
                raise TypeError("O anúncio padrão deve ser AnuncioGenerico.")
            self._indexar_anuncio(anuncio_padrao, None)

    def _indexar_anuncio(self, anuncio: Anuncio, campanha: Campanha | None) -> None:
        if anuncio.id in self._anuncios:
            raise ValueError("Um anúncio deve ter ID único e pertencer a uma só campanha.")
        self._anuncios[anuncio.id] = (anuncio, campanha)

    @property
    def anuncio_padrao(self) -> AnuncioGenerico:
        if self._anuncio_padrao is None:
            raise ValueError("Anúncio genérico padrão não configurado.")
        return self._anuncio_padrao

    def obter(self, pergunta_id: UUID) -> Pergunta | None:
        with self._lock:
            return self._perguntas.get(pergunta_id)

    def listar_ativas(self) -> list[Campanha]:
        with self._lock:
            return [campanha for campanha in self._campanhas.values() if campanha.esta_ativa()]

    def obter_anuncio(self, anuncio_id: UUID) -> Anuncio | None:
        with self._lock:
            registro = self._anuncios.get(anuncio_id)
            return registro[0] if registro is not None else None

    def _obter_registro(self, anuncio_id: UUID) -> tuple[Anuncio, Campanha | None]:
        try:
            return self._anuncios[anuncio_id]
        except KeyError:
            raise AnuncioNaoEncontrado(f"Anúncio {anuncio_id} não encontrado.") from None

    def registrar_visualizacao(self, anuncio_id: UUID) -> None:
        with self._lock:
            anuncio, _ = self._obter_registro(anuncio_id)
            anuncio.obter_estatisticas().incrementar_visualizacao()

    def registrar_clique_atomico(self, anuncio_id: UUID) -> None:
        with self._lock:
            anuncio, campanha = self._obter_registro(anuncio_id)
            if campanha is not None and (
                not campanha.esta_ativa() or not campanha.possui_orcamento()
            ):
                raise CampanhaInelegivel("Campanha inativa ou sem saldo para o clique.")

            estatisticas = anuncio.obter_estatisticas()
            cliques_anteriores = estatisticas.cliques
            saldo_anterior = campanha.saldo_restante if campanha is not None else None
            status_anterior = campanha.status if campanha is not None else None
            try:
                if campanha is not None:
                    campanha.debitar_clique(campanha.custo_por_clique)
                estatisticas.incrementar_clique()
            except Exception:
                # Débito e contador formam uma única operação, inclusive em falhas.
                estatisticas.cliques = cliques_anteriores
                if campanha is not None:
                    campanha.saldo_restante = saldo_anterior
                    campanha.status = status_anterior
                raise

    @classmethod
    def seed(cls) -> "RepositorioAds":
        """Cria dados de demonstração isolados; não carrega perguntas reais."""
        python = Tag("python")
        anuncio_a = AnuncioContextual(
            UUID(int=11), "Curso de Python", "/static/curso-python.png", "/cursos/python"
        )
        anuncio_b = AnuncioContextual(
            UUID(int=12), "Comunidade Python", "/static/comunidade.png", "/comunidades/python"
        )
        campanhas = [
            Campanha(
                id=UUID(int=1), tags_alvo=[python], orcamento=Decimal("10.00"),
                saldo_restante=Decimal("5.00"), custo_por_clique=Decimal("1.00"),
                status=StatusCampanha.ATIVA, anuncios=[anuncio_a],
            ),
            Campanha(
                id=UUID(int=2), tags_alvo=[python], orcamento=Decimal("30.00"),
                saldo_restante=Decimal("20.00"), custo_por_clique=Decimal("2.00"),
                status=StatusCampanha.ATIVA, anuncios=[anuncio_b],
            ),
            Campanha(
                id=UUID(int=3), tags_alvo=[Tag("fastapi")], orcamento=Decimal("10.00"),
                saldo_restante=Decimal("0.00"), custo_por_clique=Decimal("1.00"),
                status=StatusCampanha.ESGOTADA,
            ),
        ]
        perguntas = [
            Pergunta(UUID(int=101), "Como aprender Python?", [python]),
            Pergunta(UUID(int=102), "Pergunta sem campanha compatível", [Tag("desconhecida")]),
        ]
        generico = AnuncioGenerico(
            UUID(int=30), "Fórum da comunidade", "/static/forum.png", "/",
            mensagem_padrao="Participe da comunidade.",
        )
        return cls(campanhas=campanhas, perguntas=perguntas, anuncio_padrao=generico)
