import inspect
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from uuid import UUID

import pytest

from subequipe3_strategy.ads.controller import controlador_entrega as modulo_controlador
from subequipe3_strategy.ads.controller.controlador_entrega import (
    ControladorEntrega,
    FallbackSemAnuncio,
    PerguntaNaoEncontrada,
)
from subequipe3_strategy.ads.model.campanha import StatusCampanha
from subequipe3_strategy.ads.model.match_exato import EstrategiaMatchExatoDeTag
from subequipe3_strategy.ads.model.repositorio import AnuncioNaoEncontrado, CampanhaInelegivel, RepositorioAds
from subequipe3_strategy.ads.service.seletor import PoliticaDesconhecida, SeletorDeEstrategia

PERGUNTA_COM_MATCH = UUID(int=101)
PERGUNTA_SEM_MATCH = UUID(int=102)
ANUNCIO_CAMPANHA_1 = UUID(int=11)
ANUNCIO_CAMPANHA_2 = UUID(int=12)
ANUNCIO_PADRAO = UUID(int=30)


class FallbackDeTeste:
    """Dublê da estratégia genérica (#26): devolve o anúncio padrão configurado."""

    def __init__(self, anuncio):
        self.anuncio = anuncio
        self.chamadas = 0

    def obter_nome(self):
        return "generico"

    def selecionar_anuncio(self, pergunta, campanhas):
        self.chamadas += 1
        return self.anuncio


class MaiorSaldoDeTeste:
    """Dublê de uma segunda política, para provar a troca sem alterar o Context."""

    def obter_nome(self):
        return "maior_saldo"

    def selecionar_anuncio(self, pergunta, campanhas):
        campanha = max(campanhas, key=lambda c: c.saldo_restante, default=None)
        return campanha.anuncios[0] if campanha is not None else None


@pytest.fixture
def repositorio():
    return RepositorioAds.seed()


@pytest.fixture
def fallback(repositorio):
    return FallbackDeTeste(repositorio.anuncio_padrao)


@pytest.fixture
def criar_controlador(repositorio, fallback):
    def criar(politica="match_exato", estrategia_fallback=None):
        seletor = SeletorDeEstrategia([EstrategiaMatchExatoDeTag(), MaiorSaldoDeTeste()])
        return ControladorEntrega(
            seletor=seletor,
            politica=politica,
            fallback=estrategia_fallback or fallback,
            perguntas=repositorio,
            campanhas=repositorio,
            metricas=repositorio,
        )
    return criar


def estado(repositorio):
    campanhas = sorted(repositorio.listar_ativas(), key=lambda c: c.id.int)
    anuncios = [repositorio.obter_anuncio(UUID(int=n)) for n in (11, 12, 30)]
    return (
        [(c.saldo_restante, c.status) for c in campanhas],
        [(a.obter_estatisticas().visualizacoes, a.obter_estatisticas().cliques) for a in anuncios],
    )


def test_entrega_contextual_pela_politica_configurada(criar_controlador, fallback):
    entrega = criar_controlador().entregar_anuncio(PERGUNTA_COM_MATCH)
    assert entrega.anuncio.id == ANUNCIO_CAMPANHA_1
    assert entrega.pergunta.id == PERGUNTA_COM_MATCH
    assert entrega.politica == "match_exato"
    assert entrega.usou_fallback is False
    assert fallback.chamadas == 0


def test_fallback_apenas_quando_estrategia_devolve_none(criar_controlador, fallback):
    entrega = criar_controlador().entregar_anuncio(PERGUNTA_SEM_MATCH)
    assert entrega.anuncio.id == ANUNCIO_PADRAO
    assert entrega.politica == "generico"
    assert entrega.usou_fallback is True
    assert fallback.chamadas == 1


def test_troca_de_politica_muda_o_anuncio_sem_alterar_o_context(criar_controlador):
    controlador = criar_controlador()
    assert controlador.entregar_anuncio(PERGUNTA_COM_MATCH).anuncio.id == ANUNCIO_CAMPANHA_1
    controlador.definir_estrategia("maior_saldo")
    assert controlador.politica_atual == "maior_saldo"
    assert controlador.entregar_anuncio(PERGUNTA_COM_MATCH).anuncio.id == ANUNCIO_CAMPANHA_2


def test_politica_configurada_desconhecida_falha_na_construcao(criar_controlador):
    with pytest.raises(PoliticaDesconhecida):
        criar_controlador(politica="maior_lance")


def test_definir_politica_desconhecida_preserva_a_atual(criar_controlador):
    controlador = criar_controlador()
    with pytest.raises(PoliticaDesconhecida):
        controlador.definir_estrategia("maior_lance")
    assert controlador.politica_atual == "match_exato"


def test_pergunta_inexistente(criar_controlador):
    with pytest.raises(PerguntaNaoEncontrada):
        criar_controlador().entregar_anuncio(UUID(int=999))


def test_fallback_sem_anuncio_e_erro_de_configuracao(criar_controlador):
    with pytest.raises(FallbackSemAnuncio, match="generico"):
        criar_controlador(estrategia_fallback=FallbackDeTeste(None)).entregar_anuncio(PERGUNTA_SEM_MATCH)


def test_fallback_precisa_atender_ao_contrato(criar_controlador):
    with pytest.raises(TypeError):
        criar_controlador(estrategia_fallback=object())


def test_selecionar_nao_registra_eventos_nem_debita(criar_controlador, repositorio):
    antes = estado(repositorio)
    controlador = criar_controlador()
    controlador.entregar_anuncio(PERGUNTA_COM_MATCH)
    controlador.entregar_anuncio(PERGUNTA_SEM_MATCH)
    assert estado(repositorio) == antes


def test_context_nao_tem_condicional_especifico_de_estrategia():
    codigo = inspect.getsource(modulo_controlador)
    for nome in ("match_exato", "maior_saldo", "EstrategiaMatchExatoDeTag", "isinstance(anuncio"):
        assert nome not in codigo


def test_registrar_visualizacao_incrementa_uma_vez(criar_controlador, repositorio):
    criar_controlador().registrar_visualizacao(ANUNCIO_CAMPANHA_1)
    estatisticas = repositorio.obter_anuncio(ANUNCIO_CAMPANHA_1).obter_estatisticas()
    assert (estatisticas.visualizacoes, estatisticas.cliques) == (1, 0)


def test_clique_contextual_debita_e_conta(criar_controlador, repositorio):
    criar_controlador().registrar_clique(ANUNCIO_CAMPANHA_1)
    anuncio = repositorio.obter_anuncio(ANUNCIO_CAMPANHA_1)
    campanha = next(c for c in repositorio.listar_ativas() if anuncio in c.anuncios)
    assert anuncio.obter_estatisticas().cliques == 1
    assert campanha.saldo_restante == Decimal("4.00")


def test_clique_generico_conta_sem_debitar(criar_controlador, repositorio):
    saldos = [c.saldo_restante for c in repositorio.listar_ativas()]
    criar_controlador().registrar_clique(ANUNCIO_PADRAO)
    assert repositorio.anuncio_padrao.obter_estatisticas().cliques == 1
    assert [c.saldo_restante for c in repositorio.listar_ativas()] == saldos


def test_clique_em_anuncio_inexistente(criar_controlador):
    with pytest.raises(AnuncioNaoEncontrado):
        criar_controlador().registrar_clique(UUID(int=999))


def test_clique_sem_saldo_nao_altera_estado(criar_controlador, repositorio):
    controlador = criar_controlador()
    for _ in range(5):
        controlador.registrar_clique(ANUNCIO_CAMPANHA_1)
    antes = estado(repositorio)
    with pytest.raises(CampanhaInelegivel):
        controlador.registrar_clique(ANUNCIO_CAMPANHA_1)
    assert estado(repositorio) == antes


def test_cliques_concorrentes_nao_deixam_saldo_negativo(criar_controlador, repositorio):
    controlador = criar_controlador()
    anuncio = repositorio.obter_anuncio(ANUNCIO_CAMPANHA_1)
    campanha = next(c for c in repositorio.listar_ativas() if anuncio in c.anuncios)

    def clicar(_):
        try:
            controlador.registrar_clique(ANUNCIO_CAMPANHA_1)
            return "aceito"
        except CampanhaInelegivel:
            return "recusado"

    with ThreadPoolExecutor(max_workers=16) as executor:
        resultados = list(executor.map(clicar, range(200)))

    assert resultados.count("aceito") == 5
    assert resultados.count("recusado") == 195
    assert campanha.saldo_restante == Decimal("0.00")
    assert campanha.status == StatusCampanha.ESGOTADA
    assert anuncio.obter_estatisticas().cliques == 5
