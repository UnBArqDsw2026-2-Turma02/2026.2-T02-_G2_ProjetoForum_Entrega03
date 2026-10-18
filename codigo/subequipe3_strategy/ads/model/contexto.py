from dataclasses import dataclass, field
from uuid import UUID

from subequipe1_factory_method.produtos import Pergunta as PerguntaConteudo

from .campanha import Tag


@dataclass(frozen=True)
class Pergunta:
    """Projeção de leitura de Conteúdo; não é uma segunda entidade do fórum."""

    id: UUID
    titulo: str
    tags: list[Tag] = field(default_factory=list)

    def obter_tags(self) -> list[Tag]:
        return list(self.tags)


def projetar_pergunta(pergunta: PerguntaConteudo, tags: list[Tag]) -> Pergunta:
    # Conteúdo ainda não fornece tags: exigir o dado evita simular integração.
    return Pergunta(id=pergunta.id, titulo=pergunta.titulo, tags=list(tags))
