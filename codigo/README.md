# Fórum — GoF Criacional: Factory Method (SubEquipe 01)

Implementação do padrão criacional **Factory Method** aplicado à criação de conteúdos (`Pergunta`, `Resposta`) no fórum utilizando Python e FastAPI.

## Estrutura do Código

```text
codigo/
├── subequipe1_factory_method/
│   ├── __init__.py
│   ├── produtos.py        # Conteudo (abstrato), Pergunta e Resposta (concretos)
│   ├── criadores.py       # CriadorDeConteudo (abstrato, com publicar()), CriadorDePergunta e CriadorDeResposta
│   ├── repositorio.py     # RepositorioConteudo em memória
│   ├── dependencias.py    # Providers do Depends(): repositórios, criadores e busca da pergunta (404)
│   ├── schemas.py         # Schemas Pydantic de entrada e saída
│   └── main.py            # API FastAPI e endpoints (Client)
├── tests/                 # Testes com pytest + TestClient
├── pytest.ini
├── requirements.txt       # Dependências do projeto (FastAPI, pytest)
└── README.md
```

## Endpoints

| Método | Rota | Criador usado | Respostas |
|---|---|---|---|
| POST | `/perguntas` | `CriadorDePergunta` | 201, 422 |
| GET | `/perguntas/{pergunta_id}` | — | 200 (com as respostas), 404 |
| POST | `/perguntas/{pergunta_id}/respostas` | `CriadorDeResposta` | 201, 404, 422 |

Os controllers recebem o criador via `Depends()` tipado como o abstrato `CriadorDeConteudo` e só chamam `publicar()`. Nenhum controller sabe qual classe concreta é instanciada.

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
