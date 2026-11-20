# Experimental archive · NEXO

**Language:** English | [Português (Brasil)](README.pt-BR.md)

This is an archive of **independently developed laboratory mechanisms**, rather than a package exposing one unified API. The original experiment sources, tests, reports, measured outputs and manifests are left in their historical folders. Many local READMEs and technical reports remain in Portuguese because they are part of the preserved scientific record.

[Return to the main overview](../README.md) · [Read the results](../docs/RESULTS.md) · [Reproduce](../docs/REPRODUCIBILITY.md) · [Check provenance](../docs/PROVENANCE.md)

## Navigation by research question

| Study | Research question | Where to inspect |
| :-- | :-- | :-- |
| **08 · Structural learning** | Can binary observations induce and maintain new organizations? | [Source and experiment README](../experiments/08-aprendizagem-esferas/) · `resultados.json` |
| **14 · Integrated Morphon** | How do rays, context, ordering, persistence and pruning behave together? | [Source, technical report, tests and data](../experiments/14-morfon-integrado/) |
| **17 · Contextual reasoning** | Can learned references compose across unseen worlds and support binary transitions? | [Source, report and evaluations](../experiments/17-raciocinio-contextual/) |
| **21 · Continuous memory** | Can dialogue observations survive persistence, incremental teaching and revision? | [Source, sessions and tests](../experiments/21-memoria-continua/) |
| **23 · Functional surfaces** | Do surface marks causally affect predicted consequences? | [Source, intervention tests and results](../experiments/23-faces-funcionais/) |
| **24 · Integrated cycle** | Can one experimental memory connect observation, prediction, action, feedback and revision? | [Source, controls and demos](../experiments/24-ciclo-integrado/) |
| **Shared relational meshes** | When is cross-mesh composition conservative, and can provenance be factorized? | [Code, results and report](../experiments/malhas-compartilhadas/) |
| **Separate V4.0 archive** | What can binary memory-mapped arenas and experimental autonomous engines demonstrate? | [Historical V4.0 research archive](../experiments/NEXO_PROJETO_FINAL_AUTONOMO_COMPLETO/NEXO_RESEARCH/) |

The numbering records experimental history; **there are no implied results for missing experiment numbers**. The V4.0 research archive is separate from the seven regressions counted by the repository's primary test runner.

## How to reproduce without changing evidence

From the repository root:

~~~bash
python -m pip install -r requirements-optional.txt
python scripts/test_all.py --no-save
python scripts/verify_results.py
python scripts/verify_source_hashes.py
~~~

Long evaluations can overwrite their own stored output. Run them in a separate clone/copy; follow [the per-experiment command matrix](../docs/REPRODUCIBILITY.md). The SHA-256 manifest [source_hashes.json](../reproducibility/source_hashes.json) is the reference for original files.

The archived suite totals **115 tests** in the recorded November 10, 2026 run. The data and implementations belong to their individual test contracts; joining their results does not establish one general-purpose system.

**For the currently deployed related interactive application, visit [Morphons AI](https://morphons-ai.vercel.app/).** Its runtime is maintained separately from these archived suites.
