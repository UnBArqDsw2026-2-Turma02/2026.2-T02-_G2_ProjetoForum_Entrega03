import pytest
from fastapi import HTTPException

from subequipe3_strategy.ads.service import dependencias
from subequipe3_strategy.ads.service.dependencias import (
    ConfiguracaoAds,
    get_configuracao_ads,
    get_delivery_service,
    get_estrategia_fallback,
    get_repositorio_ads,
    get_seletor,
)


class FallbackDeTeste:
    def __init__(self, anuncio):
        self.anuncio = anuncio

    def obter_nome(self):
        return "generico"

    def selecionar_anuncio(self, pergunta, campanhas):
        return self.anuncio


def test_politica_padrao_e_match_exato(monkeypatch):
    monkeypatch.delenv(dependencias.VARIAVEL_POLITICA, raising=False)
    assert get_configuracao_ads() == ConfiguracaoAds(politica="match_exato")


def test_politica_vem_da_configuracao(monkeypatch):
    monkeypatch.setenv(dependencias.VARIAVEL_POLITICA, "maior_saldo")
    assert get_configuracao_ads().politica == "maior_saldo"


def test_repositorio_compartilhado_entre_requisicoes():
    assert get_repositorio_ads() is get_repositorio_ads()


def test_seletor_registra_as_politicas_disponiveis():
    assert get_seletor().politicas() == ("match_exato",)


def test_fallback_pendente_da_issue_26_responde_503():
    with pytest.raises(HTTPException) as erro:
        get_estrategia_fallback()
    assert erro.value.status_code == 503
    assert "#26" in erro.value.detail


def test_controlador_novo_por_requisicao_com_a_politica_configurada():
    repositorio = get_repositorio_ads()
    fallback = FallbackDeTeste(repositorio.anuncio_padrao)
    argumentos = dict(
        configuracao=ConfiguracaoAds(), seletor=get_seletor(),
        fallback=fallback, repositorio=repositorio,
    )
    primeiro = get_delivery_service(**argumentos)
    segundo = get_delivery_service(**argumentos)
    assert primeiro is not segundo
    assert primeiro.politica_atual == "match_exato"


def test_politica_configurada_inexistente_responde_503():
    repositorio = get_repositorio_ads()
    with pytest.raises(HTTPException) as erro:
        get_delivery_service(
            configuracao=ConfiguracaoAds(politica="maior_lance"), seletor=get_seletor(),
            fallback=FallbackDeTeste(repositorio.anuncio_padrao), repositorio=repositorio,
        )
    assert erro.value.status_code == 503
    assert "maior_lance" in erro.value.detail
