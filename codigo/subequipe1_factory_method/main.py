from typing import Annotated

from fastapi import Depends, FastAPI

from .criadores import CriadorDeConteudo
from .dependencias import (
    get_criador_de_comentario,
    get_criador_de_pergunta,
    get_criador_de_resposta,
    obter_pergunta,
)
from .produtos import Pergunta
from .schemas import (
    ComentarioIn,
    ComentarioOut,
    PerguntaIn,
    PerguntaOut,
    RespostaIn,
    RespostaOut,
)

app = FastAPI(title="Fórum: Factory Method")

NAO_ENCONTRADA = {404: {"description": "Pergunta não encontrada"}}


# Client: o controller recebe o criador já pronto e só conhece o tipo abstrato CriadorDeConteudo
@app.post("/perguntas", status_code=201, response_model=PerguntaOut, tags=["Perguntas"])
def criar_pergunta(
    dados: PerguntaIn,
    criador: Annotated[CriadorDeConteudo, Depends(get_criador_de_pergunta)],
):
    return criador.publicar(dados.model_dump())


@app.get(
    "/perguntas/{pergunta_id}",
    response_model=PerguntaOut,
    responses=NAO_ENCONTRADA,
    tags=["Perguntas"],
)
def buscar_pergunta(pergunta: Annotated[Pergunta, Depends(obter_pergunta)]):
    return pergunta


@app.post(
    "/perguntas/{pergunta_id}/respostas",
    status_code=201,
    response_model=RespostaOut,
    responses=NAO_ENCONTRADA,
    tags=["Respostas"],
)
def responder_pergunta(
    dados: RespostaIn,
    pergunta: Annotated[Pergunta, Depends(obter_pergunta)],
    criador: Annotated[CriadorDeConteudo, Depends(get_criador_de_resposta)],
):
    return criador.publicar({**dados.model_dump(), "pergunta": pergunta})


# Client (GoF): o controller depende apenas da interface abstrata CriadorDeConteudo
@app.post(
    "/perguntas/{pergunta_id}/comentarios",
    status_code=201,
    response_model=ComentarioOut,
    responses=NAO_ENCONTRADA,
    tags=["Comentários"],
)
def comentar_pergunta(
    dados: ComentarioIn,
    pergunta: Annotated[Pergunta, Depends(obter_pergunta)],
    criador: Annotated[CriadorDeConteudo, Depends(get_criador_de_comentario)],
):
    return criador.publicar({
        "corpo": dados.corpo,
        "autor": dados.autor,
        "pergunta": pergunta,
    })
