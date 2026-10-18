import threading
from typing import ClassVar
from uuid import UUID

from .produtos import Conteudo


class RepositorioConteudo:
    """Singleton (GAMMA et al., 2000): única instância compartilhada por toda a API (RNF04, RNF07)."""

    _instancia: ClassVar["RepositorioConteudo | None"] = None
    # [não-GoF] double-checked locking: o FastAPI roda endpoints `def` em um pool de threads
    _lock: ClassVar[threading.Lock] = threading.Lock()
    # Python não tem construtor privado: só instancia() conhece este token
    _token: ClassVar[object] = object()

    def __init__(self, token: object = None) -> None:
        if token is not RepositorioConteudo._token:
            raise TypeError("RepositorioConteudo é um Singleton: use RepositorioConteudo.instancia()")
        self._conteudos: dict[UUID, Conteudo] = {}

    @classmethod
    def instancia(cls) -> "RepositorioConteudo":
        if cls._instancia is None:
            with cls._lock:
                # 2ª checagem: outra thread pode ter criado a instância enquanto esta esperava o lock
                if cls._instancia is None:
                    cls._instancia = cls(cls._token)
        return cls._instancia

    def salvar(self, conteudo: Conteudo) -> None:
        self._conteudos[conteudo.id] = conteudo

    def buscar_por_id(self, conteudo_id: UUID) -> Conteudo | None:
        return self._conteudos.get(conteudo_id)

    def atualizar(self, conteudo: Conteudo) -> None:
        if conteudo.id not in self._conteudos:
            raise KeyError(f"Conteúdo {conteudo.id} não está no repositório")
        self._conteudos[conteudo.id] = conteudo

    @classmethod
    def _resetar(cls) -> None:
        """Somente para testes: descarta a instância atual."""
        with cls._lock:
            cls._instancia = None
