# Issue #25 — Estratégia de match exato

Implementação `app.ads.model.match_exato.EstrategiaMatchExatoDeTag`, consumindo os contratos da #24. A classe atende ao Protocol sem herança explícita e retorna o nome de política `match_exato`.

Uma campanha é elegível quando ATIVA, com anúncio contextual, tag em comum e `saldo_restante >= custo_por_clique > 0`. As tags são comparadas por `casefold()`. O desempate usa menor UUID da campanha e depois menor UUID do anúncio, sem depender da ordem da entrada. Não existe prioridade por número de tags, CPC ou saldo.

A seleção não altera métricas, status, saldo ou a lista recebida. Sem candidato, retorna `None`; cabe ao Context da #27 chamar a estratégia genérica da #26.

A partir de `codigo/`, após preparar o ambiente:

```python
from uuid import UUID
from app.ads.model.match_exato import EstrategiaMatchExatoDeTag
from app.ads.model.repositorio import RepositorioAds

repo = RepositorioAds.seed()
estrategia = EstrategiaMatchExatoDeTag()
pergunta = repo.obter(UUID(int=101))
anuncio = estrategia.selecionar_anuncio(pergunta, repo.listar_ativas())
assert anuncio.id == UUID(int=11)
assert estrategia.selecionar_anuncio(repo.obter(UUID(int=102)), repo.listar_ativas()) is None
```

Executar `python -m pytest -q tests/ads/test_ads_match_exato.py` para testar elegibilidade, empate determinístico e ausência de efeitos colaterais. O seed contém dados de demonstração e não representa integração com perguntas/tags reais.

O ranking por maior lance/CPC que constava anteriormente na issue foi substituído pela política do diagrama por orientação de Pedro. A divergência com a referência anterior RF02 permanece uma decisão a validar pelo grupo, sem alegação de atendimento ao requisito antigo.
