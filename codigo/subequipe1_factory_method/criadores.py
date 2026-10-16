from abc import ABC, abstractmethod

from .produtos import Conteudo, Pergunta, Resposta


class CriadorDeConteudo(ABC):
    """Creator abstrato: declara a fábrica, mas não decide a classe concreta."""

    @abstractmethod
    def criar_conteudo(self, dados: dict) -> Conteudo:
        ...


class CriadorDePergunta(CriadorDeConteudo):
    def criar_conteudo(self, dados: dict) -> Conteudo:
        return Pergunta(corpo=dados["corpo"], titulo=dados["titulo"])


class CriadorDeResposta(CriadorDeConteudo):
    def criar_conteudo(self, dados: dict) -> Conteudo:
        return Resposta(corpo=dados["corpo"])
