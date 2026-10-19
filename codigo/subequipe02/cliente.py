"""Cliente do padrão: encaminha a operação pelo contrato comum de votação."""

from .contratos import ServicoVotacao
from .dominio import ResultadoVotacao, SolicitacaoVotoPositivo


class ClienteVotacaoFastAPI:
    def __init__(self, servico: ServicoVotacao) -> None:
        self.servico = servico

    def registrar_voto(self, s: SolicitacaoVotoPositivo) -> ResultadoVotacao:
        return self.servico.votar(s)
