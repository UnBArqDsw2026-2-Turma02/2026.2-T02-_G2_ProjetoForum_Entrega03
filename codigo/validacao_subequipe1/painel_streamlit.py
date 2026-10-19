"""Painel Streamlit para validar a API do Factory Method (SubEquipe 01).

O painel fala com a API só por HTTP, como qualquer cliente. A partir de codigo/,
em dois terminais:
    uvicorn subequipe1_factory_method.main:app --reload
    streamlit run validacao_subequipe1/painel_streamlit.py
"""

from uuid import uuid4

import httpx
import streamlit as st

# Qual Concrete Creator atende cada rota (quem decide é o provider em dependencias.py)
CRIADOR_POR_ROTA = {
    "Pergunta": ("POST /perguntas", "CriadorDePergunta", "Pergunta"),
    "Resposta": ("POST /perguntas/{id}/respostas", "CriadorDeResposta", "Resposta"),
    "Comentário": ("POST /perguntas/{id}/comentarios", "CriadorDeComentario", "Comentario"),
}


def validar(api: str) -> list[dict]:
    """Roda os cenários que a arquitetura pede e compara o esperado com o obtido."""
    cenarios = []

    def registrar(cenario: str, esperado, obtido) -> None:
        cenarios.append({"ok": "✅" if esperado == obtido else "❌", "cenário": cenario,
                         "esperado": str(esperado), "obtido": str(obtido)})

    with httpx.Client(base_url=api) as cliente:
        pergunta = cliente.post("/perguntas", json={"titulo": "a", "corpo": "a", "autor": "Maria"})
        registrar("Pergunta no limite (1 caractere) → CriadorDePergunta", 201, pergunta.status_code)
        pid = pergunta.json()["id"]

        resposta = cliente.post(f"/perguntas/{pid}/respostas", json={"corpo": "a", "autor": "João"})
        registrar("Resposta no limite → CriadorDeResposta", 201, resposta.status_code)

        comentario = cliente.post(f"/perguntas/{pid}/comentarios", json={"corpo": "a", "autor": "Ana"})
        registrar("Comentário no limite → CriadorDeComentario", 201, comentario.status_code)

        for campo in ("corpo", "autor"):
            dados = {"corpo": "a", "autor": "a", campo: ""}
            obtido = cliente.post(f"/perguntas/{pid}/comentarios", json=dados).status_code
            registrar(f"Comentário com {campo} vazio (abaixo do limite)", 422, obtido)

        obtido = cliente.post("/perguntas", json={"titulo": "a", "corpo": "a", "autor": ""}).status_code
        registrar("Pergunta com autor vazio", 422, obtido)

        obtido = cliente.post(f"/perguntas/{uuid4()}/comentarios", json={"corpo": "a", "autor": "a"}).status_code
        registrar("Comentário em pergunta inexistente (obter_pergunta, caminho do if)", 404, obtido)

        rid = resposta.json()["id"]
        obtido = cliente.post(f"/perguntas/{rid}/comentarios", json={"corpo": "a", "autor": "a"}).status_code
        registrar("Comentário usando o id de uma resposta", 404, obtido)

        completa = cliente.get(f"/perguntas/{pid}").json()
        # Cada produto vai para a sua lista e guarda o próprio autor
        registrar("GET: autor da pergunta", "Maria", completa["autor"])
        registrar("GET: autores na lista de respostas", ["João"], [r["autor"] for r in completa["respostas"]])
        registrar("GET: autores na lista de comentários", ["Ana"], [c["autor"] for c in completa["comentarios"]])

        rota = cliente.get("/openapi.json").json()["paths"]["/perguntas/{pergunta_id}/comentarios"]["post"]
        registrar("Rota nova documentada no /docs", ["Comentários"], rota["tags"])

    return cenarios


st.set_page_config(page_title="Factory Method: validação", layout="wide")
st.title("Factory Method no fórum: painel de validação")

api = st.sidebar.text_input("URL da API", "http://127.0.0.1:8000")
st.sidebar.caption("O painel só usa HTTP: não importa nenhuma classe do padrão.")
if "perguntas" not in st.session_state:
    st.session_state.perguntas = {}

st.header("1. Publicar conteúdo")
tipo = st.radio("Tipo de conteúdo", list(CRIADOR_POR_ROTA), horizontal=True)
rota, criador, produto = CRIADOR_POR_ROTA[tipo]
st.info(f"`{rota}` → Client recebe `CriadorDeConteudo` → o provider entrega **{criador}** → nasce um **{produto}**")

with st.form("publicar"):
    pergunta_escolhida = None
    if tipo == "Pergunta":
        titulo = st.text_input("Título", "O que é Factory Method?")
    else:
        pergunta_escolhida = st.selectbox("Pergunta", list(st.session_state.perguntas),
                                          format_func=lambda pid: st.session_state.perguntas[pid])
    corpo = st.text_area("Corpo", "Alguém explica?")
    autor = st.text_input("Autor", "Maria")
    enviado = st.form_submit_button("Publicar")

if enviado:
    if tipo == "Pergunta":
        retorno = httpx.post(f"{api}/perguntas", json={"titulo": titulo, "corpo": corpo, "autor": autor})
        if retorno.status_code == 201:
            st.session_state.perguntas[retorno.json()["id"]] = titulo
    else:
        caminho = "respostas" if tipo == "Resposta" else "comentarios"
        retorno = httpx.post(f"{api}/perguntas/{pergunta_escolhida}/{caminho}", json={"corpo": corpo, "autor": autor})
    st.write(f"Status **{retorno.status_code}**")
    st.json(retorno.json())

st.header("2. Ver pergunta")
if st.session_state.perguntas:
    pid = st.selectbox("Pergunta publicada", list(st.session_state.perguntas),
                       format_func=lambda pid: st.session_state.perguntas[pid], key="ver")
    completa = httpx.get(f"{api}/perguntas/{pid}").json()
    st.write(f"**{completa['titulo']}**, por {completa['autor']}")
    coluna_respostas, coluna_comentarios = st.columns(2)
    coluna_respostas.subheader("Respostas (CriadorDeResposta)")
    coluna_respostas.dataframe(completa["respostas"], column_order=["autor", "corpo", "id"])
    coluna_comentarios.subheader("Comentários (CriadorDeComentario)")
    coluna_comentarios.dataframe(completa["comentarios"], column_order=["autor", "corpo", "id"])
else:
    st.caption("Publique uma pergunta primeiro.")

st.header("3. Validação automática da arquitetura")
if st.button("Rodar cenários"):
    cenarios = validar(api)
    aprovados = sum(c["ok"] == "✅" for c in cenarios)
    st.metric("Cenários aprovados", f"{aprovados}/{len(cenarios)}")
    # Altura fixa para a tabela mostrar todos os cenários sem rolagem interna
    st.dataframe(cenarios, use_container_width=True, hide_index=True, height=35 * (len(cenarios) + 1) + 3)
