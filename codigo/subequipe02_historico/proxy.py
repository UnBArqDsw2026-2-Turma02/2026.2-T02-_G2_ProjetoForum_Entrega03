"""Proxy de proteção: autoriza a consulta e delega só quando permitido."""

from .contratos import ServicoConsultaHistorico
from .dominio import (
    CodigoConsulta,
    Perfil,
    ResultadoConsultaHistorico,
    SolicitacaoConsultaHistorico,
)


class ProxyConsultaHistorico(ServicoConsultaHistorico):
    def __init__(self, real: ServicoConsultaHistorico) -> None:
        self.real = real

    def consultar(
        self, s: SolicitacaoConsultaHistorico
    ) -> ResultadoConsultaHistorico:
        proprio_historico = s.solicitante.id == s.usuario_consultado_id
        moderador = s.solicitante.perfil is Perfil.MODERADOR

        if not (proprio_historico or moderador):
            return ResultadoConsultaHistorico(
                codigo=CodigoConsulta.ACESSO_NEGADO,
                mensagem=(
                    "Somente o próprio usuário ou um moderador pode consultar "
                    "este histórico de votos."
                ),
                usuario_id=s.usuario_consultado_id,
            )

        return self.real.consultar(s)
