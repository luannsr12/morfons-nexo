# NEXO — Malhas Relacionais Compartilhadas

## Objetivo e contrato

Investigar uma extensão **isolada**, sem alterar o motor original do NEXO: vários arranjos relacionais podem fazer referência à mesma unidade de memória (Mórfon), preservando núcleos invariáveis, organização externa modificável, fragmentos com identidade global, conexões/portas, registros de contexto, proveniência, ativação com um raio e sustentação pela quantidade de emissores distintos. Os Mórfons Gênesis são pressupostos como unidades operacionais preexistentes; **não é exigida criação de funções do nada**.

As perguntas são: (1) a composição entre malhas permite consequências ausentes das malhas individuais? (2) compartilhar identidade e contexto evita junções espúrias? (3) há economia estrutural? (4) regularidades entre malhas podem ser generalizadas conservativamente? (5) é possível conservar demonstrações alternativas sem explosão de memória?

Este laboratório implementa um executor relacional genérico em Python para **testar essas propriedades matemáticas**. Não testa que os Gênesis aprenderam autonomamente sua política de criação, de roteamento, de seleção de experiências ou de promoção. Identidades, tipos de relações e contextos são fornecidos nas observações estruturadas do gerador. O núcleo permanece imutável: os sinais possíveis são `−1,0,+1`; a organização mutável está nas faces, marcas, ligações e pertenças às malhas.

## Definições

Uma memória com malhas é `M = (V, L, {R_l}, Γ, ρ)`, onde `V` é a população canônica de Mórfons (identidades globais), `L` é o conjunto de malhas, `R_l` são relações orientadas tipadas dentro de cada malha, `Γ(e)` é o conjunto de contextos em que a relação observada `e` é aplicável e `ρ(e)` identifica a ocorrência/evidência que a originou. Cada Mórfon pode pertencer a várias malhas; duas aparições da mesma identidade representam uma única unidade. A superfície (faces, contexto, referências, etc.) é mutável, o núcleo não.

Para uma consulta composta `Q = (r₁,…,r_k)`, no contexto `c`, uma consequência de `s` a `t` é sustentada se existem `v₀=s,…,v_k=t` e evidências `e_i=(v_{i-1},r_i,v_i)` tais que `c∈Γ(e_i)` para todo `i`. Uma trajetória sem contexto fixo conserva o conjunto de aplicabilidade `Γ(π)=∩Γ(e_i)`. A composição sem interseção contextual ou apenas por nomes não é equivalente a essa relação.

A ativação física mantém `a(v,t)=1[|S(v,t)|≥1]`, `w(v,t)=|S(v,t)|`, em que `S` é o conjunto de **fragmentos emissores distintos**. O peso `w` não é inferido do número de provas nem representa automaticamente probabilidade ou certeza.

## Teorema 1 — Colagem conservativa de relações

Se todas as malhas conservam uma identidade canônica e uma consulta composta percorre somente arestas cujo tipo e contexto satisfazem `Q` e `c`, então o procedimento local que parte de `s` e atravessa as postagens das relações relevantes retorna **exatamente** os destinos da composição relacional `R₁ᶜ∘⋯∘R_kᶜ`.

**Demonstração por indução.** Após uma etapa, os destinos enumerados são precisamente aqueles das arestas `r₁` incidentes em `s` e válidas em `c`, que correspondem à definição de `R₁ᶜ`. Suponha que após `j` etapas os destinos sejam os alcançáveis pela composição das primeiras `j` relações. A etapa seguinte inspeciona, apenas para esses destinos, as arestas `r_{j+1}` de contexto compatível. Ela acrescenta precisamente os pares que possuem um intermediário compartilhado, equivalentes à definição da composição relacional. Por indução, a propriedade vale após `k` etapas. A anotação de proveniência de um caminho é a conjunção das evidências de suas arestas; alternativas são disjuntas como justificativas, e a expressão pode ser fatorada em DAG. `∎`

**Condição de validade.** Esta é uma garantia relativa às **relações observadas e à semântica da consulta**, não à verdade de relações ainda desconhecidas no mundo. O algoritmo não descobre sozinho se os fragmentos de dois sensores representam a mesma entidade.

### Contraprovas construtivas da necessidade das condições

1. `A→B₁` e `B₂→C` com nomes visíveis iguais `nome(B₁)=nome(B₂)`, porém identidades diferentes. A composição por *nome* produz um caminho inexistente; por identidade, não.
2. `A→B` válida apenas em `c₀` e `B→C` válida apenas em `c₁`, com `c₀≠c₁`. A composição sem interseção de contextos produz uma consequência sem testemunha contextual.

Os dois contraexemplos foram também reproduzidos no experimento.

## Experimento A — Composição, identidade e contexto

Foram gerados 600 casos com três relações (`r0,r1,r2`) distribuídas em três malhas. Cada caso recebeu independentemente uma condição de identidade compartilhada e outra de concordância contextual. A consequência foi definida como válida se **ambas** as condições fossem satisfeitas. O mesmo conjunto foi consultado pelas cinco implementações/ablações.

**Categorias do gerador:** 313 casos com identidade e contexto compatíveis; 126 com identidade compartilhada e contextos distintos; 110 com nomes iguais mas identidades distintas e contextos compatíveis; 51 violando ambas as condições. As sementes foram fixadas no código.

| Condição | VP | FP | FN | VN | Acertos/600 |
|:--|--:|--:|--:|--:|--:|
| Identidade canônica + contexto | 313 | 0 | 0 | 287 | **600** |
| Apenas uma malha | 0 | 0 | 313 | 287 | 287 |
| Identidade canônica sem contexto | 313 | **126** | 0 | 161 | 474 |
| Correspondência por nome com contexto | 313 | **110** | 0 | 177 | 490 |
| Correspondência por nome sem contexto | 313 | **287** | 0 | 0 | 313 |

**Interpretação.** A composição intermalhas produziu 313 consequências cujo percurso não cabia numa só malha; sem identidade compartilhada elas não puderam ser obtidas. As duas ablações produziram falsos positivos distintos que ilustram por que não se devem fundir organizações somente por rótulo ou sem preservar contexto. Como o gerador foi construído com essa regra, a acurácia de 100% confirma sua implementação, mas **não** demonstra que o NEXO aprendeu autonomamente a regra.

## Teorema 2 — Economia de compartilhamento sob custo explícito

Sejam `m=Σ_l |V_l|` o total de participações de unidades nas malhas e `u=|∪_l V_l|` a quantidade de identidades distintas. Considere custo `b` por unidade armazenada, `q` por referência unidade–malha e `c` por ligação explícita entre cópias de uma unidade. Representar cada ocorrência por uma cópia e acrescentar apenas as `h=m−u` ligações mínimas necessárias para conectar cópias da mesma identidade custa

`C_cópias = mb + hc`.

Uma representação com unidade canônica compartilhada e referências por malha custa

`C_compartilhado = ub + mq`.

Portanto, a diferença é exatamente

`Δ = C_cópias − C_compartilhado = (m−u)(b+c) − mq`.

**Demonstração.** Uma identidade presente em `d` malhas corresponde a `d` cópias e exige pelo menos `d−1` ligações para conectar as cópias. Somando por identidade, `h=Σ(d−1)=m−u`. A subtração dos custos fornece a expressão. `∎`

A representação compartilhada é economicamente melhor quando `Δ>0`. **Ela não é sempre melhor:** custo elevado de referências ou pouca reutilização pode inverter o sinal.

**Números medidos no universo sintético**: `m=3.600`, `u=2.561`, `h=1.039`. Com o modelo *hipotético*, porém explícito, `b=64 B, q=8 B, c=16 B`:

- cópias + ligações: **247.024 B**;
- unidades compartilhadas + referências: **192.704 B**;
- diferença: **54.320 B**, ou **21,99%**.

Esses valores são **custo calculado pelo modelo de representação**, não alocação física de memória RAM medida no processo Python. A busca com índice local examinou em média 2,253 relações candidatas por caso. Inserir 20.000 Mórfons desconectados não alterou as seis contagens de inspeção selecionadas; não constitui benchmark de densidade elevada.

## Teorema 3 — Generalização estrutural conservativa de um percurso entre malhas

Seja `P` a antiunificação de dois percursos observados `E₁,E₂`, preservando identidade de variáveis entre posições repetidas. Existem substituições `θ₁,θ₂` tais que `Pθ₁=E₁` e `Pθ₂=E₂`; portanto a nova organização é conservativa relativamente às duas experiências que a originaram. Se uma nova ocorrência satisfizer o padrão, ela conserva as igualdades posicionais descobertas; se quebrar uma dessas igualdades, não corresponde ao padrão.

**Demonstração.** A antiunificação substitui pares de subexpressões diferentes por variáveis; ocorrências repetidas do mesmo par recebem a mesma variável. Substituir essas variáveis pelos fragmentos originais reconstrói cada observação por indução sobre as subexpressões. As igualdades entre posições preservadas são condições do reconhecimento da próxima ocorrência. `∎`

**Teste executado:** dois percursos completos, com identidades e contextos distintos, produziram um padrão com **cinco variáveis independentes**: fonte, dois intermediários, destino e contexto. Um terceiro percurso com novos fragmentos e contexto novo foi reconhecido. Um percurso com intermediário trocado e outro com contexto incompatível foram rejeitados. Ambas as experiências de origem foram reconstruídas exatamente.

Também foi repetido o exemplo básico de promoção do artigo: `[(a,a),(b,b),(c,c)]` induz a relação de igualdade `X→X`, com uma variável independente. No custo definido `m=2`, `v=1`, `b=8`, `q=4`, `c=10`, o ganho é `n[(m−v)b−q]−c=4n−10`: negativo para duas ocorrências, positivo para três. Com pares não correlacionados (duas variáveis), a mesma conta é negativa. Esse teste verifica **reconstrução e custo formal**; não demonstra política de promoção autonomamente escolhida por um Gênesis.

## Teorema 4 — A fatoração de provas evita expansão desnecessária

Considere `k` losangos consecutivos no grafo relacional. Cada losango possui dois percursos alternativos que se encontram antes do próximo. Há precisamente `2^k` provas completas para o destino final, embora o número de relações individuais seja `4k`.

As provas podem ser representadas por uma expressão compartilhada, com `+` representando alternativas e `·` a conjunção de evidências (semiring booleano ou polinômios de proveniência). Por exemplo, duas alternativas com prefixo comum podem ser expressas como `a·b·c + a·d·e = a·(b·c + d·e)` sem duplicar `a`. Aplicando a estrutura de maneira recursiva, o DAG armazena o compartilhamento das subprovas sem enumerar os `2^k` monômios expandidos.

**Demonstração construtiva.** Ao ampliar a cadeia com um losango, cada prova anterior adquire duas alternativas, dobrando a quantidade de provas completas. Porém o DAG cria um número constante de novos nós e arestas para as duas alternativas e sua junção, referenciando a prova compartilhada que já existia. Por indução, o número de caminhos completos é exponencial e o DAG da construção tem tamanho linear. `∎`

| Losangos `k` | Relações | Caminhos explícitos | Nós do DAG | Inspeções da busca fatorada | Raios físicos distintos no destino |
|--:|--:|--:|--:|--:|--:|
| 1 | 4 | 2 | 9 | 4 | 2 |
| 2 | 8 | 4 | 18 | 8 | 2 |
| 3 | 12 | 8 | 27 | 12 | 2 |
| 5 | 20 | 32 | 45 | 20 | 2 |
| 8 | 32 | 256 | 72 | 32 | 2 |
| 10 | 40 | 1.024 | 90 | 40 | 2 |
| 12 | 48 | **4.096** | **108** | **48** | **2** |

**Verificações adversariais:** retirar uma das alternativas na primeira bifurcação conserva uma prova válida; retirar ambas elimina todas as provas; um raio incidente sem relação com o percurso aumenta o peso físico mas não cria uma justificativa adicional; registros negativos opostos à evidência positiva são conservados e sinalizados, sem apagar automaticamente a história.

A busca por caminhos explícitos examinou 16.380 incidências no ensaio com 12 losangos; a fatoração examinou 48. Esses valores se referem à **construção particular** com reconvergência, não a qualquer rede arbitrária. A prova de correção de consultas de três relações foi ainda confrontada com uma enumeração bruta independente em **250 grafos aleatórios**; todas as respostas e respectivas combinações de proveniência coincidiram. Também passaram dez testes de regressão, incluindo 20 mundos adicionais com 120 consultas cada.

## Consequências para o NEXO

1. **Compartilhar nós** não significa fundir indiscriminadamente experiências: identidades, contextos e tipos de ligação mantêm organizações distintas mesmo quando usam o mesmo Mórfon.
2. **Compartilhar subprovas** é um segundo nível de reutilização: os Mórfons podem conservar a estrutura justificativa de suas funções sem materializar cada combinação possível.
3. **Um raio ativa; raios distintos sustentam.** O número de demonstrações combinatórias não é a quantidade física de emissores. No teste com 4.096 caminhos, o destino possui peso 2.
4. **Os Gênesis preexistem e agem sobre a periferia.** Este laboratório usa suas operações de criação e edição de modo explícito e conserva o núcleo como propriedade somente de leitura, mas ainda não faz a política de descobrir e promover novas organizações surgir dos próprios Gênesis.
5. **Aprendizagem de interface** deve distinguir (a) descoberta de identidade compartilhada por evidência, (b) reconhecimento de configurações estruturais, (c) seleção de alterações/persistência. Só (b), sob entrada estruturada, foi experimentado com antiunificação aqui.

## Limitações honestas do ensaio

- Dados sintéticos deliberadamente simples e com relações etiquetadas; a taxa de 600/600 não é generalização para linguagem, visão ou mundo físico.
- A composição e a fatoração são executadas por algoritmos genéricos Python neste laboratório. Não se demonstrou que esses algoritmos são organizados e executados causalmente apenas por ativações de Mórfons em uma implementação completa do NEXO.
- A política de seleção de interações, descoberta da identidade global entre fontes sem anotação, reconciliação de contextos ambíguos e promoção persistente baseada em custo real não foram implementadas de ponta a ponta.
- A representação fatorada permite responder existência e reavaliar proveniência sem enumerar, mas a enumeração de todas as provas permanece exponencial no pior caso: não existe compressão que elimine o tamanho de uma saída explicitamente exigida com 2^k itens.
- Busca local não implica custo constante em hubs ou em grafos densos.
- O núcleo é estável e sua superfície é mutável; a semântica cognitiva das três vias `−1,0,+1` **não** foi derivada nesta experiência. Também não se trata de descoberta de computação quântica nem de aplicação de Diffie–Hellman.

## Próximo experimento discriminante

Partir do mesmo MorphMemory real, com Gênesis já configurados, e exigir: (i) aquisição de uma identidade comum a partir de observações de fontes diferentes, sem o gerador indicar a fusão; (ii) formação e ativação de uma interface entre malhas a partir das faces; (iii) previsão ou ação nova sustentada por múltiplas malhas; (iv) ablação de raios/portas decisivos que retire essa conclusão e de raios irrelevantes que a preserve; (v) registro de contexto, proveniência e revisão; (vi) medição dos custos efetivos de criação/compartilhamento versus cópias. Esse é um ensaio de integração, não um pretexto para substituir o núcleo.

## Referências de apoio matemático

- Kivelä, M. et al. (2014). *Multilayer networks*. Journal of Complex Networks 2(3), 203–271. DOI: 10.1093/comnet/cnu016. Trata formalmente redes multilayer e identificações nó–camada; não reivindicar que o simples compartilhamento de vértices é inédito.
- Green, T. J.; Karvounarakis, G.; Tannen, V. (2007). *Provenance Semirings*. PODS 2007. Fundamenta a composição multiplicativa de evidências e a soma de justificativas alternativas.
- O NEXO forneceu a motivação arquitetural adicional: Gênesis, núcleo invariável, faces e portas mutáveis, marca contextual, ativação por um raio, sustentação por vários, conservação de ocorrências e promoção por custo.

## Reprodução

Executar em Python 3.10+ (sem dependências de terceiros):

```
cd nexo_malhas_experimento
python -m unittest -v
python experiment.py
```

Saídas: `results.json` (métricas e exemplos), `case_predictions.jsonl` (todos os 3.000 pares modo/consulta), `test_output.txt` (regressão), `figures/` (visualizações), `console_output.json` (saída completa da execução). Tempo de execução varia por máquina e deve ser tratado apenas como referência local. Nenhum arquivo do NEXO original foi modificado.
