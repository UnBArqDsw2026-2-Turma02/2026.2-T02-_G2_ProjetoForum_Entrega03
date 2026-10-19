"""API e colaboração dos participantes reais, sem servidor HTTP externo."""

from contextlib import ExitStack
from datetime import date
import unittest
from unittest.mock import create_autospec, patch

from fastapi.testclient import TestClient

from subequipe02.app import criar_app
from subequipe02.cliente import ClienteVotacaoFastAPI
from subequipe02.contratos import ServicoVotacao
from subequipe02.dominio import (
    CodigoResultado,
    ConteudoVotavel,
    ResultadoVotacao,
    SolicitacaoVotoPositivo,
    Usuario,
)


class TestClienteVotacaoFastAPI(unittest.TestCase):
    def test_encaminha_mesma_solicitacao_e_devolve_mesmo_resultado(self):
        servico = create_autospec(ServicoVotacao, instance=True, spec_set=True)
        autor, votante = Usuario("A1", 100), Usuario("V2", 14)
        alvo = ConteudoVotavel("P101", "pergunta", autor, 0)
        s = SolicitacaoVotoPositivo(votante, alvo, date(2026, 10, 16))
        resultado = ResultadoVotacao(
            CodigoResultado.REPUTACAO_INSUFICIENTE, "Resultado do serviço."
        )
        servico.votar.return_value = resultado
        cliente = ClienteVotacaoFastAPI(servico)

        self.assertIs(cliente.registrar_voto(s), resultado)
        self.assertIs(servico.votar.call_args.args[0], s)
        servico.votar.assert_called_once_with(s)


class TestIntegracaoFastAPI(unittest.TestCase):
    def setUp(self):
        self.app = criar_app()
        self.http = self.enterContext(TestClient(self.app))

    def preparar(self, cenario="C01"):
        resposta = self.http.post(f"/demo/cenarios/{cenario}")
        self.assertEqual(resposta.status_code, 200)
        return resposta.json()

    def estado(self):
        resposta = self.http.get("/estado")
        self.assertEqual(resposta.status_code, 200)
        return resposta.json()

    def test_composicao_compartilha_cota_e_preserva_identidades(self):
        demo = self.app.state.demonstracao
        self.assertIs(demo.cliente.servico, demo.proxy)
        self.assertIs(demo.proxy.real, demo.real)
        self.assertIs(demo.proxy.cota, demo.cota)
        self.assertIs(demo.real.cota, demo.cota)
        for conteudo in demo.conteudos.values():
            self.assertIs(conteudo.autor, demo.usuarios["A1"])

    def test_entrada_documentacao_e_rotas_disponiveis(self):
        inicio = self.http.get("/")
        self.assertEqual(inicio.status_code, 200)
        self.assertIn("text/html", inicio.headers["content-type"])
        self.assertIn('href="/docs"', inicio.text)
        self.assertIn("Preparar cenário", inicio.text)
        self.assertEqual(self.http.get("/docs").status_code, 200)
        esquema = self.http.get("/openapi.json").json()
        for rota in ("/estado", "/votos", "/demo/cenarios/{cenario}"):
            self.assertIn(rota, esquema["paths"])

    def test_cenarios_c01_c02_c03_pela_api_com_componentes_reais(self):
        casos = (
            ("C01", "V1", 201, "REGISTRADO", 0),
            ("C02", "V2", 403, "REPUTACAO_INSUFICIENTE", 0),
            ("C03", "V1", 429, "COTA_ESGOTADA", 3),
        )
        for cenario, votante_id, status, codigo, uso_inicial in casos:
            with self.subTest(cenario=cenario):
                antes = self.preparar(cenario)
                demo = self.app.state.demonstracao
                self.assertEqual(antes["dia_utc"], "2026-10-16")
                self.assertEqual(antes["limite_diario"], 3)
                self.assertEqual(demo.real.votos, ())
                self.assertEqual(demo.real.eventos, ())
                self.assertEqual(demo.usuarios["A1"].reputacao, 100)
                self.assertEqual(demo.conteudos["P101"].placar, 0)
                self.assertEqual(
                    demo.cota.consultar_uso(votante_id, demo.dia), uso_inicial
                )
                with ExitStack() as espias:
                    cliente = espias.enter_context(patch.object(
                        demo.cliente, "registrar_voto", wraps=demo.cliente.registrar_voto
                    ))
                    proxy = espias.enter_context(patch.object(
                        demo.proxy, "votar", wraps=demo.proxy.votar
                    ))
                    real = espias.enter_context(patch.object(
                        demo.real, "votar", wraps=demo.real.votar
                    ))
                    disponivel = espias.enter_context(patch.object(
                        demo.cota, "disponivel", wraps=demo.cota.disponivel
                    ))
                    consultar = espias.enter_context(patch.object(
                        demo.cota, "consultar_uso", wraps=demo.cota.consultar_uso
                    ))
                    consumir = espias.enter_context(patch.object(
                        demo.cota, "registrar_consumo", wraps=demo.cota.registrar_consumo
                    ))
                    resposta = self.http.post(
                        "/votos", json={"votante_id": votante_id, "alvo_id": "P101"}
                    )
                    self.assertEqual(resposta.status_code, status)
                    dados = resposta.json()
                    self.assertEqual(dados["codigo"], codigo)
                    self.assertTrue(dados["mensagem"].strip())
                    cliente.assert_called_once()
                    proxy.assert_called_once()
                    s = cliente.call_args.args[0]
                    self.assertIs(proxy.call_args.args[0], s)
                    self.assertIs(s.votante, demo.usuarios[votante_id])
                    self.assertIs(s.alvo, demo.conteudos["P101"])
                    self.assertEqual(s.dia, date(2026, 10, 16))
                    if cenario == "C02":
                        disponivel.assert_not_called()
                        consultar.assert_not_called()
                    else:
                        disponivel.assert_called_once_with(votante_id, demo.dia)
                        consultar.assert_called_once_with(votante_id, demo.dia)
                    if cenario == "C01":
                        real.assert_called_once_with(s)
                        self.assertIs(real.call_args.args[0], s)
                        consumir.assert_called_once_with(votante_id, demo.dia)
                    else:
                        real.assert_not_called()
                        consumir.assert_not_called()
                depois = self.estado()
                if cenario == "C01":
                    self.assertEqual(demo.conteudos["P101"].placar, 1)
                    self.assertEqual(demo.usuarios["A1"].reputacao, 110)
                    self.assertEqual(demo.usuarios["V1"].reputacao, 20)
                    self.assertEqual(demo.cota.consultar_uso("V1", demo.dia), 1)
                    self.assertEqual(len(depois["votos"]), 1)
                    self.assertEqual(len(depois["eventos"]), 1)
                    self.assertEqual(dados["voto"], depois["votos"][0])
                    self.assertEqual(dados["evento"], depois["eventos"][0])
                    self.assertEqual(dados["voto"], {
                        "votante_id": "V1", "alvo_id": "P101", "dia": "2026-10-16"
                    })
                    self.assertEqual(dados["evento"]["beneficiario_id"], "A1")
                    self.assertEqual(dados["evento"]["variacao"], 10)
                    self.assertEqual(dados["evento"]["voto"], dados["voto"])
                    self.assertIs(demo.real.eventos[0].voto, demo.real.votos[0])
                    self.assertIs(demo.real.eventos[0].beneficiario, demo.usuarios["A1"])
                else:
                    self.assertIsNone(dados["voto"])
                    self.assertIsNone(dados["evento"])
                    self.assertEqual(depois, antes)

    def test_resposta_comum_percorre_mesmo_fluxo(self):
        resposta = self.http.post("/votos", json={"votante_id": "V1", "alvo_id": "R101"})
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json()["voto"]["alvo_id"], "R101")
        demo = self.app.state.demonstracao
        self.assertEqual(demo.conteudos["R101"].placar, 1)
        self.assertEqual(demo.conteudos["P101"].placar, 0)
        self.assertEqual(demo.usuarios["A1"].reputacao, 110)
        self.assertEqual(demo.usuarios["V1"].reputacao, 20)
        self.assertEqual(demo.cota.consultar_uso("V1", demo.dia), 1)

    def test_consulta_de_estado_nao_cria_entradas_nem_altera_dados(self):
        for cenario in ("C01", "C02", "C03"):
            with self.subTest(cenario=cenario):
                antes = self.preparar(cenario)
                demo = self.app.state.demonstracao
                consumos = demo.cota._consumos.copy()
                for _ in range(2):
                    self.assertEqual(self.estado(), antes)
                self.assertEqual(demo.cota._consumos, consumos)

    def test_reinicio_recria_dados_e_isola_cenarios(self):
        for cenario in ("C01", "C02", "C03"):
            with self.subTest(cenario=cenario):
                self.preparar("C01")
                anterior = self.app.state.demonstracao
                self.http.post("/votos", json={"votante_id": "V1", "alvo_id": "P101"})
                estado = self.preparar(cenario)
                novo = self.app.state.demonstracao
                self.assertIsNot(novo.cota, anterior.cota)
                self.assertIsNot(novo.real, anterior.real)
                self.assertIsNot(novo.proxy, anterior.proxy)
                self.assertIsNot(novo.usuarios["A1"], anterior.usuarios["A1"])
                self.assertEqual(novo.usuarios["A1"].reputacao, 100)
                self.assertEqual(novo.conteudos["P101"].placar, 0)
                self.assertEqual(estado["votos"], [])
                self.assertEqual(estado["eventos"], [])
                self.assertEqual(novo.cota.consultar_uso("V1", novo.dia), 3 if cenario == "C03" else 0)
                self.assertIs(novo.cliente.servico, novo.proxy)
                self.assertIs(novo.proxy.real, novo.real)
                self.assertIs(novo.real.cota, novo.proxy.cota)

    def test_aplicacoes_nao_compartilham_estado(self):
        with TestClient(criar_app()) as outra_http:
            inicial = outra_http.get("/estado").json()
            self.http.post("/votos", json={"votante_id": "V1", "alvo_id": "P101"})
            self.assertEqual(outra_http.get("/estado").json(), inicial)
            self.assertNotEqual(self.estado(), inicial)

    def test_payload_invalido_e_campos_de_estado_nao_executam_votacao(self):
        valido = {"votante_id": "V1", "alvo_id": "P101"}
        invalidos = [
            {}, {"votante_id": "V1"}, {"votante_id": 1, "alvo_id": "P101"},
            {"votante_id": "", "alvo_id": "P101"}, [],
            {**valido, "reputacao": 999}, {**valido, "cota": 0},
            {**valido, "dia": "2020-01-01"},
        ]
        antes = self.estado()
        demo = self.app.state.demonstracao
        with patch.object(demo.cliente, "registrar_voto", wraps=demo.cliente.registrar_voto) as votar:
            for pedido in invalidos:
                with self.subTest(pedido=pedido):
                    self.assertEqual(self.http.post("/votos", json=pedido).status_code, 422)
                    self.assertEqual(self.estado(), antes)
            votar.assert_not_called()

    def test_ids_inexistentes_nao_executam_votacao(self):
        antes = self.estado()
        demo = self.app.state.demonstracao
        with patch.object(demo.cliente, "registrar_voto", wraps=demo.cliente.registrar_voto) as votar:
            for usuario_id, alvo_id in (("desconhecido", "P101"), ("V1", "desconhecido")):
                with self.subTest(usuario_id=usuario_id, alvo_id=alvo_id):
                    resposta = self.http.post("/votos", json={"votante_id": usuario_id, "alvo_id": alvo_id})
                    self.assertEqual(resposta.status_code, 404)
                    self.assertEqual(self.estado(), antes)
            votar.assert_not_called()

    def test_autovoto_e_repeticao_preservam_precondicoes(self):
        inicial = self.estado()
        self.assertEqual(self.http.post("/votos", json={"votante_id": "A1", "alvo_id": "P101"}).status_code, 409)
        self.assertEqual(self.estado(), inicial)
        pedido = {"votante_id": "V1", "alvo_id": "P101"}
        self.assertEqual(self.http.post("/votos", json=pedido).status_code, 201)
        depois = self.estado()
        self.assertEqual(self.http.post("/votos", json=pedido).status_code, 409)
        self.assertEqual(self.estado(), depois)

    def test_cenario_invalido_nao_substitui_estado(self):
        antes = self.estado()
        demo = self.app.state.demonstracao
        self.assertEqual(self.http.post("/demo/cenarios/C99").status_code, 422)
        self.assertIs(self.app.state.demonstracao, demo)
        self.assertEqual(self.estado(), antes)


if __name__ == "__main__":
    unittest.main()
