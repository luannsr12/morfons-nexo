# A research guide to NEXO

**English** | [Português (Brasil)](GUIA_DA_PESQUISA.md) · [Main overview](../README.md) · [Live Morphons AI](https://morphons-ai.vercel.app/)

## The question behind the research

When a machine observes an event, it can store a record of what happened. But **could that same experience change the structures through which the machine later computes?** This is the motivating question behind NEXO.

Conventional storage and computation are often discussed as separate activities: data sits somewhere, and a program processes it. NEXO investigates a memory whose **relational organization itself participates in processing**. The purpose is not simply to retrieve a similar old answer; it is to find reusable relations, compose them in new contexts, and revise them when consequences contradict expectations.

The associated model proposal is called **LIM — Large Interaction Memory**.

## A concrete intuition

Imagine an observer encountering a small system: a switch, a lamp and an environmental condition. Over several experiences, it notices that toggling the switch sometimes turns the lamp on, sometimes not. It records **what was present, what changed, and under which conditions**.

A memory that only stores episodes can answer "What happened last time?" A relational, functional memory could instead represent the learned dependencies and test a new combination: "If this condition is absent but the switch is pressed, what follows?" Later observations might reveal an exception, requiring **revision rather than an ever-growing list of identical responses**.

This is an *illustrative analogy*, not a claim that the archived experiments used this particular lamp setup. The experiments operationalize components of the idea with controlled worlds, measured outcomes and interventions.

## The basic vocabulary

| Concept | Plain-language description |
| :-- | :-- |
| **Morphon (Mórfon)** | A persistent unit whose stable signaling core operates through changeable surfaces, marks and relational connections |
| **Genesis Morphons** | Initially organized units providing elementary operations for creating, copying, modifying and removing variable organizations |
| **Ray** | A signal incident on a Morphon; one ray is enough to activate it |
| **Face / fragment** | Modifiable sites where interaction traces, data and functional arrangements can be represented |
| **Port** | A typed relation through which requirements, contexts, inhibition or consequences connect |
| **Relational mesh** | A network of Morphon identities and relationships, potentially sharing identities across contexts |
| **Provenance** | A trace of which observations, rules and premises support a result |
| **Functional memory** | Memory organization that takes part in operations, not merely information retrieval |

The key architectural choice is to distinguish the **invariant operational core** (−1, 0, +1) from what changes as learning proceeds: **faces, ports, fragments, marks and configurations**.

## Why experiments 23 and 24 matter

Earlier research investigates how structures can form, connect and persist. Experiments 23 and 24 ask a sharper question: **does the learned memory organization actually cause the output, or does a separate algorithm produce the answer while the memory only stores it?**

Experiment 23 intervenes on active/inactive marks and on pulses, recording changes or absence of changes in predicted outcomes. Experiment 24 connects a trained experimental memory to information-seeking, planning, simulated action, feedback and revision.

These are particularly meaningful experiments because they assess **causal dependence on specific internal structures**. The detailed controls, failures and conditions are published in [Results & controls](RESULTS.md).

## What has been demonstrated — and what remains a research direction?

**Recorded in the archive:** structural promotion and persistence; composition across new test worlds; taught binary transitions; dialogue-memory persistence; functional-mark interventions; feedback/revision loops; conservative cross-mesh composition and DAG-factorized provenance.

**Still being investigated as a broader goal:** general learning and reasoning across open-ended experiences and language using the same underlying architectural principles. The archived tasks are controlled laboratories, not a claim that every part of that goal has already been achieved.

The distinction matters because experiments 17 and 21 use taught linguistic patterns; experiments 23 and 24 employ general-purpose implementations of GF(2) operations and plan selection while learning specific target-world regularities. The research asks how much of computation can migrate into acquired relational organization over time.

## How to explore it yourself

Start with the [interactive Morphons AI demonstration](https://morphons-ai.vercel.app/) for a related evolving application. Then follow the source of specific findings:

1. Read the [main README](../README.md) for the high-level evidence map.
2. Open the [experiment directory](../experiments/README.md) to pick a research question.
3. Examine [results and controls](RESULTS.md), not just the headline number.
4. Use the [reproducibility guide](REPRODUCIBILITY.md) to run tests and check archived data.
5. Study the [technical architecture](ARCHITECTURE.md) and the [primary Zenodo publication](https://doi.org/10.5281/zenodo.24094723) when you want equations and formal definitions.

The application and this archive share a research lineage, but **they are separate codebases** and should not be interpreted as identical snapshots.

---

*Research by Luan Rosa · [ORCID 0009-0000-2754-7135](https://orcid.org/0009-0000-2754-7135)*
