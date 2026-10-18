"""Composição da aplicação: reaproveita o app FastAPI do fórum e acrescenta as rotas de Ads.

Executar a partir de codigo/: uvicorn subequipe3_strategy.main:app --reload
"""

from pathlib import Path

from fastapi.staticfiles import StaticFiles

from subequipe1_factory_method.main import app

from .ads.controller.rotas import router as rotas_ads

# Imagens de exemplo usadas pelos anúncios de demonstração (RepositorioAds.seed).
DIRETORIO_ESTATICOS = Path(__file__).parent / "ads" / "view" / "static"

app.include_router(rotas_ads)
app.mount("/static", StaticFiles(directory=DIRETORIO_ESTATICOS), name="static")
