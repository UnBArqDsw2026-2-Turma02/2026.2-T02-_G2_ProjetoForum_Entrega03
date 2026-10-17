# Ads — contratos e seleção por Strategy

Contratos compartilhados da issue #24; a implementação de match exato é entregue separadamente na #25. O diagrama técnico é a referência funcional: interface estrutural com `Protocol`, correspondência de tags e desempate pelo menor ID.

## Escopo

| Parte | Situação | Responsável na divisão de issues |
|---|---|---|
| Domínio, portas de repositório, adaptador em memória e DTO | Implementado nesta alteração | #24 — Pedro |
| `EstrategiaMatchExatoDeTag` | Implementação separada, consumindo estes contratos | #25 — Pedro |
| `EstrategiaAnuncioGenerico` | Contrato disponível; implementação não incluída | #26 — Bruno |
| `ControladorEntrega`, registro de políticas, templates e rotas | Não implementados aqui | #27 — Alberto |
| `EstrategiaMaiorSaldoNaTag` | Contrato disponível; implementação não incluída | #28 — Kaio |

`AnuncioGenerico` é um modelo de anúncio; sua presença não significa que a estratégia de fallback da #26 já foi implementada.

## Contrato das estratégias

```python
class EstrategiaSelecaoAnuncio(Protocol):
    def selecionar_anuncio(
        self, pergunta: Pergunta, campanhas: list[Campanha]
    ) -> Anuncio | None: ...

    def obter_nome(self) -> str: ...
```

As concretas implementam os métodos sem precisar herdar do Protocol. Selecionar não altera métricas ou saldo. Nenhuma estratégia chama outra para fazer fallback: o futuro Context da #27 deve chamar a genérica se a principal retornar `None`.

`EstrategiaMatchExatoDeTag.obter_nome()` retorna `match_exato`. Uma campanha é elegível se estiver ATIVA, tiver anúncio contextual e tag em comum, e satisfizer `saldo_restante >= custo_por_clique > 0`. A comparação de tags usa `casefold()` e ignora diferenças de caixa. Escolhe a campanha de menor UUID e, dentro dela, o anúncio de menor UUID, independentemente da ordem da entrada. Não ranqueia por número de tags, CPC ou saldo.

O requisito anterior RF02 mencionava maior lance/CPC. A revisão das issues passou a seguir o diagrama, que define match exato e maior saldo. Essa divergência de requisito ainda precisa ser validada pelo grupo e registrada no relatório; os testes atuais não comprovam atendimento ao antigo RF02.

## Integração com Conteúdo

O código atual de `subequipe1_factory_method.produtos.Pergunta` fornece UUID e título, mas ainda não fornece tags. `contexto.Pergunta` é uma projeção de leitura, não uma entidade substituta. Use o adaptador com tags obtidas explicitamente da futura integração:

```python
from app.ads.model.campanha import Tag
from app.ads.model.contexto import projetar_pergunta

# pergunta_conteudo é a instância original do módulo Conteúdo.
projecao = projetar_pergunta(pergunta_conteudo, tags=[Tag("python")])
assert projecao.id == pergunta_conteudo.id
```

A lista de tags não é inferida silenciosamente nem extraída de um atributo inexistente. O adaptador preserva a identidade e não altera a instância original. A origem real das tags permanece pendente do contrato com a subequipe 01.

UUID acompanha a implementação atual do fórum. O `int` do diagrama corresponde à proposta anterior de persistência; essa anotação precisa ser atualizada antes da integração definitiva. `Tag` é um valor pelo nome nesta etapa: ainda não há uma identidade de Tag exposta por Conteúdo para preservar.

## Portas de repositório

| Porta | Métodos |
|---|---|
| `RepositorioPerguntas` | `obter(UUID) -> Pergunta | None` |
| `RepositorioCampanhas` | `listar_ativas() -> list[Campanha]` |
| `RepositorioMetricas` | `registrar_visualizacao(UUID)`, `registrar_clique_atomico(UUID)` |

Uma instância de `RepositorioAds` atende às três portas e deve ser compartilhada pelas dependências da aplicação. O inventário é configurado na construção; não alterar diretamente as listas de anúncios depois de criar o repositório. `obter_anuncio()` auxilia a consulta; `anuncio_padrao` exige que um `AnuncioGenerico` tenha sido configurado.

As estatísticas retornadas por `Anuncio.obter_estatisticas()` são a mesma instância modificada pelo repositório. Não criar contadores paralelos. Para registrar eventos no fluxo integrado, usar as operações do repositório em vez de modificar saldo ou estatísticas diretamente.

Cliques contextuais revalidam status e saldo, debitam o CPC e incrementam a métrica sob o mesmo `RLock`. Uma falha restaura saldo, status e contador. Saldo remanescente inferior ao CPC marca a campanha como ESGOTADA. Cliques genéricos incrementam apenas a métrica. Visualizações não debitam saldo. `AnuncioNaoEncontrado` e `CampanhaInelegivel` devem ser traduzidos pelo futuro controller para 404 e 409, respectivamente.

Cada chamada representa um novo evento; a interface atual não recebe chave de idempotência e não deduplica solicitações repetidas. A garantia de concorrência vale para threads que usam a mesma instância, em um único processo. Não há persistência após reinício nem proteção entre múltiplos workers. SQLAlchemy/MySQL e deduplicação persistente são evolução futura, não implementada aqui.

## Domínio e apresentação

Campanhas usam `Decimal`, status explícitos e anúncios contextuais. Uma campanha PAUSADA pode ser preparada sem anúncios; `ativar()` exige ao menos um contextual. O anúncio genérico é configurado fora das campanhas.

`AnuncioResponse` usa Pydantic v2 e `from_attributes=True`. É um DTO para a futura view, não uma decisão de criar endpoint JSON. `renderizar()` produz um fragmento BANNER escapado e aceita URLs HTTP/HTTPS absolutas ou caminhos locais iniciados por uma única barra. Dados modificados após a construção são revalidados na renderização. NATIVE e VIDEO existem no enum, mas sua renderização lança `NotImplementedError` nesta etapa.

`imagem_banner` permite uma imagem contextual específica; quando vazia, usa `banner_url`. Os dois campos aparecem no diagrama, embora possam representar o mesmo dado; a view deve usar o fragmento renderizado para respeitar uma imagem específica.

## Demonstração isolada

A partir de `codigo/`:

```python
from uuid import UUID
from app.ads.model.repositorio import RepositorioAds

repo = RepositorioAds.seed()
pergunta = repo.obter(UUID(int=101))
assert pergunta.id == UUID(int=101)
assert len(repo.listar_ativas()) == 2
assert repo.obter_anuncio(UUID(int=11)).titulo == "Curso de Python"
assert repo.anuncio_padrao.id == UUID(int=30)
```

`seed()` cria uma nova instância com fixtures de demonstração e UUIDs estáveis. Não carrega nem modifica o armazenamento de perguntas real. As URLs `/static/...` ilustram os dados do domínio; os arquivos de imagem e sua publicação não estão incluídos. Não apresentar esta demonstração como integração HTTP/SSR concluída.

## Testes

Dependências de execução permanecem em `codigo/requirements.txt`; `requirements-dev.txt` acrescenta o pytest. Após preparar um ambiente com essas dependências, executar a partir de `codigo/`:

```bash
python -m pytest -q
```

Os testes cobrem domínio, URLs/HTML, DTO Pydantic, preservação da identidade de Conteúdo, seleção determinística, reversão de falha e concorrência em memória. Não substituem os testes HTTP da #27.

A seleção da #25 está documentada em `MATCH_EXATO.md`, distribuído junto da implementação dessa estratégia.

Os testes de Ads ficam em `tests/ads/`, com fixtures locais para evitar conflito com o `conftest.py` do PR #32 (subequipe 01). O pytest.ini segue o mesmo conteúdo proposto naquele PR. O intervalo de pytest no requirements-dev é compatível com o pin 9.1.1 proposto pela subequipe 01; a validação local desta alteração foi feita com pytest 7.4.4.
