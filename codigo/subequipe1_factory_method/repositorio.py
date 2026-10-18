from uuid import UUID

from .produtos import Conteudo


class RepositorioConteudo:
    """Repositório em memória (RNF04): guarda conteúdos por id e some quando a API reinicia."""

    def __init__(self) -> None:
        self._itens: dict[UUID, Conteudo] = {}

    def salvar(self, conteudo: Conteudo) -> None:
        self._itens[conteudo.id] = conteudo

    def buscar(self, conteudo_id: UUID) -> Conteudo | None:
        return self._itens.get(conteudo_id)
