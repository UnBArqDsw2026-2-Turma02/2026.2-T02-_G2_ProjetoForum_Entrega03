"""Caixa-preta: análise de valor limite nos campos de texto da API.

Todo campo tem min_length=1, então a borda fica entre 0 e 1 caractere:
1 caractere é o menor valor aceito (201) e 0 fica logo abaixo dela (422).
"""

import pytest

# Todos os campos com 1 caractere (exatamente no limite), um valor diferente por campo
NO_LIMITE = {
    "/perguntas": {"titulo": "t", "corpo": "c", "autor": "a"},
    "/perguntas/{id}/respostas": {"corpo": "c", "autor": "a"},
}

# Cada caso zera um único campo: logo abaixo do limite
ABAIXO_DO_LIMITE = [
    ("/perguntas", "titulo"),
    ("/perguntas", "corpo"),
    ("/perguntas", "autor"),
    ("/perguntas/{id}/respostas", "corpo"),
    ("/perguntas/{id}/respostas", "autor"),
]


@pytest.mark.parametrize("rota", NO_LIMITE)
def test_no_limite_retorna_201(client, pergunta_id, rota):
    resposta = client.post(rota.format(id=pergunta_id), json=NO_LIMITE[rota])

    assert resposta.status_code == 201
    for campo, valor in NO_LIMITE[rota].items():
        assert resposta.json()[campo] == valor


@pytest.mark.parametrize("rota, campo", ABAIXO_DO_LIMITE)
def test_abaixo_do_limite_retorna_422(client, pergunta_id, rota, campo):
    dados = {**NO_LIMITE[rota], campo: ""}

    resposta = client.post(rota.format(id=pergunta_id), json=dados)

    assert resposta.status_code == 422
