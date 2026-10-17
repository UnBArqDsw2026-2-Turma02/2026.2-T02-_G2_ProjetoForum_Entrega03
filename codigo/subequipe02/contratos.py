"""Interfaces comuns ao Proxy, serviço real e componente de cota."""

from abc import ABC, abstractmethod
from datetime import date

from .dominio import ResultadoVotacao, SolicitacaoVotoPositivo


class ServicoVotacao(ABC):
    @abstractmethod
    def votar(self, s: SolicitacaoVotoPositivo) -> ResultadoVotacao:
        """Retorna o resultado da votação pelo contrato comum do padrão."""
        raise NotImplementedError


class CotaDiaria(ABC):
    @abstractmethod
    def consultar_uso(self, usuario_id: str, dia: date) -> int:
        """Retorna uso não negativo (0 sem registro), sem modificar estado."""
        raise NotImplementedError

    @abstractmethod
    def disponivel(self, usuario_id: str, dia: date) -> bool:
        """Consulta se o uso é menor que o limite positivo, sem mutação."""
        raise NotImplementedError

    @abstractmethod
    def registrar_consumo(self, usuario_id: str, dia: date) -> None:
        """Soma uma unidade; o serviço real chama após autorização do Proxy."""
        raise NotImplementedError
