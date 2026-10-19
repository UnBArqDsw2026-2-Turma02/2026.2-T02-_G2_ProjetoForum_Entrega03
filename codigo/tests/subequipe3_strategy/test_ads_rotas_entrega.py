from decimal import Decimal
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from subequipe3_strategy.ads.model.anuncio import AnuncioGenerico
from subequipe3_strategy.ads.model.campanha import Tag
from subequipe3_strategy.ads.model.contexto import Pergunta
from subequipe3_strategy.ads.model.repositorio import RepositorioAds

from subequipe3_strategy.ads.service.dependencias import (
    ConfiguracaoAds,
    get_configuracao_ads,
    get_estrategia_fallback,
    get_repositorio_ads,
)
from subequipe3_strategy.main import app

PERGUNTA_COM_MATCH = UUID(int=101)
PERGUNTA_SEM_MATCH = UUID(int=102)
ANUNCIO_CONTEXTUAL = UUID(int=11)
ANUNCIO_PADRAO = UUID(int=30)


class FallbackDeTeste:
    """Dublê da estratégia genérica (#26) até sua integração."""

    def __init__(self, anuncio):
        self.anuncio = anuncio

    def obter_nome(self):
        return "generico"

    def selecionar_anuncio(self, pergunta, campanhas):
        return self.anuncio


@pytest.fixture
def repositorio():
    return RepositorioAds.seed()


@pytest.fixture
def configurar_app(repositorio):
    def configurar(politica="match_exato", com_fallback=True):
        app.dependency_overrides[get_repositorio_ads] = lambda: repositorio
        app.dependency_overrides[get_configuracao_ads] = lambda: ConfiguracaoAds(politica)
        if com_fallback:
            fallback = FallbackDeTeste(repositorio.anuncio_padrao)
            app.dependency_overrides[get_estrategia_fallback] = lambda: fallback
        return TestClient(app)

    yield configurar
    app.dependency_overrides.clear()


@pytest.fixture
def cliente_ads(configurar_app):
    return configurar_app()


def metricas(repositorio, anuncio_id):
    estatisticas = repositorio.obter_anuncio(anuncio_id).obter_estatisticas()
    return estatisticas.visualizacoes, estatisticas.cliques


def campanha_do_anuncio(repositorio, anuncio_id):
    anuncio = repositorio.obter_anuncio(anuncio_id)
    return next(c for c in repositorio.listar_ativas() if anuncio in c.anuncios)


def test_pagina_com_anuncio_contextual(cliente_ads, repositorio):
    resposta = cliente_ads.get(f"/perguntas/{PERGUNTA_COM_MATCH}/pagina")
    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/html")
    assert "Como aprender Python?" in resposta.text
    assert 'alt="Curso de Python"' in resposta.text
    assert "Anúncio contextual · política: match_exato" in resposta.text
    assert metricas(repositorio, ANUNCIO_CONTEXTUAL) == (1, 0)


def test_pagina_com_fallback_generico(cliente_ads, repositorio):
    resposta = cliente_ads.get(f"/perguntas/{PERGUNTA_SEM_MATCH}/pagina")
    assert resposta.status_code == 200
    assert "Anúncio genérico · política: generico" in resposta.text
    assert "Participe da comunidade." in resposta.text
    assert metricas(repositorio, ANUNCIO_PADRAO) == (1, 0)
    assert metricas(repositorio, ANUNCIO_CONTEXTUAL) == (0, 0)


def test_uma_visualizacao_por_exibicao(cliente_ads, repositorio):
    for _ in range(3):
        cliente_ads.get(f"/perguntas/{PERGUNTA_COM_MATCH}/pagina")
    assert metricas(repositorio, ANUNCIO_CONTEXTUAL) == (3, 0)


def test_pergunta_inexistente_responde_404_sem_registrar(cliente_ads, repositorio):
    resposta = cliente_ads.get(f"/perguntas/{UUID(int=999)}/pagina")
    assert resposta.status_code == 404
    assert metricas(repositorio, ANUNCIO_CONTEXTUAL) == (0, 0)
    assert metricas(repositorio, ANUNCIO_PADRAO) == (0, 0)


def test_identificador_invalido_responde_422(cliente_ads):
    assert cliente_ads.get("/perguntas/nao-e-uuid/pagina").status_code == 422


def test_sem_fallback_funciona_quando_ha_match(configurar_app): # Antigo test_sem_fallback_integrado_responde_503
    cliente = configurar_app(com_fallback=False)

    resposta = cliente.get(
        f"/perguntas/{PERGUNTA_COM_MATCH}/pagina"
    )

    assert resposta.status_code == 200
    assert "Curso de Python" in resposta.text


def test_politica_nao_registrada_responde_503(configurar_app):
    resposta = configurar_app(politica="maior_lance").get(f"/perguntas/{PERGUNTA_COM_MATCH}/pagina")
    assert resposta.status_code == 503
    assert "maior_lance" in resposta.json()["detail"]


def test_clique_contextual_debita_e_conta(cliente_ads, repositorio):
    campanha = campanha_do_anuncio(repositorio, ANUNCIO_CONTEXTUAL)
    resposta = cliente_ads.post(f"/anuncios/{ANUNCIO_CONTEXTUAL}/cliques")
    assert resposta.status_code == 204
    assert resposta.content == b""
    assert metricas(repositorio, ANUNCIO_CONTEXTUAL) == (0, 1)
    assert campanha.saldo_restante == Decimal("4.00")


def test_clique_generico_conta_sem_debitar(cliente_ads, repositorio):
    saldos = [c.saldo_restante for c in repositorio.listar_ativas()]
    assert cliente_ads.post(f"/anuncios/{ANUNCIO_PADRAO}/cliques").status_code == 204
    assert metricas(repositorio, ANUNCIO_PADRAO) == (0, 1)
    assert [c.saldo_restante for c in repositorio.listar_ativas()] == saldos


def test_clique_em_anuncio_inexistente_responde_404(cliente_ads):
    assert cliente_ads.post(f"/anuncios/{UUID(int=999)}/cliques").status_code == 404


def test_clique_sem_saldo_responde_409_sem_alteracao_parcial(cliente_ads, repositorio):
    campanha = campanha_do_anuncio(repositorio, ANUNCIO_CONTEXTUAL)
    for _ in range(5):
        assert cliente_ads.post(f"/anuncios/{ANUNCIO_CONTEXTUAL}/cliques").status_code == 204
    resposta = cliente_ads.post(f"/anuncios/{ANUNCIO_CONTEXTUAL}/cliques")
    assert resposta.status_code == 409
    assert metricas(repositorio, ANUNCIO_CONTEXTUAL) == (0, 5)
    assert campanha.saldo_restante == Decimal("0.00")


def test_rotas_documentadas_no_openapi(cliente_ads):
    caminhos = cliente_ads.get("/openapi.json").json()["paths"]
    pagina = caminhos["/perguntas/{pergunta_id}/pagina"]["get"]
    clique = caminhos["/anuncios/{anuncio_id}/cliques"]["post"]
    assert "text/html" in pagina["responses"]["200"]["content"]
    assert {"404", "503"} <= set(pagina["responses"])
    assert {"204", "404", "409", "503"} <= set(clique["responses"])
    assert pagina["tags"] == clique["tags"] == ["Anúncios"]


def test_rotas_de_conteudo_continuam_disponiveis(cliente_ads):
    resposta = cliente_ads.post("/perguntas", json={"titulo": "Factory?", "corpo": "Dúvida", "autor": "Maria"})
    assert resposta.status_code == 201


def test_fallback_real_usa_repositorio_injetado(): # Teste que cria repositório isolado com anúncio id=900 e fallback real
    anuncio_id = UUID(int=900)
    pergunta_id = UUID(int=902)

    anuncio_padrao = AnuncioGenerico(
        anuncio_id,
        "Anúncio de teste",
        "/static/teste.png",
        "/teste",
        mensagem_padrao="Anúncio injetado.",
    )

    pergunta = Pergunta(
        pergunta_id,
        "Pergunta sem campanha compatível",
        [Tag("sem-match")],
    )

    repositorio_teste = RepositorioAds(
        campanhas=[],
        perguntas=[pergunta],
        anuncio_padrao=anuncio_padrao,
    )

    app.dependency_overrides[get_repositorio_ads] = (
        lambda: repositorio_teste
    )
    app.dependency_overrides[get_configuracao_ads] = (
        lambda: ConfiguracaoAds("match_exato")
    )
    app.dependency_overrides.pop(get_estrategia_fallback, None)

    try:
        with TestClient(app) as cliente:
            resposta = cliente.get(
                f"/perguntas/{pergunta_id}/pagina"
            )

        assert resposta.status_code == 200
        assert "Anúncio injetado." in resposta.text

        estatisticas = repositorio_teste.obter_anuncio(
            anuncio_id
        ).obter_estatisticas()

        assert estatisticas.visualizacoes == 1
        assert estatisticas.cliques == 0
    finally:
        app.dependency_overrides.clear()
