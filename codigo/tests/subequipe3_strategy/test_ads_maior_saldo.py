from decimal import Decimal
from itertools import permutations
from uuid import UUID

import pytest

from subequipe3_strategy.ads.model.campanha import StatusCampanha, Tag
from subequipe3_strategy.ads.model.contexto import Pergunta
from subequipe3_strategy.ads.model.maior_saldo_strategy import EstrategiaMaiorSaldoNaTag
from subequipe3_strategy.ads.model.strategies import EstrategiaSelecaoAnuncio


def pergunta(*nomes):
    return Pergunta(UUID(int=500), "DÃºvida", [Tag(nome) for nome in nomes])


def test_contrato_e_nome():
    estrategia = EstrategiaMaiorSaldoNaTag()
    assert isinstance(estrategia, EstrategiaSelecaoAnuncio)
    assert estrategia.obter_nome() == "maior_saldo"


def test_maior_saldo_vence_mesmo_com_cpc_e_tags_menores(criar_campanha):
    pobre = criar_campanha(
        id=UUID(int=1),
        tags_alvo=[Tag("python"), Tag("fastapi"), Tag("django")],
        saldo_restante=Decimal("5"),
        custo_por_clique=Decimal("5"),
    )
    rica = criar_campanha(
        id=UUID(int=2),
        tags_alvo=[Tag("python")],
        saldo_restante=Decimal("50"),
        custo_por_clique=Decimal("1"),
    )
    for ordem in permutations([pobre, rica]):
        assert EstrategiaMaiorSaldoNaTag().selecionar_anuncio(
            pergunta("PYTHON", "fastapi"), list(ordem)
        ) is rica.anuncios[0]


def test_empate_de_saldo_menor_id_da_campanha(criar_campanha):
    a = criar_campanha(id=UUID(int=10), saldo_restante=Decimal("20"))
    b = criar_campanha(id=UUID(int=3), saldo_restante=Decimal("20"))
    for ordem in permutations([a, b]):
        assert EstrategiaMaiorSaldoNaTag().selecionar_anuncio(
            pergunta("python"), list(ordem)
        ) is b.anuncios[0]


def test_empate_menor_id_de_anuncio_independe_da_ordem(criar_campanha, criar_anuncio):
    menor = criar_anuncio(id=UUID(int=10))
    maior = criar_anuncio(id=UUID(int=20))
    for ordem in permutations([maior, menor]):
        campanha = criar_campanha(saldo_restante=Decimal("30"), anuncios=list(ordem))
        assert EstrategiaMaiorSaldoNaTag().selecionar_anuncio(
            pergunta("python"), [campanha]
        ) is menor


def test_match_unico_insensivel_a_caixa(criar_campanha):
    campanha = criar_campanha()
    assert (
        EstrategiaMaiorSaldoNaTag().selecionar_anuncio(pergunta("PYTHON"), [campanha])
        is campanha.anuncios[0]
    )


@pytest.mark.parametrize("nomes", [(), ("java",)])
def test_sem_match_retorna_none(criar_campanha, nomes):
    assert (
        EstrategiaMaiorSaldoNaTag().selecionar_anuncio(pergunta(*nomes), [criar_campanha()])
        is None
    )


def test_sem_campanhas_retorna_none():
    assert EstrategiaMaiorSaldoNaTag().selecionar_anuncio(pergunta("python"), []) is None


@pytest.mark.parametrize("status", [s for s in StatusCampanha if s != StatusCampanha.ATIVA])
def test_campanhas_inativas_ignoradas(criar_campanha, status):
    assert (
        EstrategiaMaiorSaldoNaTag().selecionar_anuncio(
            pergunta("python"), [criar_campanha(status=status)]
        )
        is None
    )


@pytest.mark.parametrize(
    "saldo,cpc",
    [
        (Decimal("0"), Decimal("1")),
        (Decimal("0.99"), Decimal("1")),
        (Decimal("10"), Decimal("0")),
    ],
)
def test_saldo_ou_cpc_inelegivel(criar_campanha, saldo, cpc):
    campanha = criar_campanha(saldo_restante=saldo, custo_por_clique=cpc)
    assert (
        EstrategiaMaiorSaldoNaTag().selecionar_anuncio(pergunta("python"), [campanha])
        is None
    )


def test_selecao_nao_altera_saldo_status_metricas_ou_ordem(criar_campanha):
    campanhas = [
        criar_campanha(id=UUID(int=2), saldo_restante=Decimal("5")),
        criar_campanha(id=UUID(int=1), saldo_restante=Decimal("40")),
    ]
    antes = [
        (c.id, c.saldo_restante, c.status, c.anuncios[0].obter_estatisticas().cliques)
        for c in campanhas
    ]
    selecionado = EstrategiaMaiorSaldoNaTag().selecionar_anuncio(
        pergunta("python"), campanhas
    )
    depois = [
        (c.id, c.saldo_restante, c.status, c.anuncios[0].obter_estatisticas().cliques)
        for c in campanhas
    ]
    assert antes == depois
    assert selecionado is campanhas[1].anuncios[0]
    assert selecionado.obter_estatisticas().visualizacoes == 0
