# Architecture · NEXO

**English** | [Português (Brasil)](ARQUITETURA.md) · [Research overview](../README.md) · [Results](RESULTS.md)

NEXO studies **executable relational memory**: the interaction of representation, persistence, activation, inference, and learned functional organizations. The term *Morphon* identifies a persistent unit capable of receiving signals and maintaining modifiable relational structures.

## 1. The Morphon

The architecture separates a stable operational contract from an editable organization:

- **Invariant core:** three signaling paths/states, **−1, 0, +1**. The architecture does not need to learn new instructions *inside* this core.
- **Modifiable surfaces:** faces, fragments, marks, typed ports, references and configurations can be created, changed, connected and reused.
- **Activation by rays:** one incoming ray is sufficient to activate a unit. Additional incidences can increase contextual or physical support; they do **not** automatically count as independent proof.
- **Internal history and provenance:** observations, contexts, origins and revision records can be part of persistent organizations rather than only an external log.
- **Genesis Morphons:** an initial organized set that supplies elementary operations to create, replicate, change and remove Morphons and their variable parts. The research does **not** posit a system starting without any operational units.

The core's stability and the mutability of the unit's surfaces are compatible. **Self-organization can modify the variable organization of a Morphon**; a narrow restriction against a unit writing to itself appears in Experiment 24 as a specific laboratory contract and must not be generalized to every future implementation.

## 2. From observations to locally organized memory

A conceptual learning cycle:

1. An observation arrives with fragments and context.
2. Existing fragments are identified, or new ones are established.
3. Related Morphons receive local activation and contextual support.
4. Repeated configurations can motivate the creation, replication or promotion of more durable organizations.
5. These organizations may participate in conditional emission, prediction, action and later revision.

A persistent Morphon remains modifiable. An experimental implementation may also use transient units and pruning. The distinction between transient and persistent is about longevity, not immutability of faces and ports.

## 3. Activation is not certification

Let `R_i` denote rays incident on unit `i` in a pulse. Let `P_i^+` and `P_i^-` be its positive and negative requirements, and `B^+` / `B^-` the currently supported conditions. In the archived formalization:

\[
a_i=\mathbf{1}\{|R_i|\ge1\},
\qquad
c_i=\mathbf{1}\{P_i^+\subseteq B^+\}
    \mathbf{1}\{P_i^-\subseteq B^-\}
    \mathbf{1}\{|P_i^+|+|P_i^-|>0\}.
\]

The first expression models **activation on incidence**. The second models **certification of prerequisites** before emission. This is the basis for investigating negative conditions, conjunctions and multi-hop composition without mistaking the number of traversed graph paths for the number of independent emitters.

For a relational memory at time `t`, one useful description is

\[
\mathcal{M}_t=(V_t,E_t,\mathcal{F}_t,\mathcal{H}_t),
\]

where `V` are Morphons, `E` their relational ports, `\mathcal F` surface marks/fragments and `\mathcal H` history and revision links. It is a model of a mutable structure, not a claim that all experiments use the same physical representation.

## 4. Locality, context and identity

A Morphon identity can participate in more than one relational mesh. Cross-mesh composition requires **compatible identity, relation types, and context**; matching human-readable labels alone is insufficient.

For `m` mesh participations, `u` unique identities, unit cost `b`, reference cost `q` and duplicate-bridge cost `c`, a formal sharing model gives:

\[
\Delta = (m-u)(b+c)-mq.
\]

With `m=3600`, `u=2561`, `b=64` bytes, `q=8` bytes and `c=16` bytes, the calculated difference is **54,320 bytes (21.99%)**. This is a **parameterized accounting model**, not a measured reduction in Python process RAM.

In the mesh experiment, factorized proofs use shared DAG substructures so that one logical dependency need not be repeated in every possible derivation path. [Inspect the mesh results](RESULTS.md#shared-relational-meshes).

## 5. Induction, functional organization and revision

The archive explores complementary mechanisms:

- **Structural regularities:** forming and promoting organizations from observed configurations, including MEET/JOIN-style composition.
- **Temporal predictive structure:** comparing histories by the future observations and actions accessible from them.
- **Functional surfaces:** learning world-specific patterns as marks involved in computation; controlled interventions on these marks test causal dependence.
- **Action and feedback:** choosing experiments or actions, observing outcomes and revising functional memory.
- **Provenance and counterexamples:** distinguishing supporting evidence, contradictions, contextual exceptions and multiple derivations.

For example, an MDL-inspired promotion criterion for a repeated structural pattern `P` is

\[
\Delta(P)=n[(m-v)b-q]-c(P).
\]

Here `n` is the number of independent empirical roots, `m` pattern length, `v` variable positions, `b` symbol cost, `q` reference cost and `c(P)` pattern overhead. Positive `\Delta(P)` denotes modeled description savings under **the chosen cost model**, not a universal statistical guarantee.

Some experiments select a **GF(2)** function family to isolate learned coefficients and relational patterns. The code still implements general algebraic procedures and planning mechanisms; the worlds' specific functional regularities are obtained from training experiences. The distinction between implemented operators and acquired content is tracked in [Results](RESULTS.md).

## 6. Experimental lineage

| Experiment | Mechanism studied |
| :-- | :-- |
| [08](../experiments/08-aprendizagem-esferas/) | Creating, promoting and forgetting learned structures |
| [14](../experiments/14-morfon-integrado/) | Integrated Morphon substrate, context, ordering, persistence and pruning |
| [17](../experiments/17-raciocinio-contextual/) | Grounded references, contextual composition, learned binary transitions |
| [21](../experiments/21-memoria-continua/) | Persistent dialogue memory, incremental teaching, revisions |
| [23](../experiments/23-faces-funcionais/) | Functional surfaces, mark interventions, active investigation |
| [24](../experiments/24-ciclo-integrado/) | Experience → hypothesis → prediction → action → feedback → revision |
| [Shared meshes](../experiments/malhas-compartilhadas/) | Canonical identity, contextual safety and proof factorization |

These are **distinct research branches**. They should not be collapsed into one claimed integrated implementation simply because they share terminology.

**Reference paper:** [Rosa (2026), NEXO](https://doi.org/10.5281/zenodo.24094723). · [Experiment directory](EXPERIMENTS.md) · [Live related demo](https://morphons-ai.vercel.app/)
