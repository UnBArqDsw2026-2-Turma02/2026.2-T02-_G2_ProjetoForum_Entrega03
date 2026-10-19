"""Verifica acesso e delegação; não simula os efeitos do serviço real."""

from dataclasses import asdict
from datetime import date
import unittest
from unittest.mock import Mock, call, create_autospec

from subequipe02.contratos import CotaDiaria, ServicoVotacao
from subequipe02.dominio import (
    CodigoResultado,
    ConteudoVotavel,
    EventoReputacao,
    ResultadoVotacao,
    SolicitacaoVotoPositivo,
    Usuario,
    Voto,
)
from subequipe02.proxy import ProxyProtecaoVotacao


class TestProxyProtecaoVotacao(unittest.TestCase):
    def setUp(self) -> None:
        self.dia = date(2026, 10, 16)
        self.autor = Usuario(id="A1", reputacao=100)
        self.alvo = ConteudoVotavel(
            id="P101", tipo="pergunta", autor=self.autor, placar=0
        )
        self.votante = Usuario(id="V1", reputacao=20)
        self.s = SolicitacaoVotoPositivo(self.votante, self.alvo, self.dia)
        self.cota = create_autospec(CotaDiaria, instance=True, spec_set=True)
        self.real = create_autospec(ServicoVotacao, instance=True, spec_set=True)
        self.chamadas = Mock()
        self.chamadas.attach_mock(self.cota, "cota")
        self.chamadas.attach_mock(self.real, "real")
        self.proxy = ProxyProtecaoVotacao(real=self.real, cota=self.cota)

    def configurar_cota(self, uso: int) -> None:
        # Respostas fixas por cenário: não implementam a cota em memória.
        self.cota.consultar_uso.return_value = uso
        self.cota.disponivel.return_value = uso < 3
        self.cota.registrar_consumo.side_effect = AssertionError(
            "O Proxy não pode consumir a cota."
        )

    def preparar_resultado(self) -> ResultadoVotacao:
        # Registros de resposta predefinidos, sem atualizar o domínio ou a cota.
        voto = Voto(self.votante, self.alvo, self.dia)
        evento = EventoReputacao(voto, self.autor)
        resultado = ResultadoVotacao(
            CodigoResultado.REGISTRADO, "Voto registrado.", voto, evento
        )
        self.real.votar.return_value = resultado
        return resultado

    def estado_dominio(self) -> dict:
        return asdict(self.s)

    def conferir_rejeicao(self, resultado: ResultadoVotacao, codigo: CodigoResultado):
        self.assertIs(resultado.codigo, codigo)
        self.assertTrue(resultado.mensagem.strip())
        self.assertIsNone(resultado.voto)
        self.assertIsNone(resultado.evento)
        self.real.votar.assert_not_called()
        self.cota.registrar_consumo.assert_not_called()

    def test_c01_delega_uma_vez_apos_consultar_cota_e_preserva_identidades(self):
        self.configurar_cota(0)
        esperado = self.preparar_resultado()
        antes = self.estado_dominio()

        resultado = self.proxy.votar(self.s)

        self.assertIsInstance(self.proxy, ServicoVotacao)
        self.assertIs(self.proxy.real, self.real)
        self.assertIs(self.proxy.cota, self.cota)
        self.assertIs(resultado, esperado)
        self.assertIs(self.real.votar.call_args.args[0], self.s)
        self.assertIs(resultado.voto.alvo, self.alvo)
        self.assertIs(resultado.evento.beneficiario, self.autor)
        self.assertEqual(
            self.chamadas.mock_calls,
            [call.cota.disponivel("V1", self.dia), call.real.votar(self.s)],
        )
        self.assertEqual(self.estado_dominio(), antes)
        self.assertEqual(self.cota.consultar_uso.return_value, 0)

    def test_c02_rejeita_reputacao_sem_qualquer_chamada_a_cota_ou_servico(self):
        self.votante.id = "V2"
        self.votante.reputacao = 14
        self.configurar_cota(0)
        antes = self.estado_dominio()

        resultado = self.proxy.votar(self.s)

        self.conferir_rejeicao(resultado, CodigoResultado.REPUTACAO_INSUFICIENTE)
        self.assertIn("padrão", resultado.mensagem)
        self.assertIn("15", resultado.mensagem)
        self.assertEqual(self.chamadas.mock_calls, [])
        self.assertEqual(self.estado_dominio(), antes)
        self.assertEqual(self.cota.consultar_uso.return_value, 0)

    def test_c03_rejeita_cota_esgotada_sem_delegacao_ou_consumo(self):
        self.configurar_cota(3)
        antes = self.estado_dominio()

        resultado = self.proxy.votar(self.s)

        self.conferir_rejeicao(resultado, CodigoResultado.COTA_ESGOTADA)
        self.assertEqual(
            self.chamadas.mock_calls, [call.cota.disponivel("V1", self.dia)]
        )
        self.assertEqual(self.estado_dominio(), antes)
        self.assertEqual(self.cota.consultar_uso.return_value, 3)

    def test_reputacao_exatamente_15_permite_delegacao(self):
        self.votante.reputacao = 15
        self.configurar_cota(0)
        esperado = self.preparar_resultado()

        self.assertIs(self.proxy.votar(self.s), esperado)
        self.real.votar.assert_called_once_with(self.s)
        self.cota.disponivel.assert_called_once_with("V1", self.dia)
        self.cota.registrar_consumo.assert_not_called()

    def test_reputacao_prevalece_quando_a_cota_tambem_esta_esgotada(self):
        self.votante.id = "V2"
        self.votante.reputacao = 14
        self.configurar_cota(3)
        antes = self.estado_dominio()

        resultado = self.proxy.votar(self.s)

        self.conferir_rejeicao(resultado, CodigoResultado.REPUTACAO_INSUFICIENTE)
        self.assertEqual(self.chamadas.mock_calls, [])
        self.assertEqual(self.estado_dominio(), antes)
        self.assertEqual(self.cota.consultar_uso.return_value, 3)

    def test_consulta_cota_com_id_e_dia_recebidos_sem_valores_fixos(self):
        self.votante.id = "V9"
        outro_dia = date(2026, 10, 17)
        s = SolicitacaoVotoPositivo(self.votante, self.alvo, outro_dia)
        self.configurar_cota(3)

        resultado = self.proxy.votar(s)

        self.conferir_rejeicao(resultado, CodigoResultado.COTA_ESGOTADA)
        self.cota.disponivel.assert_called_once_with("V9", outro_dia)

    def test_mesmo_contrato_admite_resposta_comum(self):
        self.alvo.id = "R101"
        self.alvo.tipo = "resposta"
        self.configurar_cota(0)
        esperado = self.preparar_resultado()

        self.assertIs(self.proxy.votar(self.s), esperado)
        self.real.votar.assert_called_once_with(self.s)
        self.cota.registrar_consumo.assert_not_called()


if __name__ == "__main__":
    unittest.main()
