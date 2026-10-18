from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient

from subequipe1_factory_method.dependencias import (
    get_repositorio_perguntas,
    get_repositorio_respostas,
)
from subequipe1_factory_method.main import app
from subequipe1_factory_method.repositorio import RepositorioConteudo


@dataclass
class Repositorios:
    perguntas: RepositorioConteudo
    respostas: RepositorioConteudo


@pytest.fixture
def repositorios() -> Repositorios:
    return Repositorios(perguntas=RepositorioConteudo(), respostas=RepositorioConteudo())


@pytest.fixture
def client(repositorios: Repositorios):
    # Cada teste usa repositórios novos, então um teste não enxerga dados de outro
    app.dependency_overrides[get_repositorio_perguntas] = lambda: repositorios.perguntas
    app.dependency_overrides[get_repositorio_respostas] = lambda: repositorios.respostas
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()


@pytest.fixture
def pergunta_id(client: TestClient) -> str:
    resposta = client.post("/perguntas", json={"titulo": "O que é Factory Method?", "corpo": "Alguém explica?", "autor": "artur", "tags": ["gof"]})
    assert resposta.status_code == 201
    return resposta.json()["id"]
