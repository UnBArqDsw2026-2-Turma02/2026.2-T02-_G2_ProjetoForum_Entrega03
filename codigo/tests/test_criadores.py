"""F1: produtos e criadores (RF04, RNF01, issue #6)."""

from subequipe1_factory_method.criadores import CriadorDePergunta, CriadorDeResposta
from subequipe1_factory_method.produtos import Conteudo, Pergunta, Resposta
from subequipe1_factory_method.repositorio import RepositorioConteudo


def test_criador_de_pergunta_publica_pergunta_e_salva_no_repositorio():
    repositorio = RepositorioConteudo()
    dados = {"titulo": "O que é Factory Method?", "corpo": "Alguém explica?", "autor": "artur", "tags": ["gof", "criacional"]}

    pergunta = CriadorDePergunta(repositorio).publicar(dados)

    assert isinstance(pergunta, Pergunta) and isinstance(pergunta, Conteudo)
    assert (pergunta.autor, pergunta.tags, pergunta.status) == ("artur", ["gof", "criacional"], "ABERTA")
    assert pergunta.data_criacao is not None
    assert repositorio.buscar(pergunta.id) is pergunta


def test_criador_de_pergunta_aceita_pergunta_sem_tags():
    pergunta = CriadorDePergunta(RepositorioConteudo()).publicar({"titulo": "t", "corpo": "c", "autor": "artur"})

    assert pergunta.tags == []


def test_criador_de_resposta_publica_resposta_e_salva_no_repositorio():
    repositorio = RepositorioConteudo()
    pergunta = Pergunta(corpo="c", titulo="t", autor="caio")

    resposta = CriadorDeResposta(repositorio).publicar({"corpo": "r", "autor": "artur", "pergunta": pergunta})

    assert isinstance(resposta, Resposta) and isinstance(resposta, Conteudo)
    assert (resposta.autor, resposta.pergunta_id, resposta.aceita) == ("artur", pergunta.id, False)
    assert repositorio.buscar(resposta.id) is resposta


def test_post_perguntas_retorna_autor_e_tags(client):
    r = client.post("/perguntas", json={"titulo": "t", "corpo": "c", "autor": "artur", "tags": ["gof"]})

    assert r.status_code == 201
    assert r.json()["autor"] == "artur" and r.json()["tags"] == ["gof"]


def test_pergunta_sem_autor_retorna_422(client):
    assert client.post("/perguntas", json={"titulo": "t", "corpo": "c"}).status_code == 422
