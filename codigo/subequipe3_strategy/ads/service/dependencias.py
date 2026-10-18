"""Providers do FastAPI: montam o Context de Ads a cada requisição via Depends()."""

import os
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException

from ..controller.controlador_entrega import ControladorEntrega
from ..model.maior_saldo_strategy import EstrategiaMaiorSaldoNaTag
from ..model.match_exato import EstrategiaMatchExatoDeTag
from ..model.repositorio import RepositorioAds
from ..model.strategies import EstrategiaSelecaoAnuncio
from ..view.pergunta_view import PerguntaView
from .seletor import PoliticaDesconhecida, SeletorDeEstrategia

VARIAVEL_POLITICA = "ADS_POLITICA"
POLITICA_PADRAO = "match_exato"


@dataclass(frozen=True)
class ConfiguracaoAds:
    politica: str = POLITICA_PADRAO


def get_configuracao_ads() -> ConfiguracaoAds:
    return ConfiguracaoAds(politica=os.environ.get(VARIAVEL_POLITICA, POLITICA_PADRAO))


# Adaptador em memória compartilhado no processo, com dados de demonstração.
_repositorio_ads = RepositorioAds.seed()


def get_repositorio_ads() -> RepositorioAds:
    return _repositorio_ads


def get_seletor() -> SeletorDeEstrategia:
    # Novas políticas entram apenas por registro aqui (OCP / Issue #28).
    return SeletorDeEstrategia(
        [EstrategiaMatchExatoDeTag(), EstrategiaMaiorSaldoNaTag()]
    )


def get_estrategia_fallback() -> EstrategiaSelecaoAnuncio:
    # A estratégia genérica pertence à Issue #26; o Context não a substitui.
    raise HTTPException(
        status_code=503,
        detail="Estratégia genérica de fallback (Issue #26) ainda não integrada.",
    )


def get_delivery_service(
    configuracao: Annotated[ConfiguracaoAds, Depends(get_configuracao_ads)],
    seletor: Annotated[SeletorDeEstrategia, Depends(get_seletor)],
    fallback: Annotated[EstrategiaSelecaoAnuncio, Depends(get_estrategia_fallback)],
    repositorio: Annotated[RepositorioAds, Depends(get_repositorio_ads)],
) -> ControladorEntrega:
    try:
        return ControladorEntrega(
            seletor=seletor,
            politica=configuracao.politica,
            fallback=fallback,
            perguntas=repositorio,
            campanhas=repositorio,
            metricas=repositorio,
        )
    except PoliticaDesconhecida as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from None


def get_pergunta_view() -> PerguntaView:
    return PerguntaView()
