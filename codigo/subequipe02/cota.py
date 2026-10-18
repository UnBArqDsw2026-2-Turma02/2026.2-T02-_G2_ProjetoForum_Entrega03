"""Implementação em memória da cota diária de votos positivos."""

from datetime import date

from .contratos import CotaDiaria


class CotaDiariaEmMemoria(CotaDiaria):
    """Conta consumos por (usuario_id, dia), sem persistência entre processos.

    O limite deve ser um inteiro positivo. Consultas não alteram o estado;
    registrar_consumo incrementa apenas a chave informada e pressupõe que a
    autorização já tenha sido feita pelo Proxy.
    """

    def __init__(self, limite: int = 3) -> None:
        if isinstance(limite, bool) or not isinstance(limite, int) or limite <= 0:
            raise ValueError("O limite diário deve ser um inteiro positivo.")
        self.limite = limite
        self._consumos: dict[tuple[str, date], int] = {}

    def consultar_uso(self, usuario_id: str, dia: date) -> int:
        """Retorna o uso registrado; chaves ausentes têm uso zero."""
        return self._consumos.get((usuario_id, dia), 0)

    def disponivel(self, usuario_id: str, dia: date) -> bool:
        """Indica se ainda há cota, sem criar nem alterar registros."""
        return self.consultar_uso(usuario_id, dia) < self.limite

    def registrar_consumo(self, usuario_id: str, dia: date) -> None:
        """Soma uma unidade à chave informada; não aplica autorização."""
        chave = (usuario_id, dia)
        self._consumos[chave] = self._consumos.get(chave, 0) + 1
