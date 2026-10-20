"""Rota FastAPI com Proxy, serviço real e dados reais observando delegação."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from subequipe02_historico.app import criar_app


class TestRotaHistoricoVotos(unittest.TestCase):
    def setUp(self) -> None:
        self.app = criar_app()
        self.client = TestClient(self.app)

    def get(self, usuario_id: str, solicitante_id: str):
        return self.client.get(
            f"/usuarios/{usuario_id}/historico-votos",
            params={"solicitante_id": solicitante_id},
        )

    def observar_real(self):
        return patch.object(
            self.app.state.real,
            "consultar",
            wraps=self.app.state.real.consultar,
        )

    def test_a_rota_usa_o_proxy_configurado_sobre_o_servico_real(self):
        self.assertIs(self.app.state.servico.real, self.app.state.real)

    def test_h01_proprio_historico(self):
        with self.observar_real() as real:
            resposta = self.get("V1", "V1")

        self.assertEqual(resposta.status_code, 200)
        corpo = resposta.json()
        self.assertEqual(corpo["codigo"], "CONSULTADO")
        self.assertEqual(corpo["usuario_id"], "V1")
        self.assertEqual(
            corpo["votos"],
            [
                {"votante_id": "V1", "alvo_id": "P101", "dia": "2026-10-16"},
                {"votante_id": "V1", "alvo_id": "R101", "dia": "2026-10-17"},
            ],
        )
        self.assertEqual(real.call_count, 1)

    def test_h02_consulta_sem_permissao(self):
        with self.observar_real() as real:
            resposta = self.get("V1", "V2")

        self.assertEqual(resposta.status_code, 403)
        corpo = resposta.json()
        self.assertEqual(corpo["codigo"], "ACESSO_NEGADO")
        self.assertEqual(corpo["votos"], [])
        self.assertEqual(real.call_count, 0)

    def test_h03_moderador_consulta_outro_usuario(self):
        with self.observar_real() as real:
            resposta = self.get("V2", "M1")

        self.assertEqual(resposta.status_code, 200)
        corpo = resposta.json()
        self.assertEqual(corpo["codigo"], "CONSULTADO")
        self.assertEqual(
            corpo["votos"],
            [{"votante_id": "V2", "alvo_id": "P101", "dia": "2026-10-16"}],
        )
        self.assertEqual(real.call_count, 1)

    def test_permitida_sem_registros_retorna_lista_vazia(self):
        resposta = self.get("A1", "A1")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["votos"], [])

    def test_ids_inexistentes_retornam_404_sem_chamar_o_proxy(self):
        with patch.object(
            self.app.state.servico,
            "consultar",
            wraps=self.app.state.servico.consultar,
        ) as proxy:
            solicitante = self.get("V1", "X9")
            consultado = self.get("X9", "V1")

        self.assertEqual(solicitante.status_code, 404)
        self.assertEqual(consultado.status_code, 404)
        self.assertEqual(proxy.call_count, 0)

    def test_solicitante_ausente_e_invalido(self):
        resposta = self.client.get("/usuarios/V1/historico-votos")

        self.assertEqual(resposta.status_code, 422)

    def test_requisicao_nao_concede_papel_de_moderador(self):
        resposta = self.client.get(
            "/usuarios/V1/historico-votos",
            params={"solicitante_id": "V2", "perfil": "MODERADOR"},
        )

        self.assertEqual(resposta.status_code, 403)

    def test_consultas_preservam_os_dados(self):
        base = self.app.state.base
        votos_antes = list(base.votos)
        placares = {k: c.placar for k, c in base.conteudos.items()}
        reputacoes = {k: u.reputacao for k, u in base.usuarios.items()}

        self.get("V1", "V1")
        self.get("V1", "V2")
        self.get("V2", "M1")

        self.assertEqual(base.votos, votos_antes)
        self.assertEqual(placares, {k: c.placar for k, c in base.conteudos.items()})
        self.assertEqual(
            reputacoes, {k: u.reputacao for k, u in base.usuarios.items()}
        )


if __name__ == "__main__":
    unittest.main()
