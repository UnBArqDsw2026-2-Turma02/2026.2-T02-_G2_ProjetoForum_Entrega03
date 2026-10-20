"""Serviço real: apenas busca os votos do usuário consultado."""

from collections.abc import Sequence

from subequipe02.dominio import Voto

from .contratos import ServicoConsultaHistorico
from .dominio import (
    CodigoConsulta,
    ResultadoConsultaHistorico,
    SolicitacaoConsultaHistorico,
)


class ServicoConsultaHistoricoReal(ServicoConsultaHistorico):
    def __init__(self, votos: Sequence[Voto]) -> None:
        self._votos = votos

    def consultar(
        self, s: SolicitacaoConsultaHistorico
    ) -> ResultadoConsultaHistorico:
        """Filtra por ID; a permissão pertence ao Proxy e nada é modificado."""
        encontrados = tuple(
            voto
            for voto in self._votos
            if voto.votante.id == s.usuario_consultado_id
        )
        return ResultadoConsultaHistorico(
            codigo=CodigoConsulta.CONSULTADO,
            mensagem="Histórico de votos consultado.",
            usuario_id=s.usuario_consultado_id,
            votos=encontrados,
        )
