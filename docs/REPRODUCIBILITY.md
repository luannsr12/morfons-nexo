# Reproducibility guide

**English** | [Português (Brasil)](REPRODUCAO.md) · [Research overview](../README.md)

## Environment

- **Python:** 3.11 or later is the repository-wide recommended version.
- Most experiments use **standard-library Python**.
- Experiment 14 and optional figures use packages listed in [`requirements-optional.txt`](../requirements-optional.txt).
- The seven archived suites are run **in separate working directories** by the top-level runner.

From the repository root:

~~~bash
git clone https://github.com/luannsr12/morfons-nexo.git
cd morfons-nexo
python -m pip install -r requirements-optional.txt

python scripts/verify_source_hashes.py
python scripts/verify_results.py
python scripts/test_all.py --no-save
~~~

These commands check different things:

1. **`verify_source_hashes.py`** compares preserved experimental files with the recorded SHA-256 inventory.
2. **`verify_results.py`** checks recorded primary result metrics against the repository's expected values. It does **not** regenerate every long benchmark.
3. **`test_all.py --no-save`** actually executes the seven original regression suites, returning nonzero exit status if a suite fails.

Without `--no-save`, the test runner also writes `reproducibility/local_test_run.json` and `local_test_run.log`.

## Per-experiment commands

Change to the indicated folder **before** running each row.

| Folder (under `experiments/`) | Command(s) |
| :-- | :-- |
| `08-aprendizagem-esferas` | `python -m unittest discover -s tests -v`; `python -m experimentos.run` |
| `14-morfon-integrado` | `python -m unittest discover -s testes -v`; see the local `README.md` for nine world families |
| `17-raciocinio-contextual` | `python -m unittest discover -s tests -v`; `python src/laboratorio.py`; `python src/controles.py`; `python src/chat_cli.py` |
| `21-memoria-continua` | `python -m unittest discover -s tests -v`; `python src/evaluate.py`; `python src/evaluate_paraphrases.py`; `python src/adversarial.py`; `python src/chat.py` |
| `23-faces-funcionais` | `python -m unittest discover -s tests -v`; `python src/confirmatory.py`; `python src/causal_ablations.py`; `python src/active_design.py` |
| `24-ciclo-integrado` | `python -m unittest discover -s tests -v`; `python src/evaluate.py 12`; `python src/adversarial.py`; `python src/scale.py`; `python src/demo.py` |
| `malhas-compartilhadas` | `python -m unittest -v test_experiment`; `python experiment.py` |

**Important:** longer evaluations can **overwrite** original files under `results/` or `dados/`. Use a second clone or a separate working copy for regenerating benchmarks; leave the reference archive unchanged.

## Archived run and continuous integration

The independent retest prepared on **November 10, 2026** is preserved in [`retest_2026-11-10.json`](../reproducibility/retest_2026-11-10.json) with all **115 tests passed**. The record documents its own environment. The [CI workflow](../.github/workflows/tests.yml) repeats the source-integrity check, metric verification and seven test suites on Python 3.11.

An archived passing run is **not** a claim that a new environment has already passed. Consult the [live CI history](https://github.com/luannsr12/morfons-nexo/actions/workflows/tests.yml) and run locally when investigating regressions.

## Historical archives and SHA-256

The [source archive inventory](../reproducibility/source_archives.json) identifies the original packages and omitted nested duplicates. The [file-level hash inventory](../reproducibility/source_hashes.json) identifies byte-for-byte preserved experimental files.

The source and data under `experiments/` are **historical research artifacts**, deliberately not normalized or translated in place. New bilingual overview documents belong outside the frozen source inventory.

See [Provenance](PROVENANCE.md) and the [experiment directory](../experiments/README.md).
