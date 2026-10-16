from abc import ABC
from datetime import datetime
from uuid import UUID, uuid4


class Conteudo(ABC):
    """Product abstrato: o que todo conteúdo do fórum tem em comum."""

    def __init__(self, corpo: str):
        self.id: UUID = uuid4()
        self.corpo = corpo
        self.data_criacao = datetime.now()


class Pergunta(Conteudo):
    def __init__(self, corpo: str, titulo: str):
        super().__init__(corpo)
        self.titulo = titulo
        self.status = "ABERTA"
        self.respostas: list["Resposta"] = []


class Resposta(Conteudo):
    def __init__(self, corpo: str):
        super().__init__(corpo)
        self.aceita = False
