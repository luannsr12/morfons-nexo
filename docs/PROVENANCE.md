# Provenance & integrity of the research archive

**English** | [Português (Brasil)](PROVENIENCIA.md) · [Overview](../README.md)

The seven primary experiment packages were extracted from preserved original archives. Original **code, tests, data, reports, logs and figures** selected for `experiments/` have not been silently rewritten as part of this editorial repository. Each included historical file is auditable by SHA-256.

## Traceability

| Resource | Purpose |
| :-- | :-- |
| [`reproducibility/source_archives.json`](../reproducibility/source_archives.json) | Original package names, package hashes and inventory of omitted nested duplicates |
| [`reproducibility/source_hashes.json`](../reproducibility/source_hashes.json) | SHA-256 manifest for each included source file under `experiments/` |
| [`scripts/verify_source_hashes.py`](../scripts/verify_source_hashes.py) | Byte-level integrity check of the historical experiment collection |
| [`reproducibility/retest_2026-11-10.json`](../reproducibility/retest_2026-11-10.json) | Documented regression retest of the seven primary suites |
| [`docs/RESULTS.md`](RESULTS.md) | Research outcomes and the locations of the primary records |

Historical **nested ZIP archives** and cache directories that duplicated earlier packages were not all duplicated in the public tree. The original archive index explains the omissions. The selected seven experiment directories retain their primary source and evidence files; the V4.0 archival research tree is also navigable as a separate historical branch.

## Editorial versus experimental files

The repository-wide landing pages, bilingual navigation, architecture illustration and introductory guide are **editorial documentation**. They may evolve to improve clarity and accessibility.

By contrast, original experiment materials and their recorded output must remain traceable to their original manifest. A new presentation, translation or reorganization **does not constitute a new experimental result** and cannot replace a controlled evaluation.

Images under `assets/` used for experimental results were copied from the archived experiments; the cover banner and conceptual flow illustration are editorial. Any future correction to a historic experimental source should explicitly distinguish **a corrected version** from the immutable reference record.

## Interpretation and attribution

This repository collates research directions evaluated separately. They share architectural ideas but **were not necessarily merged into a single engine**. The companion live application, [Morphons AI](https://morphons-ai.vercel.app/), is a related and separately maintained implementation, not an identical runtime for all archived tests.

For attribution and the role of computational assistance, see [NOTICE](../NOTICE.md). For usage rights, see [MIT](../LICENSE) and [CC BY 4.0](../LICENSE-DOCS.md).

To repeat verification:

~~~bash
python scripts/verify_source_hashes.py
python scripts/verify_results.py
python scripts/test_all.py --no-save
~~~
