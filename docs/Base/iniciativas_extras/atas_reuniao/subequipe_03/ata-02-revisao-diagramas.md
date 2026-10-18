# Ata 02 - Revisão dos diagramas e planejamento da entrega

**Data:** 17/10/2026<br>
**Subgrupo:** SubEquipe_03<br>
**Canal:** Google Meet<br>
**Liderança responsável:** Pedro Felipe Silva Vargas

### Participantes

| Nome do Membro | Presente |
| -- | :-: |
| Alberto Côrtes Cavalcante | Sim |
| Bruno Souza Assis Furtado | Não |
| Kaio Amoury Sasaki Acacio | Não |
| Pedro Felipe Silva Vargas | Sim |

### Gravação

<div style="text-align: center;">
  <iframe width="560" height="315" src="https://www.youtube.com/embed/BNTC2ppxa4w" title="Reunião 2 - Revisão dos diagramas - SubEquipe_03" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>
</div>

### Resumo

Reunião de revisão dos dois diagramas de classes do Strategy, o teórico e o
técnico, e de organização da reta final da entrega. O grupo aprovou a
estrutura teórica com o limite de cinco tags por pergunta, retirou o status
de campanha em rascunho do diagrama técnico, definiu o conteúdo obrigatório
do relatório (contexto, diagramas UML, trechos de código e vídeo de execução)
e combinou usar as issues do GitHub como referência das tarefas, com os
responsáveis definidos com antecedência, e uma nova reunião na noite
seguinte para revisar o código.

### Pauta

1. Revisão do diagrama teórico no Miro
2. Revisão do diagrama técnico, dos status de campanha e dos formatos de anúncio
3. Organização visual do diagrama e pendências gerais
4. Requisitos do relatório e gravação do vídeo da API
5. Alinhamento sobre as issues e a integração com a SubEquipe_01
6. Avaliação da disciplina e retorno sobre rastreabilidade
7. Orientação do diagrama e análise das issues geradas com apoio de IA
8. Prazos, atribuições e próxima reunião

### Detalhes da discussão

**Revisão do diagrama teórico.** Pedro Vargas apresentou o rascunho e a
versão final do diagrama teórico no Miro, explicando o funcionamento do
controlador de entrega e do seletor de estratégia, que escolhe entre as
estratégias de match exato de tag, de maior saldo na tag e de anúncio
genérico (00:00:03). Alberto Côrtes concordou com a estrutura (00:01:34).
Sobre a quantidade de tags, Pedro Vargas sugeriu um máximo de cinco por
pergunta, e Alberto Côrtes ponderou que isso depende da definição da
SubEquipe_01, responsável pelo conteúdo, mas concordou com o número a
princípio (00:04:27). A estrutura teórica foi aprovada com o limite de cinco
tags (00:03:09).

**Revisão do diagrama técnico.** Pedro Vargas destacou que o diagrama
técnico, alinhado à stack em Python, reduz erros de codificação e especifica
os formatos de anúncio (banner, nativo e vídeo) (00:05:18). Também sugeriu
retirar o status de rascunho das campanhas, por considerá-lo desnecessário,
mantendo ativa, pausada, esgotada, suspensa, encerrada e cancelada. Alberto
Côrtes avaliou o diagrama como bem organizado, e o grupo manteve o diagrama
técnico sem o status de rascunho (00:06:26).

**Organização visual e pendências.** Alberto Côrtes comentou que a
disposição vertical do diagrama exige rolagem, embora não prejudique a
compreensão. Pedro Vargas relatou que uma ferramenta de IA generativa
continuou editando o Miro automaticamente mesmo após atingir o limite de
conexão (00:09:37). Em seguida, listou as pendências: criação das branches,
organização das pastas de código, atualização do relatório e gravação do
vídeo (00:10:48). O grupo considerou a orientação aceitável e decidiu focar
nas pendências (00:09:37).

**Requisitos do relatório e do vídeo.** Pedro Vargas detalhou as seções
obrigatórias do relatório: contexto do problema, imagens da modelagem UML e
implementação, com trechos de código e um vídeo mostrando a API no Swagger
com a troca de estratégias (00:12:28) (00:16:03). Alberto Côrtes questionou a
estrutura do repositório no GitHub e a rastreabilidade entre a modelagem e a
implementação (00:13:48). Ficou definido incluir no relatório o contexto, os
dois diagramas UML, os trechos de código e o vídeo de execução (00:16:03).

**Issues e integração com a SubEquipe_01.** Alberto Côrtes sugeriu
acompanhar o andamento da SubEquipe_01 para entender a integração das
perguntas e das tags (00:17:34). Pedro Vargas argumentou que as issues do
GitHub já detalham endpoints, parâmetros esperados e critérios de aceite,
servindo de modelo direto para o trabalho (00:19:03). O grupo decidiu usar as
issues como referência, sem reuniões conjuntas adicionais (00:17:34).

**Avaliação da disciplina e rastreabilidade.** Pedro Vargas e Alberto Côrtes
conversaram sobre a expectativa de menção máxima (SS) nas entregas
(00:21:39). Sobre o retorno da entrega anterior, que apontou falhas de
rastreabilidade, Alberto Côrtes explicou que faltou mostrar com clareza como
as contribuições individuais se relacionavam entre si. O grupo reconheceu a
necessidade de evidenciar essa integração nas próximas etapas (00:26:56).

**Orientação do diagrama e issues geradas com apoio de IA.** Pedro Vargas
passou o diagrama do Miro para o modo paisagem, preferido por Alberto Côrtes
para a leitura no notebook (00:28:18). Em seguida, apresentou issues e
trechos de código gerados com apoio de IA generativa para orientar a
implementação das estratégias (00:33:34). Alberto Côrtes recomendou usar os
diagramas de classes como base principal, sem seguir à risca o código
gerado. O grupo manteve o diagrama em paisagem e as issues como diretrizes
alinhadas à modelagem UML (00:28:18) (00:35:36).

**Prazos, atribuições e próxima reunião.** Pedro Vargas propôs uma reunião
na noite seguinte para revisar o código e gravar o vídeo, e sugeriu definir
com antecedência os responsáveis de cada issue no GitHub, para evitar
atrasos. Alberto Côrtes concordou e confirmou que atualizaria as atas e
publicaria a documentação em docsify no GitHub Pages. Ficou combinado
concluir a documentação e os vídeos até a entrega de segunda-feira, 19/10
(00:38:44) (00:41:25).

### Decisões

| Decisão | Situação |
| -- | :-: |
| Incluir no relatório dois diagramas UML: um teórico e explicativo e outro técnico, baseado na stack | Alinhada |
| Limite de cinco tags por pergunta no diagrama teórico, a confirmar com a SubEquipe_01 | Alinhada |
| Retirar o status de campanha em rascunho do diagrama técnico | Alinhada |
| Realizar nova reunião na noite seguinte para revisar o código | Alinhada |
| Definir com antecedência os responsáveis de cada issue do código | Alinhada |

### Encaminhamentos

| Responsável | Encaminhamento |
| -- | -- |
| Pedro Vargas | Criar as issues do código e definir os responsáveis de cada uma |
| Pedro Vargas | Enviar um áudio no grupo informando as decisões e a situação do projeto |
| Alberto Côrtes | Publicar a documentação em docsify no GitHub Pages, com as atas atualizadas |
| Alberto Côrtes | Registrar as datas corretas das reuniões nas atas |
| SubEquipe_03 | Participar da reunião da noite seguinte para revisar a implementação e alinhar os próximos passos |

### Comprobatório

Gravação no YouTube: [https://youtu.be/BNTC2ppxa4w](https://youtu.be/BNTC2ppxa4w)
