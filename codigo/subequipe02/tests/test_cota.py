"""Testes isolados para CotaDiariaEmMemoria."""

from datetime import date
import unittest

from subequipe02.cota import CotaDiariaEmMemoria
from subequipe02.contratos import CotaDiaria


class TestCotaDiariaEmMemoria(unittest.TestCase):
    def setUp(self) -> None:
        self.cota = CotaDiariaEmMemoria()
        self.dia = date(2026, 10, 16)
        self.outro_dia = date(2026, 10, 17)

    def test_implementa_contrato_e_limite_padrao(self):
        self.assertIsInstance(self.cota, CotaDiaria)
        self.assertEqual(self.cota.limite, 3)

    def test_uso_ausente_e_zero_sem_criar_entrada(self):
        self.assertEqual(self.cota.consultar_uso("V1", self.dia), 0)
        self.assertEqual(self.cota._consumos, {})
        self.assertTrue(self.cota.disponivel("V1", self.dia))
        self.assertEqual(self.cota._consumos, {})

    def test_consumos_zero_dois_e_tres(self):
        self.assertEqual(self.cota.consultar_uso("V1", self.dia), 0)
        self.cota.registrar_consumo("V1", self.dia)
        self.cota.registrar_consumo("V1", self.dia)
        self.assertEqual(self.cota.consultar_uso("V1", self.dia), 2)
        self.assertTrue(self.cota.disponivel("V1", self.dia))
        self.cota.registrar_consumo("V1", self.dia)
        self.assertEqual(self.cota.consultar_uso("V1", self.dia), 3)
        self.assertFalse(self.cota.disponivel("V1", self.dia))

    def test_limite_configuravel(self):
        cota = CotaDiariaEmMemoria(limite=5)
        for _ in range(4):
            cota.registrar_consumo("V1", self.dia)
        self.assertTrue(cota.disponivel("V1", self.dia))
        cota.registrar_consumo("V1", self.dia)
        self.assertEqual(cota.consultar_uso("V1", self.dia), 5)
        self.assertFalse(cota.disponivel("V1", self.dia))

    def test_limite_nao_positivo_ou_nao_inteiro_e_rejeitado(self):
        for limite in (0, -1, 1.5, "3", True, None):
            with self.subTest(limite=limite):
                with self.assertRaises(ValueError):
                    CotaDiariaEmMemoria(limite=limite)

    def test_consultas_nao_mutam_consumos_existentes(self):
        self.cota.registrar_consumo("V1", self.dia)
        antes = self.cota._consumos.copy()
        for _ in range(2):
            self.cota.consultar_uso("V1", self.dia)
            self.cota.disponivel("V1", self.dia)
            self.cota.consultar_uso("desconhecido", self.outro_dia)
            self.cota.disponivel("desconhecido", self.outro_dia)
        self.assertEqual(self.cota._consumos, antes)

    def test_registrar_consumo_incrementa_exatamente_um_e_retorna_none(self):
        retorno = self.cota.registrar_consumo("V1", self.dia)
        self.assertIsNone(retorno)
        self.assertEqual(self.cota.consultar_uso("V1", self.dia), 1)
        self.cota.registrar_consumo("V1", self.dia)
        self.assertEqual(self.cota.consultar_uso("V1", self.dia), 2)

    def test_usuarios_e_datas_sao_independentes(self):
        self.cota.registrar_consumo("V1", self.dia)
        self.cota.registrar_consumo("V1", self.dia)
        self.cota.registrar_consumo("V2", self.dia)
        self.cota.registrar_consumo("V1", self.outro_dia)
        self.assertEqual(self.cota.consultar_uso("V1", self.dia), 2)
        self.assertEqual(self.cota.consultar_uso("V2", self.dia), 1)
        self.assertEqual(self.cota.consultar_uso("V1", self.outro_dia), 1)
        self.assertEqual(self.cota.consultar_uso("V2", self.outro_dia), 0)

    def test_data_e_recebida_explicitamente_sem_dependencia_do_relogio(self):
        dia_passado = date(2020, 1, 1)
        self.cota.registrar_consumo("V1", dia_passado)
        self.assertEqual(self.cota.consultar_uso("V1", dia_passado), 1)
        self.assertEqual(self.cota.consultar_uso("V1", self.dia), 0)

    def test_c03_pode_preconfigurar_cota_esgotada_sem_votos_em_p101(self):
        # Simula apenas o estado da cota; não cria Voto, Evento ou alvo P101.
        for _ in range(3):
            self.cota.registrar_consumo("V1", self.dia)
        self.assertEqual(self.cota.consultar_uso("V1", self.dia), 3)
        self.assertFalse(self.cota.disponivel("V1", self.dia))
        self.assertEqual(set(self.cota._consumos), {("V1", self.dia)})


if __name__ == "__main__":
    unittest.main()
