"""Caixa-branca: um teste por caminho básico, contado pela complexidade ciclomática.

V(G) = decisões + 1 (McCabe), medido com radon:
- criar_conteudo de cada criador concreto: V(G) = 1 (nenhum if, RNF01), 1 teste cada
- obter_pergunta: V(G) = 2 (if pergunta is None), 2 testes
- comentar_pergunta: V(G) = 1, 1 teste; resposta e comentário têm a mesma saída no POST,
  então o teste confere em qual lista da pergunta o conteúdo caiu
- publicar() e construtores: V(G) = 1, executados pelos testes acima
- rotas de pergunta e de resposta: V(G) = 1, executadas na caixa-preta e em test_respostas.py
"""

from uuid import uuid4

import pytest
from fastapi import HTTPException

from subequipe1_factory_method.criadores import CriadorDeComentario, CriadorDePergunta, CriadorDeResposta
from subequipe1_factory_method.dependencias import obter_pergunta
from subequipe1_factory_method.produtos import Comentario, Pergunta, Resposta
from subequipe1_factory_method.repositorio import RepositorioConteudo


@pytest.fixture
def pergunta() -> Pergunta:
    return Pergunta(corpo="corpo", titulo="titulo", autor="Maria")


def test_criador_de_pergunta():
    repositorio = RepositorioConteudo()

    criada = CriadorDePergunta(repositorio).publicar({"titulo": "titulo", "corpo": "corpo", "autor": "Maria"})

    assert isinstance(criada, Pergunta)
    assert (criada.titulo, criada.corpo, criada.autor) == ("titulo", "corpo", "Maria")
    assert repositorio.buscar(criada.id) is criada


def test_criador_de_resposta(pergunta):
    repositorio = RepositorioConteudo()

    resposta = CriadorDeResposta(repositorio).publicar({"corpo": "resposta", "autor": "João", "pergunta": pergunta})

    assert isinstance(resposta, Resposta)
    assert (resposta.corpo, resposta.autor, resposta.pergunta_id) == ("resposta", "João", pergunta.id)
    assert pergunta.respostas == [resposta]
    assert repositorio.buscar(resposta.id) is resposta


def test_criador_de_comentario(pergunta):
    repositorio = RepositorioConteudo()

    comentario = CriadorDeComentario(repositorio).publicar({"corpo": "comentário", "autor": "Ana", "pergunta": pergunta})

    assert isinstance(comentario, Comentario)
    assert (comentario.corpo, comentario.autor, comentario.pergunta_id) == ("comentário", "Ana", pergunta.id)
    assert pergunta.comentarios == [comentario]
    assert repositorio.buscar(comentario.id) is comentario


def test_comentar_pergunta_usa_criador_de_comentario(client, pergunta_id):
    criado = client.post(f"/perguntas/{pergunta_id}/comentarios", json={"corpo": "comentário", "autor": "Ana"}).json()

    pergunta = client.get(f"/perguntas/{pergunta_id}").json()

    assert pergunta["comentarios"] == [criado]
    assert pergunta["respostas"] == []


def test_obter_pergunta_caminho_encontrada(pergunta):
    repositorio = RepositorioConteudo()
    repositorio.salvar(pergunta)

    assert obter_pergunta(pergunta.id, repositorio) is pergunta


def test_obter_pergunta_caminho_nao_encontrada():
    with pytest.raises(HTTPException) as erro:
        obter_pergunta(uuid4(), RepositorioConteudo())

    assert erro.value.status_code == 404
