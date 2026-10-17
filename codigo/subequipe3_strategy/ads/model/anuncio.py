from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from html import escape
from urllib.parse import urlsplit
from uuid import UUID


class FormatoAnuncio(str, Enum):
    BANNER = "BANNER"
    NATIVE = "NATIVE"
    VIDEO = "VIDEO"


@dataclass
class EstatisticasAds:
    anuncio_id: UUID
    visualizacoes: int = 0
    cliques: int = 0

    def __post_init__(self) -> None:
        for nome, valor in (
            ("visualizacoes", self.visualizacoes),
            ("cliques", self.cliques),
        ):
            if type(valor) is not int or valor < 0:
                raise ValueError(f"{nome} deve ser um inteiro não negativo.")

    def incrementar_visualizacao(self) -> None:
        self.visualizacoes += 1

    def incrementar_clique(self) -> None:
        self.cliques += 1


def validar_url_anuncio(url: str) -> None:
    if not isinstance(url, str) or not url:
        raise ValueError("A URL deve ser uma string não vazia.")
    if any(
        caractere.isspace() or ord(caractere) < 32 or ord(caractere) == 127
        for caractere in url
    ):
        raise ValueError("A URL não pode conter espaços ou caracteres de controle.")
    if "\\" in url:
        raise ValueError("A URL não pode conter barras invertidas.")

    partes = urlsplit(url)
    if url.startswith("/") and not url.startswith("//"):
        return
    if partes.scheme.lower() in ("http", "https") and partes.hostname:
        return
    raise ValueError("Use uma URL HTTP/HTTPS absoluta ou um caminho iniciado por /.")


@dataclass
class Anuncio(ABC):
    id: UUID
    titulo: str
    banner_url: str
    link_destino: str
    formato: FormatoAnuncio = FormatoAnuncio.BANNER
    _estatisticas: EstatisticasAds = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.formato, FormatoAnuncio):
            raise TypeError("formato deve ser FormatoAnuncio.")
        validar_url_anuncio(self.banner_url)
        validar_url_anuncio(self.link_destino)
        self._estatisticas = EstatisticasAds(anuncio_id=self.id)

    def obter_estatisticas(self) -> EstatisticasAds:
        """Fornece a mesma instância para o repositório de métricas compartilhar."""
        return self._estatisticas

    @abstractmethod
    def renderizar(self) -> str:
        """Retorna o fragmento HTML sem registrar eventos ou debitar campanhas."""
        raise NotImplementedError

    def _renderizar_banner(self, imagem_url: str, mensagem: str = "") -> str:
        if self.formato != FormatoAnuncio.BANNER:
            raise NotImplementedError("A renderização disponível nesta etapa é BANNER.")
        # Revalidar evita que alterações posteriores introduzam URLs executáveis.
        validar_url_anuncio(imagem_url)
        validar_url_anuncio(self.link_destino)
        titulo = escape(self.titulo, quote=True)
        imagem = escape(imagem_url, quote=True)
        destino = escape(self.link_destino, quote=True)
        texto = f"<span>{escape(mensagem)}</span>" if mensagem else ""
        return f'<a href="{destino}"><img src="{imagem}" alt="{titulo}">{texto}</a>'


@dataclass
class AnuncioContextual(Anuncio):
    imagem_banner: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.imagem_banner:
            validar_url_anuncio(self.imagem_banner)

    def renderizar(self) -> str:
        return self._renderizar_banner(self.imagem_banner or self.banner_url)


@dataclass
class AnuncioGenerico(Anuncio):
    mensagem_padrao: str = ""

    def renderizar(self) -> str:
        return self._renderizar_banner(self.banner_url, self.mensagem_padrao)
