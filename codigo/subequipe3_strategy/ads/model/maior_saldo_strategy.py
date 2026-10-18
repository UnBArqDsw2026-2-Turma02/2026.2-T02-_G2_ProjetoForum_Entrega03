"""Issue #28 â€” EstratÃ©giaMaiorSaldoNaTag: polÃ­tica contextual por maior saldo."""

from .anuncio import Anuncio, AnuncioContextual
from .campanha import Campanha
from .contexto import Pergunta


class EstrategiaMaiorSaldoNaTag:
    """Seleciona o anÃºncio contextual da campanha elegÃ­vel com maior saldo restante.

    Empate: menor ID da campanha e, em seguida, menor ID do anÃºncio.
    NÃ£o executa fallback nem altera saldo/mÃ©tricas.
    """

    def obter_nome(self) -> str:
        return "maior_saldo"

    def selecionar_anuncio(
        self, pergunta: Pergunta, campanhas: list[Campanha]
    ) -> Anuncio | None:
        tags = pergunta.obter_tags()
        candidatos = (
            (campanha.saldo_restante, campanha.id.int, anuncio.id.int, anuncio)
            for campanha in campanhas
            if campanha.esta_ativa() and campanha.possui_orcamento()
            if any(campanha.possui_tag(tag) for tag in tags)
            for anuncio in campanha.anuncios
            if isinstance(anuncio, AnuncioContextual)
        )
        # Maior saldo; em empate, menor ID de campanha e depois menor ID de anÃºncio.
        vencedor = max(
            candidatos,
            key=lambda item: (item[0], -item[1], -item[2]),
            default=None,
        )
        return vencedor[3] if vencedor is not None else None
