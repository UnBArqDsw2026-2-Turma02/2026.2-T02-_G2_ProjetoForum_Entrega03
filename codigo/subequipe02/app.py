"""Entrada HTTP e composição da demonstração do Proxy de proteção."""

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field

from .demonstracao import criar_demonstracao, dados_resultado
from .dominio import CodigoResultado, SolicitacaoVotoPositivo


class PedidoVoto(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [{"votante_id": "V1", "alvo_id": "P101"}]},
    )
    votante_id: str = Field(strict=True, min_length=1)
    alvo_id: str = Field(strict=True, min_length=1)


def criar_app() -> FastAPI:
    app = FastAPI(
        title="Proxy de proteção — votação positiva",
        description=(
            "Demonstração toy da SubEquipe 02. Prepare C01, C02 ou C03, consulte "
            "o estado, registre um voto e confira o estado novamente. "
            "IDs representam usuários simulados; não há autenticação real."
        ),
        version="1.0.0",
        redoc_url=None,
    )
    app.state.demonstracao = criar_demonstracao()

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def inicio():
        return Path(__file__).with_name("inicio.html").read_text(encoding="utf-8")

    @app.get("/estado", tags=["Demonstração"], summary="Consultar estado atual")
    async def consultar_estado() -> dict:
        return app.state.demonstracao.estado()

    @app.post(
        "/demo/cenarios/{cenario}",
        tags=["Demonstração"],
        summary="Preparar ou reiniciar um cenário independente",
    )
    async def preparar_cenario(cenario: Literal["C01", "C02", "C03"]) -> dict:
        app.state.demonstracao = criar_demonstracao(cenario)
        return app.state.demonstracao.estado()

    @app.post(
        "/votos",
        status_code=201,
        tags=["Votação"],
        summary="Solicitar um voto positivo pelo Proxy",
        responses={
            403: {"description": "Reputação insuficiente; estado preservado."},
            429: {"description": "Cota diária esgotada; estado preservado."},
            404: {"description": "Votante ou conteúdo não encontrado."},
            409: {"description": "Autovoto ou voto repetido fora do recorte."},
        },
    )
    async def votar(pedido: PedidoVoto, response: Response) -> dict:
        demo = app.state.demonstracao
        votante = demo.usuarios.get(pedido.votante_id)
        alvo = demo.conteudos.get(pedido.alvo_id)
        if votante is None:
            raise HTTPException(404, "Votante não encontrado no cenário.")
        if alvo is None:
            raise HTTPException(404, "Conteúdo não encontrado no cenário.")

        # Validações de fronteira mantêm as precondições do toy. Reputação e
        # disponibilidade continuam exclusivamente no Proxy existente.
        if votante is alvo.autor:
            raise HTTPException(409, "O recorte exige votante diferente do autor.")
        if any(
            voto.votante is votante and voto.alvo is alvo
            for voto in demo.real.votos
        ):
            raise HTTPException(409, "Voto já registrado. Reinicie o cenário.")

        solicitacao = SolicitacaoVotoPositivo(votante, alvo, demo.dia)
        resultado = demo.cliente.registrar_voto(solicitacao)
        response.status_code = {
            CodigoResultado.REGISTRADO: 201,
            CodigoResultado.REPUTACAO_INSUFICIENTE: 403,
            CodigoResultado.COTA_ESGOTADA: 429,
        }[resultado.codigo]
        return dados_resultado(resultado)

    return app


app = criar_app()
