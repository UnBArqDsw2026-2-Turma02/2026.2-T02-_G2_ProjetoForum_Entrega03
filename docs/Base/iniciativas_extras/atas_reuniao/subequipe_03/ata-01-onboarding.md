# Ata 01 - Onboarding

**Data:** 15/10/2026<br>
**Subgrupo:** SubEquipe_03<br>
**Canal:** Google Meet<br>
**Liderança responsável:** Pedro Felipe Silva Vargas

### Participantes

| Nome do Membro | Presente |
| -- | :-: |
| Alberto Côrtes Cavalcante | Sim |
| Bruno Souza Assis Furtado | Sim |
| Kaio Amoury Sasaki Acacio | Sim |
| Pedro Felipe Silva Vargas | Sim |

### Gravação

<div style="text-align: center;">
  <iframe width="560" height="315" src="https://www.youtube.com/embed/uoqYAhwyIag" title="Reunião 1 - Onboarding - SubEquipe_03" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>
</div>

### Resumo

Reunião de alinhamento da SubEquipe_03 para a Entrega 03 (Padrões de
Projeto). O grupo reconheceu o atraso no cronograma, manteve o escopo
inteiramente voltado aos anúncios e à monetização do fórum e comparou os
padrões comportamentais candidatos. Por causa do prazo, decidiu por
unanimidade aplicar um único padrão, o **Strategy**, na seleção e exibição de
anúncios, e planejou as próximas atividades: diagrama de classes no Miro,
implementação em FastAPI, vídeo de execução e relatório.

### Pauta

1. Atraso no cronograma e escopo da Entrega 03
2. Avaliação dos padrões comportamentais candidatos (Strategy e Observer)
3. Decisão sobre aplicar um ou mais padrões
4. Definição do Strategy e planejamento das atividades
5. Problemas de acesso ao Miro e alinhamento de agenda

### Detalhes da discussão

**Atraso no cronograma e escopo da entrega.** Pedro Vargas assumiu a
responsabilidade pelo atraso no cronograma da Entrega 03, causado por uma
confusão com os prazos (00:00:08). Ficou estabelecido que o escopo manterá o
foco total em anúncios e monetização, deixando de fora a API corporativa e o
Teams. Os artefatos exigidos são um padrão de projeto comportamental do GoF,
com modelo UML, código executável em FastAPI, vídeo de um a dois minutos com
o padrão em execução e relatório (00:02:33).

**Avaliação dos padrões comportamentais.** Pedro Vargas apresentou duas
opções: o padrão Strategy, para exibir anúncios contextuais ou genéricos a
partir das tags da pergunta, e o padrão Observer, para eventos de campanha,
como avisos por e-mail de limite de orçamento e pausa de banners (00:05:10).
Bruno Souza comentou que o Observer faz sentido para painéis em tempo real e
notificações, enquanto o Strategy se encaixa bem no encapsulamento da regra
de seleção de anúncios (00:08:29).

**Decisão de aplicar um único padrão.** Bruno Souza sugeriu também o padrão
State para o ciclo de vida da campanha, mas a ideia foi descartada para
evitar complexidade excessiva (00:09:45). Pedro Vargas argumentou que aplicar
dois padrões exigiria dois modelos UML, dois códigos e dois vídeos de
execução, o que não caberia no prazo (00:11:53). Após Bruno Souza confirmar
que a entrega ocorre na segunda-feira, 19/10, o grupo concordou por
unanimidade em concentrar os esforços em um único padrão (00:14:21).

**Definição do Strategy e planejamento.** A equipe decidiu aplicar o
Strategy à lógica de exibição de anúncios: o sistema seleciona anúncios
patrocinados a partir das tags da pergunta (por exemplo, Java ou Python) ou
recorre a um anúncio genérico quando nenhuma campanha corresponde
(00:16:13). Pedro Vargas propôs concluir o diagrama de classes em UML até o
dia seguinte, estruturando as ideias em um quadro no Miro, e depois
desenvolver o código, expor os endpoints e gravar o vídeo no Swagger UI
(00:17:34).

**Acesso ao Miro e agenda.** Os participantes enfrentaram falhas de
carregamento e de autenticação ao acessar o quadro do Miro, resolvidas após
redefinir o acesso (00:20:22). Bruno Souza avisou que estaria com a agenda
ocupada no dia seguinte por entregas de outros projetos e sugeriu concentrar
as atividades no sábado pela manhã (00:19:07). Depois de acessarem o Miro e
consultarem exemplos do padrão no Refactoring Guru, Pedro Vargas pediu a
Alberto Côrtes que encerrasse a gravação (00:29:11).

### Decisões

| Decisão | Situação |
| -- | :-: |
| Escopo da Entrega 03 inteiramente focado em anúncios, sem a API corporativa e o Teams | Alinhada |
| Aplicar um único padrão comportamental do GoF, por causa do prazo | Alinhada |
| Padrão Strategy escolhido para a seleção e exibição de anúncios | Alinhada |

### Encaminhamentos

| Responsável | Encaminhamento |
| -- | -- |
| SubEquipe_03 | Elaborar o diagrama de classes UML do Strategy no Miro até o dia seguinte, para revisão do grupo |
| SubEquipe_03 | Implementar as classes do Strategy e os endpoints em FastAPI |
| SubEquipe_03 | Gravar o vídeo de demonstração, de um a dois minutos, com o padrão em execução no Swagger UI |
| SubEquipe_03 | Redigir o relatório conforme os requisitos da Entrega 03, incluindo o modelo UML e o relato das atividades |

### Comprobatório

Gravação no YouTube: [https://youtu.be/uoqYAhwyIag](https://youtu.be/uoqYAhwyIag)
