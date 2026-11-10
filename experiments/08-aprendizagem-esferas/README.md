# NEXO — Experimento 08: surgimento e descarte de esferas relacionais

**Estado:** protótipo experimental isolado · **Data:** 7 de novembro de 2026  
**Linguagem:** Python 3.10+ (biblioteca padrão; não instala dependências)  
**Objetivo:** estudar se uma memória relacional inicialmente vazia pode formar unidades compostas **somente por experiências**, conservar as que explicam melhor uma consequência observada e descartar candidatas pouco úteis. A investigação sobre **funções/transformações** está guardada separadamente em `historico_separado/` e **não** faz parte dos resultados deste experimento.

## Fio condutor e compromissos

A memória do aprendiz começa sem conceitos, relações, pesos semânticos, nomes de eventos ou respostas predefinidas. Os mundos sintéticos possuem leis ocultas para gerar experiências, mas essas leis existem **somente** em `worlds.py`; o aprendiz (`learner.py`) não as importa. O aprendiz recebe vetores de sinais opacos e, após cada tentativa de previsão, observa um bit de consequência `Y`. O bit é um canal experimental fornecido pelo ambiente, **não uma categoria semântica aprendida autonomamente**. O problema investigado é *formar e preservar relações preditivas*, ainda não descobrir por conta própria os canais sensoriais nem a representação do mundo.

A imagem da esfera é operacionalizada sem exigir coordenadas 3D:

- Superfície = conjunto de fragmentos conectados.
- Cada fragmento ativado gera **um raio** para cada esfera acessível a partir dele.
- **Um raio basta para ativar** uma esfera (`state=1`).
- `rays` conta quantos fragmentos correspondentes da esfera foram observados; não é limiar de ativação.
- Uma esfera parcialmente ativada continua sendo uma **possibilidade**. Somente a correspondência completa oferece evidência de que uma condição preditiva conhecida foi satisfeita. A informação do peso não é perdida no disparo binário.
- Quando várias esferas úteis correspondem, o foco é a que recebe mais raios; empates são desfeitos por suporte preditivo observado. Ainda não há seleção distribuída entre esferas maiores.

## A matemática que efetivamente foi implementada

Para uma esfera `S` com fragmentos conectados `C(S)`, cada ocorrência atual `X` ativa um subconjunto desses fragmentos.

\[
r_S(X) = |C(S) \cap X|,\qquad a_S(X) = [r_S(X) > 0].
\]

A evidência de **configuração completa** é uma condição distinta da ativação:

\[
m_S(X)=[r_S(X)=|C(S)|].
\]

A regra `m_S` é usada apenas como condição de uma **previsão** (no caso experimental, de `Y=1`). Quando a relação não está suficientemente demonstrada, a esfera pode estar ativa, mas não produz confirmação de `Y=1`. Quando houver várias condições completas, prevalece a mais sustentada conforme a regra de foco.

Cada esfera candidata conserva somente `n_S`, o número de experiências posteriores à sua criação em que sua configuração ficou completa, e `k_S`, quantas dessas experiências tiveram `Y=1`. Também existe o agregado de prevalência `p_0` da consequência, calculado incrementalmente. A candidata é promovida quando:

- `n_S >= 14`;
- `k_S/n_S >= 0,89`;
- o limite inferior de Wilson para a frequência positiva excede tanto `0,62` quanto `p_0 + 0,27` (parâmetros experimentais globais).

Esses valores são **hiperparâmetros definidos por nós**, não relações ou significados hardcoded. Eles deverão ser submetidos a novos experimentos e análises de sensibilidade. A utilidade é **preditiva**, não causal e não medida por similaridade de texto.

### Formação de conexões distantes, sem busca global

A cada episódio, o aprendiz recebe no máximo 24 fragmentos observados. Quando um `Y=1` aparece, propõe hipóteses **somente** com os fragmentos presentes naquele episódio, formando candidatas de uma e duas entradas. Uma candidata não recebe crédito pelo episódio que provocou sua criação; passa a acumular evidências apenas em episódios posteriores. Isso evita um viés básico de seleção positiva.

Pares que acumularam evidência de alguma capacidade preditiva, mas ainda não explicam adequadamente `Y`, podem ser **estendidos por um terceiro fragmento** encontrado em experiências positivas seguintes. O programa não enumera todos os ternos: os ternos vêm de pares previamente ativados que demonstraram sinal preditivo.

A posição geométrica dos dois fragmentos é irrelevante. Uma ocorrência compartilhada estabelece a oportunidade de criar uma esfera que os conecte. Depois de criada, uma **tabela invertida** `fragmento -> esferas` permite chegar a ela sem vasculhar a memória inteira.

### Descarte de candidatas

Uma agenda indexada por tempo revisita apenas as esferas cujo prazo de revisão chegou. Uma esfera com evidência suficiente e desempenho próximo ao de um evento aleatório é descartada. Candidatas ainda insuficientemente observadas podem permanecer em teste por até seis janelas; depois expiram **por orçamento de memória**, classificadas como **incertas**, e não como inválidas. O programa registra ambas situações. Candidatas já explicadas por subconjuntos confiáveis também podem ser suprimidas como redundantes; a auditoria distingue esferas confirmadas de candidatas ainda em avaliação.

Remoções possuem pequeno período de espera para evitar recriação imediata em todo episódio. O tamanho total das candidatas possui um teto configurável. Quando se atinge o teto, novas propostas são bloqueadas e contabilizadas. **Não existe varredura global na inferência ou na revisão agendada**; uma auditoria final opcional pode naturalmente percorrer a memória para apresentar métricas e exportá-la.

## Executar

Na pasta contendo `learner.py`, `worlds.py` e `experimentos/`:

```bash
python -m unittest discover -s tests -v
python -m experimentos.run
```

O segundo comando reproduz as 5 sementes `{2, 3, 5, 7, 11}` para quatro mundos e gera `resultados.json`. O arquivo `execucao.log` contém a execução já realizada; `resumo_metricas.csv` resume os indicadores. Python 3.10+ puro, sem bibliotecas de IA e sem downloads.

### Abrir a memória aprendida

O arquivo `memoria_aprendida_exemplo.json` contém **somente as esferas úteis aprendidas** no mundo dos pares, sem guardar as 1.100 experiências brutas. Essa é uma **foto para inferência**, não um checkpoint completo de treinamento. Pode ser carregada com:

```python
from learner import NexoSphereLearner
mem = NexoSphereLearner.from_learned_memory('memoria_aprendida_exemplo.json')
print(mem.predict(mem.tokens_from_vector((1,0,0,0,1,0,0,0,0,0,0,0))))
```

As esferas são representadas por pares `(índice_sinal, valor_observado)`. Um valor `0` num fragmento é **informação afirmativa de ausência observada** e pode participar de uma esfera; não é sinônimo de falta de dado.

## Experimentos

Os quatro ambientes ficam em `worlds.py` e são **separados do algoritmo**:

1. `pares`: duas relações úteis entre pares, com sinais de distração e ruído de consequência.
2. `trincas_e_ausencia`: uma relação exige 3 componentes, inclusive o valor zero de um sinal; outra depende de 3 presenças.
3. `coocorrencia_enganosa`: dois sinais irrelevantes são frequentemente correlacionados aos relevantes, para testar coincidências espúrias.
4. `sem_relacao`: consequência independente da experiência; controle negativo.

Cada mundo é executado com conjuntos de treinamento e teste gerados independentemente. A avaliação usa acurácia, acurácia balanceada, precisão, revocação, F1, erros, falsas previsões, número de candidatas, descarte e custo de propagação medido pelos raios percorridos.

Comparações: `atomica` (até 1 componente), `pares` (até 2), `composta` (até 3 com poda) e `sem_poda` (mesmo modelo completo, sem descarte). **Os baselines são controles deliberadamente simples**, não uma comparação de estado da arte.

### Resultados: médias de cinco sementes

| Mundo | Modelo | Acurácia balanceada | F1 | Candidatas vivas (média) |
|---|---|---:|---:|---:|
| pares | atomica | 0.500 | 0.000 | 5.6 |
| pares | composta | **0.951** | **0.943** | **141.0** |
| pares | sem_poda | 0.951 | 0.943 | 288.0 |
| trincas_e_ausencia | pares | 0.500 | 0.000 | 142.0 |
| trincas_e_ausencia | composta | **0.953** | **0.942** | **649.4** |
| trincas_e_ausencia | sem_poda | 0.953 | 0.942 | 1012.6 |
| coocorrencia_enganosa | composta | **0.942** | **0.932** | **152.2** |
| sem_relacao | composta | 0.500 | 0.000 | 92.4 |

No mundo `pares`, a memória persistida de exemplo conserva apenas **duas esferas úteis** após 1.100 observações; as demais são candidatas transitórias, sujeitas a poda e expiração. No último ambiente, prever sempre `0` é a política adequada de acordo com o critério empregado: não houve identificação estável de uma relação positiva útil. Acurácia balanceada `0,5` aqui **não significa** 50% de acertos totais. Os números completos constam de `resultados.json`.

### Testes de regressão

Os testes unitários cobrem ativação com um raio, crescimento da sustentação sem mudança binária, ausência observada diferente de dado faltante, prevenção de autoconfirmação na criação da esfera, separação entre ativação parcial e condição completa, ausência de consulta a memórias desconectadas, descoberta de pares, controle sem relação e persistência do conteúdo aprendido.

## Interpretação rigorosa

**Capacidade demonstrada:** um mecanismo genérico pode acumular evidências, descobrir alguns agrupamentos úteis entre símbolos opacos, reutilizar esses agrupamentos para prever acontecimentos inéditos e podar candidatas sem perda de qualidade nesses quatro ambientes.

**Não demonstrado:** aprendizagem não supervisionada de todos os objetivos, causalidade, planejamento, inteligência geral, formação ilimitada de relações, aprendizagem da própria regra de aprendizado, linguagem ou a hierarquia plena de esferas dentro de esferas. Os sinais de entrada e o canal `Y` são oferecidos pelo ambiente sintético. As relações de ordem maior são representadas aqui por conjuntos de fragmentos, não por uma rede generalizada de esferas recursivamente encaixadas; isso seria outro experimento.

**Limites:** composição de até 3 fragmentos e eventos de até 24 observáveis; a busca local de pares ainda tem custo quadrático no número de observáveis *do episódio*, embora não dependa do tamanho total da memória. Em um mundo sem relações previsíveis, candidatas incertas ainda podem ocupar memória até expirar. Os hiperparâmetros podem afetar a aprendizagem em ambientes diferentes. Associação observacional não demonstra causalidade. A poda foi eficiente nos quatro cenários gerados, ainda não uma garantia de escalabilidade generalizada.

## Relação com literatura externa

Esta implementação é uma hipótese experimental própria, não uma reinvenção declarada de matemática estabelecida. Referências que orientam o método e a avaliação:

- Domingos, P.; Hulten, G. (2000). *Mining High-Speed Data Streams*. KDD. Aprendizagem incremental com estatísticas suficientes e critérios de criação de estruturas.
- Kanerva, P. (1988). *Sparse Distributed Memory*. MIT Press. Endereçamento e associação em memórias distribuídas.
- Furutachi, S.; Hofer, S. B. (2026). *Rethinking Predictive Processing*. Annual Review of Neuroscience, 49, 471–494. DOI: 10.1146/annurev-neuro-102124-031410. Discussão crítica da hipótese de erro preditivo no cérebro; não é evidência de equivalência do nosso modelo a um cérebro.

## Próximo problema — ainda não implementado

Diminuir a proposição de pares localmente e criar **esferas de esferas** sem que o algoritmo percorra todas as combinações de fragmentos no mesmo episódio. O teste deverá separar ganho preditivo de coocorrência espúria e acompanhar os casos nos quais o sistema não possui evidência suficiente para decidir.
