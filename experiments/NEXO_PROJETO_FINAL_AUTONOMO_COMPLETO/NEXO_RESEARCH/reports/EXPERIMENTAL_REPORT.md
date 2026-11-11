# Relatório Experimental Consolidado (7 Fases Autônomas + Benchmarks)

1. **Fase 1 (Fragmentação Sub-Simbólica Autônoma e Marcas de Superfície):**
   - O estímulo composto bruto `"fogo+agua+turbina"` foi decomposto autonomamente pelo Gênesis `G_FRAG` nos fragmentos `['fogo+agua+turbina', 'fogo', 'agua', 'turbina']`.
   - Afinidade de superfície $E(i,j)$ e Excedente Contrastivo $E^+(i,j)$ atingiram **AUC = 1,0000**, superando a geometria de centroides 3D (**AUC = 0,8001**).
2. **Fases 2 e 3 (Auto-Organização MDL e Generalização 75/75):**
   - **75/75 (100%)** em identidades inéditas (`Pessoa_Inedita_0..74`) via transporte binário de slot, contra **0/75 (0%)** da memória literal.
   - Em variáveis acopladas ($R(X,X)$), certificou $100\%$ dos pares idênticos e bloqueou $100\%$ dos pares cruzados ($R(A,B)$).
3. **Fases 4 e 5 (Composição de 3 Saltos $T_C \circ T_B \circ T_A$ e Revisão por Contraexemplo):**
   - Diante de `"fogo+agua+turbina"` sem `"litio"`, emergiu a cadeia completa de 3 saltos `['aquece', 'vapor', 'energia_eletrica']` (Mórfons `[34, 25, 31]`, 33 raios, 13 nós tocados).
   - Com a presença de `"litio"`, a porta negativa de `[34]` bloqueou imediatamente toda a cadeia (`[]`).
4. **Fase 6 (Indução de Estados Preditivos Sem Oráculo e Investigação Ativa):**
   - A partir apenas das transições empíricas vividas, o Teorema 1.7 reconstruiu os **3 estados preditivos mínimos** na `NodeArena` (`oracle_used: False`).
   - Diante do estímulo incompleto `"vapor"`, a memória acionou autonomamente a Investigação Ativa apontando a porta discriminante faltante `['turbina']`.
5. **Fase 7 (Invariância $O(\text{grau local})$ com +10.000 Mórfons e Rota Factual 40/40):**
   - Antes de adicionar +10.000 Mórfons desconectados: **48 raios percorridos / 16 nós tocados**.
   - Depois de adicionar +10.000 Mórfons desconectados (total de **10.228 nós** na arena): **48 raios percorridos / 16 nós tocados** (invariância absoluta!).
   - Rota factual revisada: **40/40 acertos** com energia ativa, **0 vazamentos** de versões obsoletas e **0/40** quando a energia dos raios é cortada.
