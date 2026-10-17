from decimal import Decimal
from itertools import permutations
from uuid import UUID

import pytest

from app.ads.model.campanha import StatusCampanha, Tag
from app.ads.model.contexto import Pergunta
from app.ads.model.match_exato import EstrategiaMatchExatoDeTag
from app.ads.model.strategies import EstrategiaSelecaoAnuncio


def pergunta(*nomes):
    return Pergunta(UUID(int=500), "Dúvida", [Tag(nome) for nome in nomes])


def test_match_unico_insensivel_a_caixa(criar_campanha):
    campanha = criar_campanha()
    estrategia = EstrategiaMatchExatoDeTag()
    assert isinstance(estrategia, EstrategiaSelecaoAnuncio)
    assert estrategia.obter_nome() == "match_exato"
    assert estrategia.selecionar_anuncio(pergunta("PYTHON"), [campanha]) is campanha.anuncios[0]


@pytest.mark.parametrize("nomes", [(), ("java",)])
def test_sem_match_retorna_none(criar_campanha, nomes):
    assert EstrategiaMatchExatoDeTag().selecionar_anuncio(pergunta(*nomes), [criar_campanha()]) is None


def test_sem_campanhas_retorna_none():
    assert EstrategiaMatchExatoDeTag().selecionar_anuncio(pergunta("python"), []) is None


def test_menor_id_vence_saldo_cpc_e_quantidade_de_tags(criar_campanha):
    menor = criar_campanha(id=UUID(int=1), saldo_restante=Decimal("1"))
    maior = criar_campanha(
        id=UUID(int=2), tags_alvo=[Tag("python"), Tag("fastapi")],
        saldo_restante=Decimal("99"), custo_por_clique=Decimal("10"),
    )
    for ordem in permutations([maior, menor]):
        assert EstrategiaMatchExatoDeTag().selecionar_anuncio(
            pergunta("python", "fastapi", "PYTHON"), list(ordem)
        ) is menor.anuncios[0]


def test_menor_id_da_campanha_prevalece_sobre_id_do_anuncio(criar_campanha, criar_anuncio):
    anuncio_da_menor = criar_anuncio(id=UUID(int=99))
    anuncio_da_maior = criar_anuncio(id=UUID(int=5))
    menor = criar_campanha(id=UUID(int=1), anuncios=[anuncio_da_menor])
    maior = criar_campanha(id=UUID(int=2), anuncios=[anuncio_da_maior])
    for ordem in permutations([maior, menor]):
        assert EstrategiaMatchExatoDeTag().selecionar_anuncio(
            pergunta("python"), list(ordem)
        ) is anuncio_da_menor


def test_menor_id_de_anuncio_independe_da_ordem(criar_campanha, criar_anuncio):
    menor = criar_anuncio(id=UUID(int=10))
    maior = criar_anuncio(id=UUID(int=20))
    for ordem in permutations([maior, menor]):
        campanha = criar_campanha(anuncios=list(ordem))
        assert EstrategiaMatchExatoDeTag().selecionar_anuncio(pergunta("python"), [campanha]) is menor


@pytest.mark.parametrize("status", [s for s in StatusCampanha if s != StatusCampanha.ATIVA])
def test_campanhas_inativas_ignoradas(criar_campanha, status):
    assert EstrategiaMatchExatoDeTag().selecionar_anuncio(
        pergunta("python"), [criar_campanha(status=status)]
    ) is None


@pytest.mark.parametrize("saldo,cpc", [
    (Decimal("0"), Decimal("1")), (Decimal("0.99"), Decimal("1")),
    (Decimal("10"), Decimal("0")),
])
def test_saldo_ou_cpc_inelegivel(criar_campanha, saldo, cpc):
    campanha = criar_campanha(saldo_restante=saldo, custo_por_clique=cpc)
    assert EstrategiaMatchExatoDeTag().selecionar_anuncio(pergunta("python"), [campanha]) is None


def test_saldo_exatamente_cpc_e_elegivel(criar_campanha):
    campanha = criar_campanha(saldo_restante=Decimal("1"), custo_por_clique=Decimal("1"))
    assert EstrategiaMatchExatoDeTag().selecionar_anuncio(pergunta("python"), [campanha]) is campanha.anuncios[0]


def test_inventario_sem_anuncio_nao_gera_candidato(criar_campanha):
    campanha = criar_campanha()
    campanha.anuncios.clear()
    assert EstrategiaMatchExatoDeTag().selecionar_anuncio(pergunta("python"), [campanha]) is None


def test_selecao_nao_altera_saldo_status_metricas_ou_ordem(criar_campanha):
    campanhas = [criar_campanha(id=UUID(int=2)), criar_campanha(id=UUID(int=1))]
    antes = [(c.id, c.saldo_restante, c.status, c.anuncios[0].obter_estatisticas().cliques) for c in campanhas]
    selecionado = EstrategiaMatchExatoDeTag().selecionar_anuncio(pergunta("python"), campanhas)
    depois = [(c.id, c.saldo_restante, c.status, c.anuncios[0].obter_estatisticas().cliques) for c in campanhas]
    assert antes == depois
    assert selecionado.obter_estatisticas().visualizacoes == 0
