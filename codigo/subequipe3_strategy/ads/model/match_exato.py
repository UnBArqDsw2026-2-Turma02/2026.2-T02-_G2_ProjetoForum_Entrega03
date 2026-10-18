from .anuncio import Anuncio, AnuncioContextual
from .campanha import Campanha
from .contexto import Pergunta


class EstrategiaMatchExatoDeTag:
    def obter_nome(self) -> str:
        return "match_exato"

    def selecionar_anuncio(
        self, pergunta: Pergunta, campanhas: list[Campanha]
    ) -> Anuncio | None:
        tags = pergunta.obter_tags()
        candidatos = (
            (campanha.id.int, anuncio.id.int, anuncio)
            for campanha in campanhas
            if campanha.esta_ativa() and campanha.possui_orcamento()
            if any(campanha.possui_tag(tag) for tag in tags)
            for anuncio in campanha.anuncios
            if isinstance(anuncio, AnuncioContextual)
        )
        vencedor = min(candidatos, key=lambda item: item[:2], default=None)
        return vencedor[2] if vencedor is not None else None
