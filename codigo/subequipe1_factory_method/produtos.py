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


# Concrete Product (GoF)
class Pergunta(Conteudo):
    def __init__(self, corpo: str, titulo: str, autor: str):
        super().__init__(corpo, autor)
        self.titulo = titulo
        self.status = "ABERTA"
        self.respostas: list["Resposta"] = []

    def adicionar_resposta(self, resposta: "Resposta") -> None:
        # Composição (diagrama v2): a Resposta pertence a uma única Pergunta
        self.respostas.append(resposta)


# Concrete Product (GoF)
class Resposta(Conteudo):
    def __init__(self, corpo: str, autor: str, pergunta_id: UUID):
        super().__init__(corpo, autor)
        self.pergunta_id = pergunta_id
        self.aceita = False
