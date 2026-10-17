"""Dados compartilhados da votação, conforme o Diagrama de Classes v1.0."""

from dataclasses import dataclass
from datetime import date
from enum import Enum


@dataclass
class Usuario:
    id: str
    reputacao: int


@dataclass
class ConteudoVotavel:
    id: str
    tipo: str
    autor: Usuario
    placar: int

    def __post_init__(self) -> None:
        if self.tipo not in {"pergunta", "resposta"}:
            raise ValueError("O conteúdo simulado deve ser pergunta ou resposta.")


@dataclass(frozen=True)
class Voto:
    votante: Usuario
    alvo: ConteudoVotavel
    dia: date


@dataclass(frozen=True)
class EventoReputacao:
    voto: Voto
    beneficiario: Usuario
    variacao: int = 10

    def __post_init__(self) -> None:
        if self.beneficiario is not self.voto.alvo.autor:
            raise ValueError("O beneficiário deve ser o autor do conteúdo votado.")


@dataclass(frozen=True)
class SolicitacaoVotoPositivo:
    """Referências internas do toy; dia representa uma data UTC já definida."""

    votante: Usuario
    alvo: ConteudoVotavel
    dia: date


class CodigoResultado(Enum):
    REGISTRADO = "REGISTRADO"
    REPUTACAO_INSUFICIENTE = "REPUTACAO_INSUFICIENTE"
    COTA_ESGOTADA = "COTA_ESGOTADA"


@dataclass(frozen=True)
class ResultadoVotacao:
    codigo: CodigoResultado
    mensagem: str
    voto: Voto | None = None
    evento: EventoReputacao | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.codigo, CodigoResultado):
            raise ValueError("O código deve pertencer a CodigoResultado.")
        if self.codigo is CodigoResultado.REGISTRADO:
            if self.voto is None or self.evento is None:
                raise ValueError("O sucesso exige voto e evento presentes.")
        elif self.voto is not None or self.evento is not None:
            raise ValueError("Uma rejeição não pode conter voto ou evento.")
