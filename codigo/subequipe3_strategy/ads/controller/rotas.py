from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse

from ..model.repositorio import AnuncioNaoEncontrado, CampanhaInelegivel
from ..service.dependencias import get_controlador_entrega, get_pergunta_view
from ..view.pergunta_view import PerguntaView
from .controlador_entrega import ControladorEntrega, PerguntaNaoEncontrada

router = APIRouter(tags=["Anúncios"])

INDISPONIVEL = {503: {"description": "Política ou estratégia de fallback não configurada"}}


@router.get(
    "/perguntas/{pergunta_id}/pagina",
    response_class=HTMLResponse,
    summary="Exibe a pergunta com o anúncio selecionado (HTML SSR)",
    description=(
        "Delega a seleção à política configurada (Strategy) e usa o fallback "
        "genérico quando nenhuma campanha é compatível. Cada exibição bem-sucedida "
        "registra uma visualização do anúncio entregue."
    ),
    responses={
        200: {"description": "Página HTML com a pergunta e o anúncio"},
        404: {"description": "Pergunta não encontrada"},
        **INDISPONIVEL,
    },
)
def exibir_pergunta(
    pergunta_id: UUID,
    request: Request,
    controlador: Annotated[ControladorEntrega, Depends(get_controlador_entrega)],
    view: Annotated[PerguntaView, Depends(get_pergunta_view)],
) -> HTMLResponse:
    try:
        entrega = controlador.entregar_anuncio(pergunta_id)
    except PerguntaNaoEncontrada:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada") from None

    # A visualização só conta depois de a página ser montada com sucesso.
    resposta = view.renderizar(request, entrega)
    controlador.registrar_visualizacao(entrega.anuncio.id)
    return resposta


@router.post(
    "/anuncios/{anuncio_id}/cliques",
    status_code=204,
    summary="Registra um clique no anúncio",
    description=(
        "Clique contextual revalida status e saldo, debita o custo por clique e "
        "incrementa a métrica em uma única operação. Clique genérico só incrementa "
        "a métrica. Cada chamada conta como um novo evento (sem deduplicação)."
    ),
    responses={
        204: {"description": "Clique registrado"},
        404: {"description": "Anúncio não encontrado"},
        409: {"description": "Campanha inativa ou sem saldo; nada foi alterado"},
        **INDISPONIVEL,
    },
)
def registrar_clique(
    anuncio_id: UUID,
    controlador: Annotated[ControladorEntrega, Depends(get_controlador_entrega)],
) -> Response:
    try:
        controlador.registrar_clique(anuncio_id)
    except AnuncioNaoEncontrado:
        raise HTTPException(status_code=404, detail="Anúncio não encontrado") from None
    except CampanhaInelegivel as erro:
        raise HTTPException(status_code=409, detail=str(erro)) from None
    return Response(status_code=204)
