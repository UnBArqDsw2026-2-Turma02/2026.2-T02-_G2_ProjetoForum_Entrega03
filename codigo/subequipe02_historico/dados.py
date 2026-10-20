"""Dados simulados em memória: usuários, perfis, conteúdos e votos."""

from dataclasses import dataclass
from datetime import date

from subequipe02.dominio import ConteudoVotavel, Usuario, Voto

from .dominio import Participante, Perfil


@dataclass
class BaseHistorico:
    participantes: dict[str, Participante]
    usuarios: dict[str, Usuario]
    conteudos: dict[str, ConteudoVotavel]
    votos: list[Voto]


def criar_base() -> BaseHistorico:
    """V1 e V2 são comuns, M1 é moderador e A1 é autor dos conteúdos."""
    usuarios = {
        "A1": Usuario("A1", 100),
        "V1": Usuario("V1", 20),
        "V2": Usuario("V2", 30),
        "M1": Usuario("M1", 500),
    }
    perfis = {
        "A1": Perfil.COMUM,
        "V1": Perfil.COMUM,
        "V2": Perfil.COMUM,
        "M1": Perfil.MODERADOR,
    }
    participantes = {
        uid: Participante(uid, perfis[uid]) for uid in usuarios
    }
    autor = usuarios["A1"]
    conteudos = {
        "P101": ConteudoVotavel("P101", "pergunta", autor, 2),
        "R101": ConteudoVotavel("R101", "resposta", autor, 1),
    }
    votos = [
        Voto(usuarios["V1"], conteudos["P101"], date(2026, 10, 16)),
        Voto(usuarios["V2"], conteudos["P101"], date(2026, 10, 16)),
        Voto(usuarios["V1"], conteudos["R101"], date(2026, 10, 17)),
    ]
    return BaseHistorico(participantes, usuarios, conteudos, votos)
