# NEXO — Experimento 24: núcleo constante, marcas recebidas, ação entre Mórfons

**Data:** 9/11/2026. **Condição:** bateria executada, código e experiências incluídos. **Núcleo herdado:** `MorphMemory` do Exp21/22, `morfon_exp21_original.py`, conservado byte a byte.

## Problema investigado

O Exp23 tratava subdivisões de faces como edições desencadeadas por divergência. Essa era uma hipótese adicionada pelo pesquisador, não um invariante aprovado. A reformulação preserva os invariantes corrigidos pelo autor:

1. **Face = marca de uma interação recebida** pelo Mórfon, registrada com origem e episódio. Uma nova divergência não desencadeia, por regra, uma subdivisão geométrica.
2. **Núcleo constante:** para cada Mórfon existe uma lei de operação `Nucleus`, congelada (`dataclass(frozen=True)`), com mesma álgebra genérica para os episódios deste ensaio. Nenhuma experiência muda a lei do núcleo.
3. **Não há autoedição:** um Mórfon não escreve em suas próprias faces. Sempre há `actor_uid != target_uid`. O Mórfon da ocorrência, por meio do seu núcleo constante, inscreve marcas no Mórfon da relação que ela modifica. Mórfons de relação podem inscrever previsões e intenções em outros Mórfons.
4. **Raios:** uma incidência ativa, incidências adicionais aumentam o suporte físico; completude das portas é outra propriedade, como no núcleo original.
5. **Memória única:** rastros observados, marcas aprendidas, perguntas internas, antecipações, decisões e última ação vivida são unidades/atividades da mesma `MorphMemory`.

Nenhum algoritmo de mundo, ação especial ou resposta-alvo é embutido no aprendiz. As *operações genéricas* do núcleo (eliminação em GF(2), restrição, busca em grafo de transições, gravação em outro Mórfon) são declaradas como parte do programa, de forma auditável.

## O mecanismo efetivamente implementado

Cada episódio `e`, com observação `(x,a,y)`, é um Mórfon distinto. O evento recebe raios das fontes sensoriais/da ação, e o seu núcleo escreve em outro Mórfon `R_(a,j)` uma face de experiência para cada consequência observada `y_j`.

O núcleo da ocorrência consulta as faces de experiência do receptor e calcula a função booleano-relacional de **menor grau que as satisfaz** até o grau máximo da experiência:

\[
\hat y_j(x) = \bigoplus_{S:|S|\le d} c_S \prod_{i\in S} x_i.
\]

Isso usa eliminação de Gauss sobre o campo finito GF(2). O código é genérico: não recebe os coeficientes verdadeiros nem o significado dos sinais. Cada coeficiente não nulo aprendido é outro Mórfon ligado por portas ao Mórfon da relação e aos sinais necessários; o evento escritor coloca uma marca na face desse Mórfon, com `actor_uid != target_uid`.

Se a marca de interação continua sendo pertinente após novos episódios, o receptor **reutiliza a mesma marca**. Faces históricas não são apagadas. A versão atual é uma nova face, escrita pelo evento; não ocorre mutação da face pelo próprio Mórfon receptor.

A consulta de uma consequência realmente dispara `MorphMemory.pulse_units`: marca e relação precisam de portas certificadas. O resultado XOR resulta das marcas certificadas presentes, **não do valor que o solver calculou como resposta**. A eliminação também verifica se o valor é identificável com as observações; se não for, a consulta se abstém.

A simulação interna grava sua consequência como um Mórfon de origem `internal`, não como episódio `observed`. Uma decisão de ação por consequência desejada é registrada em outro Mórfon. O ambiente externo é chamado pelo laboratório, e a consequência real volta como evento. A última ação executada fica registrada na face do Mórfon de sessão, escrita pelo Mórfon do episódio. Dessa forma o histórico consultado no passo seguinte vem da própria memória.

### Ciclo completo executado (caso individual)

No mundo 0, semente 0, a memória encontrou, simulou internamente e executou o plano `(ação 0, ação 1)` após aprender as ações por episódios independentes:

| Passo | Antes: 3 sinais + última ação | Ação | Previsto | Observado |
|---|---|---:|---|---|
| 1 | `0,1,0,1` | 0 | `1,1,0` | `1,1,0` |
| 2 | `1,1,0,0` | 1 | `1,0,0` | `1,0,0` |

O segundo contexto, `última ação=0`, foi gravado na memória **depois da primeira ação real**. Cada consequência gerou novas marcas de interação, mantendo o núcleo invariável. O objetivo final foi atingido. Casos equivalentes e rastros completos constam em `results/integrated.json`.

## Avaliação confirmatória principal

**Quatro famílias de processos binários distintas × 12 variações isomórficas de canais por semente = 48 instâncias por condição.** Cada instância possui 3 sinais de estado, 1 sinal de histórico efetivo (última ação), 2 ações e 3 resultados sensoriais. Os efeitos de mundo são de grau algébrico até 2 por construção. As sementes permutam e invertem canais físicos, preservando o grau das transformações; **não se trata de 48 famílias estruturalmente independentes**. Os geradores estão em `src/evaluate.py` e **não são importados pelo aprendiz**.

Cada condição recebeu exatamente **11 experiências por ação**, 22 por instância. A condição `rank` escolhe a próxima experiência a partir da independência informacional das experiências já inscritas nas faces dos Mórfons. A condição `random` recebe o mesmo orçamento em entradas sorteadas. As consultas reservadas de cada condição são as suas próprias entradas não ensinadas (não o mesmo subconjunto literal entre condições); os mundos e as tarefas de ação são idênticos por semente.

| Medida | Seleção por marcas | Amostragem aleatória |
|---|---:|---:|
| Experiências ensinadas | 1.056 | 1.056 |
| Entradas reservadas | 480 | 480 |
| Previsões corretas | **480** | **328** |
| Previsões erradas emitidas | 0 | 0 |
| Abstenções | 0 | 152 |
| Planos com objetivos alcançáveis | 1.034 | 1.034 |
| Planos efetivamente bem-sucedidos | **1.034** | **942** |
| Tarefas de alcançar um sinal desejado | 576 | 576 |
| Sinais alcançados | **576** | **559** |
| Passos de plano com previsão interna + execução + observação/atualização | **96** | 90 |
| Perguntas internas geradas durante aquisição | **1.056** | 0 (controle sem escolha ativa) |

A tarefa contínua exigiu **ao menos duas ações** para atingir o estado-alvo (seleção feita pelo laboratório, sem revelar o plano ao aprendiz). Após cada ação executada, a consequência retornou para a mesma memória; 96 ações nessas trajetórias foram registradas na condição ativa.

Nota: `questions` é a inscrição de uma consulta informativa, não evidência de que o sistema formulou linguisticamente perguntas abertas. O controle aleatório não chama a rotina de escolher perguntas e, portanto, registra zero por construção.

## Escala de representação

Seis mundos adicionais foram gerados independentemente com cinco sinais de estado, um bit de histórico, duas ações e cinco consequências observáveis. Cada ação tem função de até grau 2 em seis entradas. O núcleo escolheu 22 experiências por ação (44 por mundo) e confrontou as funções com as 84 entradas restantes de cada mundo.

| Medida | Resultado |
|---|---:|
| Mundos | 6 |
| Experiências | 264 |
| Consultas não ensinadas | **504** |
| Acertos | **504** |
| Mórfons finais, somados nos seis mundos | 894 |
| Marcas funcionais novas | 180 |
| Reutilizações de marcas existentes | 1.838 |

A escolha foi feita de modo que o conjunto de experiências cubra todas as direções da base de grau 2; o resultado de generalização exata é esperado nessa classe algébrica, mas a execução comprova a integração do núcleo original, marcas e consultas por incidência.

## Testes adversariais e ablações

1. **Ordem algébrica insuficiente.** Em quatro sementes de um mundo com interações de terceira ordem, depois de 11 exemplos por ação houve, por semente, 1 previsão correta, **1 errada** e **8 abstenções** nas 10 entradas não observadas. Uma ação real com resultado contrário foi registrada como nova experiência (com previsão interna antes). Após completar 15 observações por ação, a mesma memória — sem alterar o núcleo — incorporou marcas de terceira ordem e acertou **2/2 consultas restantes** por semente. O erro anterior foi preservado nos dados.
2. **Contradição exata sem informação adicional.** Duas experiências com entradas e ação idênticas e consequências diferentes geraram a razão `inconsistent` e abstenção. As duas faces permaneceram na memória; nenhuma subdivisão arbitrária foi acionada.
3. **Ablação física de porta.** Em uma consulta correta, removi diretamente a aresta que liga a relação à marca aprendida na `cache` de portas do núcleo original. A consequência mudou de `(1,0,1)` para `(0,0,1)`. Restabelecer a aresta recuperou `(1,0,1)`; remover uma aresta não utilizada naquela inferência não alterou a resposta. Isso evidencia causalidade da ligação real.
4. **Supressão de raios.** Consultas com pulsos impedidos não produziram previsão.
5. **História ausente.** Nos quatro mundos, respectivamente **12, 16, 14 e 8** pares de configurações por família apresentavam o mesmo estado físico e a mesma ação, mas consequências diferentes segundo a última ação vivida. Sem conservar história, qualquer função determinística precisaria errar em pelo menos uma ocorrência por par.
6. **Autorreforma.** Cada marca de face conserva o `writer_uid` e o `receiver_uid`; em todas as instâncias, `writer != receiver`. A classe `Nucleus` é congelada e o contrato não permite escrita em si mesmo.
7. **Restaurar memória.** Os snapshots restaurados produziram as mesmas previsões em todas as consultas reservadas da bateria.
8. **Imaginar não é observar.** A simulação gera Mórfons de proveniência interna; não incrementa o conjunto de experiências observadas nem confirma a própria previsão.

**13/13 testes de software** passaram, incluindo ablações, núcleo congelado, um raio versus dois, experiências incompatíveis, restauração, simulação interna e generalização.

## Resultado contra o projeto original

- **Mantido:** `MorphMemory` original, portas, raios, ativação com uma incidência, suporte físico, rastros, memória única, histórico, experiências, atualizações e modelos aprendidos. Núcleo constante que atua sobre outros Mórfons.
- **Corrigido em relação ao Exp23:** nenhuma regra inventada de subdivisão de face quando há contradição. Faces são exclusivamente marcas recebidas de interações, com proveniência. Nenhum Mórfon escreve em si; marcas reaproveitadas não são recriadas incessantemente.
- **Demonstrado em execução integrada:** receber estímulos, escolher experiências discriminantes com base na memória, aprender transformações, produzir previsões por raios e marcas, planejar combinações, emitir uma decisão, executar ações, observar o retorno e continuar aprendendo na **mesma** `MorphMemory`.

### Limites localizados (critérios de próximos experimentos)

A rotina de eliminação GF(2) e a busca por planos são **leis gerais previamente programadas no núcleo constante**; as funções específicas de mundo e suas marcas são aprendidas. Isso implementa a hipótese de função fundamental invariável, mas não demonstra que o NEXO tenha adquirido autonomamente o próprio algoritmo de eliminação ou busca. A posição física 3D das faces não é usada na decisão — o que age causalmente são sua proveniência, conteúdo e portas. O espaço de hipóteses é de grau limitado, e vimos uma previsão errada de terceira ordem antes de obter experiências suficientes. O ambiente de laboratório permite resetar situações para investigação e não introduz obstáculos de alcance físico, custo ou risco; esses problemas pertencem à próxima camada de avaliação. A linguagem livre e a formação de conceitos abertos não foram tarefas deste ensaio.

Esses limites não desfazem os resultados: delimitam exatamente o mecanismo executado e as partes da teoria que receberam um teste causal.

## Referências técnicas contrastadas

- Lafont, Y. (1990), *Interaction Nets*, POPL, https://doi.org/10.1145/96709.96718 — reescrita local como antecedente formal, **não** implementada aqui como tradução de seu cálculo.
- Singh et al., *Learning Predictive State Representations* (ICML 2003), https://aiinternational.org/Library/ICML/2003/icml03-093.php — contexto como história testável por interações e consequentes previsíveis; as classes PSR completas não foram reproduzidas aqui.
- Materiais anteriores do projeto, preservados no pacote: EXP22 (reorganização contextual) e EXP23 (ANF e marcas causais). O Experimento 24 preserva os mecanismos relevantes à continuidade e corrige o contrato das faces/núcleos.

## Reprodução

Requer Python 3.10+; nenhuma biblioteca externa para os testes matemáticos:

```bash
python -m unittest discover -s tests -v
python src/evaluate.py 12
python src/adversarial.py
python src/scale.py
```

Os logs e observações individuais produzidos pelos comandos estão em `results/`.
