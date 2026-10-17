"""Composição da aplicação: reaproveita o app FastAPI do fórum e acrescenta as rotas de Ads.

Executar a partir de codigo/: uvicorn subequipe3_strategy.main:app --reload
"""

from subequipe1_factory_method.main import app

from .ads.controller.rotas import router as rotas_ads

app.include_router(rotas_ads)
