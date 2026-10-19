"""Providers do FastAPI: montam os criadores e entregam ao controller via Depends()."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException

from .criadores import (
    CriadorDeComentario,
    CriadorDeConteudo,
    CriadorDePergunta,
    CriadorDeResposta,
)
from .produtos import Pergunta
from .repositorio import RepositorioConteudo


def get_repositorio() -> RepositorioConteudo:
    # Client do Singleton: único ponto da API que chama instancia()
    return RepositorioConteudo.instancia()


def get_criador_de_pergunta(
    repositorio: Annotated[RepositorioConteudo, Depends(get_repositorio)],
) -> CriadorDeConteudo:
    return CriadorDePergunta(repositorio)


def get_criador_de_resposta(
    repositorio: Annotated[RepositorioConteudo, Depends(get_repositorio)],
) -> CriadorDeConteudo:
    return CriadorDeResposta(repositorio)


def get_criador_de_comentario(
    repositorio: Annotated[RepositorioConteudo, Depends(get_repositorio)],
) -> CriadorDeConteudo:
    return CriadorDeComentario(repositorio)


def obter_pergunta(
    pergunta_id: UUID,
    repositorio: Annotated[RepositorioConteudo, Depends(get_repositorio)],
) -> Pergunta:
    conteudo = repositorio.buscar_por_id(pergunta_id)
    # O repositório é único para todos os tipos; como_pergunta() é polimórfico, sem isinstance (RNF01)
    pergunta = conteudo.como_pergunta() if conteudo is not None else None
    if pergunta is None:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada")
    return pergunta
