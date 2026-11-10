# NEXO — Experimento 14: Mórfon Integrado

**Laboratório experimental independente, 08/11/2026. Não substitui automaticamente as versões anteriores do NEXO.**

## Questão

Conseguimos fazer **ativação binária por raios**, **sustentação pela contagem de raios**, **formação/avaliação de composições aprendidas**, **memória persistente nos próprios nós**, **aninhamento**, **seleção aprendida do nível de composição** e **revisão da memória** operarem num mesmo ciclo de experiência? Qual alternativa melhora capacidades reais, e qual é apenas uma representação mais cara?

## Resultado geral

- Sim, foi montado um motor com **um único substrato de Mórfons** que é usado ao treinar, prever, serializar, restaurar e continuar o treinamento. A representação persistente está nos Mórfons; os índices externos são reconstruídos a partir das portas.
- Nos **9 mundos sintéticos × 3 sementes × 260 consultas reservadas**, a versão integrada com controle aprendeu pares, trincas, condições explícitas de zero e quatro partes. A de quatro partes obteve acurácia balanceada **1,000** contra **0,500** do Exp.08 limitado a trincas; preservou resultados altos nos ambientes simples. Confira `dados/principal_*_individuais.json`.
- Um Mórfon de controle aprende, a partir de resultados *prequenciais anteriores*, qual profundidade `k=2,3,4` vem funcionando melhor. As alternativas são avaliadas com o estado **antes** de receber o rótulo do episódio.
- A representação **aninhada** produziu as mesmas previsões da versão de portas diretas nesses mundos, muitas vezes com menos acessos a conexões. **O peso físico de raios não é o mesmo**: 4 folhas podem virar 2 raios de 2 Mórfons componentes.
- A **poda periódica** reaproveita o mecanismo previamente experimentado no Exp.08; reduziu memória e conexões percorridas nos mundos de pares e quatro componentes em três sementes, preservando as previsões dessas tarefas.
- O motor original do Exp.08 **foi realmente executado** como comparador, não estimado de relatórios anteriores: `codigo/legado_exp08.py`.
- A integração **não superou o original nos dígitos reais** (0,770 vs 0,796 de balanced accuracy em três divisões). No mundo nulo chegou ao teto de 1.800 Mórfons. Sob mudança não observada de regra a balanced accuracy ficou ~0,508. Essas são limitações **reais**, não omitidas.
- Filtro espectral polinomial local: equivale à operação matricial de dois saltos com erro numérico de ~1e-16, mas **não melhorou a classificação binária**; foi mantido como ablação, não como requisito.
- Face/forma facetada e 4D funcionaram na codificação, mas **não acrescentaram capacidade** às previsões testadas. Compressão holográfica perdeu informação em alta sobreposição; duplicação ingênua aumentou raios sem introduzir nova evidência.

## Reproduzir

Python 3.11+ com `numpy`, `matplotlib`, `scikit-learn`.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s testes -v
python codigo/rodar.py --seeds 3 --train 520 --test 260 --variants ORIGINAL_08 B_integrated W_order_controller X_controller_nested --worlds pair_or triple_absence xor --prefix principal_a
python codigo/rodar.py --seeds 3 --train 520 --test 260 --variants ORIGINAL_08 B_integrated W_order_controller X_controller_nested --worlds quad context noisy --prefix principal_b
python codigo/rodar.py --seeds 3 --train 520 --test 260 --variants ORIGINAL_08 B_integrated W_order_controller X_controller_nested --worlds null correlated drift --prefix principal_c
python codigo/rodar.py --seeds 3 --train 520 --test 260 --variants W_order_controller AD_pruned_controller AE_pruned_nested --worlds quad pair_or --prefix poda_robustez
python codigo/probes.py
python codigo/replicacao_probe.py
python codigo/consolidar.py
python codigo/figuras.py
```

**Observação:** `probes.py` inclui uma avaliação em imagens reais e pode ser mais demorada. Reproduz o dataset `digits` instalado com scikit-learn, sem downloads. Cada linha individual contém `world`, `seed`, `variant` e as contagens TP/FP/FN/TN. Arquivos de auditoria também registram entradas, saídas e snapshots de algumas execuções.

## Organização

- `codigo/morfon.py`: contrato integrado; Mórfons, portas, foco, formação, meta-controle, poda, snapshot/restauração.
- `codigo/mundos.py`: gerador de mundos ocultos, **não importado pelo aprendiz**.
- `codigo/rodar.py`: comparações pareadas com mesma entrada, incluindo o Exp.08 original.
- `codigo/probes.py`: verificações com dados reais, 3D/4D, escala, HRR, espectro local.
- `codigo/replicacao_probe.py`: contraexemplo de duplicação/contagem de raios.
- `codigo/consolidar.py` e `codigo/figuras.py`: agrega resultados e reconstrói figuras.
- `testes/`: testes automatizados, incluindo reinício do treinamento após serialização.
- `dados/`: métricas individuais e agregadas, logs, exemplos de estados persistidos, controles e insucessos.
- `figuras/`: gráficos e diagrama derivados dos dados.
- `RELATORIO_TECNICO.md`: análise matemática completa, limitações e decisões.
- `FONTES_PESQUISA.md`: matemática externa investigada e o que foi efetivamente implementado.
- `historico/`: cópias congeladas dos ZIPs 08–13 para comparação, sem alteração desses protótipos.

## Escopo das alegações

Não é aprendizagem sem qualquer viés: o aprendiz recebe vetores binários observados e uma consequência binária posterior, e nós fornecemos operações elementares, um orçamento e políticas gerais de formação. Ele **não conhece as fórmulas ocultas dos mundos**, mas ainda não inventa o próprio algoritmo matemático, não descobre sensores e não planeja a longo prazo nesse protótipo. A ramificação anterior de **funções sobre dados** permanece separada.
