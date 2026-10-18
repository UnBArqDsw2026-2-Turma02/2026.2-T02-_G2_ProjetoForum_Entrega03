# Votação positiva padrão — base Python e Proxy de proteção

Implementação da base compartilhada e do Proxy da [Issue #35](https://github.com/UnBArqDsw2026-2-Turma02/2026.2-T02-_G2_ProjetoForum_Entrega03/issues/35), conforme o [Diagrama de Classes e os contratos](../../docs/Base/Relatórios/1.1.2.SubEquipe_02.md#contratos-de-entrada-resultado-e-cota).

Requer **Python 3.10 ou superior**. Este núcleo utiliza somente a biblioteca
padrão; não exige instalar dependências para executar seus testes.

## Organização

| Arquivo | Responsabilidade |
| --- | --- |
| `dominio.py` | Usuário, conteúdo, voto, evento, solicitação, resultado e códigos de resultado. |
| `contratos.py` | Interfaces abstratas `ServicoVotacao` (Subject) e `CotaDiaria`. |
| `proxy.py` | `ProxyProtecaoVotacao`: autorização e delegação pelo contrato comum. |
| `cota.py` | `CotaDiariaEmMemoria`: implementação em memória de `CotaDiaria`, com consumo por `(usuario_id, dia)` e limite configurável (padrão 3). |
| `tests/test_proxy.py` | Comportamento isolado do Proxy, com substitutos de serviço e cota. |
| `tests/test_dominio.py` | Restrições de resultado, beneficiário e tipo de conteúdo previstas na modelagem. |
| `tests/test_cota.py` | Comportamento isolado da cota: uso ausente, consumos 0/2/3, limite configurável e inválido, consultas sem mutação, incremento e independência por usuário e data. |

## Executar os testes

Na raiz do repositório:

```powershell
python -m unittest discover -s codigo/subequipe02/tests -t codigo -v
```

Se o terminal já estiver na pasta `codigo`:

```powershell
python -m unittest discover -s subequipe02/tests -t . -v
```

Cada teste monta objetos novos, sem acumular efeitos entre cenários. Os testes
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

Os substitutos são criados com `unittest.mock` a partir das interfaces. A cota
devolve respostas fixas configuradas para cada teste. O serviço devolve um
resultado de sucesso previamente montado, sem executar efeitos. Portanto, estes
testes **não demonstram** criação/armazenamento de registros pelo serviço real,
placar +1, reputação do autor +10 ou consumo +1 no caminho aceito. Esses efeitos
serão verificados na integração dos componentes concretos.

## Contratos para os próximos componentes

- `ServicoVotacao` define `votar(s: SolicitacaoVotoPositivo) -> ResultadoVotacao`.
  O Proxy recebe `real: ServicoVotacao` e `cota: CotaDiaria` no construtor.
- A reputação mínima do Proxy é 15. Ele consulta a reputação antes de chamar
  `cota.disponivel(s.votante.id, s.dia)`. Só delega quando ambas permitem.
- `CotaDiaria` define `consultar_uso`, `disponivel` e `registrar_consumo`, sempre
  com `usuario_id: str` e `dia: date`. Consultas não alteram estado; uso ausente
  vale 0; disponibilidade significa uso menor que o limite positivo configurado.
  O limite inicial dos cenários é 3. `registrar_consumo` soma 1 e retorna `None`.
- A futura composição fornecerá **a mesma instância de cota ao Proxy e ao
  serviço real**. Somente o serviço real consumirá uma unidade no caminho aceito.
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

# Cota diária em memória

O arquivo `cota.py` implementa `CotaDiariaEmMemoria`, classe concreta de `CotaDiaria` responsável por controlar a quantidade de votos positivos consumidos por usuário e por data.

A implementação utiliza um dicionário em memória, indexado pela combinação `(usuario_id, dia)`. O limite é configurável, com valor padrão de 3 consumos por dia.

- `consultar_uso(usuario_id, dia)`: retorna a quantidade de consumos registrados para a chave informada. Quando não existe registro, retorna 0 sem modificar o estado.
- `disponivel(usuario_id, dia)`: retorna `True` quando o consumo é menor que o limite configurado e `False` quando o limite foi atingido. A consulta não altera os registros.
- `registrar_consumo(usuario_id, dia)`: incrementa em uma unidade o consumo da chave informada. Esse método pressupõe que a autorização já foi realizada e não cria votos ou eventos nem modifica placares ou reputações.

Os consumos são independentes por usuário e data. Como o armazenamento é exclusivamente em memória, os registros não são persistidos entre processos.

## Testes da cota diária

O arquivo `tests/test_cota.py` verifica o uso inicial igual a zero, os consumos 0/2/3, a configuração de limites diferentes de 3, a rejeição de limites inválidos, a ausência de mutação nas consultas, o incremento de uma unidade e o isolamento entre usuários e datas.

O cenário C03 pode ser preparado configurando diretamente três consumos para o usuário e a data do teste. Dessa forma, a cota fica esgotada sem exigir votos anteriores no conteúdo P101.

```   
  cota = CotaDiariaEmMemoria()
  for _ in range(3):
    cota.registrar_consumo("V1", date(2026, 10, 16))
```
Execute a suíte do projeto a partir da raiz do repositório:

```powershell
python -m unittest discover -s codigo/subequipe02/tests -t codigo -v
```

A implementação da cota não altera o Proxy: o Proxy verifica a autorização, enquanto o serviço real é responsável por registrar o consumo após aceitar a votação.

---


Este bloco não implementa `ServicoVotacaoReal` (Luis Guilherme),
`CotaDiariaEmMemoria` (Cauã Nicolas) nem a entrada FastAPI. A execução pressupõe
entidades existentes, votante distinto do autor e ausência de voto anterior no
alvo. Concorrência, falhas durante o registro, persistência e autenticação reais
não integram os cenários iniciais.
