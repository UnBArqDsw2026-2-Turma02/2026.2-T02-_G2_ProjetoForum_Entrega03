import pytest
from fastapi.testclient import TestClient

from subequipe1_factory_method.main import app
from subequipe1_factory_method.repositorio import RepositorioConteudo


@pytest.fixture(autouse=True)
def singleton_vazio():
    # Cada teste começa com um Singleton novo e vazio, então um teste não enxerga dados de outro
    RepositorioConteudo._resetar()
    yield
    RepositorioConteudo._resetar()


@pytest.fixture
def repositorio() -> RepositorioConteudo:
    return RepositorioConteudo.instancia()


@pytest.fixture
def client():
    # Sem dependency_overrides: as requisições usam o Singleton de verdade
    with TestClient(app) as cliente:
        yield cliente


@pytest.fixture
def pergunta_id(client: TestClient) -> str:
    resposta = client.post("/perguntas", json={"titulo": "O que é Factory Method?", "corpo": "Alguém explica?"})
    assert resposta.status_code == 201
    return resposta.json()["id"]
