# Relatório Arquitetural — Motor Binário Autônomo (NEXO V4.0)

## 1. Eliminação Total de Controladores Exógenos
Em `src/nexo_autonomous_engine.py`, o Python atua unicamente como fornecedor de energia (`pulse_energy(stimulus, energy_quanta)`). Os **8 Mórfons Gênesis** residem fisicamente nos endereços `0..7` da `NodeArena` (`G_INS`, `G_FRAG`, `G_MEET`, `G_JOIN`, `G_POL`, `G_GATE`, `G_PROMOTE`, `G_REVISE`) e governam todas as transformações da memória.

## 2. Layout Binário Exato em `mmap`
- **`MorphonNode` (64 Bytes):** Alinhado a 1 linha de cache L1 (`_pack_ = 1`), contendo núcleo $K$, polaridade $q$, ativação $a_i$, certificação $c_i$, sustentação $s_i$, valor de Belnap, contadores de portas, espectro estrutural $\Lambda_i$, cabeças intrusivas, $\Delta(P)$ MDL, slots de variáveis e quanta de energia.
- **`PortEdge` (32 Bytes):** Arestas dirigidas intrusivas tipadas com flag de ablação física individual.
- **`SurfaceFaceMark` (32 Bytes):** Marcas de superfície contendo payload binário do fragmento, profundidade $c_{ik}$, raízes de proveniência $\mathbb{N}[Z]$ e espectro temporal $\Sigma_D(u)$.
