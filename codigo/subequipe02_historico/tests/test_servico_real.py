"""Serviço real isolado: filtra os votos existentes sem alterar dados."""

from datetime import date
import unittest

from subequipe02.dominio import Voto
from subequipe02_historico.contratos import ServicoConsultaHistorico
from subequipe02_historico.dados import criar_base
from subequipe02_historico.dominio import (
    CodigoConsulta,
    SolicitacaoConsultaHistorico,
)
from subequipe02_historico.servico_real import ServicoConsultaHistoricoReal


class TestServicoConsultaHistoricoReal(unittest.TestCase):
    def setUp(self) -> None:
        self.base = criar_base()
        self.real = ServicoConsultaHistoricoReal(self.base.votos)

    def consultar(self, solicitante_id: str, consultado_id: str):
        s = SolicitacaoConsultaHistorico(
            self.base.participantes[solicitante_id], consultado_id
        )
        return self.real.consultar(s)

    def test_implementa_o_contrato_comum(self):
        self.assertIsInstance(self.real, ServicoConsultaHistorico)

    def test_filtra_somente_os_votos_do_usuario_consultado(self):
        resultado = self.consultar("V1", "V1")

        self.assertIs(resultado.codigo, CodigoConsulta.CONSULTADO)
        self.assertEqual(resultado.usuario_id, "V1")
        self.assertEqual(
            [(v.votante.id, v.alvo.id, v.dia) for v in resultado.votos],
            [("V1", "P101", date(2026, 10, 16)), ("V1", "R101", date(2026, 10, 17))],
        )

    def test_devolve_os_mesmos_objetos_armazenados(self):
        resultado = self.consultar("V2", "V2")

        self.assertEqual(len(resultado.votos), 1)
        self.assertIs(resultado.votos[0], self.base.votos[1])

    def test_usuario_sem_votos_retorna_lista_vazia(self):
        resultado = self.consultar("A1", "A1")

        self.assertIs(resultado.codigo, CodigoConsulta.CONSULTADO)
        self.assertEqual(resultado.votos, ())

    def test_nao_aplica_regra_de_permissao(self):
        # A autorização é do Proxy: o serviço real só busca pelo ID pedido.
        resultado = self.consultar("V2", "V1")

        self.assertEqual(len(resultado.votos), 2)

    def test_enxerga_registros_adicionados_depois(self):
        self.base.votos.append(
            Voto(
                self.base.usuarios["V2"],
                self.base.conteudos["R101"],
                date(2026, 10, 18),
            )
        )

        self.assertEqual(len(self.consultar("V2", "V2").votos), 2)

    def test_consulta_nao_modifica_votos_placares_ou_reputacoes(self):
        votos_antes = list(self.base.votos)
        placares = {k: c.placar for k, c in self.base.conteudos.items()}
        reputacoes = {k: u.reputacao for k, u in self.base.usuarios.items()}

        self.consultar("V1", "V1")
        self.consultar("M1", "V2")

        self.assertEqual(self.base.votos, votos_antes)
        self.assertEqual(
            placares, {k: c.placar for k, c in self.base.conteudos.items()}
        )
        self.assertEqual(
            reputacoes, {k: u.reputacao for k, u in self.base.usuarios.items()}
        )


if __name__ == "__main__":
    unittest.main()
