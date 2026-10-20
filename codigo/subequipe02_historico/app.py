"""Entrada HTTP (cliente do padrão): resolve IDs e chama o Proxy."""

from fastapi import FastAPI, HTTPException, Query, Response

from .dados import criar_base
from .dominio import CodigoConsulta, SolicitacaoConsultaHistorico
from .proxy import ProxyConsultaHistorico
from .servico_real import ServicoConsultaHistoricoReal


def criar_app() -> FastAPI:
    app = FastAPI(
        title="Proxy de proteção — histórico de votos",
        description=(
            "Complemento da SubEquipe 02. O usuário consulta o próprio "
            "histórico; um moderador simulado consulta o de qualquer usuário. "
            "Os IDs são simulados e não há autenticação real."
        ),
        version="1.0.0",
        redoc_url=None,
    )
    base = criar_base()
    real = ServicoConsultaHistoricoReal(base.votos)
    app.state.base = base
    app.state.real = real
    app.state.servico = ProxyConsultaHistorico(real)

    @app.get(
        "/usuarios/{usuario_id}/historico-votos",
        tags=["Histórico"],
        summary="Consultar o histórico de votos pelo Proxy",
        responses={
            403: {"description": "Acesso negado; nenhum voto retornado."},
            404: {"description": "Solicitante ou usuário consultado inexistente."},
        },
    )
    async def consultar_historico(
        usuario_id: str,
        response: Response,
        solicitante_id: str = Query(min_length=1),
    ) -> dict:
        base = app.state.base
        solicitante = base.participantes.get(solicitante_id)
        if solicitante is None:
            raise HTTPException(404, "Solicitante não encontrado.")
        if usuario_id not in base.participantes:
            raise HTTPException(404, "Usuário consultado não encontrado.")

        resultado = app.state.servico.consultar(
            SolicitacaoConsultaHistorico(solicitante, usuario_id)
        )
        if resultado.codigo is CodigoConsulta.ACESSO_NEGADO:
            response.status_code = 403

        return {
            "codigo": resultado.codigo.value,
            "mensagem": resultado.mensagem,
            "usuario_id": resultado.usuario_id,
            "votos": [
                {
                    "votante_id": voto.votante.id,
                    "alvo_id": voto.alvo.id,
                    "dia": voto.dia.isoformat(),
                }
                for voto in resultado.votos
            ],
        }

    return app


app = criar_app()
