"""Proxy isolado: permissão verificada, delegação só quando permitida."""

import unittest
from unittest.mock import call, create_autospec

from subequipe02_historico.contratos import ServicoConsultaHistorico
from subequipe02_historico.dominio import (
    CodigoConsulta,
    Participante,
    Perfil,
    ResultadoConsultaHistorico,
    SolicitacaoConsultaHistorico,
)
from subequipe02_historico.proxy import ProxyConsultaHistorico


class TestProxyConsultaHistorico(unittest.TestCase):
    def setUp(self) -> None:
        self.real = create_autospec(
            ServicoConsultaHistorico, instance=True, spec_set=True
        )
        self.resultado_real = ResultadoConsultaHistorico(
            CodigoConsulta.CONSULTADO, "ok", "V1"
        )
        self.real.consultar.return_value = self.resultado_real
        self.proxy = ProxyConsultaHistorico(self.real)

    def solicitacao(self, solicitante: Participante, consultado_id: str):
        return SolicitacaoConsultaHistorico(solicitante, consultado_id)

    def test_implementa_o_contrato_comum(self):
        self.assertIsInstance(self.proxy, ServicoConsultaHistorico)

    def test_h01_proprio_historico_delega_uma_vez_com_a_mesma_solicitacao(self):
        s = self.solicitacao(Participante("V1", Perfil.COMUM), "V1")

        resultado = self.proxy.consultar(s)

        self.assertIs(resultado, self.resultado_real)
        self.assertEqual(self.real.mock_calls, [call.consultar(s)])
        self.assertIs(self.real.consultar.call_args.args[0], s)

    def test_h02_outro_usuario_comum_e_rejeitado_sem_delegar(self):
        s = self.solicitacao(Participante("V2", Perfil.COMUM), "V1")

        resultado = self.proxy.consultar(s)

        self.assertIs(resultado.codigo, CodigoConsulta.ACESSO_NEGADO)
        self.assertEqual(resultado.usuario_id, "V1")
        self.assertEqual(resultado.votos, ())
        self.assertTrue(resultado.mensagem.strip())
        self.assertEqual(self.real.mock_calls, [])

    def test_h03_moderador_consulta_historico_de_outro_usuario(self):
        s = self.solicitacao(Participante("M1", Perfil.MODERADOR), "V2")

        resultado = self.proxy.consultar(s)

        self.assertIs(resultado, self.resultado_real)
        self.assertEqual(self.real.mock_calls, [call.consultar(s)])

    def test_moderador_tambem_consulta_o_proprio_historico(self):
        s = self.solicitacao(Participante("M1", Perfil.MODERADOR), "M1")

        self.proxy.consultar(s)

        self.assertEqual(self.real.consultar.call_count, 1)

    def test_o_papel_vem_do_participante_e_nao_do_id(self):
        # Um ID parecido com o do moderador, mas com perfil comum, é rejeitado.
        s = self.solicitacao(Participante("M1", Perfil.COMUM), "V1")

        resultado = self.proxy.consultar(s)

        self.assertIs(resultado.codigo, CodigoConsulta.ACESSO_NEGADO)
        self.assertEqual(self.real.mock_calls, [])


class TestResultadoConsultaHistorico(unittest.TestCase):
    def test_rejeicao_nao_aceita_votos(self):
        with self.assertRaises(ValueError):
            ResultadoConsultaHistorico(
                CodigoConsulta.ACESSO_NEGADO, "x", "V1", votos=(object(),)
            )

    def test_codigo_deve_ser_do_enum(self):
        with self.assertRaises(ValueError):
            ResultadoConsultaHistorico("CONSULTADO", "x", "V1")


if __name__ == "__main__":
    unittest.main()
