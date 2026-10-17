"""Proxy de proteção: verifica o acesso e delega pelo contrato de votação."""

from .contratos import CotaDiaria, ServicoVotacao
from .dominio import CodigoResultado, ResultadoVotacao, SolicitacaoVotoPositivo


class ProxyProtecaoVotacao(ServicoVotacao):
    def __init__(self, real: ServicoVotacao, cota: CotaDiaria) -> None:
        self.real = real
        self.cota = cota
        self._reputacao_minima = 15

    def votar(self, s: SolicitacaoVotoPositivo) -> ResultadoVotacao:
        if s.votante.reputacao < self._reputacao_minima:
            return ResultadoVotacao(
                codigo=CodigoResultado.REPUTACAO_INSUFICIENTE,
                mensagem=(
                    "A votação positiva padrão exige pelo menos "
                    f"{self._reputacao_minima} pontos de reputação neste recorte."
                ),
            )

        if not self.cota.disponivel(s.votante.id, s.dia):
            return ResultadoVotacao(
                codigo=CodigoResultado.COTA_ESGOTADA,
                mensagem="A cota diária de votos positivos da demonstração foi esgotada.",
            )

        return self.real.votar(s)
