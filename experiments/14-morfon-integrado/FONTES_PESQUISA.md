# Referências matemáticas consultadas — o que foi testado e o que não foi

1. **Hammond, Vandergheynst e Gribonval (2011), Wavelets on Graphs via Spectral Graph Theory.** https://doi.org/10.1016/j.acha.2010.04.005 — motivação para operações polinomiais locais com Laplaciano de grafo sem diagonalização. Testado: operador de dois passos, validado numericamente. NÃO testado: a wavelet integral dos autores.
2. **Plate (1995), Holographic Reduced Representations.** https://pubmed.ncbi.nlm.nih.gov/18263348/ — composição por convolução circular e desvinculação por correlação. Testado: recuperação em dimensões 16/64/256 e sobreposição 1/4/8, usando estruturas do Mórfon treinado. NÃO substituiu o motor preditivo.
3. **Grünwald (2000), Model Selection Based on Minimum Description Length.** https://pubmed.ncbi.nlm.nih.gov/10733861/ — princípio de descrição concisa; testado um critério MDL de tabela binária como alternativa de promoção. A variante piorou a avaliação; isso não invalida toda a teoria MDL.
4. **Manku e Motwani (2002), Approximate Frequency Counts over Data Streams.** https://dblp.dagstuhl.de/rec/conf/vldb/MankuM02.html — alternativa para investigação futura de candidatos frequentes em fluxos. Não implementada neste experimento.
5. **Survey on Hypergraph Neural Networks (KDD 2024).** https://doi.org/10.1145/3637528.3671457 — conexões de ordem superior e incidência, útil para o contrato de portas e subunidades. O NEXO não implementou uma rede neural hipergráfica convencional.
6. **Representing Higher-Order Networks: A Survey of Graph-Based Frameworks (2026).** https://fs.unm.edu/RepresentingHigherOrderNetworks-v3.pdf — estruturas por faces/células e alta ordem. Testado: faces discretas e divisão de portas. Não implementado um cálculo topológico completo.

Nenhuma dessas fontes é reivindicada como prova de capacidade do NEXO. Os números válidos vêm do código e dos testes locais fornecidos no ZIP.
