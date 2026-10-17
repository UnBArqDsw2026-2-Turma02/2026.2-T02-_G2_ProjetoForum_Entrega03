# Como contribuir

Este repositório é mantido em grupo. Para manter o histórico organizado e evitar
retrabalho, siga o fluxo abaixo em toda contribuição (documentação ou código).

## 1. Nunca commitar direto na `main`

A branch `main` só recebe alterações por meio de Pull Request revisado por
outra pessoa do grupo. Nenhum push direto é permitido.

## 2. Fluxo de branch

1. Atualize sua `main` local:
   ```shell
   git checkout main
   git pull origin main
   ```
2. Confira as branches já existentes no remoto (`git branch -a`) antes de
   criar uma nova, para não duplicar trabalho de outro integrante ou
   subgrupo.
3. Crie uma branch a partir da `main`, com um nome curto e descritivo do que
   será feito. A SubEquipe_03 vem usando o padrão `feat/S{N}-descricao`
   (um branch por issue/etapa da Strategy), por exemplo:
   - `feat/S0-setup-contratos-ads`
   - `feat/S1-estrategia-contextual`
   - `feat/S2-estrategia-generica`
   - `feat/S3-controlador-entrega`
   - `feat/S4-estrategia-maior-saldo`

   Para documentação sem issue de código associada, use `docs/descricao`
   (ex.: `docs/relatorio-subequipe03`).
4. Trabalhe e commite na sua branch.
5. Antes de abrir o Pull Request (ou se ele demorar para ser revisado),
   atualize sua branch com a `main` para evitar conflitos:
   ```shell
   git fetch origin
   git merge origin/main
   ```
6. Envie a branch para o repositório remoto:
   ```shell
   git push -u origin nome-da-sua-branch
   ```
7. Abra um Pull Request para a `main` explicando o que foi feito. Se a
   contribuição fechar uma issue do GitHub, referencie-a no corpo do PR
   (ex. `Refs #27` ou `Closes #27`, conforme o estado real do trabalho).
8. Aguarde a aprovação de pelo menos uma outra pessoa do grupo antes do merge.

## 3. Mensagens de commit

- Todas as mensagens de commit devem ser escritas em português.
- Prefira mensagens curtas e diretas, no imperativo, descrevendo o que a
  alteração faz, por exemplo:
  - `Implementa EstrategiaAnuncioGenerico (Issue #26)`
  - `Adiciona ControladorEntrega e rotas FastAPI (Issue #27)`
  - `Corrige link quebrado no sidebar`

## 4. Identidade nos commits

Cada commit deve ficar atrelado à conta GitHub de quem efetivamente realizou
a contribuição. Confira se `git config user.name` e `git config user.email`
correspondem à sua conta antes de commitar.

## 5. Estrutura de documentação

A documentação segue o template oficial da disciplina, organizada em
`docs/Base` e `docs/Projeto`. Não omita seções exigidas pelo template; se uma
seção ainda não tiver conteúdo, deixe um placeholder claro indicando que está
pendente, em vez de removê-la.

## 6. Legenda das imagens e links internos do docsify

Toda imagem de artefato (diagrama UML, print de ferramenta de modelagem)
deve ter uma legenda logo abaixo, no seguinte formato:

```html
<p align="center">
  <img src="/Base/Relatórios/assets/nome-do-arquivo.png" alt="Descrição da imagem" width="600">
</p>
<p align="center"><b>Figura N</b> — Descrição breve do que a imagem mostra.<br>
<b>Fonte:</b> origem da imagem (ferramenta de modelagem, "Elaborado pela SubEquipe 0X", etc.).</p>
```

- **Todo link interno do docsify (imagem, `[]()` markdown ou link do
  `_sidebar.md`) deve ser absoluto, começando com `/` a partir da raiz de
  `docs/`** (ex.: `/Base/Relatórios/assets/arquivo.png`,
  `/Base/Relatórios/1.1.3.SubEquipe_03.md`). Nunca usar `./` ou `../`.
  Isso vale tanto para `<img>` em HTML puro quanto para a sintaxe
  `![]()`/`[]()` de markdown: o docsify, por padrão
  (`relativePath: false`), resolve **todo** link relativo a partir da raiz
  de `docs/`, não da pasta do arquivo onde o link foi escrito. Usar `./`
  ou `../` gera uma tela de "página não encontrada" da SPA assim que o
  usuário navega para fora da Home - esse bug já ocorreu de verdade na
  Entrega 02 (corrigido no PR `fix/links-sidebar-absolutos`, #19) e deve
  ser evitado desde o início aqui.
- A numeração das Figuras é **sequencial pelo documento inteiro**,
  seguindo a ordem em que as imagens aparecem no arquivo (não reinicia por
  seção nem por autor). Antes de adicionar uma imagem nova, confira qual é
  a última Figura já numerada no arquivo e continue a partir dela. Se você
  inserir uma imagem antes de figuras já numeradas, renumere as
  seguintes.

## 7. Código (quando a contribuição envolver `codigo/`)

- Antes de abrir o Pull Request, rode os testes a partir de `codigo/`:
  ```shell
  python -m pytest -q
  ```
- Documente a implementação com um trecho de código relevante no relatório
  (`docs/Base/Relatórios/1.1.3.SubEquipe_03.md`), com link direto para o
  arquivo real no repositório, além do vídeo pré-gravado mostrando o
  padrão em execução - exigência explícita da disciplina para esta
  entrega (Padrões de Projeto).
- Siga o contrato já definido para a Strategy em
  `codigo/app/ads/model/strategies.py` e os pontos em aberto documentados
  em `codigo/app/ads/README.md` antes de propor mudanças de design.
