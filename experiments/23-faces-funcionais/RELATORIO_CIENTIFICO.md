# NEXO — Experimento 23: marcas funcionais nas faces de Mórfons

**Data:** 09/11/2026. **Tipo:** extensão experimental isolada, verificável, da `MorphMemory` original; não constitui substituição dos EXP14–22 nem alteração do núcleo.  
**Pergunta central:** uma configuração de faces, marcas e raios pode ser modificada por observações e passar a *causar* previsões e sequências de ações novas? Que cálculo conhecido oferece a melhor forma para aprender essas marcas?  
**Estado científico:** avaliação terminada para os ambientes e operações descritos; arquivos e casos individuais estão em `results/`.

## 1. Continuidade verificável

- `originals/morfon_exp21_original.py` é uma cópia **byte a byte** do núcleo original EXP21 preservado no EXP22; SHA-256: `842fffcbe268be3b7fc4bd311098c4dbb1b58a52e0291d7359f80434d6c70669`. Nenhuma linha desse arquivo foi modificada.
- A memória do núcleo contém Mórfons com `ports`, `facets`, `holes`, marca temporal, núcleo ativado por um raio, sustentação por quantidade de raios e `pulse_units`. A inferência desta experiência utiliza as portas e os pulsos reais dessa memória.
- As modificações ficam em três adaptadores de laboratório, nunca no arquivo-fonte original: `src/facets.py` (subdivisão), `src/spectral_faces.py` (marcas funcionais) e os avaliadores. As faces aprendidas são Mórfons `spectral-face` ou `face`; os componentes aprendidos ficam em Mórfons `face-harmonic` com ligações de entrada para a face e as fontes relevantes.
- Cada `episode` é persistido na mesma memória, com `before`, `action`, `after` e proveniência. Os resultados das transições não estão na tabela Python do aprendiz. Apenas o simulador, separado em `evaluate.py`, conhece as funções verdadeiras do ambiente.

## 2. Hipóteses e formulações comparadas

### H1 — Divisão de faces por diferença observada

Uma face tem contorno e relações de adjacência. Uma ocorrência incompatível com uma face ativa pode exigir subdividir a região por um sinal sensorial distinguível. Cada descendente recebe portas `parent_face` e `sensor_value`, permitindo que o núcleo original complete e propague a condição. O critério de divisão gulosa minimiza impureza observada na face; comparou-se a árvore sem divisão e uma variante comprimida por Minimum Description Length (MDL), com modelo de Jeffreys/Krichevsky–Trofimov para codificação dos dados binários.

**Falha observada:** a escolha gulosa nem sempre escolhe a distinção com melhor comportamento futuro; a compressão excessiva também descartou interações necessárias. O protótipo foi corrigido para manter os episódios nos ancestrais das faces, necessário à poda MDL (o primeiro algoritmo de compressão usava apenas experiências anteriores à primeira divisão, produzindo poda inválida). A bateria confirmatória usa exclusivamente a versão corrigida.

### H2 — Marcas algébricas de interação nas faces

Cada componente observável da consequência de uma ação passa a ser uma função das propriedades observadas da situação, representada em forma algébrica normal (ANF) em \(\mathbb F_2\):

\[
\widehat y_{a,j}(x)=\bigoplus_{S\subseteq\{1,\ldots,m\},\,|S|\le d}
 c_{a,j,S}\prod_{k\in S}x_k.
\]

Os termos da base são *candidatos estruturais*, não regras do domínio. A memória começa sem coeficientes. As experiências geram um sistema linear \(\Phi_dc=y\pmod2\). A eliminação de Gauss determina o menor grau até um teto representacional declarado capaz de acomodar todas as observações. Os coeficientes não nulos tornam-se **marcas em Mórfons-filhos**, cada uma com portas reais para a face-pai e os sensores correspondentes. A saída é o XOR das marcas *efetivamente certificadas* por raios no núcleo original. O motor não consulta o valor esperado durante `query`.

O grau da marca aumenta quando os exemplos tornam grau menor incompatível: grau 0, depois 1, depois 2, etc. Um operador geométrico `sector` também é preservado na face, mas **a posição métrica 3D do setor não participa dos cálculos** desta bateria; apenas a estrutura de portas e a marca funcional são causalmente necessárias. Não foi demonstrada uma vantagem cognitiva da geometria euclidiana sobre essa representação de incidências.

**Identificabilidade:** se a linha de um teste não está no espaço gerado pelas experiências na base atual, ele produz `abstenção` em vez de extrapolar coeficientes não identificados. Se observações idênticas contradizem um modelo determinístico de grau máximo, a memória preserva os episódios, invalida a função do contexto atual e registra a contradição.

### H3 — Correção de observações corrompidas

As tabelas de valores de polinômios booleanos de grau até \(r\) nas \(2^m\) entradas constituem o código Reed–Muller \(RM(r,m)\). Seu comprimento é \(n=2^m\), dimensão \(k=\sum_{i=0}^{r}\binom mi\) e distância mínima \(d_{min}=2^{m-r}\). Em \(RM(2,5)\): \([n,k,d_{min}]=[32,16,8]\), com correção garantida de até 3 inversões numa palavra completa de 32 sinais. A decodificação laboratorial enumera as 65.536 palavras de código por canal e escolhe o mínimo de distância Hamming, exigindo minimizador único e distância no máximo 3. É uma demonstração de existência executável, **não uma implementação escalável de decodificação Reed–Muller**.

### H4 — Escolha de experimentos a partir das próprias lacunas

Para a matriz de incidências aprendida, uma nova experiência \(x\) é informativa quando sua linha ainda não pertence ao espaço gerado pelas linhas observadas:

\[
\Delta \operatorname{rank}(x)=\operatorname{rank}(\Phi\cup\{\phi(x)\})-\operatorname{rank}(\Phi)=1.
\]

O experimento `active_design.py` escolhe a próxima consulta pelo aumento de posto. Ele exige um laboratório capaz de reiniciar o mundo em estados de entrada acessíveis. A seleção por posto é calculada por um agendador genérico externo; a bateria demonstra o valor matemático das experiências escolhidas, não autonomia motora nem aprendizagem da regra de seleção pelos próprios Mórfons.

### H5 — Pensamento/simulação sem falsificar observações

`imagine()` utiliza as mesmas marcas certificadas para criar um Mórfon `internal-imagination` ligado às condições e à prova da antecipação. Essa ocorrência interna não entra na coleção de experiências observadas. Vinte simulações repetidas não alteraram a função aprendida, nem viraram vinte confirmações independentes. A memória foi restaurada por snapshot do núcleo original e manteve inferência e capacidade de revisão.

## 3. Protocolo principal

- Cinco famílias de mundos, todas com cinco entradas observáveis binárias, duas ações binárias rotuladas por identificadores arbitrários e cinco componentes de saída. Uma dimensão é distração irrelevante; outras são condições/estado. A avaliação utiliza as mesmas situações e sementes por variante.
- Em cada mundo e semente, cada ação é observada em 24 dos 32 estados, restando 8 inéditos por ação. Total: **48 episódios de treino e 16 testes reservados** por instância. Mundo e função verdadeira aparecem apenas no simulador, não no indutor.
- Bateria de desenvolvimento: 5 famílias × 2 sementes = 10 instâncias. **Bateria confirmatória independente:** 5 famílias × 12 sementes (2 a 13) = **60 instâncias**, 2.880 experiências, 960 testes reservados.
- Planejamento: o programa genérico efetua busca em largura por sequências de até três ações usando **exclusivamente as transições retornadas pelos Mórfons**. Objetivos alcançáveis são obtidos pelo simulador antes da busca e não são fornecidos como tabelas de transições. São testados até 35 objetivos por instância; casos em que objetivo já é estado atual são removidos.
- O planejamento usa um **escalonador BFS externo**. A organização relacional determina as consequências, mas ainda não escolhe autonomamente toda a agenda de pensamento. Não confundir a prova de uso causal das marcas com prova de política cognitiva inteiramente aprendida.

### Resultado confirmatório, sementes 2–13

| Mecanismo | Corretos/960 | Respondidos/960 | Erros | Objetivos alcançados/962 | Nós médios por memória | Faces ou marcas vivas médias |
|---|---:|---:|---:|---:|---:|---:|
| Uma face fixa com maioria | 6 | 960 | 954 | 15 | 316,0 | 10,0 |
| Subdivisão gulosa | 793 | 960 | 167 | 905 | 395,17 | 89,17 |
| Subdivisão MDL | 690 | 960 | 270 | 731 | 418,8 | 112,8 |
| Marcas grau até 1 | 576 | 576 | 0 | 745 | 342,68 | 11,2 |
| **Marcas grau até 2** | **960** | **960** | **0** | **962** | **382,58** | **13,0** |

Uma função quadrática em cinco variáveis possui no máximo \(1+5+10=16\) coeficientes independentes. As 24 experiências por ação foram suficientes para identificar as operações nos mundos regulares. A afirmação é sobre essa família de operações; isso não seria esperado para tabelas aleatórias de 32 entradas nem para relações com memória oculta não observada. O resultado alto não pode ser extrapolado mecanicamente para linguagem ou inteligência geral.

### Ablações causais, 15 instâncias e 240 consultas

- Desativação dos pulsos reais de `MorphMemory`: **240/240** consultas deixam de emitir resultado.
- Retirada de marca **ativa** participante da inferência: **651/651** saídas alteradas.
- Retirada de marca **inativa**: **240/240** saídas preservadas.
- Retirada da face consultada: **240/240** consultas bloqueadas.
- Restaurar Mórfons a partir de snapshot preserva a função; observações novas continuam alterando a memória.

Os controles verificam causalidade das **portas e marcas**. Não demonstram relevância das coordenadas geométricas da esfera, que não foram utilizadas na decisão.

## 4. Testes adversariais e limites identificados

**Interação de terceira ordem:** o mundo contém efeito cúbico sobre três entradas. Com teto algébrico 2 e 24 episódios/ação, houve 0 respostas em 64 avaliações reservadas (abstenção por contradição de representação). Com grau 3 e 24 episódios/ação, o aprendiz respondeu **10/64**, todas corretas, e se absteve nas demais por insuficiência de posto. Com 30 episódios/ação, o grau 3 alcançou **16/16** respostas corretas. Resultado de quatro sementes.

**Controle de tabelas aleatórias:** 20 instâncias com funções arbitrárias não desenhadas para serem polinômios quadráticos, 960 experiências e 320 consultas reservadas. Houve **0 respostas e 320 abstenções**. Isso diferencia aprender uma regularidade da simples memorização com extrapolação arbitrária.

**Conflito não identificável:** duas observações da mesma ação/entrada com consequências diferentes foram mantidas como episódios distintos. A memória detectou modelo determinístico inconsistente e recusou conclusão única. Não inventou um contexto escondido.

**Ruído corrigível:** 15 instâncias (5 famílias × 3 sementes), 32 estados observados por ação, exatamente três erros por canal de saída (450 alterações individuais no total). Decodificação RM(2,5) recuperou as 960 consequências verdadeiras verificadas: **960/960**. Distância mínima 8 verificada pela enumeração das 65.535 palavras não nulas; correção garantida até 3. Um caso adversarial com quatro alterações produziu oito minimizadores equidistantes; decodificador se absteve.

**Escolha ativa:** 50 instâncias (5 famílias × 10 sementes), orçamento igual de 32 episódios por instância. Seleção por ganho de posto: **3.200/3.200** previsões identificadas corretamente. Seleção aleatória de estados–ações distintos: **2.897/3.200** identificadas corretamente, 303 abstenções. A seleção ativa envolve reset controlado de estado no laboratório e agendador externo, não a capacidade do agente de alcançar qualquer estado apenas pelas ações disponíveis.

## 5. Resultado central e caminho técnico

**Propriedade testada:** um Mórfon com faces e marcas relacionais pode converter ocorrências em coeficientes funcionais, recebendo raios em portas adquiridas. A própria marca aprendida, e não o significado programado de uma palavra, determina a saída; a mesma marca é reutilizada na simulação de transições e na composição de planos. Contradições podem exigir grau maior ou suspender uma conclusão. Redundância de experiências pode permitir correção por álgebra de códigos.

**O caminho que emerge da comparação não é reinventar processamento de linguagem ou planejamento do zero.** Ele é integrar mecanismos já estabelecidos numa única dinâmica relacional, preservando o substrato:

1. **Núcleo Mórfon:** manter portas, faces, raios e rastros do EXP14–22, com identificação de origem da incidência.
2. **Marcas funcionais:** usar interações booleanas/assinadas como graus adquiridos no caso discreto; para sinais contínuos, comparar bases de operadores de Koopman e aproximações locais, em vez de fingir que todo domínio será XOR.
3. **História/contexto:** recuperar do EXP22 o refinamento de estados a partir de históricos discriminantes e comparar com *predictive state representations*. A regra geral é que históricos são distintos quando oferecem diferentes consequências de futuras ações, não por rótulos semânticos de alto nível.
4. **Pensamento e ação:** simulação interna como novas ocorrências de proveniência interna; planejamento e investigação devem ganhar **controle causal pela própria rede**, enquanto o host fica responsável apenas por executar operações primitivas e agendar recursos. A próxima ablação forte seria retirar a ativação de um Mórfon de dúvida e verificar se a escolha do experimento muda, sem manipular a política no host.
5. **Morfologia autônoma:** estudar regras locais de reescrita de grafos (*interaction nets*) e autômatos celulares neurais para fazer a escolha de subdividir, compartilhar ou suprimir faces resultar de atividade residente. Os testes atuais mostram a causalidade das faces funcionais, mas o reescritor/indutor genérico ainda é uma operação externa fixa.

O próximo experimento **não deveria** abandonar os Mórfons nem iniciar outro sistema de conversação com respostas prontas: deve fazer o **mesmo núcleo** produzir uma decisão de consulta ou revisão a partir dos Mórfons de discrepância, com desativação causal desses Mórfons e comparação contra o algoritmo de seleção externo já medido aqui. Essa é a ligação mais curta entre os resultados deste laboratório e a autonomia que motivou o projeto.

## 6. Antecedentes técnicos utilizados

- M. L. Littman, R. S. Sutton, *Predictive Representations of State*, NeurIPS (2001), https://mlanthology.org/neurips/2001/littman2001neurips-predictive/ — representação de estados por testes sobre consequências de ações.
- Y. Lafont, *Interaction Nets*, POPL (1990), https://doi.org/10.1145/96709.96718 — regras de reescrita local em grafos.
- A. Mordvintsev et al., *Growing Neural Cellular Automata*, Distill (2020), https://distill.pub/2020/growing-ca/ — alteração morfológica por interação local.
- T. Parr, G. Pezzulo, K. J. Friston, *Active Inference* (MIT Press, 2022), https://doi.org/10.7551/mitpress/12441.001.0001 — seleção de atividade com consequências esperadas e informação.
- E. Abbe et al., *Efficiently Decoding Reed–Muller Codes From Random Errors*, IEEE Transactions on Information Theory 63(4), 2017, https://doi.org/10.1109/TIT.2017.2671410 — propriedades dos códigos RM.
- H. Wu et al., *Rule Learning over Knowledge Graphs: A Review*, TGDK (2023), https://doi.org/10.4230/TGDK.1.1.7 — algoritmos existentes para aprender regras a partir de estruturas relacionais.

## 7. Reprodutibilidade e integridade

Executar em Python 3.11+ na raiz do pacote:

```bash
python -m unittest discover -s tests -v
python src/confirmatory.py
python src/adversarial.py
python src/negative_controls.py
python src/active_design.py
python src/causal_ablations.py
```

`results/confirmatory.json` contém avaliações individuais de cada transição reservada e dos planos propostos, não apenas médias. `results/adversarial.json` contém todos os contraexemplos de grau cúbico e os casos de correção de ruído. `results/active_design.json` guarda casos individuais. `results/causal_ablations.json` guarda os controles de intervenção. `originals/morfon_exp21_original.py` conserva o núcleo original, hash citado acima. O manifesto contém SHA-256 dos artefatos.
