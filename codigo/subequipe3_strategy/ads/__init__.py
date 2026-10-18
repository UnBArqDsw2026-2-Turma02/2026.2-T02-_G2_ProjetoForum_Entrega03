
"""Domínio de anúncios e contratos do padrão Strategy."""

from .model.anuncio import AnuncioGenerico
from .model.strategies import EstrategiaSelecaoAnuncio

__all__ = [
    "AnuncioGenerico",
    "EstrategiaSelecaoAnuncio",
]
