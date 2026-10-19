"""Serviço real: registra os efeitos de uma votação autorizada pelo Proxy."""

from .contratos import CotaDiaria, ServicoVotacao
from .dominio import (
    CodigoResultado,
    EventoReputacao,
    ResultadoVotacao,
    SolicitacaoVotoPositivo,
    Voto,
)


class ServicoVotacaoReal(ServicoVotacao):
    def __init__(self, cota: CotaDiaria) -> None:
        self.cota = cota
        self._votos: list[Voto] = []
        self._eventos: list[EventoReputacao] = []

    @property
    def votos(self) -> tuple[Voto, ...]:
        """Consulta os registros sem expor a lista interna para alteração."""
        return tuple(self._votos)

    @property
    def eventos(self) -> tuple[EventoReputacao, ...]:
        """Consulta os eventos preservando as referências dos registros."""
        return tuple(self._eventos)

    def votar(self, s: SolicitacaoVotoPositivo) -> ResultadoVotacao:
        """Executa o caminho aceito; a autorização pertence ao Proxy."""
        voto = Voto(votante=s.votante, alvo=s.alvo, dia=s.dia)
        evento = EventoReputacao(
            voto=voto, beneficiario=s.alvo.autor, variacao=10
        )

        self._votos.append(voto)
        self._eventos.append(evento)
        s.alvo.placar += 1
        s.alvo.autor.reputacao += evento.variacao
        self.cota.registrar_consumo(s.votante.id, s.dia)

        return ResultadoVotacao(
            codigo=CodigoResultado.REGISTRADO,
            mensagem="Voto positivo registrado.",
            voto=voto,
            evento=evento,
        )
