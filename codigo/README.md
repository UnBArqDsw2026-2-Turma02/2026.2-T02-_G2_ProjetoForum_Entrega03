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
