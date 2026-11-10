# Relatório técnico — Experimento 14: integração, não coleção de vitórias isoladas

Data: 08/11/2026. Objetivo: integrar capacidades dos experimentos anteriores sem modificar o núcleo do NEXO principal, explicitando o que está completo, o que foi ablação e o que continua fora do contrato.

## 1. Contrato matemático do Mórfon

Uma unidade Mórfon `i` contém **um estado estrutural persistente**

```
M_i = (id_i, tipo_i, q_i, portas_i, marcas_i, faces_i,
       observações_i, positivos_i, subunidades_i)
```

- `q_i ∈ R^d`, com `d=3` ou `d=4`, é uma coordenada de organização; no Exp14 seu valor foi inicializado por hash estável da configuração, **não aprendido espacialmente**. Essa variante não prova que posições sejam uma memória semântica útil.
- `portas_i` é uma lista de **identificadores de outros Mórfons**, inclusive compostos aninhados. `marcas_i` é a representação persistente da presença de portas. As evidências de previsão e a fila de revisão são persistidas no próprio Mórfon.
- `faces_i` representa subdivisões discretas, e no Mórfon controlador conserva alternativas de operação com pares `n_testado,n_correto`. Não há rede secundária com outra classe de conhecimento.
- Um Mórfon `ledger` guarda os totais globais de experiências e resultados positivos. Assim, os agregados usados na seleção são também memória persistente em uma unidade.
- `id -> Mórfon`, `literal -> id` e `porta -> pais` são **índices de execução reconstruíveis** a partir das unidades. Não são um arquivo externo que substitui o conhecimento.

Em cada episódio, os raios atuais são conjuntos efêmeros `R_i(t)` de IDs que chegaram ao núcleo. A semântica é:

```
w_i(t) = |R_i(t)|
a_i(t) = 1[w_i(t) >= 1]
```

**UM raio ativa; MAIS raios elevam a sustentação; não há limiar de 2 ou mais para ativar.**

É essencial separar **ativação** de **correspondência completa** (`cert_i`):

```
cert_i(t) = AND_{j em portas_i} cert_j(t)
```

Com apenas uma porta que dispara, `a_i=1` mesmo que `cert_i=0`. Nesta implementação, apenas unidades completamente reconhecidas encaminham raios de composição a níveis superiores (`propagation=completed`) e podem fundamentar previsões. A alternativa `propagation=all` foi testada; produz propagação parcial adicional sem fornecer nova certificação.

Nas composições aninhadas, quatro fragmentos em duas subunidades disparam **dois raios diretos** para o Mórfon maior, não quatro. Comparar pesos físicos entre formas diferentes como se fossem o mesmo número de evidências seria um erro.

## 2. Operações aprendidas e não aprendidas

**Aprendido:** quais conjunções de literais de entrada (`(índice,bit)`), quais composições com até quatro partes, quantas vezes as combinações apareceram, taxa de consequências favoráveis, quais são promovidas, e qual profundidade de composição teve maior histórico prequencial de acertos.

**Fornecido:** proposta de pares após acontecimentos positivos; expansão incremental para trincas e quartetos na presença de erros; critério Wilson e margens fixas do Exp08; operação de poda e custo de execução; tabela de alternativas de profundidade 2,3,4. A descoberta autônoma das próprias operações matemáticas **não está demonstrada**.

A promoção básica reutiliza uma família de critérios experimentada no Exp08:

```
observações >= 10
P(y=1 | configuração) >= 0.83
Wilson_lower(pos,obs,z=1.28) >= max(0.63, P(y=1) + 0.19)
```

Uma configuração maior ainda é confrontada com subconjuntos já promovidos para evitar, quando possível, explicações redundantes. Em uma ablação, foi substituída por um critério MDL sobre tabela 2×2: esse substituto teve **desempenho ruim** nos mundos selecionados; não foi adotado. Trata-se de uma formulação específica testada, não de refutação do princípio MDL.

A máquina controla alternativas de profundidade `k` em um Mórfon cujas faces persistem os dados de acertos/erros:

```
D_k(x) = OR_{i: ordem(i)<=k} (cert_i(x) AND promovido_i)
conta_k(t+1) = conta_k(t) + 1
acertos_k(t+1) = acertos_k(t) + [D_k(x_t) = y_t]
k*(t) = argmax_k(acertos_k/conta_k), desempate pelo k menor
```

Após os primeiros 30 episódios de avaliação de cada alternativa, sua taxa passada é usada para decidir o foco de ordem. O rótulo `y_t` **só atualiza a memória depois** das previsões `D_k(x_t)`. Não houve seleção sobre o gabarito reservado de teste.

A seleção de **qual explicação focalizar dentro da ordem** utiliza o número de raios e evidências acumuladas; em tarefas de consequência exclusivamente positiva, trocar o foco entre dois candidatos positivos NÃO muda o rótulo predito. Esse detalhe é decisivo ao avaliar os espectros.

## 3. Os experimentos comparativos

Foram usados nove mundos de regras desconhecidas para o aprendiz (`pair_or`, `triple_absence`, `xor`, `quad`, `context`, `correlated`, `noisy`, `null`, `drift`). O gerador embaralha as posições dos sensores por semente. Cada versão recebeu **exatamente os mesmos 520 episódios de aprendizagem** e **260 novos episódios de avaliação**, em três sementes (`41`,`42`,`43`). A regra real fica em `codigo/mundos.py`; `morfon.py` não importa esse arquivo. Os resultados individuais ficam em `dados/principal_{a,b,c}_individuais.json`, inclusive contagens TP/FP/FN/TN.

**Acurácia balanceada média (3 sementes):**

| Mundo | Exp08 original | Integração sem controle | Com controlador | Com controlador e aninhamento |
|---|---:|---:|---:|---:|
| Pares OR | 0,9863 | 0,9190 | 0,9879 | 0,9879 |
| Trinca com valor zero explícito | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| XOR | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| Quatro componentes necessários | **0,5000** | 1,0000 | **1,0000** | **1,0000** |
| Contexto observado | 1,0000 | 0,9620 | **1,0000** | **1,0000** |
| Ruído | 0,9246 | 0,8881 | 0,9273 | 0,9273 |
| Sensores correlacionados | 0,9823 | 0,9597 | 0,9832 | 0,9832 |
| Mundo sem estrutura | 0,5000 | 0,5014 | 0,5014 | 0,5014 |
| Regra trocada no teste | 0,5079 | 0,5079 | 0,5079 | 0,5079 |

Os resultados de 1,0000 nos mundos pequenos não são demonstração de domínio geral; os mundos foram construídos para discriminar comportamentos de composição. **Diferentes sementes NÃO equivalem a nove topologias completamente inéditas**; diversidade vem sobretudo das nove famílias explicitadas.

A integração direta de quatro níveis é um experimento necessário: melhora a representação do mundo `quad`, mas **piora pares/contexto/ruído** por candidatos mais complexos e insuficientemente discriminados. O Mórfon controlador corrige parte dessa perda ao escolher o nível baseado apenas no passado.

O cenário `drift` não contém sinais antecipatórios da troca de regra; é avaliado com aprendizado congelado. Nenhuma variante previu uma mudança para a qual não recebeu nova evidência. O mundo `null` produz candidatos espúrios e crescimento até 1.800 unidades: **falha demonstrada de controle de memória** nesse regime. Não chamar 0,5014 de superioridade estatística significativa sobre 0,5000.

## 4. Aninhamento, faces e atualização estrutural

`nested=True` permite que um Mórfon de quatro literais tenha como portas **dois outros Mórfons de dois literais**. É uma estrutura explícita armazenada na própria memória, não uma lista de IDs de alto nível fora dela. Durante a consulta os dois filhos recebem raios de suas portas e, quando certificados, emitem para o pai. Testes confirmaram que ativação de um só raio é mantida, e que o pai não é certificado por uma combinação incompleta.

Nos três mundos de quatro componentes, aninhar reduziu as conexões visitadas por consulta de `693,64` para `416,66`, com a mesma balanced accuracy `1,000`. Com poda do Exp08 reintroduzida por agenda, a memória média passou de `443` unidades sem poda para `321,33` com poda; combinar poda e aninhamento resultou em `330,67` unidades e `282,32` acessos a conexões por evento, mantendo 1,000 na mesma bateria.

Em pares OR, o conjunto integrado caiu de `373` para `276` unidades com poda, e de `460,1` para `316,7` acessos, sem alterar a balanced accuracy `0,9879`.

Esses são **custos de operações instrumentadas**, não benchmarks de tempo de execução assintótico nem garantia de custo constante. Alguns mundos, principalmente o nulo, ainda ativam milhares de candidatas e batem no orçamento máximo.

`facet=True` armazena faces discretas e suas portas; `facet_capacity=2` subdivide uma unidade maior em subunidades de faces. Foi de fato executado com as mesmas experiências, preservando previsões em dois cenários comparados. `xyz` em 3D e 4D também foi persistido, com foco opcional por coordenada. O **4D não alterou acertos** nos três ensaios de quatro partes; apenas aumentou o snapshot JSON em ~3%–4%. Não aprendemos aqui uma geometria espacial semântica. Isso permanece em investigação isolada dos Exp11–13.

Duplicação literal (`codigo/replicacao_probe.py`): dois Mórfons clonados do mesmo par de fontes produzem dois raios físicos para o pai, mesmo que representem **uma única configuração experiencial**. É possível duplicar, mas a replicação ingênua infla o peso sem informação nova; não entra no núcleo proposto.

## 5. Espectro, física matemática e memória holográfica

O filtro operacional local é calculado sobre os candidatos efetivamente encontrados pelos raios. Se `W` é a média normalizada por vizinhos por incidência e `r` o vetor de sustentação atual, então:

```
Z_1 = W*r
Z_2 = W*Z_1
F = Z_1-Z_2
```

Isso é a avaliação de um polinômio do operador de grafo, sem autovetores e sem diagonalização. Um avaliador denso, usado **apenas como oráculo numérico**, confirmou a saída com erro máximo `1,11e-16` num caso com quatro candidatas úteis. É uma realização simples da família de filtragem localizada em grafos; não é uma implementação integral das wavelets de Hammond et al.

Em nossa tarefa binária, o espectro só desempata/promove a **relevância de explicações já positivas**. Por construção, não muda a previsão binária quando existe ao menos uma explicação. Os ensaios espectrais não mostraram melhora de acurácia; seria falso dizer que a prova algébrica implica ganho cognitivo. O custo adicional e a necessidade de um domínio com **consequências concorrentes** são motivos para não incorporá-lo como obrigatório agora.

Uma segunda ablação usou **Holographic Reduced Representations**: convolução circular entre assinaturas para vincular pares, e correlação circular para tentar desvinculá-los, usando relações presentes na própria memória integrada treinada. O resultado médio da recuperação do parceiro foi:

| Dimensões | 1 par | 4 pares sobrepostos | 8 pares sobrepostos |
|---|---:|---:|---:|
| 16 | 1,000 | 0,417 | 0,417 |
| 64 | 1,000 | 1,000 | 0,792 |
| 256 | 1,000 | 1,000 | 0,917 |

O armazenamento explícito de portas é exato (1,000). Esta ablação mede **capacidade da codificação comprimida sobre o grafo aprendido**, não um segundo sistema de previsão extremo-a-extremo: a HRR não foi autorizada a substituir todas as portas no motor principal. A recuperação aproximada perde precisão sob sobreposição. Sem vantagem demonstrada, a escolha atual é portas explícitas + espectro opcional.

A analogia de compartilhamento algébrico à Diffie–Hellman serviu como inspiração de **composição de representações**, não como operação criptográfica implementada. Nenhum hardware quântico foi utilizado ou requerido.

## 6. Dados reais: limite de transferência

Usamos 1.797 imagens `load_digits` do scikit-learn. A consequência observada foi paridade do dígito (binária); o aprendiz **não recebeu a identidade nem a paridade como atributo de entrada**. Em cada uma de três divisões, os nove pixels foram escolhidos usando somente a variância das imagens de treino (não os rótulos). O motor recebeu os estados binários desses pixels e consequências posteriores. Treino de 1.347 imagens, teste de 450.

**Balanced accuracy média (3 divisões):** Exp08 original `0,796`; Mórfon integrado com controle `0,770`; aninhado `0,770`. Nesse teste real, a nova arquitetura **não superou a anterior**. Precisamos investigar seu excesso de candidatos e seu viés de seleção antes de afirmar avanço de generalização real. Reproduzir: `python codigo/probes.py`; casos em `dados/digitos_reais.json`.

## 7. Escalabilidade

Prova por instrumentação: acrescentar `10.000` átomos completamente desconectados à memória não alterou as **2** conexões percorridas por uma consulta fixa. O índice inverso evita busca global nessa situação.

Contraexemplo: conectar `100`, `1.000` ou `4.000` Mórfons à mesma porta central fez a consulta examinar respectivamente `100`, `1.000` e `4.000` conexões. **Localidade não implica custo constante em hubs**. A geração inicial de combinações ainda cresce combinatoriamente no número de sinais simultâneos, e o mundo nulo saturou o teto de 1.800 Mórfons nas três sementes.

Isso favorece estruturas de adjacência esparsa, poda contextual e eventualmente métodos de mineração incremental de conjuntos frequentes. Não é necessário diagonalizar matrizes densas para avaliar o filtro local. O crescimento de superfícies facetadas e possível divisão precisam respeitar proveniência, identidade e custo de roteamento.

## 8. Controle de vazamento e validade

- O gerador dos mundos é separado do motor; todas as variantes recebem as mesmas experiências por mundo/seed.
- Em `train_one`, prevê-se ANTES de observar `y`, e as esferas criadas por `y` não recebem crédito desse mesmo exemplo.
- O Mórfon controlador compara alternativas de profundidade usando **predições do mesmo estado pré-atualização**, depois atualiza as marcas de acertos.
- Avaliação reservada chama somente `predict` e não altera contadores de evidência ou cria novas relações. Observações temporárias de ativação são efêmeras.
- Serialização/restauração e continuação com poda produzem as mesmas unidades persistentes que treinamento contínuo no teste automatizado.
- O resultado do mundo nulo, a transferência de dígitos, o MDL ruim, a mudança de regime e a replicação enganosa estão preservados como resultados adversos.

## 9. Decisão arquitetural e o que permanece

**Candidato a continuar integrando:** núcleo com portas/marcas e contadores no Mórfon, ativação OR, certificação de composição, controle de profundidade aprendido, poda periódica e opção de composição aninhada. **Não substituímos o NEXO principal**: é um candidato validado em tarefas delimitadas, ainda sem desempenho real satisfatório nos dígitos e com risco de explosão de candidatos.

**Não integrar por ora:** matrizes espectrais globais, wavelets como parte obrigatória, HRR comprimida substituindo portas exatas, dimensionalidade 4D como truque de aprendizado, replicação cega, política MDL testada neste episódio, expansão descontrolada de combinações.

**Questão arquitetural restante:** compartilhar um mesmo núcleo de memória para previsões de múltiplos resultados e revisão temporal, preservando a causalidade prequencial e controlando fan-out e custo de formação. A integração de aprendizado de **transformações funcionais sobre dados** é hipótese separada e não foi incorporada silenciosamente.

O próximo experimento não deveria reabrir o que já demonstramos nem perseguir uma métrica arbitrária: deve demonstrar uma capacidade NOVA do ciclo unificado (ex.: selecionar entre consequências incompatíveis ou alterar utilmente relações após uma mudança observada), com baselines e ablações comparáveis.
