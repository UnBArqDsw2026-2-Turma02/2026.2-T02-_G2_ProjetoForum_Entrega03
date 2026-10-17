from decimal import Decimal
from uuid import UUID

import pytest

from app.ads.model.anuncio import AnuncioContextual
from app.ads.model.campanha import Campanha, StatusCampanha, Tag


@pytest.fixture
def criar_anuncio():
    def criar(**alteracoes):
        dados = dict(
            id=UUID(int=11), titulo="Curso de Python",
            banner_url="/static/python.png", link_destino="https://example.org/python",
        )
        dados.update(alteracoes)
        return AnuncioContextual(**dados)
    return criar


@pytest.fixture
def criar_campanha(criar_anuncio):
    def criar(**alteracoes):
        campanha_id = alteracoes.get("id", UUID(int=1))
        dados = dict(
            id=campanha_id, tags_alvo=[Tag("python")], orcamento=Decimal("100.00"),
            saldo_restante=Decimal("10.00"), custo_por_clique=Decimal("1.00"),
            status=StatusCampanha.ATIVA,
            anuncios=[criar_anuncio(id=UUID(int=1000 + campanha_id.int))],
        )
        dados.update(alteracoes)
        return Campanha(**dados)
    return criar
