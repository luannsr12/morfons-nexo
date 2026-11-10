# NEXO Experimento 24 — Mórfons com núcleos constantes e faces recebidas

**Execução integrada, com núcleo legado original preservado.**

Este pacote não substitui o projeto: corrige o contrato arquitetural do Experimento 23 e testa o ciclo completo numa única `MorphMemory`: experiências, memória, contexto da última ação, aprendizado funcional, antecipação, decisões, ações físicas simuladas, feedback e revisão.

**Regra inviolável:** face é marca de interação; nenhum Mórfon escreve sobre si; núcleo imutável atua sobre outro. Nenhuma contradição cria subdivisões de faces por convenção. Um raio ativa; raios adicionais sustentam. As respostas são causadas por marcas e portas do núcleo original.

Veja `RELATORIO.md` para os resultados, controles, falhas e referências.

## Executar

Em Python 3.10+ (somente biblioteca padrão):

```
python -m unittest discover -s tests -v
python src/evaluate.py 12
python src/adversarial.py
python src/scale.py
python src/demo.py
```

## Conteúdo

- `src/integrated.py`: Mórfons, núcleo constante, marcas de interação, aprendizagem GF(2), atividade interna, plano e ação.
- `src/evaluate.py`: avaliação contínua integrada e controle de experiência aleatória.
- `src/adversarial.py`: falha de ordem 3, correção, contradição, interferência em aresta física, ablação de histórico.
- `src/scale.py`: seis entradas, cinco saídas e observações que ampliam o posto.
- `tests/test_integrated.py`: regressões e invariantes.
- `originals/morfon_exp21_original.py`: **núcleo original intacto**, sem patch silencioso.
- `originals/spectral_faces_exp23_reference.py`: método algébrico anterior para comparação.
- `originals/NEXO_EXP22_REORGANIZACAO_ENDOGENA_2026-11-08.zip`, `originals/NEXO_EXP23_VERIFICADO.zip`: pacotes originais anteriores, preservados integralmente.
- `results/`: casos individuais, métricas por instância, logs, gráficos e testes adversariais.

Limite operacional relevante: embora os dados específicos de mundo sejam aprendidos em marcas e os resultados dependam causalmente das portas/rays, **a álgebra GF(2) e a busca por ações são operações genéricas programadas no núcleo invariável**. Isso responde diretamente ao desenho de núcleo constante, mas não comprova que a rede tenha inventado a álgebra. O cenário é sintético, auditável e com interface de sensores/ações estruturada.
