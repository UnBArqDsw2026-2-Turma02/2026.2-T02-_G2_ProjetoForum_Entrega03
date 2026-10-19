"""Efeitos do serviço real isolado, com cota substituída pelo contrato."""

from datetime import date
import unittest
from unittest.mock import call, create_autospec

from subequipe02.contratos import CotaDiaria, ServicoVotacao
from subequipe02.dominio import (
    CodigoResultado,
    ConteudoVotavel,
    SolicitacaoVotoPositivo,
    Usuario,
)
from subequipe02.servico_real import ServicoVotacaoReal


class TestServicoVotacaoReal(unittest.TestCase):
    def setUp(self) -> None:
        self.dia = date(2026, 10, 16)
        self.autor = Usuario(id="A1", reputacao=100)
        self.votante = Usuario(id="V1", reputacao=20)
        self.alvo = ConteudoVotavel("P101", "pergunta", self.autor, 0)
        self.s = SolicitacaoVotoPositivo(self.votante, self.alvo, self.dia)
        self.cota = create_autospec(CotaDiaria, instance=True, spec_set=True)
        self.real = ServicoVotacaoReal(self.cota)

    def test_implementa_contrato_e_inicia_sem_registros(self):
        self.assertIsInstance(self.real, ServicoVotacao)
        self.assertIs(self.real.cota, self.cota)
        self.assertEqual(len(self.real.votos), 0)
        self.assertEqual(len(self.real.eventos), 0)
        self.assertEqual(self.cota.mock_calls, [])

    def test_c01_registra_efeitos_referencias_e_consumo_unico(self):
        resultado = self.real.votar(self.s)

        self.assertIs(resultado.codigo, CodigoResultado.REGISTRADO)
        self.assertTrue(resultado.mensagem.strip())
        self.assertEqual(len(self.real.votos), 1)
        self.assertEqual(len(self.real.eventos), 1)
        self.assertIs(resultado.voto, self.real.votos[0])
        self.assertIs(resultado.evento, self.real.eventos[0])
        self.assertIs(resultado.voto.votante, self.votante)
        self.assertIs(resultado.voto.alvo, self.alvo)
        self.assertEqual(resultado.voto.dia, self.dia)
        self.assertIs(resultado.evento.voto, resultado.voto)
        self.assertIs(resultado.evento.beneficiario, self.autor)
        self.assertEqual(resultado.evento.variacao, 10)
        self.assertEqual(self.alvo.placar, 1)
        self.assertEqual(self.autor.reputacao, 110)
        self.assertEqual(self.votante.reputacao, 20)
        self.assertEqual(
            self.cota.mock_calls, [call.registrar_consumo("V1", self.dia)]
        )

    def test_mesmo_servico_admite_resposta_simulada(self):
        resposta = ConteudoVotavel("R101", "resposta", self.autor, 4)
        s = SolicitacaoVotoPositivo(self.votante, resposta, self.dia)

        resultado = self.real.votar(s)

        self.assertIs(resultado.codigo, CodigoResultado.REGISTRADO)
        self.assertIs(resultado.voto.alvo, resposta)
        self.assertIs(resultado.evento.beneficiario, self.autor)
        self.assertEqual(resposta.placar, 5)
        self.assertEqual(self.alvo.placar, 0)
        self.assertEqual(self.autor.reputacao, 110)
        self.assertEqual(self.votante.reputacao, 20)
        self.assertEqual(
            self.cota.mock_calls, [call.registrar_consumo("V1", self.dia)]
        )

    def test_solicitacoes_distintas_preservam_registros_e_usam_seus_dados(self):
        primeiro = self.real.votar(self.s)
        outro_autor = Usuario("A2", 50)
        outro_votante = Usuario("V9", 33)
        outro_alvo = ConteudoVotavel("R202", "resposta", outro_autor, 7)
        outro_dia = date(2026, 10, 17)
        outra_s = SolicitacaoVotoPositivo(outro_votante, outro_alvo, outro_dia)

        segundo = self.real.votar(outra_s)

        self.assertEqual(len(self.real.votos), 2)
        self.assertEqual(len(self.real.eventos), 2)
        self.assertIs(self.real.votos[0], primeiro.voto)
        self.assertIs(self.real.eventos[0], primeiro.evento)
        self.assertIs(self.real.votos[1], segundo.voto)
        self.assertIs(self.real.eventos[1], segundo.evento)
        self.assertIsNot(primeiro.voto, segundo.voto)
        self.assertIsNot(primeiro.evento, segundo.evento)
        self.assertIs(segundo.voto.votante, outro_votante)
        self.assertIs(segundo.voto.alvo, outro_alvo)
        self.assertEqual(segundo.voto.dia, outro_dia)
        self.assertIs(segundo.evento.voto, segundo.voto)
        self.assertIs(segundo.evento.beneficiario, outro_autor)
        self.assertEqual(self.alvo.placar, 1)
        self.assertEqual(self.autor.reputacao, 110)
        self.assertEqual(outro_alvo.placar, 8)
        self.assertEqual(outro_autor.reputacao, 60)
        self.assertEqual(self.votante.reputacao, 20)
        self.assertEqual(outro_votante.reputacao, 33)
        self.assertEqual(
            self.cota.mock_calls,
            [
                call.registrar_consumo("V1", self.dia),
                call.registrar_consumo("V9", outro_dia),
            ],
        )

    def test_instancias_do_servico_mantem_colecoes_independentes(self):
        outro_servico = ServicoVotacaoReal(self.cota)
        primeiro = self.real.votar(self.s)

        self.assertEqual(len(outro_servico.votos), 0)
        self.assertEqual(len(outro_servico.eventos), 0)

        outro_alvo = ConteudoVotavel("R101", "resposta", self.autor, 0)
        outra_s = SolicitacaoVotoPositivo(self.votante, outro_alvo, self.dia)
        segundo = outro_servico.votar(outra_s)

        self.assertEqual(len(self.real.votos), 1)
        self.assertEqual(len(self.real.eventos), 1)
        self.assertEqual(len(outro_servico.votos), 1)
        self.assertEqual(len(outro_servico.eventos), 1)
        self.assertIs(self.real.votos[0], primeiro.voto)
        self.assertIs(self.real.eventos[0], primeiro.evento)
        self.assertIs(outro_servico.votos[0], segundo.voto)
        self.assertIs(outro_servico.eventos[0], segundo.evento)
        self.assertIsNot(primeiro.voto, segundo.voto)
        self.assertIsNot(primeiro.evento, segundo.evento)


if __name__ == "__main__":
    unittest.main()
