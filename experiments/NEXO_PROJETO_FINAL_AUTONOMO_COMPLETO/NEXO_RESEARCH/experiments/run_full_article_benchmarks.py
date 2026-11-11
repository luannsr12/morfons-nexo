"""
EXECUÇÃO INTEGRADA DAS 7 FASES + BENCHMARKS DO ARTIGO SEM ORÁCULO EXTERNO
=========================================================================
Roda 100% sobre a `AutonomousMorphMemory` (`src/nexo_autonomous_engine.py`),
onde o Python atua exclusivamente injetando pulsos de energia nos 8 Gênesis (`0..7`).
"""

import os
import sys
import json
import time
import math
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from nexo_autonomous_engine import (
    AutonomousMorphMemory, KIND_FRAGMENT, KIND_FUNCTION,
    PORT_PREMISE_POS, PORT_PREMISE_NEG, PORT_CONSEQUENCE
)

def compute_roc_auc(pos_scores, neg_scores):
    wins = 0.0
    total = float(len(pos_scores) * len(neg_scores))
    if total == 0:
        return 0.0
    for ps in pos_scores:
        for ns in neg_scores:
            if ps > ns:
                wins += 1.0
            elif ps == ns:
                wins += 0.5
    return round(wins / total, 4)

def run_complete_autonomous_validation():
    mem = AutonomousMorphMemory(max_nodes=20000, max_edges=80000, max_marks=80000)
    report = {}

    # =========================================================================
    # FASE 1: EXPERIÊNCIA, FRAGMENTAÇÃO SUB-SIMBÓLICA E MARCAS DE SUPERFÍCIE
    # =========================================================================
    rng = random.Random(42)
    surface_nodes = [mem.alloc_node(KIND_FRAGMENT, sym_code=1000 + i) for i in range(40)]
    true_pairs = set()
    coords_3d = {nid: [rng.uniform(-1, 1) for _ in range(3)] for nid in surface_nodes}

    # Hub global k=9000 que polui distâncias geométricas 3D mas é neutralizado por E^+(i,j)
    for nid in surface_nodes:
        mem.inscribe_surface_mark(nid, witness_id=9000, depth_inc=15)
        for d in range(3):
            coords_3d[nid][d] = 0.85 * coords_3d[nid][d] + 0.15 * 0.5

    for p_idx in range(20):
        u = surface_nodes[2 * p_idx]
        v = surface_nodes[(2 * p_idx + 1) % 40]
        true_pairs.add((min(u, v), max(u, v)))
        w_id = 100 + p_idx
        mem.inscribe_surface_mark(u, witness_id=w_id, depth_inc=8)
        mem.inscribe_surface_mark(v, witness_id=w_id, depth_inc=8)
        target = [rng.uniform(-1, 1) for _ in range(3)]
        for d in range(3):
            coords_3d[u][d] = 0.5 * coords_3d[u][d] + 0.5 * target[d]
            coords_3d[v][d] = 0.5 * coords_3d[v][d] + 0.5 * target[d]

    pos_e, neg_e, pos_ep, neg_ep, pos_3d, neg_3d = [], [], [], [], [], []
    for i_idx in range(len(surface_nodes)):
        for j_idx in range(i_idx + 1, len(surface_nodes)):
            u, v = surface_nodes[i_idx], surface_nodes[j_idx]
            ev = mem.compute_surface_affinity(u, v)
            epv = mem.compute_contrastive_residual_affinity(u, v)
            sim3 = -math.sqrt(sum((coords_3d[u][d] - coords_3d[v][d]) ** 2 for d in range(3)))
            if (min(u, v), max(u, v)) in true_pairs:
                pos_e.append(ev); pos_ep.append(epv); pos_3d.append(sim3)
            else:
                neg_e.append(ev); neg_ep.append(epv); neg_3d.append(sim3)

    # Teste de Fragmentação Sub-Simbólica Autônoma pelo G_FRAG (Nó 1)
    comp_frag_ids = mem._genesis_frag_inscribe("fogo+agua+turbina", prov_root=500)

    report["phase_1_fragmentation_and_surface"] = {
        "composite_stimulus_input": "fogo+agua+turbina",
        "autonomously_decomposed_fragment_symbols": [mem.get_symbol_str(fid) for fid in comp_frag_ids],
        "auc_surface_depth_E": compute_roc_auc(pos_e, neg_e),
        "auc_contrastive_residual_E_plus": compute_roc_auc(pos_ep, neg_ep),
        "auc_3d_centroid_geometry": compute_roc_auc(pos_3d, neg_3d)
    }

    # =========================================================================
    # FASES 2 & 3: AUTO-ORGANIZAÇÃO MDL, INDUÇÃO X->X (75/75) E ANTI-VAZAMENTO
    # =========================================================================
    for idx, name in enumerate(["Ana", "Bia", "Joao"], start=1):
        mem.pulse_energy({
            "pos_in": ["meu_nome_e"],
            "neg_in": [],
            "slot0": name,
            "consequence": "ola_entidade",
            "prov_root": idx
        })

    novel_hits = 0
    literal_hits = 0
    literal_mem = {"Ana": "Ana", "Bia": "Bia", "Joao": "Joao"}
    for i in range(75):
        ent_name = f"Pessoa_Inedita_{i}"
        q_res = mem.pulse_energy({"pos_in": ["meu_nome_e"], "neg_in": [], "slot0": ent_name})["result"]
        if "ola_entidade" in q_res["emitted_symbols"] and q_res["bound_entity_0"] == ent_name:
            novel_hits += 1
        if literal_mem.get(ent_name) == ent_name:
            literal_hits += 1

    # Teste de Correferência / Variáveis Acopladas (R(X, X) vs R(X, Y))
    for idx, ent in enumerate(["Acido_A", "Acido_B", "Acido_C"], start=20):
        mem.pulse_energy({
            "pos_in": ["reacao_auto_simetrica"],
            "neg_in": [],
            "slot0": ent,
            "slot1": ent,
            "consequence": "equilibrio_isotropico",
            "prov_root": idx
        })
    coupled_valid = mem.pulse_energy({"pos_in": ["reacao_auto_simetrica"], "slot0": "Acido_A", "slot1": "Acido_A"})["result"]
    coupled_cross = mem.pulse_energy({"pos_in": ["reacao_auto_simetrica"], "slot0": "Acido_A", "slot1": "Acido_B"})["result"]

    report["phases_2_3_induction_and_generalization"] = {
        "novel_identities_tested": 75,
        "nexo_autonomous_correct": novel_hits,
        "literal_baseline_correct": literal_hits,
        "coupled_vars_same_entity_certified": ("equilibrio_isotropico" in coupled_valid["emitted_symbols"]),
        "coupled_vars_cross_entity_blocked": (len(coupled_cross["emitted_symbols"]) == 0)
    }

    # =========================================================================
    # FASES 4 & 5: COMPOSIÇÃO DE 3 SALTOS (T_C o T_B o T_A) E REVISÃO CAUSAL
    # =========================================================================
    # Salto 1: fogo (sem litio) -> aquece
    for r_id in (31, 32, 33):
        mem.pulse_energy({"pos_in": ["fogo"], "neg_in": ["litio"], "consequence": "aquece", "prov_root": r_id})
    # Salto 2: aquece + agua -> vapor
    for r_id in (34, 35, 36):
        mem.pulse_energy({"pos_in": ["aquece", "agua"], "neg_in": [], "consequence": "vapor", "prov_root": r_id})
    # Salto 3: vapor + turbina -> energia_eletrica
    for r_id in (37, 38, 39):
        mem.pulse_energy({"pos_in": ["vapor", "turbina"], "neg_in": [], "consequence": "energia_eletrica", "prov_root": r_id})

    # Contraexemplo empírico: fogo + litio -> None (G_REVISE especializa exigindo ausência de litio)
    rev_info = mem.pulse_energy({"pos_in": ["fogo", "litio"], "neg_in": [], "consequence": None, "prov_root": 40})["result"]

    # Execução composta usando o estímulo composto bruto "fogo+agua+turbina" (decomposto por G_FRAG!)
    chain_ok = mem.pulse_energy({"pos_in": ["fogo+agua+turbina"], "neg_in": ["litio"]})["result"]
    chain_inhibited = mem.pulse_energy({"pos_in": ["fogo+agua+turbina", "litio"], "neg_in": []})["result"]

    report["phases_4_5_multihop_composition_and_revision"] = {
        "revised_morphon_id": rev_info["revised_function_id"],
        "three_hop_emitted_chain": chain_ok["emitted_symbols"],
        "three_hop_certified_morphons": chain_ok["certified_morphons"],
        "three_hop_provenance_roots_count": len(chain_ok["provenance_roots"]),
        "inhibited_by_lithium_emitted": chain_inhibited["emitted_symbols"],
        "baseline_rays_traversed": chain_ok["rays_traversed"],
        "baseline_nodes_touched": chain_ok["nodes_touched"]
    }

    # =========================================================================
    # FASE 6: ESTADOS PREDITIVOS ENDÓGENOS (SEM ORÁCULO) E INVESTIGAÇÃO ATIVA
    # =========================================================================
    # Ambiente oculto de 3 estados (0, 1, 2) gerando apenas observações de transição empíricas
    def _env_step(st, act):
        if st == 0:
            return (0, 1) if act == 1 else (0, 0)
        elif st == 1:
            return (1, 2) if act == 1 else (0, 0)
        else:
            return (1, 0)

    empirical_transitions = []
    base_histories = [(), (0,), (1,), (0, 0), (0, 1), (1, 0), (1, 1), (1, 1, 1)]
    for h in base_histories:
        # Para que cada história base acumule na Face seu espectro de 1 e 2 passos a partir das transições vividas
        for a1 in (0, 1):
            st = 0
            for ha in h:
                _, st = _env_step(st, ha)
            o1, st_mid = _env_step(st, a1)
            h_mid = h + (a1,)
            empirical_transitions.append((h, a1, o1, h_mid))
            for a2 in (0, 1):
                o2, _ = _env_step(st_mid, a2)
                empirical_transitions.append((h_mid, a2, o2, h_mid + (a2,)))

    pred_states_res = mem.pulse_temporal_transition_endogenous(empirical_transitions)

    # Investigação Ativa: quando apenas "vapor" está presente (sem "turbina"), o Mórfon aponta a porta faltante "turbina"
    partial_probe = mem.pulse_energy({"pos_in": ["vapor"], "neg_in": []})["result"]
    missing_port_syms = []
    for inv in partial_probe["active_investigations"]:
        for mp in inv.get("missing_positive_ports", []):
            missing_port_syms.append(mem.get_symbol_str(mp))

    report["phase_6_endogenous_predictive_states_and_investigation"] = {
        "predictive_states_discovery": pred_states_res,
        "partial_stimulus_probe": "vapor",
        "autonomously_identified_missing_discriminant_ports": sorted(list(set(missing_port_syms)))
    }

    # =========================================================================
    # FASE 7: ESCALABILIDADE O(GRAU LOCAL) (+10.000 MÓRFONS) E AUDITORIA CAUSAL
    # =========================================================================
    # Rota Factual Versionada (40 fatos revisados)
    f_schema = mem.get_fragment_id("capital_ou_atributo")
    f_v_old = mem.get_fragment_id("versao_v1_historica")
    f_v_cur = mem.get_fragment_id("versao_v2_vigente")

    fact_keys, vals_old, vals_cur = [], [], []
    for k_i in range(40):
        fk = mem.get_fragment_id(f"entidade_factual_{k_i}")
        vo = mem.get_fragment_id(f"valor_obsoleto_{k_i}")
        vc = mem.get_fragment_id(f"valor_vigente_{k_i}")
        fact_keys.append(fk); vals_old.append(vo); vals_cur.append(vc)
        old_fn = mem.inscribe_or_revise_fact(f_schema, fk, f_v_old, vo, prov_root_id=600 + k_i)
        mem.inscribe_or_revise_fact(f_schema, fk, f_v_cur, vc, prov_root_id=700 + k_i, previous_fact_node=old_fn)

    # Alocar +10.000 Mórfons desconectados na NodeArena para provar invariância O(grau local)
    for d_idx in range(10000):
        mem.alloc_node(KIND_FUNCTION, sym_code=90000 + d_idx)

    chain_after_10k = mem.pulse_energy({"pos_in": ["fogo+agua+turbina"], "neg_in": ["litio"]})["result"]

    fact_hits_normal = 0
    fact_obsolete_leaks = 0
    fact_hits_no_energy = 0
    for k_i in range(40):
        r_ok = mem.propagate_localized_rays([f_schema, fact_keys[k_i], f_v_cur], [], energy_quanta=100)
        if vals_cur[k_i] in r_ok["emitted_fragments"]:
            fact_hits_normal += 1
        if vals_old[k_i] in r_ok["emitted_fragments"]:
            fact_obsolete_leaks += 1
        r_zero = mem.propagate_localized_rays([f_schema, fact_keys[k_i], f_v_cur], [], energy_quanta=0)
        if vals_cur[k_i] in r_zero["emitted_fragments"]:
            fact_hits_no_energy += 1

    report["phase_7_scalability_10k_and_causal_audit"] = {
        "disconnected_morphons_added": 10000,
        "total_allocated_nodes_in_arena": mem.node_count,
        "rays_traversed_before_10k": chain_ok["rays_traversed"],
        "rays_traversed_after_10k": chain_after_10k["rays_traversed"],
        "nodes_touched_before_10k": chain_ok["nodes_touched"],
        "nodes_touched_after_10k": chain_after_10k["nodes_touched"],
        "strict_o_local_degree_invariance_verified": (
            chain_ok["rays_traversed"] == chain_after_10k["rays_traversed"] and
            chain_ok["nodes_touched"] == chain_after_10k["nodes_touched"]
        ),
        "factual_routing_40_queries": {
            "normal_with_energy": fact_hits_normal,
            "obsolete_version_leaks": fact_obsolete_leaks,
            "ablated_zero_energy": fact_hits_no_energy
        },
        "genesis_firings_telemetry": mem.total_genesis_firings,
        "binary_arena_snapshot": mem.export_binary_snapshot_hex()
    }

    mem.close()
    out_p = os.path.join(os.path.dirname(__file__), "../results/raw/full_article_benchmarks.json")
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return report

if __name__ == "__main__":
    res = run_complete_autonomous_validation()
    print("Validação Autônoma Concluída! Nós na Arena:", res["phase_7_scalability_10k_and_causal_audit"]["total_allocated_nodes_in_arena"])
    print("Raios antes/depois de +10.000 nós:", res["phase_7_scalability_10k_and_causal_audit"]["rays_traversed_before_10k"], "->", res["phase_7_scalability_10k_and_causal_audit"]["rays_traversed_after_10k"])
    print("Cadeia de 3 saltos emitida:", res["phases_4_5_multihop_composition_and_revision"]["three_hop_emitted_chain"])
    print("Estados preditivos sem oráculo:", res["phase_6_endogenous_predictive_states_and_investigation"]["predictive_states_discovery"])
