"""Restrições explícitas dos dados e resultados do Diagrama de Classes."""

from datetime import date
import unittest

from subequipe02.contratos import CotaDiaria, ServicoVotacao
from subequipe02.dominio import (
    CodigoResultado,
    ConteudoVotavel,
    EventoReputacao,
    ResultadoVotacao,
    Usuario,
    Voto,
)


class TestContratosEDominio(unittest.TestCase):
    def setUp(self):
        self.autor = Usuario("A1", 100)
        self.votante = Usuario("V1", 20)
        self.alvo = ConteudoVotavel("P101", "pergunta", self.autor, 0)
        self.voto = Voto(self.votante, self.alvo, date(2026, 10, 16))
        self.evento = EventoReputacao(self.voto, self.autor)

    def test_interfaces_nao_podem_ser_instanciadas(self):
        for interface in (ServicoVotacao, CotaDiaria):
            with self.subTest(interface=interface.__name__):
                with self.assertRaises(TypeError):
                    interface()

    def test_sucesso_preserva_referencias_do_voto_e_evento(self):
        resultado = ResultadoVotacao(
            CodigoResultado.REGISTRADO, "Voto registrado.", self.voto, self.evento
        )
        self.assertIs(resultado.voto, self.voto)
        self.assertIs(resultado.evento, self.evento)
        self.assertIs(self.evento.voto, self.voto)
        self.assertEqual(self.evento.variacao, 10)

    def test_sucesso_exige_ambos_os_registros(self):
        for voto, evento in (
            (None, None), (self.voto, None), (None, self.evento)
        ):
            with self.subTest(voto=voto, evento=evento):
                with self.assertRaises(ValueError):
                    ResultadoVotacao(CodigoResultado.REGISTRADO, "Sucesso", voto, evento)

    def test_rejeicoes_admitem_somente_registros_ausentes(self):
        for codigo in (
            CodigoResultado.REPUTACAO_INSUFICIENTE, CodigoResultado.COTA_ESGOTADA
        ):
            with self.subTest(codigo=codigo):
                resultado = ResultadoVotacao(codigo, "Pedido rejeitado.")
                self.assertIsNone(resultado.voto)
                self.assertIsNone(resultado.evento)
            for voto, evento in (
                (self.voto, None), (None, self.evento), (self.voto, self.evento)
            ):
                with self.subTest(codigo=codigo, voto=voto, evento=evento):
                    with self.assertRaises(ValueError):
                        ResultadoVotacao(codigo, "Rejeição", voto, evento)

    def test_resultado_rejeita_codigo_fora_do_enum(self):
        with self.assertRaises(ValueError):
            ResultadoVotacao("OUTRO", "Código inválido.")

    def test_evento_nao_pode_beneficiar_votante_ou_copia_do_autor(self):
        for beneficiario in (self.votante, Usuario("A1", 100)):
            with self.subTest(beneficiario=beneficiario):
                with self.assertRaises(ValueError):
                    EventoReputacao(self.voto, beneficiario)

    def test_conteudo_simulado_restringe_tipo_a_pergunta_ou_resposta(self):
        for tipo in ("pergunta", "resposta"):
            with self.subTest(tipo=tipo):
                self.assertEqual(
                    ConteudoVotavel("C1", tipo, self.autor, 0).tipo, tipo
                )
        with self.assertRaises(ValueError):
            ConteudoVotavel("C1", "comentario", self.autor, 0)


if __name__ == "__main__":
    unittest.main()
