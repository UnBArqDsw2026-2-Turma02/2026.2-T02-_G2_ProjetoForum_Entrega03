"""F3: POST /perguntas/{id}/respostas (RF03, US02)."""

from uuid import UUID, uuid4

from subequipe1_factory_method.criadores import CriadorDeResposta
from subequipe1_factory_method.produtos import Pergunta, Resposta

CORPO = "Um padrão em que a subclasse decide qual objeto criar."


def test_responder_pergunta_existente_retorna_201(client, pergunta_id):
    resposta = client.post(f"/perguntas/{pergunta_id}/respostas", json={"corpo": CORPO})

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["corpo"] == CORPO
    assert corpo["pergunta_id"] == pergunta_id
    assert corpo["aceita"] is False
    assert "id" in corpo and "data_criacao" in corpo


def test_responder_pergunta_inexistente_retorna_404(client, repositorio):
    resposta = client.post(f"/perguntas/{uuid4()}/respostas", json={"corpo": CORPO})

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Pergunta não encontrada"}
    assert repositorio._conteudos == {}


def test_responder_usando_id_de_resposta_retorna_404(client, repositorio, pergunta_id):
    criada = client.post(f"/perguntas/{pergunta_id}/respostas", json={"corpo": CORPO}).json()

    resposta = client.post(f"/perguntas/{criada['id']}/respostas", json={"corpo": CORPO})

    assert resposta.status_code == 404
    assert len(repositorio._conteudos) == 2


def test_resposta_aparece_no_get_da_pergunta(client, pergunta_id):
    criada = client.post(f"/perguntas/{pergunta_id}/respostas", json={"corpo": CORPO}).json()

    pergunta = client.get(f"/perguntas/{pergunta_id}")

    assert pergunta.status_code == 200
    assert pergunta.json()["respostas"] == [criada]


def test_resposta_e_salva_no_repositorio_via_publicar(client, repositorio, pergunta_id):
    criada = client.post(f"/perguntas/{pergunta_id}/respostas", json={"corpo": CORPO}).json()

    salva = repositorio.buscar_por_id(UUID(criada["id"]))
    assert isinstance(salva, Resposta)
    assert str(salva.pergunta_id) == pergunta_id


def test_corpo_vazio_retorna_422(client, pergunta_id):
    resposta = client.post(f"/perguntas/{pergunta_id}/respostas", json={"corpo": ""})

    assert resposta.status_code == 422


def test_criador_de_resposta_publica_resposta_ligada_a_pergunta(repositorio):
    pergunta = Pergunta(corpo="corpo", titulo="titulo")

    resposta = CriadorDeResposta(repositorio).publicar({"corpo": CORPO, "pergunta": pergunta})

    assert isinstance(resposta, Resposta)
    assert resposta.aceita is False
    assert resposta.pergunta_id == pergunta.id
    assert pergunta.respostas == [resposta]
    assert repositorio.buscar_por_id(resposta.id) is resposta
