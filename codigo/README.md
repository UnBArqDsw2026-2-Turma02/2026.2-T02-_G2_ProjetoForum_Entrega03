# Fórum — GoF Criacional: Factory Method (SubEquipe 01)

Implementação do padrão criacional **Factory Method** aplicado à criação de conteúdos (`Pergunta`, `Resposta`, `Comentario`) no fórum utilizando Python e FastAPI.

## Estrutura do Código

```text
codigo/
├── subequipe1_factory_method/
│   ├── __init__.py
│   ├── produtos.py        # Conteudo (abstrato), Pergunta, Resposta e Comentario (concretos)
│   ├── criadores.py       # CriadorDeConteudo (abstrato, com publicar()), CriadorDePergunta, CriadorDeResposta e CriadorDeComentario
│   ├── repositorio.py     # RepositorioConteudo em memória (Singleton)
│   ├── dependencias.py    # Providers do Depends(): repositório único, criadores e busca da pergunta (404)
│   ├── schemas.py         # Schemas Pydantic de entrada e saída
│   └── main.py            # API FastAPI e endpoints (Client)
├── tests/                 # Testes com pytest + TestClient
├── validacao_subequipe1/
│   └── painel_streamlit.py  # Painel para validar a API pelo navegador
├── pytest.ini
├── requirements.txt       # Dependências do projeto (FastAPI, pytest)
└── README.md
```

## Endpoints

| Método | Rota | Criador usado | Respostas |
|---|---|---|---|
| POST | `/perguntas` | `CriadorDePergunta` | 201, 422 |
| GET | `/perguntas/{pergunta_id}` | — | 200 (com as respostas e os comentários), 404 |
| POST | `/perguntas/{pergunta_id}/respostas` | `CriadorDeResposta` | 201, 404, 422 |
| POST | `/perguntas/{pergunta_id}/comentarios` | `CriadorDeComentario` | 201, 404, 422 |

Os controllers recebem o criador via `Depends()` tipado como o abstrato `CriadorDeConteudo` e só chamam `publicar()`. Nenhum controller sabe qual classe concreta é instanciada. Todo conteúdo exige `autor` no corpo da requisição.

O `Comentario` (F4, issue #9) mostra o princípio aberto/fechado: entrou com uma subclasse de `Conteudo`, uma de `CriadorDeConteudo` e uma rota nova, sem alterar `CriadorDePergunta`, `CriadorDeResposta` nem as rotas que já existiam.

## Como Instalar e Executar

1. **Criar e ativar o ambiente virtual (venv):**
   ```bash
   cd codigo
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Instalar as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Executar a API com Uvicorn:**
   ```bash
   uvicorn subequipe1_factory_method.main:app --reload
   ```

4. **Acessar a documentação interativa (Swagger UI):**
   Abra no navegador: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

5. **Rodar os testes** (de dentro de `codigo/`):
   ```bash
   pytest -v
   ```

6. **Validar pelo navegador (opcional):** com a API rodando no passo 3, em outro terminal:
   ```bash
   pip install -r requirements-dev.txt
   streamlit run validacao_subequipe1/painel_streamlit.py
   ```
   O painel fala com a API só por HTTP: publica pergunta, resposta e comentário, mostra qual Concrete Creator atende cada rota e roda os cenários que a arquitetura pede (201, 404 e 422 nas bordas).

## Ads — SubEquipe 03 (Strategy)

Os contratos de Ads ficam em `subequipe3_strategy/ads/`; a estratégia de match exato é desenvolvida na issue #25 sobre essa base. A implementação preserva UUIDs do módulo Conteúdo e não altera os endpoints Factory Method existentes.

Consulte [contratos, integração e limitações de Ads](subequipe3_strategy/ads/README.md). Os testes ficam em `tests/` e podem ser executados, a partir de `codigo/`, com `python -m pytest -q`. As dependências de desenvolvimento estão em `requirements-dev.txt`.

O Context, o registro de políticas e as rotas SSR estão em [ENTREGA.md](subequipe3_strategy/ads/ENTREGA.md) (#27). Eles são acrescentados à mesma aplicação FastAPI do fórum por `subequipe3_strategy/main.py`; para incluir as rotas de Ads, execute `uvicorn subequipe3_strategy.main:app --reload` a partir de `codigo/`. A estratégia genérica (#26) e a política de maior saldo (#28) continuam nas issues dos respectivos responsáveis.
