from abc import ABC, abstractmethod

from .produtos import Conteudo, Pergunta, Resposta
from .repositorio import RepositorioConteudo


class CriadorDeConteudo(ABC):
    """Creator abstrato: declara a fábrica, mas não decide a classe concreta."""

    def __init__(self, repositorio: RepositorioConteudo):
        self.repositorio = repositorio

    @abstractmethod
    def criar_conteudo(self, dados: dict) -> Conteudo:
        ...

    def publicar(self, dados: dict) -> Conteudo:
        # Operação do Creator no GoF: usa o factory method sem saber qual produto sai dele
        conteudo = self.criar_conteudo(dados)
        self.repositorio.salvar(conteudo)
        return conteudo


class CriadorDePergunta(CriadorDeConteudo):
    def criar_conteudo(self, dados: dict) -> Conteudo:
        return Pergunta(corpo=dados["corpo"], titulo=dados["titulo"])


class CriadorDeResposta(CriadorDeConteudo):
    def criar_conteudo(self, dados: dict) -> Conteudo:
        pergunta: Pergunta = dados["pergunta"]
        resposta = Resposta(corpo=dados["corpo"], pergunta_id=pergunta.id)
        pergunta.adicionar_resposta(resposta)
        return resposta
