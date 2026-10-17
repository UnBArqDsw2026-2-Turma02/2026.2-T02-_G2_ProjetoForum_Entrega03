# Fórum — GoF Criacional: Factory Method (SubEquipe 01)

Implementação do padrão criacional **Factory Method** aplicado à criação de conteúdos (`Pergunta`, `Resposta`) no fórum utilizando Python e FastAPI.

## Estrutura do Código

```text
codigo/
├── subequipe1_factory_method/
│   ├── __init__.py
│   ├── produtos.py        # Conteudo (abstrato), Pergunta e Resposta (concretos)
│   ├── criadores.py       # CriadorDeConteudo (abstrato), CriadorDePergunta e CriadorDeResposta (concretos)
│   └── main.py            # API FastAPI e endpoints (Client)
├── requirements.txt       # Dependências do projeto (FastAPI)
└── README.md
```

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


## Ads — SubEquipe 03 (Strategy)

Os contratos de Ads ficam em `app/ads/`; a estratégia de match exato é desenvolvida na issue #25 sobre essa base. A implementação preserva UUIDs do módulo Conteúdo e não altera os endpoints Factory Method existentes.

Consulte [contratos, integração e limitações de Ads](app/ads/README.md). Os testes ficam em `tests/` e podem ser executados, a partir de `codigo/`, com `python -m pytest -q`. As dependências de desenvolvimento estão em `requirements-dev.txt`.

O Context, a estratégia genérica, a política de maior saldo e as rotas SSR continuam nas issues dos respectivos responsáveis; esta alteração não cria uma segunda aplicação FastAPI.
