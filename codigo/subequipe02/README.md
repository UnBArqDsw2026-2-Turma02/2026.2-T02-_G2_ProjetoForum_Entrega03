# Votação positiva padrão — Proxy de proteção com FastAPI

Implementação da base compartilhada e do Proxy da [Issue #35](https://github.com/UnBArqDsw2026-2-Turma02/2026.2-T02-_G2_ProjetoForum_Entrega03/issues/35), conforme o [Diagrama de Classes e os contratos](../../docs/Base/Relatórios/1.1.2.SubEquipe_02.md#contratos-de-entrada-resultado-e-cota).

O núcleo de domínio utiliza somente a biblioteca padrão e admite Python 3.10+.
A aplicação e a suíte completa requerem **Python 3.11 ou superior**, conforme as
dependências fixadas em `requirements.txt`. Ambiente validado: Python 3.13.7.

## Instalar e iniciar a demonstração

No Git Bash do VS Code, a partir da raiz do repositório:

```bash
python -m venv codigo/subequipe02/.venv
codigo/subequipe02/.venv/Scripts/python.exe -m pip install -r codigo/subequipe02/requirements.txt
codigo/subequipe02/.venv/Scripts/python.exe -m uvicorn subequipe02.app:app --app-dir codigo --host 127.0.0.1 --port 8000
```

Não é necessário ativar o ambiente: os comandos usam diretamente seu Python.
Em Linux/macOS, substitua `.venv/Scripts/python.exe` por `.venv/bin/python`.

- **Demonstração no navegador:** <http://127.0.0.1:8000/>.
- **Documentação interativa da API:** <http://127.0.0.1:8000/docs>.
- **Estado em JSON:** <http://127.0.0.1:8000/estado>.

A página inicial contém controles para preparar os cenários, solicitar o voto e
comparar os estados antes/depois. Ela usa arquivos locais, sem bibliotecas de
interface externas. O Swagger em `/docs` usa os assets externos padrão do FastAPI.
Após instalar as dependências, a página inicial e as operações da API funcionam
localmente. Para parar o servidor, use `Ctrl+C` no terminal.

Use um único processo, sem `--workers`: cada processo tem seus próprios dados em
memória. Reiniciar o servidor também recria o estado inicial C01.

## Organização

| Arquivo | Responsabilidade |
| --- | --- |
| `dominio.py` | Usuário, conteúdo, voto, evento, solicitação, resultado e códigos de resultado. |
| `contratos.py` | Interfaces abstratas `ServicoVotacao` (Subject) e `CotaDiaria`. |
| `proxy.py` | `ProxyProtecaoVotacao`: autorização e delegação pelo contrato comum. |
| `servico_real.py` | `ServicoVotacaoReal`: registros e efeitos da votação já autorizada. |
| `cota.py` | `CotaDiariaEmMemoria`: implementação em memória de `CotaDiaria`, com consumo por `(usuario_id, dia)` e limite configurável (padrão 3). |
| `cliente.py` | `ClienteVotacaoFastAPI`: encaminha a solicitação ao `ServicoVotacao` recebido. |
| `demonstracao.py` | Cria estados independentes e compõe cliente, Proxy, serviço real e cota compartilhada. |
| `app.py` | Entrada HTTP, validação dos IDs e do corpo, operações da demonstração e códigos HTTP. |
| `inicio.html` | Página local de demonstração, com comparação dos estados e feedback da votação. |
| `requirements.txt` | Versões das dependências da aplicação e dos testes. |
| `tests/test_proxy.py` | Comportamento isolado do Proxy, com substitutos de serviço e cota. |
| `tests/test_dominio.py` | Restrições de resultado, beneficiário e tipo de conteúdo previstas na modelagem. |
| `tests/test_cota.py` | Comportamento isolado da cota: uso ausente, consumos 0/2/3, limite configurável e inválido, consultas sem mutação, incremento e independência por usuário e data. |
| `tests/test_servico_real.py` | Efeitos do serviço real, referências dos registros, consumo único e independência das coleções. |
| `tests/test_integracao.py` | Contrato do cliente e API com componentes reais, observando delegação, efeitos, rejeições e reinício. |

## Executar os testes

Na raiz do repositório:

```bash
codigo/subequipe02/.venv/Scripts/python.exe -m unittest discover -s codigo/subequipe02/tests -t codigo -v
```

Se o terminal já estiver na pasta `codigo`:

```bash
subequipe02/.venv/Scripts/python.exe -m unittest discover -s subequipe02/tests -t . -v
```

Cada teste monta objetos novos, sem acumular efeitos entre cenários. Os testes do Proxy
C01–C03 usam o dia simulado **16/10/2026 UTC**, autor A1 com reputação 100,
pergunta P101 com placar 0 e cota de referência 3:

| Caso | Dados do votante/cota | Verificação isolada |
| --- | --- | --- |
| C01 | V1, reputação 20, uso 0/3 | Consulta disponibilidade e delega uma vez, preservando a identidade da solicitação e do resultado. |
| C02 | V2, reputação 14, uso 0/3 | Retorna `REPUTACAO_INSUFICIENTE` sem consultar a cota nem delegar. |
| C03 | V1, reputação 20, uso 3/3 predefinido | Retorna `COTA_ESGOTADA` sem delegar ou consumir a cota. |

Há verificações adicionais para reputação exatamente 15, prioridade da rejeição
por reputação quando a cota também está esgotada, parâmetros variáveis de
usuário/data e conteúdo do tipo resposta. As rejeições preservam os dados do
domínio e retornam voto/evento ausentes. Os testes também verificam que o Proxy
não chama `registrar_consumo`.

Nos testes do Proxy, os substitutos são criados com `unittest.mock` a partir das
interfaces. A cota devolve respostas fixas configuradas para cada teste. O serviço
devolve um resultado de sucesso previamente montado, sem executar efeitos. Portanto, estes
testes **não demonstram** criação/armazenamento de registros pelo serviço real,
placar +1, reputação do autor +10 ou consumo +1 no caminho aceito. Esses efeitos
são verificados pelos testes do serviço e pela integração com componentes reais.

## Contratos dos componentes

- `ServicoVotacao` define `votar(s: SolicitacaoVotoPositivo) -> ResultadoVotacao`.
  O Proxy recebe `real: ServicoVotacao` e `cota: CotaDiaria` no construtor.
- A reputação mínima do Proxy é 15. Ele consulta a reputação antes de chamar
  `cota.disponivel(s.votante.id, s.dia)`. Só delega quando ambas permitem.
- `CotaDiaria` define `consultar_uso`, `disponivel` e `registrar_consumo`, sempre
  com `usuario_id: str` e `dia: date`. Consultas não alteram estado; uso ausente
  vale 0; disponibilidade significa uso menor que o limite positivo configurado.
  O limite inicial dos cenários é 3. `registrar_consumo` soma 1 e retorna `None`.
- A composição fornece **a mesma instância de cota ao Proxy e ao serviço real**.
  Somente o serviço real consome uma unidade no caminho aceito.
- Os objetos de domínio preservam referências compartilhadas. Usuário e conteúdo
  são mutáveis para permitir os efeitos do serviço real. Voto, evento, solicitação
  e resultado usam dataclasses congeladas: seus campos não são reatribuídos,
  mas os usuários e conteúdos referenciados continuam mutáveis.
- `ConteudoVotavel.tipo` admite `pergunta` e `resposta`. O beneficiário do evento
  deve ser a própria instância de `voto.alvo.autor`. O resultado exige voto/evento
  presentes no sucesso e ambos ausentes nas rejeições. Essas restrições são
  verificadas na construção dos respectivos objetos.
- A solicitação contém referências internas já carregadas, e o dia é uma data
  UTC escolhida pela demonstração. Ela não é o corpo de uma requisição HTTP que
  permita ao solicitante escolher sua reputação.

## Cota diária em memória

O arquivo `cota.py` implementa `CotaDiariaEmMemoria`, classe concreta de `CotaDiaria` responsável por controlar a quantidade de votos positivos consumidos por usuário e por data.

A implementação utiliza um dicionário em memória, indexado pela combinação `(usuario_id, dia)`. O limite é configurável, com valor padrão de 3 consumos por dia.

- `consultar_uso(usuario_id, dia)`: retorna a quantidade de consumos registrados para a chave informada. Quando não existe registro, retorna 0 sem modificar o estado.
- `disponivel(usuario_id, dia)`: retorna `True` quando o consumo é menor que o limite configurado e `False` quando o limite foi atingido. A consulta não altera os registros.
- `registrar_consumo(usuario_id, dia)`: incrementa em uma unidade o consumo da chave informada. Esse método pressupõe que a autorização já foi realizada e não cria votos ou eventos nem modifica placares ou reputações.

Os consumos são independentes por usuário e data. Como o armazenamento é exclusivamente em memória, os registros não são persistidos entre processos.

### Testes da cota diária

O arquivo `tests/test_cota.py` verifica o uso inicial igual a zero, os consumos 0/2/3, a configuração de limites diferentes de 3, a rejeição de limites inválidos, a ausência de mutação nas consultas, o incremento de uma unidade e o isolamento entre usuários e datas.

O cenário C03 pode ser preparado configurando diretamente três consumos para o usuário e a data do teste. Dessa forma, a cota fica esgotada sem exigir votos anteriores no conteúdo P101.

Em uma sessão Python iniciada na pasta `codigo`:

```python
from datetime import date
from subequipe02.cota import CotaDiariaEmMemoria

cota = CotaDiariaEmMemoria()
for _ in range(3):
    cota.registrar_consumo("V1", date(2026, 10, 16))
```

Execute a suíte do projeto a partir da raiz do repositório:

```bash
codigo/subequipe02/.venv/Scripts/python.exe -m unittest discover -s codigo/subequipe02/tests -t codigo -v
```

A implementação da cota não altera o Proxy: o Proxy verifica a autorização, enquanto o serviço real é responsável por registrar o consumo após aceitar a votação.

## Serviço real de votação

`ServicoVotacaoReal`, implementado na [Issue #55](https://github.com/UnBArqDsw2026-2-Turma02/2026.2-T02-_G2_ProjetoForum_Entrega03/issues/55), é o participante RealSubject. Recebe uma `CotaDiaria` no construtor e implementa o mesmo contrato `ServicoVotacao` do Proxy.

Em cada solicitação autorizada, `votar` cria um `Voto` e um `EventoReputacao`, guarda os registros, acrescenta 1 ao placar e 10 à reputação do autor, preserva a reputação do votante e registra um consumo na cota recebida. O resultado `REGISTRADO` contém uma mensagem e os mesmos objetos de voto e evento armazenados.

As coleções privadas `_votos` e `_eventos` correspondem às propriedades internas do Diagrama de Classes. As propriedades de consulta `votos` e `eventos` retornam tuplas com os registros: permitem inspecionar os resultados sem expor as listas internas para alteração. Cada instância do serviço tem suas próprias coleções.

Os testes isolados do serviço usam um substituto de `CotaDiaria` para conferir a chamada única de consumo, seus parâmetros e a ausência de consultas de autorização. Cobrem C01, resposta simulada, solicitações válidas distintas e independência das instâncias. `test_integracao.py` verifica a contagem concreta e os caminhos C02/C03 pela API, com o Proxy, o serviço real e a cota em memória. O serviço continua pressupondo que a solicitação já foi autorizada.

### Exemplo isolado do serviço real

Em uma sessão Python iniciada na pasta `codigo`:

```python
from datetime import date
from subequipe02.cota import CotaDiariaEmMemoria
from subequipe02.dominio import ConteudoVotavel, SolicitacaoVotoPositivo, Usuario
from subequipe02.servico_real import ServicoVotacaoReal

cota = CotaDiariaEmMemoria()
real = ServicoVotacaoReal(cota)
autor = Usuario("A1", 100)
votante = Usuario("V1", 20)
alvo = ConteudoVotavel("P101", "pergunta", autor, 0)
dia = date(2026, 10, 16)
solicitacao = SolicitacaoVotoPositivo(votante, alvo, dia)

# Chamada isolada para inspecionar efeitos de uma solicitação já autorizada.
# A aplicação receberá os pedidos pelo Proxy na composição dos componentes.
resultado = real.votar(solicitacao)
print(resultado.codigo.value)               # REGISTRADO
print(alvo.placar, autor.reputacao)           # 1 110
print(votante.reputacao)                     # 20
print(cota.consultar_uso("V1", dia))          # 1
print(len(real.votos), len(real.eventos))     # 1 1
```

Os testes deste componente usam o mesmo comando de execução da suíte indicado acima.

## API e roteiro de demonstração — Issue #56

A composição monta `cliente.servico = proxy`, `proxy.real = real` e
`proxy.cota is real.cota`. O cliente encaminha a mesma solicitação pelo contrato
comum. As regras de reputação e disponibilidade permanecem no Proxy existente.

O corpo de `POST /votos` aceita somente `votante_id` e `alvo_id`. A aplicação
resolve esses IDs para objetos do cenário e usa a data UTC simulada do servidor;
não recebe reputação, consumo ou data do solicitante. Os IDs são uma escolha
didática de usuário simulado, sem autenticação real.

| Operação | Finalidade | HTTP |
| --- | --- | --- |
| `GET /` | Abrir a página de demonstração e o link da documentação. | 200 |
| `GET /estado` | Ler usuários, reputações, conteúdos, placares, consumos, votos e eventos. | 200 |
| `POST /demo/cenarios/{cenario}` | Recriar todos os dados de C01, C02 ou C03. | 200 |
| `POST /votos` | Solicitar a votação por cliente → Proxy → serviço real. | 201, 403 ou 429 |

Os três cenários começam no dia **16/10/2026 UTC**, com autor A1 de reputação
100 e pergunta P101 de placar 0. R101 é uma resposta comum do mesmo autor,
também com placar 0. V1 tem reputação 20 e V2 tem reputação 14.

| Cenário | Pedido sugerido | Resultado esperado após uma tentativa |
| --- | --- | --- |
| C01 | V1 em P101, consumo inicial 0/3 | HTTP 201, `REGISTRADO`; placar 1, A1 = 110, V1 = 20, consumo 1/3, um voto e um evento. |
| C02 | V2 em P101, consumo inicial 0/3 | HTTP 403, `REPUTACAO_INSUFICIENTE`; sem delegação ou alterações; voto/evento ausentes. |
| C03 | V1 em P101, consumo inicial 3/3 | HTTP 429, `COTA_ESGOTADA`; sem delegação ou alterações; voto/evento ausentes. |

C03 prepara somente três consumos na cota, sem votos anteriores em P101, sem
eventos e sem efeitos em placar/reputações. A operação de reinício cria novas
instâncias dos componentes e objetos do domínio; a consulta de estado não
modifica os dados.

### Pelo navegador

1. Abra a página inicial e selecione C01, C02 ou C03.
2. Clique em **Preparar cenário**. O votante sugerido é selecionado automaticamente.
3. Confira o estado inicial e clique em **Registrar voto positivo** uma vez.
4. Confira o código HTTP, a mensagem e os estados antes/depois.
5. Prepare o próximo cenário para não acumular efeitos entre demonstrações.

Para demonstrar resposta, prepare C01 e selecione R101 antes de votar. Apenas
seu placar passa a 1; P101 permanece com placar 0. Os efeitos sobre autor/cota
seguem o mesmo contrato da pergunta.

### Pelo Git Bash, em outro terminal

Mantenha o servidor em execução. Cada sequência prepara um cenário independente:

```bash
# C01: sucesso
curl -s -X POST http://127.0.0.1:8000/demo/cenarios/C01
curl -s http://127.0.0.1:8000/estado
curl -i -X POST http://127.0.0.1:8000/votos -H 'Content-Type: application/json' -d '{"votante_id":"V1","alvo_id":"P101"}'
curl -s http://127.0.0.1:8000/estado

# C02: reputação insuficiente
curl -s -X POST http://127.0.0.1:8000/demo/cenarios/C02
curl -s http://127.0.0.1:8000/estado
curl -i -X POST http://127.0.0.1:8000/votos -H 'Content-Type: application/json' -d '{"votante_id":"V2","alvo_id":"P101"}'
curl -s http://127.0.0.1:8000/estado

# C03: cota esgotada
curl -s -X POST http://127.0.0.1:8000/demo/cenarios/C03
curl -s http://127.0.0.1:8000/estado
curl -i -X POST http://127.0.0.1:8000/votos -H 'Content-Type: application/json' -d '{"votante_id":"V1","alvo_id":"P101"}'
curl -s http://127.0.0.1:8000/estado
```

### Validação, registros e limites

Campos ausentes, tipos inválidos, campos extras e cenário desconhecido recebem
HTTP 422; IDs inexistentes recebem 404. A fronteira HTTP também preserva as
precondições do toy: autovoto e repetição de um voto já aceito recebem 409,
sem chegar ao Proxy ou alterar dados. Esses casos usam `detail` no JSON de
erro; não acrescentam códigos ao contrato de resultado da votação.

No caminho do padrão, o JSON contém `codigo`, `mensagem`, `voto` e `evento`.
Um voto informa `votante_id`, `alvo_id` e `dia`; o evento informa o mesmo voto,
`beneficiario_id` e `variacao`. Nas rejeições do Proxy, voto e evento são `null`.
As referências de objetos são preservadas internamente e verificadas nos testes.

As consultas antes/depois da página são operações explícitas de leitura; elas
não são verificações adicionais de autorização. Os testes observam as chamadas
durante o pedido de voto: C02 não consulta a cota, C03 consulta e não delega,
e C01 delega e consome uma única vez. Os componentes reais executam os efeitos;
os mocks da integração apenas observam suas chamadas.

A execução permanece sequencial, sem banco de dados, autenticação real,
concorrência ou recuperação de falhas durante o registro. O controle de
repetição é limitado ao estado em memória desta demonstração.

## Referências técnicas da integração

- [FastAPI: testes com TestClient](https://fastapi.tiangolo.com/tutorial/testing/).
- [FastAPI: código de status da resposta](https://fastapi.tiangolo.com/advanced/response-change-status-code/).
- [Pydantic: configuração de validação e campos extras](https://docs.pydantic.dev/latest/api/config/).
- [Uvicorn: configuração do servidor](https://uvicorn.dev/settings/).
