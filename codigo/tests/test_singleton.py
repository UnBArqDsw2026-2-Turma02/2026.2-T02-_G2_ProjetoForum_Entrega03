"""F5: Singleton no RepositorioConteudo (RNF07, #19)."""

import threading
import time
from uuid import uuid4

import pytest

from subequipe1_factory_method.dependencias import (
    get_criador_de_comentario,
    get_criador_de_pergunta,
    get_criador_de_resposta,
    get_repositorio,
)
from subequipe1_factory_method.produtos import Pergunta
from subequipe1_factory_method.repositorio import RepositorioConteudo


def test_instancia_sempre_devolve_o_mesmo_objeto():
    assert RepositorioConteudo.instancia() is RepositorioConteudo.instancia()


def test_construtor_direto_eh_bloqueado():
    with pytest.raises(TypeError):
        RepositorioConteudo()


def test_instancia_eh_thread_safe(monkeypatch):
    # Construção lenta abre a janela de corrida entre o `if` e a atribuição;
    # sem ela o GIL quase nunca troca de thread ali e o teste passaria mesmo sem lock
    init_original = RepositorioConteudo.__init__

    def init_lento(self, *args, **kwargs):
        time.sleep(0.01)
        init_original(self, *args, **kwargs)

    monkeypatch.setattr(RepositorioConteudo, "__init__", init_lento)
    total = 50
    barreira = threading.Barrier(total)
    instancias = []

    def pedir_instancia():
        # Todas as threads chegam juntas ao `if _instancia is None`
        barreira.wait()
        instancias.append(RepositorioConteudo.instancia())

    threads = [threading.Thread(target=pedir_instancia) for _ in range(total)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(instancias) == total
    assert len({id(instancia) for instancia in instancias}) == 1


def test_resetar_gera_instancia_nova_e_vazia():
    antiga = RepositorioConteudo.instancia()
    antiga.salvar(Pergunta(corpo="corpo", titulo="titulo", autor="Maria"))

    RepositorioConteudo._resetar()
    nova = RepositorioConteudo.instancia()

    assert nova is not antiga
    assert nova._conteudos == {}


def test_salvar_e_buscar_por_id():
    repositorio = RepositorioConteudo.instancia()
    pergunta = Pergunta(corpo="corpo", titulo="titulo", autor="Maria")

    repositorio.salvar(pergunta)

    assert repositorio.buscar_por_id(pergunta.id) is pergunta
    assert repositorio.buscar_por_id(uuid4()) is None


def test_atualizar_substitui_conteudo_salvo():
    repositorio = RepositorioConteudo.instancia()
    pergunta = Pergunta(corpo="corpo", titulo="titulo", autor="Maria")
    repositorio.salvar(pergunta)
    pergunta.corpo = "corpo editado"

    repositorio.atualizar(pergunta)

    assert repositorio.buscar_por_id(pergunta.id).corpo == "corpo editado"


def test_atualizar_conteudo_nao_salvo_lanca_erro():
    with pytest.raises(KeyError):
        RepositorioConteudo.instancia().atualizar(Pergunta(corpo="corpo", titulo="titulo", autor="Maria"))


def test_criadores_compartilham_a_mesma_instancia():
    criador_de_pergunta = get_criador_de_pergunta(get_repositorio())
    criador_de_resposta = get_criador_de_resposta(get_repositorio())
    criador_de_comentario = get_criador_de_comentario(get_repositorio())

    assert criador_de_pergunta.repositorio is criador_de_resposta.repositorio
    assert criador_de_comentario.repositorio is criador_de_pergunta.repositorio


def test_resposta_aparece_no_get_da_pergunta(client):
    # Ponta a ponta, sem dependency_overrides: as três requisições usam o mesmo Singleton
    pergunta_id = client.post("/perguntas", json={"titulo": "Singleton?", "corpo": "Como funciona?", "autor": "Maria"}).json()["id"]
    criada = client.post(f"/perguntas/{pergunta_id}/respostas", json={"corpo": "Uma instância só.", "autor": "João"}).json()

    resposta = client.get(f"/perguntas/{pergunta_id}")

    assert resposta.status_code == 200
    assert resposta.json()["respostas"] == [criada]
    assert len(RepositorioConteudo.instancia()._conteudos) == 2
