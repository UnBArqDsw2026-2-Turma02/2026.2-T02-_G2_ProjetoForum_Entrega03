"""Monta estados independentes e permite inspecionar a demonstração em memória."""

from dataclasses import dataclass
from datetime import date

from .cliente import ClienteVotacaoFastAPI
from .cota import CotaDiariaEmMemoria
from .dominio import ConteudoVotavel, EventoReputacao, ResultadoVotacao, Usuario, Voto
from .proxy import ProxyProtecaoVotacao
from .servico_real import ServicoVotacaoReal


def dados_voto(voto: Voto) -> dict:
    return {
        "votante_id": voto.votante.id,
        "alvo_id": voto.alvo.id,
        "dia": voto.dia.isoformat(),
    }


def dados_evento(evento: EventoReputacao) -> dict:
    return {
        "voto": dados_voto(evento.voto),
        "beneficiario_id": evento.beneficiario.id,
        "variacao": evento.variacao,
    }


def dados_resultado(resultado: ResultadoVotacao) -> dict:
    return {
        "codigo": resultado.codigo.value,
        "mensagem": resultado.mensagem,
        "voto": dados_voto(resultado.voto) if resultado.voto is not None else None,
        "evento": (
            dados_evento(resultado.evento) if resultado.evento is not None else None
        ),
    }


@dataclass
class Demonstracao:
    cenario: str
    dia: date
    usuarios: dict[str, Usuario]
    conteudos: dict[str, ConteudoVotavel]
    cota: CotaDiariaEmMemoria
    real: ServicoVotacaoReal
    proxy: ProxyProtecaoVotacao
    cliente: ClienteVotacaoFastAPI

    def estado(self) -> dict:
        """Produz valores de consulta sem inserir ou modificar consumos."""
        return {
            "cenario": self.cenario,
            "dia_utc": self.dia.isoformat(),
            "limite_diario": self.cota.limite,
            "pedido_sugerido": {
                "votante_id": "V2" if self.cenario == "C02" else "V1",
                "alvo_id": "P101",
            },
            "usuarios": [
                {"id": u.id, "reputacao": u.reputacao}
                for u in self.usuarios.values()
            ],
            "conteudos": [
                {
                    "id": c.id,
                    "tipo": c.tipo,
                    "autor_id": c.autor.id,
                    "placar": c.placar,
                }
                for c in self.conteudos.values()
            ],
            "consumos": [
                {
                    "usuario_id": usuario_id,
                    "dia": self.dia.isoformat(),
                    "uso": self.cota.consultar_uso(usuario_id, self.dia),
                }
                for usuario_id in ("V1", "V2")
            ],
            "votos": [dados_voto(voto) for voto in self.real.votos],
            "eventos": [dados_evento(evento) for evento in self.real.eventos],
        }


def criar_demonstracao(cenario: str = "C01") -> Demonstracao:
    if cenario not in {"C01", "C02", "C03"}:
        raise ValueError("Cenário desconhecido. Use C01, C02 ou C03.")

    dia = date(2026, 10, 16)
    autor = Usuario("A1", 100)
    usuarios = {"A1": autor, "V1": Usuario("V1", 20), "V2": Usuario("V2", 14)}
    conteudos = {
        "P101": ConteudoVotavel("P101", "pergunta", autor, 0),
        "R101": ConteudoVotavel("R101", "resposta", autor, 0),
    }
    cota = CotaDiariaEmMemoria(limite=3)
    if cenario == "C03":
        # Prepara somente a cota; não cria votos/eventos ou efeitos no domínio.
        for _ in range(3):
            cota.registrar_consumo("V1", dia)

    real = ServicoVotacaoReal(cota)
    proxy = ProxyProtecaoVotacao(real=real, cota=cota)
    cliente = ClienteVotacaoFastAPI(servico=proxy)
    return Demonstracao(cenario, dia, usuarios, conteudos, cota, real, proxy, cliente)
