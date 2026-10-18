import re
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from subequipe3_strategy.ads.model.repositorio import RepositorioAds
from subequipe3_strategy.ads.service.dependencias import (
    get_estrategia_fallback,
    get_repositorio_ads,
)
from subequipe3_strategy.main import app


class FallbackDeTeste:
    """Dublê da estratégia genérica (#26) até sua integração."""

    def __init__(self, anuncio):
        self.anuncio = anuncio

    def obter_nome(self):
        return "generico"

    def selecionar_anuncio(self, pergunta, campanhas):
        return self.anuncio


def imagens_do_seed():
    repositorio = RepositorioAds.seed()
    anuncios = [a for c in repositorio.listar_ativas() for a in c.anuncios]
    anuncios.append(repositorio.anuncio_padrao)
    return sorted({url for a in anuncios for url in (a.banner_url, getattr(a, "imagem_banner", "")) if url})


@pytest.fixture
def cliente():
    repositorio = RepositorioAds.seed()
    app.dependency_overrides[get_repositorio_ads] = lambda: repositorio
    app.dependency_overrides[get_estrategia_fallback] = lambda: FallbackDeTeste(repositorio.anuncio_padrao)
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_seed_usa_imagens_de_exemplo_locais():
    assert imagens_do_seed() == ["/static/comunidade.png", "/static/curso-python.png", "/static/forum.png"]


@pytest.mark.parametrize("url", imagens_do_seed())
def test_imagens_do_seed_sao_servidas(cliente, url):
    resposta = cliente.get(url)
    assert resposta.status_code == 200
    assert resposta.headers["content-type"] == "image/png"
    assert resposta.content.startswith(b"\x89PNG")


@pytest.mark.parametrize("pergunta_id", [UUID(int=101), UUID(int=102)])
def test_imagens_da_pagina_carregam(cliente, pergunta_id):
    pagina = cliente.get(f"/perguntas/{pergunta_id}/pagina")
    assert pagina.status_code == 200
    imagens = re.findall(r'<img src="([^"]+)"', pagina.text)
    assert imagens
    for url in imagens:
        assert cliente.get(url).status_code == 200


def test_arquivo_estatico_inexistente_responde_404(cliente):
    assert cliente.get("/static/nao-existe.png").status_code == 404
