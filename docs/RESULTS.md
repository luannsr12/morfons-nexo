# Experimental results & controls

**English** | [Português (Brasil)](RESULTADOS.md) · [Back to NEXO](../README.md)

This is an evidence inventory, not a pooled benchmark. Each result belongs to a **specified laboratory protocol**. Original reports, metrics, tests and controls are preserved under [`experiments/`](../experiments/).

## Experiment 08 · Structural discovery

An experimental learner starts without previously taught relations and observes opaque binary signals and their outcomes. It proposes, promotes, persists and discards sphere organizations derived from experience; a ray activates a sphere, while the completion of conditions is assessed separately.

**Archived regression suite:** 8 tests, covering observed absence versus unknown value, local indexing, persistence and structural formation.

**Primary files:** [`resultados.json`](../experiments/08-aprendizagem-esferas/resultados.json), [test suite](../experiments/08-aprendizagem-esferas/tests/), [original README](../experiments/08-aprendizagem-esferas/README.md).

## Experiment 14 · Integrated substrate

Across **9 worlds × 3 seeds × 260 held-out queries per configuration**, the integrated approach reached **1.000 balanced accuracy** in the four-part world, compared with **0.500** for an earlier lower-reach comparator. Drift, null-world and real-digit conditions were also studied. The integrated approach **did not outperform the comparator universally** across these settings.

**Archived regression suite:** 14 tests.

**Primary files:** [`consolidacao.json`](../experiments/14-morfon-integrado/dados/consolidacao.json), the individual `dados/principal_*_individuais.json` records and the [original technical report](../experiments/14-morfon-integrado/RELATORIO_TECNICO.md).

## Experiment 17 · Reference composition and arithmetic

Training covered **240 worlds**, **8,160 grounded statements**, **10,080 demonstrated questions** and **1,920 reference demonstrations**. Evaluation on **40 held-out worlds** produced **2,000/2,000** correct queries, including **320** new two- or three-hop compositions not demonstrated as whole chains. Binary transitions learned with supervised intermediate states yielded **1,000/1,000** unseen additions.

Controls included fact removal and answer shuffling.

**Archived regression suite:** 18 tests.

**Primary files:** `experiments/17-raciocinio-contextual/results/metricas.json`, `results/avaliacao_individual.json`, `results/avaliacao_numerica.json`, [original technical report](../experiments/17-raciocinio-contextual/RELATORIO_TECNICO.md).

## Experiment 21 · Continuous memory

The historical dialogue memory branch recorded **384/384** queries over new observations, **6/6** constructions taught through dialogue, **175/175** queries after paraphrase teaching, and **173/173** adversarial checks. Persistence and restoration were evaluated.

**Archived regression suite:** 38 tests.

**Primary files:** `experiments/21-memoria-continua/results/summary.json`, `paraphrase_summary.json`, `adversarial_summary.json`, original sessions, [technical report](../experiments/21-memoria-continua/RELATORIO_TECNICO.md).

**Causal qualification from the historical audit:** some factual retrieval here relied partly on external indexing, not exclusively on physical ray propagation. Direct intervention evidence for operational marks and ports comes more specifically from Experiments 23–24.

## Experiment 23 · Functional surface marks

Confirmatory study: **5 binary-world families**, **12 seeds**, **60 instances**, **2,880 experiences** and **960 held-out queries**. With learned degree-≤2 algebraic marks, results were **960/960 correct predictions** and **962/962 targets achieved**.

Recorded interventions and controls:

- Blocking pulses removed **240/240** results.
- Removing active marks changed **651/651** outputs.
- Removing inactive marks left **240/240** outputs unchanged.
- A separate active-selection comparison reached **3,200/3,200** versus **2,897/3,200** with random selection at equal budget.
- Three errors per word were corrected in **960/960** observed consequences.
- Random functions outside the learned family produced **320 abstentions**, rather than unwarranted extrapolations.

**Archived regression suite:** 13 tests.

**Primary files:** `experiments/23-faces-funcionais/results/confirmatory.json`, `causal_ablations.json`, `active_design.json`, `adversarial.json`, [original scientific report](../experiments/23-faces-funcionais/RELATORIO_CIENTIFICO.md).

## Experiment 24 · Integrated learning, intervention and revision

In **48 instances**, each condition received **22 experiences per instance** (equal budget). Information-gain selection identified **480/480** predictions; random experience selection identified **328/480**, abstaining on 152. Successful plans were **1,034/1,034** versus **942/1,034**; signal targets **576/576** versus **559/576**.

A simulated physical action loop linked planning, action, observation, and updating within one experimental memory. The adversarial run registered an initial failure for third-order functions, followed by additional experiences and **2/2** correct remaining queries per seed. Removing a port actually used by a prediction changed its result; restoring the port restored it. Contradictory observations with identical inputs produced abstentions.

**Archived regression suite:** 13 tests.

**Primary files:** `experiments/24-ciclo-integrado/results/integrated.json`, `adversarial.json`, `scale.json`, [original report](../experiments/24-ciclo-integrado/RELATORIO.md).

## Shared relational meshes

Under canonical identity and compatible context, **600/600** synthetic classifications were correct: **313** positive cross-mesh compositions and **287** negatives. Removing context constraints caused **126** false positives; conflating labels caused **110** false positives.

A parameterized storage model estimated **21.99%** savings from shared identities; **this is not a measured Python RAM benchmark**. In the 12-diamond example, factorized provenance represented **4,096** potential paths with **108 DAG nodes**, examining **48** relational incidences rather than **16,380** in explicit expansion. Factorized queries were checked against independent enumeration on **250 random graphs**.

**Archived regression suite:** 11 tests.

**Primary files:** [`results.json`](../experiments/malhas-compartilhadas/results.json), [`case_predictions.jsonl`](../experiments/malhas-compartilhadas/case_predictions.jsonl), [`test_experiment.py`](../experiments/malhas-compartilhadas/test_experiment.py), [original report](../experiments/malhas-compartilhadas/RELATORIO.md).

## Evidence boundaries and repeatability

The program uses deliberately controlled worlds: hidden target regularities, separated training and evaluation, explicit baselines, interventions on active structures, adversarial or abstention cases, saved memory, and provenance checks. The **linguistic experiments use taught grammatical structures**, GF(2) is a selected experimental family, and the relational-mesh work verifies formal properties over supplied structures.

These findings support the **specified properties under their stated protocols**; they are not measurements of unrestricted natural-language understanding or all-purpose autonomy. The [Morphons AI web app](https://morphons-ai.vercel.app/) is maintained separately from these historical evaluation snapshots.

## Run the verification

From the repository root:

~~~bash
python scripts/verify_results.py
python scripts/verify_source_hashes.py
python scripts/test_all.py --no-save
~~~

The preserved [November 10, 2026 retest](../reproducibility/retest_2026-11-10.json) reports **115/115 tests passed**, comprising 8 + 14 + 18 + 38 + 13 + 13 + 11. The [GitHub Actions workflow](../.github/workflows/tests.yml) runs source-integrity, result verification and regression tests.

See [Reproducibility](REPRODUCIBILITY.md), [Provenance](PROVENANCE.md), and the [primary Zenodo paper](https://doi.org/10.5281/zenodo.24094723).
