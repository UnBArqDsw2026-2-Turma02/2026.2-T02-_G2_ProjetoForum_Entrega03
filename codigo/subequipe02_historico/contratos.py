"""Contrato comum ao Proxy e ao serviço real (papel de Subject)."""

from abc import ABC, abstractmethod

from .dominio import ResultadoConsultaHistorico, SolicitacaoConsultaHistorico


class ServicoConsultaHistorico(ABC):
    @abstractmethod
    def consultar(
        self, s: SolicitacaoConsultaHistorico
    ) -> ResultadoConsultaHistorico:
        """Retorna o resultado da consulta pelo contrato comum do padrão."""
        raise NotImplementedError
