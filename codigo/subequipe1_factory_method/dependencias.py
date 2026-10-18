"""Providers do FastAPI: montam os criadores e entregam ao controller via Depends()."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException

from .criadores import CriadorDeConteudo, CriadorDePergunta, CriadorDeResposta
from .produtos import Pergunta
from .repositorio import RepositorioConteudo

# Repositórios em memória: um por tipo de produto, para a busca não precisar checar tipo
_repositorio_perguntas = RepositorioConteudo()
_repositorio_respostas = RepositorioConteudo()


def get_repositorio_perguntas() -> RepositorioConteudo:
    return _repositorio_perguntas


def get_repositorio_respostas() -> RepositorioConteudo:
    return _repositorio_respostas


def get_criador_de_pergunta(
    repositorio: Annotated[RepositorioConteudo, Depends(get_repositorio_perguntas)],
) -> CriadorDeConteudo:
    return CriadorDePergunta(repositorio)


def get_criador_de_resposta(
    repositorio: Annotated[RepositorioConteudo, Depends(get_repositorio_respostas)],
) -> CriadorDeConteudo:
    return CriadorDeResposta(repositorio)


def obter_pergunta(
    pergunta_id: UUID,
    repositorio: Annotated[RepositorioConteudo, Depends(get_repositorio_perguntas)],
) -> Pergunta:
    pergunta = repositorio.buscar(pergunta_id)
    if pergunta is None:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada")
    return pergunta
