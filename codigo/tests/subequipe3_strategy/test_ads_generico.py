from uuid import UUID

import pytest

from subequipe3_strategy.ads import (
    AnuncioGenerico,
    EstrategiaSelecaoAnuncio,
)
from subequipe3_strategy.ads.model.generico import (
    EstrategiaAnuncioGenerico,
)
from subequipe3_strategy.ads.model.repositorio import RepositorioAds


@pytest.fixture
def repositorio():
    return RepositorioAds.seed()


@pytest.fixture
def estrategia(repositorio):
    return EstrategiaAnuncioGenerico(repositorio.anuncio_padrao)


def test_implementa_contrato_da_estrategia(estrategia):
    assert isinstance(estrategia, EstrategiaSelecaoAnuncio)
    assert estrategia.obter_nome() == "generico"


def test_retorna_anuncio_padrao_sem_campanhas(estrategia, repositorio):
    anuncio = estrategia.selecionar_anuncio(
        pergunta=None,
        campanhas=[],
    )

    assert anuncio is repositorio.anuncio_padrao


def test_preserva_id_do_anuncio_padrao(estrategia, repositorio):
    anuncio_original = repositorio.anuncio_padrao

    for _ in range(3):
        anuncio_selecionado = estrategia.selecionar_anuncio(
            pergunta=None,
            campanhas=[],
        )

        assert anuncio_selecionado.id == UUID(int=30)
        assert anuncio_selecionado.id == anuncio_original.id


def test_selecao_nao_altera_metricas_ou_saldo(estrategia, repositorio):
    anuncio = repositorio.anuncio_padrao

    metricas_antes = (
        anuncio.obter_estatisticas().visualizacoes,
        anuncio.obter_estatisticas().cliques,
    )
    saldos_antes = [
        campanha.saldo_restante
        for campanha in repositorio.listar_ativas()
    ]

    estrategia.selecionar_anuncio(
        pergunta=None,
        campanhas=repositorio.listar_ativas(),
    )

    metricas_depois = (
        anuncio.obter_estatisticas().visualizacoes,
        anuncio.obter_estatisticas().cliques,
    )
    saldos_depois = [
        campanha.saldo_restante
        for campanha in repositorio.listar_ativas()
    ]

    assert metricas_depois == metricas_antes
    assert saldos_depois == saldos_antes


def test_rejeita_anuncio_padrao_invalido():
    with pytest.raises(TypeError):
        EstrategiaAnuncioGenerico(anuncio_padrao=None)
