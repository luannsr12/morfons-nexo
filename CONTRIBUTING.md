# Contributing to the NEXO research archive

**English** | [Português (Brasil)](CONTRIBUTING.pt-BR.md)

The most useful contributions are **replications, bug reports with reproducible cases, methodological questions, and precise documentation corrections**.

Before proposing a change, review [Reproducibility](docs/REPRODUCIBILITY.md), [Results & controls](docs/RESULTS.md), and [Provenance](docs/PROVENANCE.md).

## How to report a finding

Open a GitHub issue and include the **experiment folder**, **commit SHA**, **Python/environment version**, **commands**, **actual output**, **expected output**, and (when possible) **the smallest input that reproduces the difference**. For a scientific claim, identify the specific metric file and test condition instead of citing only a headline score.

## Preservation policy

The files under `experiments/` are historical sources tracked by SHA-256; do not silently reformat, translate or overwrite the recorded originals. Propose corrected experiments in a **clearly distinguished new version or directory**, with their own tests and metrics. Improvements to research guides, translations, navigation, accessibility and diagrams can be made in editorial files.

Suggested local checks:

~~~bash
python scripts/verify_source_hashes.py
python scripts/verify_results.py
python scripts/test_all.py --no-save
~~~

Please distinguish tested observations from proposed hypotheses, preserve provenance, and document the failure cases alongside successes.

**Related application:** [Morphons AI](https://morphons-ai.vercel.app/) is developed in a separate repository; this archive's issues should concern its **own code, data and scientific documentation**.
