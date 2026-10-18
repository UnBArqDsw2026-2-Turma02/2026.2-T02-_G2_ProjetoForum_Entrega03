"""F2: POST /perguntas e GET /perguntas/{id} (RF01, RF02, US01, US03)."""

from uuid import UUID, uuid4

from subequipe1_factory_method.produtos import Pergunta

PERGUNTA = {
    "titulo": "Como usar Factory Method?",
    "corpo": "Estou estudando padrões criacionais.",
    "tags": ["python", "design-patterns"],
}


def test_publicar_pergunta_retorna_201_com_id(client, repositorio):
    resposta = client.post("/perguntas", json=PERGUNTA)

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["titulo"] == PERGUNTA["titulo"]
    assert corpo["tags"] == PERGUNTA["tags"]
    assert corpo["respostas"] == []
    assert isinstance(repositorio.buscar_por_id(UUID(corpo["id"])), Pergunta)


def test_publicar_pergunta_sem_tags_retorna_lista_vazia(client):
    dados = {k: v for k, v in PERGUNTA.items() if k != "tags"}

    resposta = client.post("/perguntas", json=dados)

    assert resposta.status_code == 201
    assert resposta.json()["tags"] == []


def test_publicar_pergunta_sem_titulo_retorna_422(client):
    dados = {k: v for k, v in PERGUNTA.items() if k != "titulo"}

    assert client.post("/perguntas", json=dados).status_code == 422


def test_publicar_pergunta_com_corpo_vazio_retorna_422(client):
    assert client.post("/perguntas", json={**PERGUNTA, "corpo": ""}).status_code == 422


def test_buscar_pergunta_retorna_tags_e_respostas(client):
    pergunta_id = client.post("/perguntas", json=PERGUNTA).json()["id"]
    criada = client.post(f"/perguntas/{pergunta_id}/respostas", json={"corpo": "Use subclasses."}).json()

    resposta = client.get(f"/perguntas/{pergunta_id}")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["id"] == pergunta_id
    assert corpo["tags"] == PERGUNTA["tags"]
    assert corpo["respostas"] == [criada]


def test_buscar_pergunta_inexistente_retorna_404(client):
    resposta = client.get(f"/perguntas/{uuid4()}")

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Pergunta não encontrada"}


def test_buscar_pergunta_com_id_de_resposta_retorna_404(client, pergunta_id):
    criada = client.post(f"/perguntas/{pergunta_id}/respostas", json={"corpo": "Use subclasses."}).json()

    assert client.get(f"/perguntas/{criada['id']}").status_code == 404
