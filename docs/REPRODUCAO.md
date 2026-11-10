# Reproduzir os experimentos

Execute cada comando **na pasta indicada**, a partir do repositório. Python 3.11 ou superior. Para o Exp. 14: `python -m pip install -r requirements-optional.txt` (executado na raiz do repositório).

| Ensaio | Diretório | Comandos |
|---|---|---|
| 08 | `experiments/08-aprendizagem-esferas` | `python -m unittest discover -s tests -v` e `python -m experimentos.run` |
| 14 | `experiments/14-morfon-integrado` | `python -m unittest discover -s testes -v`; ver `README.md` local para as nove famílias |
| 17 | `experiments/17-raciocinio-contextual` | `python -m unittest discover -s tests -v`; `python src/laboratorio.py`; `python src/controles.py`; `python src/chat_cli.py` |
| 21 | `experiments/21-memoria-continua` | `python -m unittest discover -s tests -v`; `python src/evaluate.py`; `python src/evaluate_paraphrases.py`; `python src/adversarial.py`; `python src/chat.py` |
| 23 | `experiments/23-faces-funcionais` | `python -m unittest discover -s tests -v`; `python src/confirmatory.py`; `python src/causal_ablations.py`; `python src/active_design.py` |
| 24 | `experiments/24-ciclo-integrado` | `python -m unittest discover -s tests -v`; `python src/evaluate.py 12`; `python src/adversarial.py`; `python src/scale.py`; `python src/demo.py` |
| Malhas | `experiments/malhas-compartilhadas` | `python -m unittest -v test_experiment`; `python experiment.py` |

## Um comando para a regressão

Na **raiz**:

```bash
python scripts/test_all.py
python scripts/verify_results.py
python scripts/verify_source_hashes.py
```

O arquivo `reproducibility/retest_2026-11-10.json` contém a reexecução independente realizada ao preparar este repositório. O script `test_all.py` registra relatório próprio em `reproducibility/local_test_run.json` ao ser usado sem `--no-save`. Essa saída local pode ser atualizada e não integra os hashes das fontes.

## Cópias originais e organização

Cada pasta de `experiments/` contém os arquivos primários extraídos de uma versão original, **sem alterações no código-fonte**. Arquivos históricos ZIP duplicados/encapsulados foram excluídos para que o repositório seja navegável; seus nomes, hashes e exclusões são relacionados em `docs/PROVENIENCIA.md`. Os dados e resultados primários dos sete experimentos selecionados foram mantidos. O manifesto `reproducibility/source_hashes.json` audita byte a byte tudo que foi copiado.

## Reprodutibilidade das baterias

Os scripts de avaliação frequentemente atualizam seus arquivos `results/` e `dados/`. Para preservar os registros publicados, execute-os preferencialmente numa cópia de trabalho (`cp -a experiments/24-ciclo-integrado /tmp/nexo-exp24`, por exemplo) ou registre um commit antes. O pipeline automatizado roda as suítes e valida os resultados arquivados, sem substituir os dados originais por saídas novas.
