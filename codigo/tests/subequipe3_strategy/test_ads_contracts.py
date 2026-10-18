from decimal import Decimal
from uuid import UUID

import pytest
from pydantic import ValidationError

from subequipe3_strategy.ads.model.anuncio import (
    Anuncio, AnuncioGenerico, EstatisticasAds, FormatoAnuncio,
)
from subequipe3_strategy.ads.model.campanha import Campanha, StatusCampanha, Tag
from subequipe3_strategy.ads.model.contexto import Pergunta, projetar_pergunta
from subequipe3_strategy.ads.model.strategies import EstrategiaSelecaoAnuncio
from subequipe3_strategy.ads.view.schemas import AnuncioResponse
from subequipe1_factory_method.produtos import Pergunta as PerguntaConteudo


def test_anuncio_abstrato():
    with pytest.raises(TypeError):
        Anuncio(UUID(int=1), "Título", "/banner", "/destino")


def test_protocol_aceita_estrategia_sem_heranca():
    class EstrategiaVazia:
        def selecionar_anuncio(self, pergunta, campanhas):
            return None

        def obter_nome(self):
            return "vazia"

    estrategia = EstrategiaVazia()
    assert isinstance(estrategia, EstrategiaSelecaoAnuncio)
    assert estrategia.selecionar_anuncio(Pergunta(UUID(int=1), "Título"), []) is None


def test_projecao_preserva_identidade_sem_modificar_conteudo():
    original = PerguntaConteudo("Corpo", "Título", "Maria")
    tags = [Tag("python")]
    projecao = projetar_pergunta(original, tags)
    assert projecao.id == original.id
    assert projecao.titulo == original.titulo
    assert projecao.obter_tags() == tags
    assert not hasattr(original, "tags")
    tags.clear()
    copia = projecao.obter_tags()
    copia.clear()
    assert projecao.obter_tags() == [Tag("python")]
    with pytest.raises(TypeError):
        projetar_pergunta(original)


def test_renderizacao_escapa_atributos_e_mensagem(criar_anuncio):
    anuncio = criar_anuncio(titulo='<img onerror="teste">', banner_url="/img?a=1&b=2")
    html = anuncio.renderizar()
    assert 'alt="&lt;img onerror=&quot;teste&quot;&gt;"' in html
    assert 'src="/img?a=1&amp;b=2"' in html
    generico = AnuncioGenerico(
        UUID(int=2), "Fórum", "/img", "/", mensagem_padrao="<script>teste</script>"
    )
    assert "<span>&lt;script&gt;teste&lt;/script&gt;</span>" in generico.renderizar()


def test_imagem_contextual_especifica(criar_anuncio):
    html = criar_anuncio(imagem_banner="/outra-imagem.png").renderizar()
    assert 'src="/outra-imagem.png"' in html


@pytest.mark.parametrize("url", [
    "javascript:alert(1)", "data:text/html,teste", "//example.org/img", "",
    "/\\example.org/img", "/imagem\n.png", " https://example.org",
    "https:///sem-host", "https://[host-invalido",
])
@pytest.mark.parametrize("campo", ["link_destino", "banner_url"])
def test_urls_invalidas_rejeitadas(criar_anuncio, campo, url):
    with pytest.raises(ValueError):
        criar_anuncio(**{campo: url})


@pytest.mark.parametrize("campo", ["link_destino", "imagem_banner"])
def test_mutacao_nao_contorna_validacao_html(criar_anuncio, campo):
    anuncio = criar_anuncio()
    setattr(anuncio, campo, "javascript:alert(1)")
    with pytest.raises(ValueError):
        anuncio.renderizar()


@pytest.mark.parametrize("formato", [FormatoAnuncio.NATIVE, FormatoAnuncio.VIDEO])
def test_formato_futuro_nao_renderiza_como_banner(criar_anuncio, formato):
    with pytest.raises(NotImplementedError):
        criar_anuncio(formato=formato).renderizar()


def test_estatisticas_estaveis_e_renderizacao_sem_eventos(criar_anuncio):
    anuncio = criar_anuncio()
    stats = anuncio.obter_estatisticas()
    anuncio.renderizar()
    anuncio.renderizar()
    assert stats is anuncio.obter_estatisticas()
    assert stats.anuncio_id == anuncio.id
    assert (stats.visualizacoes, stats.cliques) == (0, 0)
    stats.incrementar_visualizacao()
    stats.incrementar_clique()
    assert (stats.visualizacoes, stats.cliques) == (1, 1)
    assert criar_anuncio().obter_estatisticas().cliques == 0


@pytest.mark.parametrize("campo", ["visualizacoes", "cliques"])
@pytest.mark.parametrize("valor", [-1, 0.5, True])
def test_estatisticas_invalidas(campo, valor):
    with pytest.raises(ValueError):
        EstatisticasAds(UUID(int=1), **{campo: valor})


def test_dto_le_anuncio_e_serializa_uuid_enum(criar_anuncio):
    anuncio = criar_anuncio()
    dto = AnuncioResponse.model_validate(anuncio)
    assert dto.id == anuncio.id
    assert dto.model_dump(mode="json")["id"] == str(anuncio.id)
    assert dto.model_dump(mode="json")["formato"] == "BANNER"
    assert "_estatisticas" not in dto.model_dump()


def test_dto_rejeita_url_executavel(criar_anuncio):
    dados = AnuncioResponse.model_validate(criar_anuncio()).model_dump()
    dados["link_destino"] = "javascript:alert(1)"
    with pytest.raises(ValidationError):
        AnuncioResponse.model_validate(dados)


def test_ativacao_requer_anuncio_contextual(criar_campanha, criar_anuncio):
    campanha = criar_campanha(status=StatusCampanha.PAUSADA, anuncios=[])
    with pytest.raises(ValueError):
        campanha.ativar()
    assert campanha.status == StatusCampanha.PAUSADA
    campanha.anuncios.append(criar_anuncio())
    campanha.ativar()
    assert campanha.esta_ativa()
    with pytest.raises(ValueError):
        criar_campanha(anuncios=[])
    with pytest.raises(ValueError):
        criar_campanha(anuncios=[AnuncioGenerico(UUID(int=5), "Casa", "/img", "/")])


def test_tags_insensiveis_a_caixa(criar_campanha):
    campanha = criar_campanha()
    assert campanha.possui_tag(Tag("PYTHON"))
    assert not campanha.possui_tag(Tag("java"))


def test_saldo_exato_e_esgotamento(criar_campanha):
    campanha = criar_campanha(saldo_restante=Decimal("0.30"), custo_por_clique=Decimal("0.10"))
    for esperado in (Decimal("0.20"), Decimal("0.10"), Decimal("0.00")):
        assert campanha.possui_orcamento()
        campanha.debitar_clique(Decimal("0.10"))
        assert campanha.saldo_restante == esperado
    assert campanha.status == StatusCampanha.ESGOTADA


@pytest.mark.parametrize("valor", [Decimal("0"), Decimal("-1"), Decimal("11"), Decimal("NaN"), Decimal("Infinity")])
def test_debito_invalido_nao_altera_campanha(criar_campanha, valor):
    campanha = criar_campanha()
    with pytest.raises(ValueError):
        campanha.debitar_clique(valor)
    assert campanha.saldo_restante == Decimal("10.00")
    assert campanha.status == StatusCampanha.ATIVA


@pytest.mark.parametrize("status", [s for s in StatusCampanha if s != StatusCampanha.ATIVA])
def test_status_inativo_nao_recebe_clique(criar_campanha, status):
    campanha = criar_campanha(status=status)
    with pytest.raises(ValueError):
        campanha.debitar_clique(Decimal("1"))
    assert campanha.saldo_restante == Decimal("10")
    assert campanha.status == status


@pytest.mark.parametrize("campo", ["orcamento", "saldo_restante", "custo_por_clique"])
@pytest.mark.parametrize("valor", [Decimal("-1"), Decimal("NaN"), Decimal("Infinity")])
def test_dinheiro_invalido(criar_campanha, campo, valor):
    with pytest.raises(ValueError):
        criar_campanha(**{campo: valor})


@pytest.mark.parametrize("campo", ["orcamento", "saldo_restante", "custo_por_clique"])
def test_float_nao_e_aceito_como_dinheiro(criar_campanha, campo):
    with pytest.raises(TypeError):
        criar_campanha(**{campo: 0.1})


def test_saldo_nao_excede_orcamento(criar_campanha):
    with pytest.raises(ValueError):
        criar_campanha(saldo_restante=Decimal("101"))


def test_listas_padrao_independentes(criar_anuncio):
    dados = dict(tags_alvo=[], orcamento=Decimal("1"), saldo_restante=Decimal("1"), custo_por_clique=Decimal("0.10"))
    a = Campanha(UUID(int=1), **dados)
    b = Campanha(UUID(int=2), **dados)
    a.anuncios.append(criar_anuncio())
    assert b.anuncios == []
