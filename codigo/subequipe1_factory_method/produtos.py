from abc import ABC
from datetime import datetime
from uuid import UUID, uuid4


class Conteudo(ABC):
    """Product abstrato: o que todo conteúdo do fórum tem em comum."""

    def __init__(self, corpo: str, autor: str):
        self.id: UUID = uuid4()
        self.corpo = corpo
        self.autor = autor
        self.data_criacao = datetime.now()

    def como_pergunta(self) -> "Pergunta | None":
        # Polimorfismo no lugar de isinstance (RNF01): só a Pergunta devolve a si mesma
        return None


# Concrete Product (GoF)
class Pergunta(Conteudo):
    def __init__(self, corpo: str, titulo: str, autor: str, tags: list[str] | None = None):
        super().__init__(corpo, autor)
        self.titulo = titulo
        self.tags: list[str] = list(tags or [])
        self.status = "ABERTA"
        self.respostas: list["Resposta"] = []
        self.comentarios: list["Comentario"] = []

    def como_pergunta(self) -> "Pergunta":
        return self

    def adicionar_resposta(self, resposta: "Resposta") -> None:
        # Composição (diagrama v2): a Resposta pertence a uma única Pergunta
        self.respostas.append(resposta)

    def adicionar_comentario(self, comentario: "Comentario") -> None:
        self.comentarios.append(comentario)


# Concrete Product (GoF)
class Resposta(Conteudo):
    def __init__(self, corpo: str, autor: str, pergunta_id: UUID):
        super().__init__(corpo, autor)
        self.pergunta_id = pergunta_id
        self.aceita = False


# Concrete Product (GoF): Comentario é um novo tipo de Conteudo do fórum
class Comentario(Conteudo):
    def __init__(self, corpo: str, autor: str, pergunta_id: UUID):
        super().__init__(corpo, autor)
        self.pergunta_id = pergunta_id
