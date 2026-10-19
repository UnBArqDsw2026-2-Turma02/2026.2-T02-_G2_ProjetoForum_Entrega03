from abc import ABC, abstractmethod

from .produtos import Comentario, Conteudo, Pergunta, Resposta
from .repositorio import RepositorioConteudo


# Creator abstrato (GoF)
class CriadorDeConteudo(ABC):
    """Creator abstrato: declara a fábrica, mas não decide a classe concreta."""

    def __init__(self, repositorio: RepositorioConteudo):
        self.repositorio = repositorio

    # Factory Method (GoF): cada subclasse decide qual Conteudo instanciar
    @abstractmethod
    def criar_conteudo(self, dados: dict) -> Conteudo:
        ...

    def publicar(self, dados: dict) -> Conteudo:
        # Operação do Creator no GoF: usa o factory method sem saber qual produto sai dele
        conteudo = self.criar_conteudo(dados)
        self.repositorio.salvar(conteudo)
        return conteudo


# Concrete Creator (GoF): implementa o Factory Method para produzir Perguntas
class CriadorDePergunta(CriadorDeConteudo):
    def criar_conteudo(self, dados: dict) -> Conteudo:
        return Pergunta(
            corpo=dados["corpo"],
            titulo=dados["titulo"],
            autor=dados["autor"],
            tags=dados.get("tags"),
        )


# Concrete Creator (GoF): implementa o Factory Method para produzir Respostas
class CriadorDeResposta(CriadorDeConteudo):
    def criar_conteudo(self, dados: dict) -> Conteudo:
        pergunta: Pergunta = dados["pergunta"]
        resposta = Resposta(
            corpo=dados["corpo"],
            autor=dados["autor"],
            pergunta_id=pergunta.id,
        )
        pergunta.adicionar_resposta(resposta)
        return resposta


# Concrete Creator (GoF): implementa o Factory Method para produzir Comentarios
class CriadorDeComentario(CriadorDeConteudo):
    def criar_conteudo(self, dados: dict) -> Conteudo:
        pergunta: Pergunta = dados["pergunta"]
        comentario = Comentario(
            corpo=dados["corpo"],
            autor=dados["autor"],
            pergunta_id=pergunta.id,
        )
        pergunta.adicionar_comentario(comentario)
        return comentario
