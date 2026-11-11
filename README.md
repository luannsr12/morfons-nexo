<div align="center">

![NEXO — arquitetura de memória relacional executável](assets/nexo-banner.svg)

# NEXO

**LIM — Large Interaction Memory**  
**Arquitetura de inteligência computacional baseada em memória relacional executável**

[![Artigo de referência](https://img.shields.io/badge/Artigo%20de%20refer%C3%AAncia-Zenodo%20%7C%20DOI-0d9488?style=flat-square)](https://doi.org/10.5281/zenodo.24094723)
[![Publicação complementar](https://img.shields.io/badge/Publica%C3%A7%C3%A3o%20complementar-Zenodo%20%7C%20DOI-0f766e?style=flat-square)](https://doi.org/10.5281/zenodo.24141657)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776ab?style=flat-square)](https://www.python.org/)
![Regressão registrada](https://img.shields.io/badge/regress%C3%A3o%20registrada-115%2F115-22a06b?style=flat-square)
[![Código MIT](https://img.shields.io/badge/c%C3%B3digo-MIT-blue?style=flat-square)](LICENSE)
[![Documentação CC BY 4.0](https://img.shields.io/badge/textos%20e%20figuras-CC%20BY%204.0-blue?style=flat-square)](LICENSE-DOCS.md)

*Aprender uma relação é modificar a memória. Aprender uma função é fazer uma organização dessa memória participar da própria computação.*

[**Arquitetura**](docs/ARQUITETURA.md) · [**Resultados e controles**](docs/RESULTADOS.md) · [**Reprodução**](docs/REPRODUCAO.md) · [**Publicações**](#publicações-e-citação)

</div>

---

## Visão geral

O **NEXO** é um programa independente de pesquisa em aprendizagem e inteligência computacional. Investiga uma arquitetura na qual experiências não são apenas armazenadas para consulta: elas podem constituir **organizações relacionais persistentes e funções executáveis**, reutilizadas para reconhecer situações, inferir consequências, produzir previsões, selecionar ações e revisar a própria memória.

A unidade fundamental é o **Mórfon**. Mórfons conectados formam malhas nas quais identidade, contexto, proveniência, ativação e condições de execução são representados explicitamente. **LIM (*Large Interaction Memory*)** denomina a proposta de modelo de inteligência baseada nessa organização adquirida por interações.

A pesquisa reúne uma sequência de experimentos computacionais, formulações matemáticas, controles comparativos, ablações causais e código reexecutável. Os resultados primários estão preservados junto aos respectivos protocolos.

## Arquitetura: da experiência à organização funcional

![Organização conceitual do NEXO](assets/arquitetura-nexo.svg)

Um Mórfon combina:

- **Núcleo operacional invariável**, com três vias/estados de sinal: $-1$, $0$ e $+1$.
- **Faces e fragmentos modificáveis**, nos quais experiências, marcas e diferenças estruturais podem ser inscritas.
- **Portas relacionais tipadas**, que distinguem premissas, inibições, consequências, contexto e vínculos.
- **Raios de ativação:** uma incidência basta para ativar uma unidade; incidências adicionais acrescentam sustentação contextual, não provas independentes por definição.
- **Identidade, proveniência e história**, permitindo compartilhamento entre malhas, revisão e reconstituição das relações.

Os **Mórfons Gênesis** compõem a organização inicial: fornecem operações elementares de criação, replicação, modificação e remoção de organizações. O núcleo não precisa adquirir novas instruções para que faces, portas e configurações funcionais sejam transformadas.

O percurso investigado é:

**Experiência → inscrição → ativação local → encontro de regularidades → organização funcional → inferência/ação → nova experiência → revisão.**

A mesma identidade morfônica pode participar de diferentes malhas. A composição entre elas depende das relações efetivas, da identidade compartilhada e da compatibilidade contextual — não apenas de nomes coincidentes.

## Fundamentos matemáticos

O formalismo trata a memória no instante $t$ como uma estrutura relacional mutável:

$$
\mathcal{M}_t=(V_t,E_t,\mathcal{F}_t,\mathcal{H}_t),
$$

em que $V_t$ é o conjunto de Mórfons, $E_t$ representa as portas, $\mathcal{F}_t$ as faces e marcas, e $\mathcal{H}_t$ os históricos e vínculos de revisão.

### Ativação e certificação são operações distintas

Para uma unidade $i$, seja $R_i$ o conjunto de raios recebidos no pulso e sejam $P_i^+$ e $P_i^-$ suas premissas positivas e negativas. A ativação exige apenas incidência; a emissão exige completude das condições:

$$
 a_i=\mathbf{1}\{|R_i|\geq 1\},\qquad
 c_i=\mathbf{1}\{P_i^+\subseteq B^+\}\,
     \mathbf{1}\{P_i^-\subseteq B^-\}\,
     \mathbf{1}\{|P_i^+|+|P_i^-|>0\}.
$$

Essa distinção sustenta a execução condicionada por relações, a inibição e a composição em múltiplos saltos.

### Indução e promoção conservativa

Os operadores **MEET** e **JOIN** identificam interfaces compartilhadas e generalizações entre experiências. A promoção de uma estrutura candidata $P$ pode ser avaliada por economia de descrição:

$$
\Delta(P)=n\big[(m-v)b-q\big]-c(P).
$$

Aqui $n$ representa raízes empíricas independentes, $m$ o comprimento estrutural, $v$ as posições variáveis, $b$ o custo por símbolo, $q$ o custo por referência e $c(P)$ o custo da estrutura promovida. A condição $\Delta(P)>0$ expressa ganho de compressão no modelo de custos escolhido.

### Afinidade contrastiva entre marcas

Para profundidades de marca $c_{ik}$ associadas a Mórfons e testemunhas, a pesquisa utiliza uma medida residual para destacar interseções informativas em meio a testemunhas frequentes:

$$
 e_{ik}=\frac{C_{i\bullet}C_{\bullet k}}{C_{\bullet\bullet}},\qquad
 d_{ik}=\max(0,c_{ik}-e_{ik}),\qquad
 E^+(i,j)=\sum_k\min(d_{ik},d_{jk}).
$$

### Estados preditivos, proveniência e localidade

Os **espectros temporais** $\Sigma_H(u)$ representam continuações de ação e observação acessíveis a partir de uma história $u$, permitindo comparar histórias pelos comportamentos futuros registrados. A **proveniência fatorada em DAG** compartilha subprovas sem enumerar todos os percursos combinatórios. Na propagação localizada, o custo da consulta acompanha a região visitada e as portas examinadas:

$$
T=O\!\left(|V_{\mathrm{tocado}}|+\sum_{u\in V_{\mathrm{tocado}}}\deg^+(u)\right).
$$

O programa também investiga **álgebra polar sobre $\mathbb F_2$**, completude funcional por certificação de portas, **revisão por contraexemplos**, acoplamento de variáveis e transformações de Möbius. Definições, hipóteses, demonstrações e ensaios estão detalhados nas publicações e nos materiais experimentais.

## Resultados experimentais

| Linha de investigação | Resultado registrado | Evidências |
|:---|:---|:---|
| **Descoberta de estruturas · Exp. 08** | Formação, promoção, descarte e persistência de organizações a partir de sinais binários; oito testes de regressão. | [Exp. 08](experiments/08-aprendizagem-esferas/) |
| **Composição de quatro condições · Exp. 14** | Acurácia balanceada **1,000**, ante **0,500** do comparador de alcance menor, no mundo de quatro condições. | [Exp. 14](experiments/14-morfon-integrado/) |
| **Composição relacional · Exp. 17** | **2.000/2.000** consultas em 40 mundos inéditos, incluindo **320** composições de dois ou três saltos não demonstradas integralmente. | [Exp. 17](experiments/17-raciocinio-contextual/) |
| **Transformação numérica · Exp. 17** | **1.000/1.000** somas inéditas mediante oito transições binárias aprendidas com estados intermediários. | [Exp. 17](experiments/17-raciocinio-contextual/) |
| **Memória conversacional · Exp. 21** | **384/384** consultas novas, **175/175** consultas após ensino de paráfrases e continuidade após persistir e restaurar a memória. | [Exp. 21](experiments/21-memoria-continua/) |
| **Funções inscritas nas faces · Exp. 23** | **960/960** previsões reservadas e **962/962** objetivos; intervenções sobre pulsos e marcas alteraram ou bloquearam as inferências. | [Exp. 23](experiments/23-faces-funcionais/) |
| **Aprender → prever → agir → revisar · Exp. 24** | **480/480** previsões e **1.034/1.034** planos; controle de seleção aleatória: **328/480** previsões identificadas e **942/1.034** planos. | [Exp. 24](experiments/24-ciclo-integrado/) |
| **Composição entre malhas** | **600/600** casos sintéticos sob identidade e contexto; sem compatibilidade contextual, **126** falsos positivos. | [Malhas](experiments/malhas-compartilhadas/) |
| **Proveniência fatorada** | **4.096** percursos representados por **108 nós DAG**; **48** exames relacionais contra **16.380** na expansão explícita, no caso de 12 losangos. | [Malhas](experiments/malhas-compartilhadas/) |

Os registros incluem condições de treinamento, avaliações reservadas, comparadores, intervenções, abstenções e casos adversariais. Para números, protocolos e arquivos de origem, consulte [**Resultados e controles**](docs/RESULTADOS.md).

### Resultados ilustrados

| Funções e marcas · Experimento 23 | Aprendizagem e ação · Experimento 24 |
|:--:|:--:|
| ![Generalização e marcas funcionais](assets/resultado-exp23.png) | ![Aprendizagem, previsão e ações](assets/resultado-exp24.png) |

| Composição contextual · Experimento 17 | Proveniência e malhas compartilhadas |
|:--:|:--:|
| ![Composição relacional](assets/composicao-exp17.png) | ![Proveniência fatorada em DAG](assets/proveniencia-malhas.png) |

## Linha experimental e implementações

Os experimentos documentam a evolução dos mecanismos: **08** (formação de estruturas), **14** (substrato integrado), **17** (referências e composição), **21** (memória conversacional), **23** (funções nas faces) e **24** (ciclo completo de experiência, previsão e ação). O estudo de **malhas compartilhadas** desenvolve composição contextual, identidade canônica e fatoração de proveniência.

O acervo inclui também a investigação **V4.0**, com arenas binárias mapeadas em memória para Mórfons (64 bytes), portas (32 bytes) e marcas de superfície (32 bytes), disponível em [`experiments/NEXO_PROJETO_FINAL_AUTONOMO_COMPLETO/`](experiments/NEXO_PROJETO_FINAL_AUTONOMO_COMPLETO/).

Cada conjunto conserva seus próprios protocolos, implementações e resultados. Essa organização permite estudar a contribuição de cada mecanismo e reproduzir a evolução da arquitetura.

## Reproduzir os experimentos

**Requisito:** Python 3.11 ou superior. A maior parte das verificações utiliza apenas a biblioteca padrão; dependências científicas opcionais constam do arquivo específico.

```bash
# Clone
git clone https://github.com/luannsr12/morfons-nexo.git
cd morfons-nexo

# Dependências opcionais para o Exp. 14 e gráficos
python -m pip install -r requirements-optional.txt

# Suítes de regressão
python scripts/test_all.py

# Conferência das métricas nos registros primários
python scripts/verify_results.py

# Integridade do acervo versionado
python scripts/verify_source_hashes.py
```

**Última reexecução documentada:** 10 de novembro de 2026, com **115/115 testes de regressão aprovados**. As baterias extensas e os gráficos possuem comandos próprios em [**Reprodução**](docs/REPRODUCAO.md); os scripts de verificação conferem separadamente os resultados arquivados.

## Publicações e citação

**Artigo de referência**

> **Rosa, Luan** (2026). *NEXO: Arquitetura de memória relacional executável — fundamentos, demonstrações e resultados experimentais com auditoria causal*. Version 1.0. Zenodo. DOI: [10.5281/zenodo.24094723](https://doi.org/10.5281/zenodo.24094723).

**Publicação complementar:** [DOI 10.5281/zenodo.24141657](https://doi.org/10.5281/zenodo.24141657).

**Autor:** Luan Rosa Alves da Silva · **assinatura bibliográfica:** Rosa, Luan · [ORCID 0009-0000-2754-7135](https://orcid.org/0009-0000-2754-7135).

O repositório inclui [`CITATION.cff`](CITATION.cff) para citação automatizada pelo GitHub.

**Documentação:** [Arquitetura](docs/ARQUITETURA.md) · [Resultados](docs/RESULTADOS.md) · [Reprodução](docs/REPRODUCAO.md) · [Proveniência](docs/PROVENIENCIA.md).

## Licenciamento

O código experimental e os scripts estão disponíveis sob **MIT**, conforme [`LICENSE`](LICENSE). Os textos, diagramas e materiais autorais de documentação estão disponíveis sob **Creative Commons Attribution 4.0 International (CC BY 4.0)**, conforme [`LICENSE-DOCS.md`](LICENSE-DOCS.md). Consulte [`NOTICE.md`](NOTICE.md) para créditos e escopo.
