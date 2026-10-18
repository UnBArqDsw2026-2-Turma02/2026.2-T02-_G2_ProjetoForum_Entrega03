import pytest

from subequipe3_strategy.ads.model.match_exato import EstrategiaMatchExatoDeTag
from subequipe3_strategy.ads.service.seletor import PoliticaDesconhecida, SeletorDeEstrategia


class EstrategiaNomeada:
    """Dublê que atende ao Protocol, usado para simular uma segunda política."""

    def __init__(self, nome):
        self.nome = nome

    def obter_nome(self):
        return self.nome

    def selecionar_anuncio(self, pergunta, campanhas):
        return None


def test_escolhe_estrategia_registrada_pelo_nome():
    match_exato = EstrategiaMatchExatoDeTag()
    seletor = SeletorDeEstrategia([match_exato])
    assert seletor.escolher("match_exato") is match_exato


def test_alterna_entre_politicas_registradas():
    match_exato = EstrategiaMatchExatoDeTag()
    maior_saldo = EstrategiaNomeada("maior_saldo")
    seletor = SeletorDeEstrategia([match_exato, maior_saldo])
    assert seletor.escolher("maior_saldo") is maior_saldo
    assert seletor.escolher("match_exato") is match_exato
    assert seletor.politicas() == ("maior_saldo", "match_exato")


def test_nova_politica_entra_apenas_por_registro():
    seletor = SeletorDeEstrategia([EstrategiaMatchExatoDeTag()])
    nova = EstrategiaNomeada("nova_politica")
    seletor.registrar(nova)
    assert seletor.escolher("nova_politica") is nova


def test_politica_desconhecida_e_erro_explicito():
    seletor = SeletorDeEstrategia([EstrategiaMatchExatoDeTag()])
    with pytest.raises(PoliticaDesconhecida, match="maior_lance.*match_exato"):
        seletor.escolher("maior_lance")


def test_seletor_vazio_informa_que_nao_ha_politicas():
    with pytest.raises(PoliticaDesconhecida, match="nenhuma"):
        SeletorDeEstrategia().escolher("match_exato")


def test_rejeita_nome_duplicado():
    seletor = SeletorDeEstrategia([EstrategiaMatchExatoDeTag()])
    with pytest.raises(ValueError, match="já está registrada"):
        seletor.registrar(EstrategiaMatchExatoDeTag())


@pytest.mark.parametrize("nome", ["", None])
def test_rejeita_nome_invalido(nome):
    with pytest.raises(ValueError):
        SeletorDeEstrategia([EstrategiaNomeada(nome)])


def test_rejeita_objeto_que_nao_atende_ao_contrato():
    with pytest.raises(TypeError):
        SeletorDeEstrategia([object()])
