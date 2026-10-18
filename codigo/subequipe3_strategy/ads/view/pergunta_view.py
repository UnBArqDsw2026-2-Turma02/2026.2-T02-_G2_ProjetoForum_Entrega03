from pathlib import Path

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from markupsafe import Markup

from ..controller.controlador_entrega import EntregaAnuncio
from .schemas import AnuncioResponse

DIRETORIO_TEMPLATES = Path(__file__).parent / "templates"


class PerguntaView:
    """Renderiza a página da pergunta (SSR) com o anúncio entregue pelo Context."""

    def __init__(self, templates: Jinja2Templates | None = None) -> None:
        self._templates = templates or Jinja2Templates(directory=str(DIRETORIO_TEMPLATES))

    def renderizar(self, request: Request, entrega: EntregaAnuncio) -> HTMLResponse:
        # O DTO revalida as URLs antes de o fragmento ser marcado como seguro.
        anuncio = AnuncioResponse.model_validate(entrega.anuncio)
        banner = Markup(entrega.anuncio.renderizar())
        return self._templates.TemplateResponse(
            request,
            "pergunta.html",
            {
                "pergunta": entrega.pergunta,
                "anuncio": anuncio,
                "banner": banner,
                "politica": entrega.politica,
                "usou_fallback": entrega.usou_fallback,
                "url_clique": request.url_for("registrar_clique", anuncio_id=anuncio.id).path,
            },
        )
