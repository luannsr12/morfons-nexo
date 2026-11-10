# Arquitetura NEXO · visão de pesquisa

O NEXO investiga uma **memória relacional executável**: organização, armazenamento, inferência e aquisição de funções são estudados sobre unidades que persistem, recebem sinais e mantêm relações explícitas.

## Unidade Mórfon

- **Núcleo estável:** contrato operacional de sinalização com três estados/vias `−1, 0, +1`. O núcleo não precisa ser reescrito para que um Mórfon aprenda novos conteúdos ou operações.
- **Superfície mutável:** faces, fragmentos, portas, marcas de interação e referências podem ser criados, atualizados, ligados e reutilizados.
- **Ativação:** um raio incidente basta para ativar; incidências adicionais podem aumentar o suporte físico/contextual. Contagem de percursos combinatórios não é igual ao número de emissores físicos distintos.
- **Memória:** observações, contexto, origem das evidências, histórico e configurações aprendidas integram organizações persistentes.
- **Mórfons Gênesis:** unidades iniciais com operações elementares de criação, replicação, modificação e remoção de organizações. Não se postula uma origem sem nenhuma capacidade operacional.

## Aprendizagem e inferência

1. Eventos produzem fragmentos observados, identificados ou criados.
2. Fragmentos ativam relações localmente, conservando contexto e proveniência.
3. Regularidades observadas podem estabelecer estruturas/funções reutilizáveis.
4. Estruturas aprendidas permitem responder a consultas e antecipar consequências não ensinadas explicitamente.
5. Ações e novas observações podem confirmar, modificar ou invalidar uma hipótese, conservando o histórico.

Nos experimentos funcionais 23 e 24, os sistemas aprendem relações específicas sobre processos binários com funções de grau limitado em GF(2). As operações genéricas de eliminação, organização e seleção de planos são implementadas como mecanismos gerais; os coeficientes e regularidades dos mundos são aprendidos das experiências.

## Malhas com identidade canônica compartilhada

Uma identidade de Mórfon pode participar de mais de uma malha sem duplicação obrigatória da unidade. Isso permite composições entre regiões distantes, desde que sejam preservadas identidade, tipos de relação e compatibilidade contextual.

No ensaio matemático, `m` participações em malhas, `u` identidades únicas, custo `b` por unidade, `q` por referência e `c` por ponte entre cópias dão a economia:

`Δ = (m − u)(b + c) − mq`.

Para `m=3600`, `u=2561`, `b=64 B`, `q=8 B`, `c=16 B`, obtém-se `Δ=54320 B` (**21,99%**) no modelo de custo explicitado. É uma conta formal sobre o modelo, não uma medição de uso de RAM Python.

As provas relacionais podem ser compactadas como DAGs com referências compartilhadas, conservando sua proveniência sem materializar todas as combinações de caminhos.

## Continuidade histórica das demonstrações

| Experimento | Questão central |
|---|---|
| 08 | Descoberta, promoção e descarte de estruturas preditivas em memória inicialmente sem relações aprendidas |
| 14 | Um único substrato para Mórfons, raios, composição, controle de ordem, persistência e poda |
| 17 | Linguagem ancorada em observações, composição relacional, contexto e transições binárias |
| 21 | Memória persistente de diálogos, ensino incremental e revisão de fatos |
| 23 | Marcas operacionais nas faces, ablações e investigação ativa |
| 24 | Fluxo integrado experiência → hipótese → previsão → ação → feedback → revisão |
| Malhas | Compartilhamento canônico entre contextos, antiunificação e fatoração de proveniência |

As implementações refletem contratos de laboratório distintos, conservados sem mesclagem silenciosa. A restrição específica `writer_uid != receiver_uid` no Exp. 24 é um contrato daquela bateria, não uma imposição universal sobre todas as futuras organizações de Mórfons.

Referência conceitual completa: [artigo no Zenodo](https://doi.org/10.5281/zenodo.24094723).
