"""F3: POST /perguntas/{id}/respostas (RF03, US02)."""

from uuid import uuid4

from subequipe1_factory_method.criadores import CriadorDeResposta
from subequipe1_factory_method.produtos import Pergunta, Resposta
from subequipe1_factory_method.repositorio import RepositorioConteudo

CORPO = "Um padrão em que a subclasse decide qual objeto criar."


def test_responder_pergunta_existente_retorna_201(client, pergunta_id):
    resposta = client.post(f"/perguntas/{pergunta_id}/respostas", json={"corpo": CORPO})

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["corpo"] == CORPO
    assert corpo["pergunta_id"] == pergunta_id
    assert corpo["aceita"] is False
    assert "id" in corpo and "data_criacao" in corpo


def test_responder_pergunta_inexistente_retorna_404(client, repositorios):
    resposta = client.post(f"/perguntas/{uuid4()}/respostas", json={"corpo": CORPO})

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Pergunta não encontrada"}
    assert repositorios.respostas._itens == {}


def test_resposta_aparece_no_get_da_pergunta(client, pergunta_id):
    criada = client.post(f"/perguntas/{pergunta_id}/respostas", json={"corpo": CORPO}).json()

    pergunta = client.get(f"/perguntas/{pergunta_id}")

    assert pergunta.status_code == 200
    assert pergunta.json()["respostas"] == [criada]


def test_resposta_e_salva_no_repositorio_via_publicar(client, repositorios, pergunta_id):
    criada = client.post(f"/perguntas/{pergunta_id}/respostas", json={"corpo": CORPO}).json()

    salvas = list(repositorios.respostas._itens.values())
    assert len(salvas) == 1
    assert isinstance(salvas[0], Resposta)
    assert str(salvas[0].id) == criada["id"]


def test_corpo_vazio_retorna_422(client, pergunta_id):
    resposta = client.post(f"/perguntas/{pergunta_id}/respostas", json={"corpo": ""})

    assert resposta.status_code == 422


def test_criador_de_resposta_publica_resposta_ligada_a_pergunta():
    repositorio = RepositorioConteudo()
    pergunta = Pergunta(corpo="corpo", titulo="titulo")

    resposta = CriadorDeResposta(repositorio).publicar({"corpo": CORPO, "pergunta": pergunta})

    assert isinstance(resposta, Resposta)
    assert resposta.aceita is False
    assert resposta.pergunta_id == pergunta.id
    assert pergunta.respostas == [resposta]
    assert repositorio.buscar(resposta.id) is resposta
