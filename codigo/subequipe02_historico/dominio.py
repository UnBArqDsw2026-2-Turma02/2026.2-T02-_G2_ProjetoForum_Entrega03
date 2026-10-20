"""Dados da consulta ao histórico; Voto vem do módulo de votação existente."""

from dataclasses import dataclass
from enum import Enum

from subequipe02.dominio import Voto


class Perfil(Enum):
    COMUM = "COMUM"
    MODERADOR = "MODERADOR"


@dataclass(frozen=True)
class Participante:
    """Usuário simulado com o perfil definido pelo servidor."""

    id: str
    perfil: Perfil


@dataclass(frozen=True)
class SolicitacaoConsultaHistorico:
    solicitante: Participante
    usuario_consultado_id: str


class CodigoConsulta(Enum):
    CONSULTADO = "CONSULTADO"
    ACESSO_NEGADO = "ACESSO_NEGADO"


@dataclass(frozen=True)
class ResultadoConsultaHistorico:
    codigo: CodigoConsulta
    mensagem: str
    usuario_id: str
    votos: tuple[Voto, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.codigo, CodigoConsulta):
            raise ValueError("O código deve pertencer a CodigoConsulta.")
        if self.codigo is CodigoConsulta.ACESSO_NEGADO and self.votos:
            raise ValueError("Uma rejeição não pode conter votos.")
