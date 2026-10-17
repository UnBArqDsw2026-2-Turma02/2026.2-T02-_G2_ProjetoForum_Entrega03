from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from uuid import UUID

import pytest

from app.ads.model.anuncio import AnuncioGenerico
from app.ads.model.campanha import StatusCampanha
from app.ads.model.contexto import Pergunta
from app.ads.model.repositorio import (
    AnuncioNaoEncontrado, CampanhaInelegivel, RepositorioAds,
    RepositorioCampanhas, RepositorioMetricas, RepositorioPerguntas,
)


def test_repositorio_atende_as_tres_portas():
    repo = RepositorioAds.seed()
    assert isinstance(repo, RepositorioPerguntas)
    assert isinstance(repo, RepositorioCampanhas)
    assert isinstance(repo, RepositorioMetricas)
    assert repo.obter(UUID(int=101)).obter_tags()
    assert repo.obter(UUID(int=999)) is None
    assert len(repo.listar_ativas()) == 2
    assert repo.obter_anuncio(UUID(int=999)) is None


def test_seed_nao_compartilha_estado_entre_instancias():
    primeiro, segundo = RepositorioAds.seed(), RepositorioAds.seed()
    primeiro.registrar_clique_atomico(UUID(int=11))
    assert primeiro.obter_anuncio(UUID(int=11)).obter_estatisticas().cliques == 1
    assert segundo.obter_anuncio(UUID(int=11)).obter_estatisticas().cliques == 0
    lista = primeiro.listar_ativas()
    lista.clear()
    assert len(primeiro.listar_ativas()) == 2


def test_visualizacao_usa_mesma_estatistica_sem_cobranca(criar_campanha):
    campanha = criar_campanha()
    anuncio = campanha.anuncios[0]
    repo = RepositorioAds(campanhas=[campanha])
    repo.registrar_visualizacao(anuncio.id)
    assert repo.obter_anuncio(anuncio.id) is anuncio
    assert anuncio.obter_estatisticas().visualizacoes == 1
    assert anuncio.obter_estatisticas().cliques == 0
    assert campanha.saldo_restante == Decimal("10")


def test_clique_generico_nao_debita_campanhas():
    repo = RepositorioAds.seed()
    saldos = [campanha.saldo_restante for campanha in repo.listar_ativas()]
    repo.registrar_clique_atomico(repo.anuncio_padrao.id)
    assert repo.anuncio_padrao.obter_estatisticas().cliques == 1
    assert [campanha.saldo_restante for campanha in repo.listar_ativas()] == saldos


@pytest.mark.parametrize("operacao", ["registrar_visualizacao", "registrar_clique_atomico"])
def test_anuncio_inexistente_nao_altera_estado(operacao):
    repo = RepositorioAds.seed()
    with pytest.raises(AnuncioNaoEncontrado):
        getattr(repo, operacao)(UUID(int=999))
    assert all(a.anuncios[0].obter_estatisticas().cliques == 0 for a in repo.listar_ativas())


def test_clique_revalida_status_e_saldo(criar_campanha):
    campanha = criar_campanha()
    anuncio = campanha.anuncios[0]
    repo = RepositorioAds(campanhas=[campanha])
    campanha.status = StatusCampanha.PAUSADA
    with pytest.raises(CampanhaInelegivel):
        repo.registrar_clique_atomico(anuncio.id)
    campanha.status = StatusCampanha.ATIVA
    campanha.saldo_restante = Decimal("0.50")
    with pytest.raises(CampanhaInelegivel):
        repo.registrar_clique_atomico(anuncio.id)
    assert campanha.saldo_restante == Decimal("0.50")
    assert anuncio.obter_estatisticas().cliques == 0


def test_falha_na_metrica_reverte_debito_e_status(criar_campanha, monkeypatch):
    campanha = criar_campanha(saldo_restante=Decimal("1"))
    anuncio = campanha.anuncios[0]
    stats = anuncio.obter_estatisticas()
    repo = RepositorioAds(campanhas=[campanha])

    def falhar_apos_incremento():
        stats.cliques += 1
        raise RuntimeError("Falha simulada na métrica")

    with monkeypatch.context() as patch:
        patch.setattr(stats, "incrementar_clique", falhar_apos_incremento)
        with pytest.raises(RuntimeError):
            repo.registrar_clique_atomico(anuncio.id)
    assert stats.cliques == 0
    assert campanha.saldo_restante == Decimal("1")
    assert campanha.status == StatusCampanha.ATIVA
    repo.registrar_clique_atomico(anuncio.id)
    assert stats.cliques == 1
    assert campanha.saldo_restante == 0


def test_cliques_concorrentes_nao_cobram_acima_do_saldo(criar_campanha):
    campanha = criar_campanha(saldo_restante=Decimal("1.00"), custo_por_clique=Decimal("0.10"))
    anuncio = campanha.anuncios[0]
    repo = RepositorioAds(campanhas=[campanha])

    def tentar_clique(_):
        try:
            repo.registrar_clique_atomico(anuncio.id)
            return True
        except CampanhaInelegivel:
            return False

    with ThreadPoolExecutor(max_workers=16) as executor:
        resultados = list(executor.map(tentar_clique, range(200)))
    assert sum(resultados) == 10
    assert anuncio.obter_estatisticas().cliques == 10
    assert campanha.saldo_restante == Decimal("0.00")
    assert campanha.status == StatusCampanha.ESGOTADA


def test_eventos_concorrentes_genericos_nao_perdem_incrementos():
    repo = RepositorioAds.seed()
    anuncio = repo.anuncio_padrao
    with ThreadPoolExecutor(max_workers=16) as executor:
        list(executor.map(lambda _: repo.registrar_clique_atomico(anuncio.id), range(200)))
        list(executor.map(lambda _: repo.registrar_visualizacao(anuncio.id), range(200)))
    stats = anuncio.obter_estatisticas()
    assert (stats.cliques, stats.visualizacoes) == (200, 200)


def test_ids_duplicados_sao_rejeitados(criar_campanha):
    campanha = criar_campanha()
    with pytest.raises(ValueError):
        RepositorioAds(campanhas=[campanha, campanha])
    outra = criar_campanha(id=UUID(int=2), anuncios=campanha.anuncios)
    with pytest.raises(ValueError):
        RepositorioAds(campanhas=[campanha, outra])
    pergunta = Pergunta(UUID(int=1), "Título")
    with pytest.raises(ValueError):
        RepositorioAds(perguntas=[pergunta, pergunta])
    generico = AnuncioGenerico(campanha.anuncios[0].id, "Casa", "/img", "/")
    with pytest.raises(ValueError):
        RepositorioAds(campanhas=[campanha], anuncio_padrao=generico)


def test_generico_deve_estar_configurado_e_ser_do_tipo_correto(criar_anuncio):
    with pytest.raises(ValueError):
        RepositorioAds().anuncio_padrao
    with pytest.raises(TypeError):
        RepositorioAds(anuncio_padrao=criar_anuncio())
