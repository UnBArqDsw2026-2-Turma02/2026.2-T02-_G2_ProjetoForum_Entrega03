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
    def __init__(self, corpo: str, titulo: str, tags: list[str] | None = None):
        super().__init__(corpo)
        self.titulo = titulo
        self.tags: list[str] = list(tags or [])
        self.status = "ABERTA"
        self.respostas: list["Resposta"] = []

    def adicionar_resposta(self, resposta: "Resposta") -> None:
        # Composição (diagrama v2): a Resposta pertence a uma única Pergunta
        self.respostas.append(resposta)


class Resposta(Conteudo):
    def __init__(self, corpo: str, pergunta_id: UUID):
        super().__init__(corpo)
        self.pergunta_id = pergunta_id
        self.aceita = False
