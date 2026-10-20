# Consulta protegida ao histórico de votos — Proxy de proteção

**Vídeo da implementação:** _link a ser inserido após a gravação_.

## O problema

O histórico de votos de um usuário é uma informação sensível: mostra o que cada pessoa votou. Se a regra de quem pode vê-lo ficasse espalhada pelas rotas ou misturada à busca dos registros, qualquer mudança de política exigiria alterações em vários lugares.

O Proxy de proteção resolve isso concentrando a decisão em um objeto que tem o mesmo contrato do serviço real. O serviço real só sabe buscar votos; o Proxy decide se a busca pode acontecer.

## Participantes do padrão

| Participante | Elemento | Responsabilidade |
| --- | --- | --- |
| Subject | `ServicoConsultaHistorico` (`contratos.py`) | Define `consultar(s: SolicitacaoConsultaHistorico) -> ResultadoConsultaHistorico`. |
| Proxy | `ProxyConsultaHistorico` (`proxy.py`) | Implementa o contrato, verifica a permissão e delega a mesma solicitação só quando permitido. |
| RealSubject | `ServicoConsultaHistoricoReal` (`servico_real.py`) | Implementa o contrato e filtra os votos pelo ID do usuário consultado. |
| Cliente | Rota FastAPI (`app.py`) | Resolve os IDs para dados simulados e chama o serviço configurado com o Proxy. |

Os demais arquivos são `dominio.py` (solicitação, resultado, perfil e códigos) e `dados.py` (dados simulados em memória). O tipo `Voto` é reaproveitado de `subequipe02.dominio` por importação.


## Dados simulados

| Usuário | Perfil | Votos no histórico |
| --- | --- | --- |
| V1 | comum | P101 (16/10/2026) e R101 (17/10/2026) |
| V2 | comum | P101 (16/10/2026) |
| M1 | moderador | nenhum |
| A1 | comum | nenhum (autor dos conteúdos) |

## Cenários

Rota: `GET /usuarios/{usuario_id}/historico-votos?solicitante_id=...`

| Cenário | Requisição | Resultado |
| --- | --- | --- |
| H01 — Próprio histórico | `/usuarios/V1/historico-votos?solicitante_id=V1` | HTTP 200, `CONSULTADO`, os dois votos de V1 e uma delegação ao serviço real. |
| H02 — Sem permissão | `/usuarios/V1/historico-votos?solicitante_id=V2` | HTTP 403, `ACESSO_NEGADO`, nenhum voto e nenhuma chamada ao serviço real. |
| H03 — Moderador | `/usuarios/V2/historico-votos?solicitante_id=M1` | HTTP 200, `CONSULTADO`, somente o voto de V2 e uma delegação ao serviço real. |

IDs de solicitante ou de usuário consultado inexistentes retornam HTTP 404 antes de chamar o Proxy; a ausência de `solicitante_id` retorna 422. O JSON de resposta tem `codigo`, `mensagem`, `usuario_id` e `votos`, e cada voto informa `votante_id`, `alvo_id` e `dia`.


## Fluxo de uma requisição

```
GET /usuarios/V1/historico-votos?solicitante_id=V2
  └─ app.py (Cliente): acha V2 e V1 nos dados do servidor (404 se não achar)
       └─ ProxyConsultaHistorico.consultar(s)      ← DECIDE
            ├─ não permitido → ACESSO_NEGADO, votos vazios (para aqui, HTTP 403)
            └─ permitido     → ServicoConsultaHistoricoReal.consultar(s)  ← BUSCA
                                  └─ filtra os votos pelo ID → CONSULTADO (HTTP 200)
```

## Executar

Requer Python 3.11 ou superior. A partir da raiz do repositório, no Git Bash do Windows:

```bash
python -m venv codigo/subequipe02_historico/.venv
codigo/subequipe02_historico/.venv/Scripts/python.exe -m pip install -r codigo/subequipe02/requirements.txt
codigo/subequipe02_historico/.venv/Scripts/python.exe -m uvicorn subequipe02_historico.app:app --app-dir codigo --host 127.0.0.1 --port 8001
```

Em Linux/macOS, troque `.venv/Scripts/python.exe` por `.venv/bin/python`. A demonstração fica em <http://127.0.0.1:8001/docs> (Swagger). Para parar o servidor, use `Ctrl+C`.

## Testes

```bash
codigo/subequipe02_historico/.venv/Scripts/python.exe -m unittest discover -s codigo/subequipe02_historico/tests -t codigo -v
```

| Arquivo | O que verifica |
| --- | --- |
| `tests/test_proxy.py` | Com um substituto do serviço real: H01 e H03 delegam uma vez com a mesma solicitação, H02 não delega, o papel vem do perfil e não do ID, e o resultado de rejeição não aceita votos. |
| `tests/test_servico_real.py` | A filtragem real dos votos existentes, os mesmos objetos armazenados, usuário sem votos, ausência de regra de permissão no serviço e preservação dos dados após consultas. |
| `tests/test_app.py` | A rota com Proxy, serviço real e dados reais: H01, H02, H03, delegação observada, 404, 422, papel de moderador não concedido pela requisição e dados preservados. |

