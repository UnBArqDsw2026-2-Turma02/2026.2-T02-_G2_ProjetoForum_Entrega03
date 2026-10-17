from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from uuid import UUID

from .anuncio import Anuncio, AnuncioContextual


@dataclass(frozen=True)
class Tag:
    nome: str


class StatusCampanha(str, Enum):
    ATIVA = "ATIVA"
    PAUSADA = "PAUSADA"
    ESGOTADA = "ESGOTADA"
    SUSPENSA = "SUSPENSA"
    ENCERRADA = "ENCERRADA"
    CANCELADA = "CANCELADA"


def _validar_valor_monetario(nome: str, valor: Decimal) -> None:
    if not isinstance(valor, Decimal):
        raise TypeError(f"{nome} deve ser Decimal.")
    if not valor.is_finite() or valor < 0:
        raise ValueError(f"{nome} deve ser finito e não negativo.")


@dataclass
class Campanha:
    id: UUID
    tags_alvo: list[Tag]
    orcamento: Decimal
    saldo_restante: Decimal
    custo_por_clique: Decimal
    status: StatusCampanha = StatusCampanha.PAUSADA
    anuncios: list[Anuncio] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validar_valor_monetario("orcamento", self.orcamento)
        _validar_valor_monetario("saldo_restante", self.saldo_restante)
        _validar_valor_monetario("custo_por_clique", self.custo_por_clique)
        if self.saldo_restante > self.orcamento:
            raise ValueError("O saldo restante não pode exceder o orçamento.")
        if not isinstance(self.status, StatusCampanha):
            raise TypeError("status deve ser StatusCampanha.")
        if any(not isinstance(anuncio, AnuncioContextual) for anuncio in self.anuncios):
            raise ValueError("Campanhas só podem conter anúncios contextuais.")
        if self.esta_ativa():
            self._validar_anuncios_para_ativacao()

    def esta_ativa(self) -> bool:
        return self.status == StatusCampanha.ATIVA

    def possui_orcamento(self) -> bool:
        return self.custo_por_clique > 0 and self.saldo_restante >= self.custo_por_clique

    def possui_tag(self, tag: Tag) -> bool:
        nome = tag.nome.casefold()
        return any(alvo.nome.casefold() == nome for alvo in self.tags_alvo)

    def ativar(self) -> None:
        self._validar_anuncios_para_ativacao()
        self.status = StatusCampanha.ATIVA

    def _validar_anuncios_para_ativacao(self) -> None:
        if not self.anuncios or any(
            not isinstance(anuncio, AnuncioContextual) for anuncio in self.anuncios
        ):
            raise ValueError("A ativação exige ao menos um anúncio contextual.")

    def debitar_clique(self, valor: Decimal) -> None:
        _validar_valor_monetario("valor", valor)
        if valor == 0:
            raise ValueError("O valor do clique deve ser positivo.")
        if not self.esta_ativa():
            raise ValueError("A campanha deve estar ativa para receber cliques.")
        if not self.possui_orcamento() or valor > self.saldo_restante:
            raise ValueError("Saldo insuficiente para debitar o clique.")

        self.saldo_restante -= valor
        if not self.possui_orcamento():
            self.status = StatusCampanha.ESGOTADA
