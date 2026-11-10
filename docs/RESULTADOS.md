# Resultados concretos e controles

Este inventário identifica a **evidência, seu protocolo e o arquivo primário**. Números de diferentes experimentos não são somados como se fossem uma única avaliação integrada.

## Experimento 08 · descoberta de estruturas

Um aprendiz com relações inicialmente não ensinadas recebe sinais binários opacos e consequências e propõe/promove/esquece esferas a partir de experiências. A emissão de um raio ativa a esfera e a completude da configuração é testada separadamente. A suíte original contém **8 testes**, incluindo ausência observada diferente de valor desconhecido, indexação local, persistência e formação. Dados em `experiments/08-aprendizagem-esferas/resultados.json`.

## Experimento 14 · substrato integrado

Em **9 mundos × 3 sementes × 260 consultas reservadas** por configuração, o modelo de controle alcançou acurácia balanceada **1,000** no mundo de quatro partes, contra **0,500** no comparador Exp08. Há também ambientes com deriva, nulo e dígitos reais; neles a integração não é universalmente superior. As métricas estão em `experiments/14-morfon-integrado/dados/consolidacao.json` e registros individuais em `dados/principal_*_individuais.json`. **14 testes** reexecutados.

## Experimento 17 · composição de referências e aritmética

Treino em 240 mundos: **8.160** enunciados ancorados, **10.080** perguntas demonstradas e **1.920** demonstrações de referência; avaliação em 40 mundos reservados: **2.000/2.000**, com **320 composições novas** de dois ou três saltos. Transições numéricas aprendidas de supervisão com estados intermediários: **1.000/1.000** cálculos inéditos. Controles incluem privação de fatos e embaralhamento de respostas. Métricas em `results/metricas.json`, instâncias em `results/avaliacao_individual.json` e `results/avaliacao_numerica.json`. **18 testes** reexecutados.

## Experimento 21 · memória contínua

**384/384** consultas sobre observações novas, **6/6** construções ensinadas em diálogo, **175/175** consultas de paráfrases ensinadas, **173/173** verificações adversariais; continuidade após salvar/restaurar. Registros em `results/summary.json`, `results/paraphrase_summary.json`, `results/adversarial_summary.json` e sessões reais. **38 testes** reexecutados.

Uma auditoria causal histórica identificou que parte da recuperação factual deste ramo dependia de índices externos, não exclusivamente da propagação física de raios. Por isso, a causalidade das marcas deve ser atribuída aos experimentos em que houve **intervenção física sobre marcas/portas**, especialmente Exp23–24, e não presumida para toda interface conversacional histórica.

## Experimento 23 · marcas nas faces

Bateria confirmatória: cinco famílias de mundos binários, 12 sementes, **60 instâncias**, 2.880 experiências e **960 consultas reservadas**. Marcas algébricas de grau até 2: **960/960 acertos**, **962/962** objetivos alcançados.

Ablações: bloquear pulsos retirou 240/240 resultados; retirar marcas ativas alterou 651/651 saídas; remover marcas inativas preservou 240/240. Seleção ativa em teste separado: **3.200/3.200**, frente a **2.897/3.200** com seleção aleatória sob igual orçamento. Ruído de três erros por palavra corrigido em **960/960** consequências observadas. Testes com funções aleatórias resultaram em **320 abstenções**, sem extrapolação injustificada. Registros em `results/confirmatory.json`, `results/causal_ablations.json`, `results/active_design.json` e `results/adversarial.json`. **13 testes** reexecutados.

## Experimento 24 · aprendizagem, intervenção e revisão integradas

48 instâncias com 22 experiências por instância em cada condição (mesmo orçamento). Estratégia de ganho informacional: **480/480** previsões identificadas; controle aleatório **328/480**, com 152 abstenções. Planos bem-sucedidos: **1.034/1.034** contra **942/1.034**. Objetivos de sinal: **576/576** contra **559/576**. Foram executados ciclos de planejamento, ação real simulada, observação e atualização na mesma memória.

Em funções de terceira ordem antes de aprendizado suficiente, houve previsão errada registrada; experiências adicionais levaram à aprendizagem de marcas de grau superior e acerto de **2/2** consultas restantes por semente. Remover uma porta realmente utilizada mudou a previsão, e restaurá-la recuperou o resultado. Abstenção foi observada diante de contradições com entrada idêntica. Registros em `results/integrated.json`, `results/adversarial.json`, `results/scale.json`. **13 testes** reexecutados.

## Malhas relacionais compartilhadas

**600/600** classificações corretas sob identidade canônica e contexto compatível, com **313** composições positivas entre malhas e **287** negativas. Ignorar contexto criou **126** falsos positivos; confundir nomes criou **110** falsos positivos. Custo sintético parametrizado: **21,99%** de economia calculada por compartilhamento de identidades. Proveniência: no caso com 12 losangos, **4.096** percursos possíveis, **108 nós** no DAG, **48** incidências examinadas contra **16.380** na expansão explícita; consultas fatoradas verificadas por comparação com enumeração independente em **250 grafos aleatórios**. `results.json`, `case_predictions.jsonl` e `test_experiment.py`. **11 testes** reexecutados.

## O que os protocolos estão medindo

A validade dos resultados decorre do **contrato de cada teste**: mundos sintéticos com leis ocultas ao aprendiz, treinamento/resposta separados, exemplos reservados, comparação com baselines, ablação física, adversários, integridade da memória e controle de origem das evidências. Os experimentos de linguagem usam supervisão estruturada; funções GF(2) pertencem à família escolhida; o laboratório de malhas verifica propriedades formais sobre estruturas fornecidas. Essas especificações tornam as conquistas **verificáveis**, sem expandir indevidamente sua definição.

Use `python scripts/verify_results.py` para verificar os números dos arquivos JSON incluídos e `python scripts/test_all.py` para reexecutar os 115 testes de regressão.
