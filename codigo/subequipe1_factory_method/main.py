from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .criadores import CriadorDePergunta, CriadorDeResposta
from .produtos import Conteudo, Pergunta

app = FastAPI(title="Fórum: Factory Method")

# Repositório em memória: some quando a API reinicia
PERGUNTAS: dict[UUID, Pergunta] = {}


class PerguntaIn(BaseModel):
    titulo: str
    corpo: str


class RespostaIn(BaseModel):
    corpo: str


class ConteudoOut(BaseModel):
    id: UUID
    tipo: str
    corpo: str


def para_saida(conteudo: Conteudo) -> ConteudoOut:
    return ConteudoOut(id=conteudo.id, tipo=type(conteudo).__name__, corpo=conteudo.corpo)


# Client: o controller pede o objeto ao criador e não conhece a classe concreta
@app.post("/perguntas", status_code=201, response_model=ConteudoOut)
def criar_pergunta(dados: PerguntaIn):
    pergunta = CriadorDePergunta().criar_conteudo(dados.model_dump())
    PERGUNTAS[pergunta.id] = pergunta
    return para_saida(pergunta)


@app.post("/perguntas/{pergunta_id}/respostas", status_code=201, response_model=ConteudoOut)
def criar_resposta(pergunta_id: UUID, dados: RespostaIn):
    pergunta = PERGUNTAS.get(pergunta_id)
    if pergunta is None:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada")
    resposta = CriadorDeResposta().criar_conteudo(dados.model_dump())
    pergunta.respostas.append(resposta)
    return para_saida(resposta)
