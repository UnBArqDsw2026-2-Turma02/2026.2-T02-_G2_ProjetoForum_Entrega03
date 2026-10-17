from uuid import UUID

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from subequipe3_strategy.ads.controller.controlador_entrega import EntregaAnuncio
from subequipe3_strategy.ads.model.anuncio import AnuncioContextual, AnuncioGenerico
from subequipe3_strategy.ads.model.campanha import Tag
from subequipe3_strategy.ads.model.contexto import Pergunta
from subequipe3_strategy.ads.view.pergunta_view import PerguntaView


def criar_cliente(entrega):
    """Aplicação mínima, só com a view e a rota de clique que ela referencia."""
    app = FastAPI()
    view = PerguntaView()

    @app.get("/pagina")
    def pagina(request: Request):
        return view.renderizar(request, entrega)

    @app.post("/anuncios/{anuncio_id}/cliques", name="registrar_clique")
    def registrar_clique(anuncio_id: UUID):
        return None

    return TestClient(app)


@pytest.fixture
def contextual():
    return AnuncioContextual(
        UUID(int=11), "Curso de Python", "/static/curso.png", "https://example.org/python",
        imagem_banner="/static/banner-python.png",
    )


def test_renderiza_pergunta_tags_e_anuncio_contextual(contextual):
    pergunta = Pergunta(UUID(int=101), "Como aprender Python?", [Tag("python"), Tag("fastapi")])
    html = criar_cliente(EntregaAnuncio(pergunta, contextual, "match_exato", False)).get("/pagina")

    assert html.status_code == 200
    assert html.headers["content-type"].startswith("text/html")
    corpo = html.text
    assert "<h1>Como aprender Python?</h1>" in corpo
    assert "<li>python</li>" in corpo and "<li>fastapi</li>" in corpo
    assert 'src="/static/banner-python.png"' in corpo
    assert 'href="https://example.org/python"' in corpo
    assert "Anúncio contextual · política: match_exato" in corpo
    assert f'data-url-clique="/anuncios/{contextual.id}/cliques"' in corpo


def test_identifica_anuncio_generico():
    generico = AnuncioGenerico(
        UUID(int=30), "Fórum da comunidade", "/static/forum.png", "/",
        mensagem_padrao="Participe da comunidade.",
    )
    pergunta = Pergunta(UUID(int=102), "Sem campanha", [Tag("desconhecida")])
    corpo = criar_cliente(EntregaAnuncio(pergunta, generico, "generico", True)).get("/pagina").text
    assert "Anúncio genérico · política: generico" in corpo
    assert "<span>Participe da comunidade.</span>" in corpo


def test_escapa_dados_da_pergunta_e_do_anuncio():
    pergunta = Pergunta(
        UUID(int=103), "<script>alert(1)</script>", [Tag('"><img src=x onerror=alert(2)>')]
    )
    anuncio = AnuncioContextual(
        UUID(int=13), '<b onmouseover="x">Curso</b>', "/static/c.png", "/cursos",
    )
    corpo = criar_cliente(EntregaAnuncio(pergunta, anuncio, "match_exato", False)).get("/pagina").text
    assert "<script>alert(1)</script>" not in corpo
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in corpo
    assert "<img src=x onerror" not in corpo
    assert '<b onmouseover="x">' not in corpo
    assert 'alt="&lt;b onmouseover=&quot;x&quot;&gt;Curso&lt;/b&gt;"' in corpo


def test_rejeita_url_alterada_depois_da_construcao(contextual):
    contextual.link_destino = "javascript:alert(1)"
    pergunta = Pergunta(UUID(int=101), "Pergunta", [Tag("python")])
    with pytest.raises(ValueError):
        criar_cliente(EntregaAnuncio(pergunta, contextual, "match_exato", False)).get("/pagina")
