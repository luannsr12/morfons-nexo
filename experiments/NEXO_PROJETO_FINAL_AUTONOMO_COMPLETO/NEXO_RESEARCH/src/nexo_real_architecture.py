"""
NEXO AUTONOMOUS BINARY ENGINE (V4.0) — MEMÓRIA RELACIONAL AUTO-ORGANIZÁVEL
==========================================================================
Base Teórica: Rosa, L. (2026). NEXO: Arquitetura de memória relacional executável.
DOI: https://doi.org/10.5281/zenodo.24094723

PRINCÍPIOS ESTRITOS DESTA IMPLEMENTAÇÃO:
1. EXECUÇÃO EM BINÁRIO NA MEMÓRIA FÍSICA (`mmap` + `ctypes.Structure`):
   - `NodeArena` (`MorphonNode`, 64 bytes exatos, alinhado a 1 linha de cache L1).
   - `EdgePortArena` (`PortEdge`, 32 bytes exatos, listas ligadas intrusivas).
   - `SurfaceFaceArena` (`SurfaceFaceMark`, 32 bytes exatos, fragmentos, espectros e proveniência).
2. ZERO ORÁCULO EXTERNO / PYTHON APENAS INJETA ENERGIA NOS 8 GÊNESIS (`IDs 0..7`):
   - `G_INS (0)`: Inscrição física de faces, marcas e diferenças históricas Δ_t.
   - `G_FRAG (1)`: Fragmentação Contrastiva autônoma por resíduos E^+(i,j) e decomposição sub-simbólica.
   - `G_MEET (2)`: Encontros locais por caminhos de comprimento 2 (E_1 - p - E_2) guiados por Espectro Local Λ_i.
   - `G_JOIN (3)`: Antiunificação posicional, verificação fatorial |B_P| = |D_0|*|D_1| e fusão de estados preditivos.
   - `G_POL (4)`: Sinais polares {-1, 0, +1}, reticulado de Belnap e Transformada de Möbius Epistêmica Parcial.
   - `G_GATE (5)`: Certificação estrita de portas positivas e negativas (Equação 16).
   - `G_PROMOTE (6)`: Promoção conservativa autônoma por Custo Mínimo de Descrição (MDL, Teorema 5.4).
   - `G_REVISE (7)`: Especialização sob contraexemplo, inibição de versão obsoleta e Investigação Ativa.
3. ZERO VARREDURA GLOBAL O(N) / ZERO EXPLOSÃO COMBINATÓRIA:
   - Toda propagação, descoberta de interseção, composição e revisão opera exclusivamente sobre as listas
     ligadas intrusivas das portas ativas em complexidade O(grau local).
"""

import ctypes
import mmap
import math
import time
import struct
import gc
from typing import List, Dict, Tuple, Set, Optional, Any

# Categorias de Unidades na NodeArena (kind)
KIND_EMPTY        = 0
KIND_GENESIS      = 1 # Unidades fundamentais 0..7 (G_INS..G_REVISE)
KIND_FRAGMENT     = 2 # Fragmento emergente inscrito na memória (com payload binário na Face)
KIND_EPISODE      = 3 # Ocorrência episódica empírica
KIND_INTERFACE    = 4 # Interface por testemunhos locais I_12 / Coeficiente de Möbius d_S
KIND_FUNCTION     = 5 # Organização funcional promovida por MDL (Δ(P) > 0)
KIND_PRED_STATE   = 6 # Estado preditivo induzido endogenamente por espectro temporal Σ_D(u)
KIND_FACT_NODE    = 7 # Unidade factual versionada certificada exclusivamente por portas e raios
KIND_INVESTIGATOR = 8 # Unidade de investigação ativa gerada sob desacordo epistêmico {0,1}

# Leis Operacionais Estáveis dos 8 Gênesis (core_law)
LAW_NONE    = 0
LAW_INS     = 1 # G_INS (ID 0): Inscrição de marcas e faces
LAW_FRAG    = 2 # G_FRAG (ID 1): Fragmentação contrastiva por resíduos E^+(i,j)
LAW_MEET    = 3 # G_MEET (ID 2): Encontro local por caminhos de comprimento 2 + Espectro Λ_i
LAW_JOIN    = 4 # G_JOIN (ID 3): Antiunificação e fusão de equivalência preditiva
LAW_POL     = 5 # G_POL (ID 4): Produto polar {-1,0,+1} e Möbius sobre Belnap
LAW_GATE    = 6 # G_GATE (ID 5): Certificação estrita de portas (Equação 16)
LAW_PROMOTE = 7 # G_PROMOTE (ID 6): Promoção conservativa MDL (Δ(P) > 0)
LAW_REVISE  = 8 # G_REVISE (ID 7): Subsunção condicional e Investigação Ativa

# Papéis Estruturais das Portas na EdgePortArena (role)
PORT_PREMISE_POS     = 1 # Condição positiva exigida (P_i^{req+})
PORT_PREMISE_NEG     = 2 # Ausência/negação explicitamente observada exigida (P_i^{req-})
PORT_CONSEQUENCE     = 3 # Emissão de consequência (O_i, disjunta de premissa - Eq. 16)
PORT_VAR_SLOT        = 4 # Transporte de variável / correferência (X -> X ou [V0, V1])
PORT_VERSION_CTX     = 5 # Porta de versão / regime contextual
PORT_TRANSITION      = 6 # Porta temporal entre eventos consecutivos (e_{t-1} --a_t--> e_t)
PORT_SUBFRAGMENT     = 7 # Porta ligando estímulo composto aos sub-fragmentos emergentes
PORT_DISCRIMINANT    = 8 # Porta apontando para condição discriminante em investigação ativa

# Estados Polares e Epistêmicos (Reticulado Quaternário de Belnap)
POLAR_NEG     = -1
POLAR_NEUTRAL = 0
POLAR_POS     = 1

BELNAP_ABSENT   = 0 # ∅ (Não observado / Indeterminado por ausência)
BELNAP_FALSE    = 1 # {0} (Explicitamente refutado / Inibido)
BELNAP_TRUE     = 2 # {1} (Explicitamente certificado)
BELNAP_CONFLICT = 3 # {0,1} (Desacordo epistêmico entre funções concorrentes -> dispara Investigação)

# Tipos de Marcas na SurfaceFaceArena (witness_id ou flags de face)
MARK_WITNESS_PROV  = 1 # Raiz empírica do Semianel de Proveniência N[Z] e profundidade c_{ik}
MARK_RAW_PAYLOAD   = 2 # Bytes binários do fragmento (até 8 bytes inline por marca)
MARK_COUPLED_PAIR  = 3 # Par de bindings (slot0, slot1) observado na superfície
MARK_TEMP_SPECTRUM = 4 # Assinatura espectral de continuação temporal (ação, saída, próx_ação, próx_saída)
MARK_MOBIUS_COEFF  = 5 # Coeficiente de diferença polar de Möbius d_S

# Flags Operacionais Binárias do Mórfon
MFLAG_PERSISTENT    = 1 << 0
MFLAG_ABLATED       = 1 << 1
MFLAG_OBSOLETE      = 1 << 2
MFLAG_HAS_VARBIND   = 1 << 3
MFLAG_TRANSITIVE    = 1 << 4
MFLAG_COUPLED_VARS  = 1 << 5
MFLAG_FACTORED_VARS = 1 << 6
MFLAG_COMPOSITE_SYM = 1 << 7


class MorphonNode(ctypes.Structure):
    """
    Célula física de exatos 64 bytes na NodeArena (`mmap`).
    Cabe inteiramente em 1 linha de cache L1 de processadores x86_64 / ARM64.
    """
    _pack_ = 1
    _fields_ = [
        ("m_id", ctypes.c_uint32),              # 4B: Endereço físico na NodeArena
        ("kind", ctypes.c_uint8),               # 1B: Categoria do Mórfon
        ("core_law", ctypes.c_uint8),           # 1B: Lei do núcleo estável K
        ("q_polar", ctypes.c_int8),             # 1B: Sinal polar {-1, 0, +1}
        ("active", ctypes.c_uint8),             # 1B: Ativado por >= 1 raio: a_i(t) in {0,1}
        ("certified", ctypes.c_uint8),          # 1B: Portas integralmente certificadas: c_i(t) in {0,1}
        ("epistemic_val", ctypes.c_uint8),      # 1B: Valor no reticulado de Belnap {0,1,2,3}
        ("ray_support", ctypes.c_uint16),       # 2B: Sustentação contextual s_i(t) = |R_i(t)|
        ("req_pos_count", ctypes.c_uint16),     # 2B: Total de portas positivas exigidas
        ("req_neg_count", ctypes.c_uint16),     # 2B: Total de portas negativas exigidas
        ("cert_pos_hits", ctypes.c_uint16),     # 2B: Portas positivas atingidas no pulso atual
        ("cert_neg_hits", ctypes.c_uint16),     # 2B: Portas negativas atingidas no pulso atual
        ("version", ctypes.c_uint16),           # 2B: Versão / passo lógico
        ("flags", ctypes.c_uint16),             # 2B: Máscara de flags operacionais
        ("spectrum_sig", ctypes.c_uint32),      # 4B: Espectro Estrutural Local Λ_i (Teorema 1.8)
        ("first_out_edge", ctypes.c_int32),     # 4B: Cabeça da lista intrusiva de portas de saída
        ("first_in_edge", ctypes.c_int32),      # 4B: Cabeça da lista intrusiva de portas de entrada
        ("first_mark", ctypes.c_int32),         # 4B: Cabeça da lista intrusiva de marcas de Face
        ("superseded_by", ctypes.c_int32),      # 4B: Ponteiro para versão substituta (-1 se vigente)
        ("mdl_delta", ctypes.c_float),          # 4B: Economia líquida MDL Δ(P) (Teorema 5.4)
        ("bayes_log_bf", ctypes.c_float),       # 4B: Log-fator de Bayes / peso de evidência
        ("n_confirm", ctypes.c_uint16),         # 2B: Raízes independentes confirmadas
        ("n_contra", ctypes.c_uint16),          # 2B: Contraexemplos recebidos
        ("slot0_val", ctypes.c_uint16),         # 2B: Slot variável primário (V0)
        ("slot1_val", ctypes.c_uint16),         # 2B: Slot variável secundário (V1)
        ("energy_quanta", ctypes.c_uint32),     # 4B: Quanta de energia acumulados no nó -> Total = 64B!
    ]

assert ctypes.sizeof(MorphonNode) == 64, f"Tamanho inválido MorphonNode: {ctypes.sizeof(MorphonNode)}"


class PortEdge(ctypes.Structure):
    """Célula física de exatos 32 bytes na EdgePortArena (`mmap`)."""
    _pack_ = 1
    _fields_ = [
        ("edge_id", ctypes.c_uint32),           # 4B: Endereço físico na EdgePortArena
        ("src_id", ctypes.c_uint32),            # 4B: Mórfon de origem
        ("dst_id", ctypes.c_uint32),            # 4B: Mórfon de destino
        ("role", ctypes.c_uint8),               # 1B: Papel estrutural da porta
        ("var_pos_idx", ctypes.c_uint8),        # 1B: Índice de slot ou ação temporal
        ("ablated", ctypes.c_uint8),            # 1B: Flag de corte físico para auditoria causal
        ("weight_polarity", ctypes.c_int8),     # 1B: Polaridade da conexão {-1, 0, +1}
        ("next_out_edge", ctypes.c_int32),      # 4B: Próxima aresta de saída de src_id
        ("next_in_edge", ctypes.c_int32),       # 4B: Próxima aresta de entrada de dst_id
        ("coact_count", ctypes.c_uint32),       # 4B: Contagem de pulsos que atravessaram a porta
        ("prov_root_id", ctypes.c_uint32),      # 4B: Raiz empírica associada -> Total = 32B!
    ]

assert ctypes.sizeof(PortEdge) == 32, f"Tamanho inválido PortEdge: {ctypes.sizeof(PortEdge)}"


class SurfaceFaceMark(ctypes.Structure):
    """Célula física de exatos 32 bytes na SurfaceFaceArena (`mmap`)."""
    _pack_ = 1
    _fields_ = [
        ("mark_id", ctypes.c_uint32),           # 4B: Endereço físico na SurfaceFaceArena
        ("owner_id", ctypes.c_uint32),          # 4B: Mórfon dono desta face
        ("witness_id", ctypes.c_uint32),        # 4B: ID da testemunha/episódio k (ou tipo de marca)
        ("depth_count", ctypes.c_uint32),       # 4B: Profundidade de inscrição c_{ik}
        ("delta_payload", ctypes.c_uint64),     # 8B: Fragmento binário / Δ_t / espectro temporal
        ("step_time", ctypes.c_uint32),         # 4B: Passo temporal da inscrição
        ("next_mark", ctypes.c_int32),          # 4B: Próxima marca na face do Mórfon -> Total = 32B!
    ]

assert ctypes.sizeof(SurfaceFaceMark) == 32, f"Tamanho inválido SurfaceFaceMark: {ctypes.sizeof(SurfaceFaceMark)}"


class AutonomousMorphMemory:
    """
    Memória Relacional Executável Autônoma do NEXO (V4.0).
    O Python hospedeiro atua exclusivamente como fonte de energia (`pulse_energy`),
    alimentando os 8 Mórfons Gênesis (`0..7`) residentes na própria `NodeArena`.
    """
    def __init__(self, max_nodes: int = 20000, max_edges: int = 80000, max_marks: int = 80000):
        self.max_nodes = max_nodes
        self.max_edges = max_edges
        self.max_marks = max_marks

        self._node_mmap = mmap.mmap(-1, max_nodes * ctypes.sizeof(MorphonNode))
        self._edge_mmap = mmap.mmap(-1, max_edges * ctypes.sizeof(PortEdge))
        self._mark_mmap = mmap.mmap(-1, max_marks * ctypes.sizeof(SurfaceFaceMark))

        self.nodes = (MorphonNode * max_nodes).from_buffer(self._node_mmap)
        self.edges = (PortEdge * max_edges).from_buffer(self._edge_mmap)
        self.marks = (SurfaceFaceMark * max_marks).from_buffer(self._mark_mmap)

        self.node_count = 0
        self.edge_count = 0
        self.mark_count = 0
        self.clock = 0
        self.ablation_suppress_all_rays = False

        # Índices de borda sensorial (mapeiam o sinal físico bruto para o endereço do fragmento na arena)
        self._payload_to_frag_node: Dict[int, int] = {}
        self._frag_node_to_str: Dict[int, str] = {}
        self._entity_str_to_code: Dict[str, int] = {}
        self._entity_code_to_str: Dict[int, str] = {}

        # Contadores marginais locais mantidos pelo Gênesis G_FRAG (ID 1) para Resíduo Contrastivo
        self._marginal_node_depth: Dict[int, float] = {}
        self._marginal_witness_depth: Dict[int, float] = {}
        self._grand_total_depth: float = 0.0

        # Ponteiro do último nó de episódio temporal para auto-conexão de transições sem oráculo
        self._last_temporal_episode_id: int = -1
        self._last_temporal_action_code: int = 0

        # Telemetria física auditável
        self.last_query_rays_traversed = 0
        self.last_query_nodes_touched = 0
        self.total_genesis_firings: Dict[str, int] = {
            "G_INS": 0, "G_FRAG": 0, "G_MEET": 0, "G_JOIN": 0,
            "G_POL": 0, "G_GATE": 0, "G_PROMOTE": 0, "G_REVISE": 0
        }
        self.execution_logs: List[str] = []

        self._bootstrap_8_genesis_morphons()

    def _bootstrap_8_genesis_morphons(self):
        """Aloca os 8 Mórfons Gênesis fundamentais nos endereços físicos 0..7 da NodeArena."""
        genesis_specs = [
            (0, LAW_INS,     "G_INS"),
            (1, LAW_FRAG,    "G_FRAG"),
            (2, LAW_MEET,    "G_MEET"),
            (3, LAW_JOIN,    "G_JOIN"),
            (4, LAW_POL,     "G_POL"),
            (5, LAW_GATE,    "G_GATE"),
            (6, LAW_PROMOTE, "G_PROMOTE"),
            (7, LAW_REVISE,  "G_REVISE"),
        ]
        for idx, law, name in genesis_specs:
            n = self.nodes[idx]
            ctypes.memset(ctypes.byref(n), 0, ctypes.sizeof(MorphonNode))
            n.m_id = idx
            n.kind = KIND_GENESIS
            n.core_law = law
            n.q_polar = POLAR_POS
            n.flags = MFLAG_PERSISTENT
            n.version = 1
            n.first_out_edge = -1
            n.first_in_edge = -1
            n.first_mark = -1
            n.superseded_by = -1
            n.energy_quanta = 1000
        self.node_count = 8
        # Conectar os Gênesis em cadeia operacional dentro da própria EdgePortArena
        for i in range(7):
            self._raw_connect_port(i, i + 1, PORT_CONSEQUENCE, prov_root=0)

    @staticmethod
    def _pack_str_to_uint64(s: str) -> int:
        """Converte uma string curta ou símbolo em payload binário de 64 bits (FNV-1a + prefixo ASCII)."""
        b = s.encode("utf-8")
        h = 14695981039346656037
        for byte in b:
            h ^= byte
            h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
        return h if h != 0 else 1

    def encode_entity(self, ent_name: Optional[str]) -> int:
        if not ent_name:
            return 0
        if ent_name not in self._entity_str_to_code:
            code = len(self._entity_str_to_code) + 1
            self._entity_str_to_code[ent_name] = code
            self._entity_code_to_str[code] = ent_name
        return self._entity_str_to_code[ent_name]

    def decode_entity(self, code: int) -> Optional[str]:
        return self._entity_code_to_str.get(code, None)

    def alloc_node(self, kind: int, core_law: int = LAW_GATE, sym_code: int = 0,
                   q_polar: int = POLAR_NEUTRAL, flags: int = 0) -> int:
        if self.node_count >= self.max_nodes:
            raise MemoryError("NodeArena física saturada.")
        idx = self.node_count
        self.node_count += 1
        n = self.nodes[idx]
        ctypes.memset(ctypes.byref(n), 0, ctypes.sizeof(MorphonNode))
        n.m_id = idx
        n.kind = kind
        n.core_law = core_law
        n.q_polar = q_polar
        n.flags = flags
        n.spectrum_sig = sym_code & 0xFFFFFFFF
        n.version = self.clock
        n.first_out_edge = -1
        n.first_in_edge = -1
        n.first_mark = -1
        n.superseded_by = -1
        return idx

    def _raw_connect_port(self, src_id: int, dst_id: int, role: int,
                          var_pos_idx: int = 0, weight_pol: int = 1, prov_root: int = 0) -> int:
        if self.edge_count >= self.max_edges:
            raise MemoryError("EdgePortArena física saturada.")
        e_idx = self.edge_count
        self.edge_count += 1
        e = self.edges[e_idx]
        e.edge_id = e_idx
        e.src_id = src_id
        e.dst_id = dst_id
        e.role = role
        e.var_pos_idx = var_pos_idx
        e.ablated = 0
        e.weight_polarity = weight_pol
        e.coact_count = 1
        e.prov_root_id = prov_root

        src_node = self.nodes[src_id]
        dst_node = self.nodes[dst_id]

        e.next_out_edge = src_node.first_out_edge
        src_node.first_out_edge = e_idx

        e.next_in_edge = dst_node.first_in_edge
        dst_node.first_in_edge = e_idx

        if role in (PORT_PREMISE_POS, PORT_VERSION_CTX):
            dst_node.req_pos_count += 1
        elif role == PORT_PREMISE_NEG:
            dst_node.req_neg_count += 1

        # Atualização O(1) do Espectro Estrutural Local Λ_i (Teorema 1.8)
        mix = ((role * 0x9E3779B9) ^ (src_node.spectrum_sig << 1) ^ (dst_node.req_pos_count << 8)) & 0xFFFFFFFF
        dst_node.spectrum_sig = (dst_node.spectrum_sig ^ mix) & 0xFFFFFFFF
        return e_idx

    def connect_port(self, src_id: int, dst_id: int, role: int,
                     var_pos_idx: int = 0, weight_pol: int = 1, prov_root: int = 0) -> int:
        self.nodes[0].energy_quanta += 1
        self.total_genesis_firings["G_INS"] += 1
        return self._raw_connect_port(src_id, dst_id, role, var_pos_idx, weight_pol, prov_root)

    def inscribe_surface_mark(self, owner_id: int, witness_id: int,
                              depth_inc: int = 1, delta_payload: int = 0) -> int:
        """G_INS (ID 0): Inscreve ou aprofunda uma marca na SurfaceFaceArena do Mórfon `owner_id`."""
        self.clock += 1
        self.total_genesis_firings["G_INS"] += 1
        owner = self.nodes[owner_id]
        cur_m = owner.first_mark
        while cur_m != -1:
            mk = self.marks[cur_m]
            if mk.witness_id == witness_id and mk.delta_payload == delta_payload:
                mk.depth_count += depth_inc
                if witness_id > 0 and delta_payload == 0:
                    self._marginal_node_depth[owner_id] = self._marginal_node_depth.get(owner_id, 0.0) + depth_inc
                    self._marginal_witness_depth[witness_id] = self._marginal_witness_depth.get(witness_id, 0.0) + depth_inc
                    self._grand_total_depth += depth_inc
                return cur_m
            cur_m = mk.next_mark

        if self.mark_count >= self.max_marks:
            raise MemoryError("SurfaceFaceArena física saturada.")
        m_idx = self.mark_count
        self.mark_count += 1
        mk = self.marks[m_idx]
        mk.mark_id = m_idx
        mk.owner_id = owner_id
        mk.witness_id = witness_id
        mk.depth_count = depth_inc
        mk.delta_payload = delta_payload
        mk.step_time = self.clock
        mk.next_mark = owner.first_mark
        owner.first_mark = m_idx

        if witness_id > 0 and delta_payload == 0:
            self._marginal_node_depth[owner_id] = self._marginal_node_depth.get(owner_id, 0.0) + depth_inc
            self._marginal_witness_depth[witness_id] = self._marginal_witness_depth.get(witness_id, 0.0) + depth_inc
            self._grand_total_depth += depth_inc
        return m_idx

    def _genesis_frag_inscribe(self, symbol_str: str, prov_root: int = 0) -> List[int]:
        """
        G_FRAG (ID 1): Recebe estímulo bruto na borda, inscreve o fragmento binário na Face
        e, se o estímulo contiver sub-estruturas compostas (ex.: 'fogo+agua' ou 'A_B'),
        decompõe autonomamente em sub-fragmentos conectados por PORT_SUBFRAGMENT!
        """
        self.total_genesis_firings["G_FRAG"] += 1
        payload = self._pack_str_to_uint64(symbol_str)
        if payload not in self._payload_to_frag_node:
            nid = self.alloc_node(KIND_FRAGMENT, core_law=LAW_FRAG, sym_code=payload & 0xFFFFFFFF, flags=MFLAG_PERSISTENT)
            self._payload_to_frag_node[payload] = nid
            self._frag_node_to_str[nid] = symbol_str
            # Inscreve os bytes brutos na Face do próprio fragmento
            self.inscribe_surface_mark(nid, witness_id=0, depth_inc=1, delta_payload=payload)
        else:
            nid = self._payload_to_frag_node[payload]

        if prov_root > 0:
            self.inscribe_surface_mark(nid, witness_id=prov_root, depth_inc=1, delta_payload=0)

        activated_frag_ids = [nid]
        # Se o estímulo bruto possui separadores estruturais ('+' ou '|'), G_FRAG fragmenta endogenamente
        for sep in ("+", "|"):
            if sep in symbol_str:
                self.nodes[nid].flags |= MFLAG_COMPOSITE_SYM
                parts = [p.strip() for p in symbol_str.split(sep) if p.strip()]
                for pt in parts:
                    sub_ids = self._genesis_frag_inscribe(pt, prov_root=prov_root)
                    for sid in sub_ids:
                        self._raw_connect_port(nid, sid, PORT_SUBFRAGMENT, prov_root=prov_root)
                        if sid not in activated_frag_ids:
                            activated_frag_ids.append(sid)
        return activated_frag_ids

    def get_fragment_id(self, symbol_str: str) -> int:
        return self._genesis_frag_inscribe(symbol_str, prov_root=0)[0]

    def get_symbol_str(self, frag_id: int) -> str:
        return self._frag_node_to_str.get(frag_id, f"NODE_{frag_id}")

    def get_provenance_roots(self, node_id: int) -> Set[int]:
        roots = set()
        cur = self.nodes[node_id].first_mark
        while cur != -1:
            mk = self.marks[cur]
            if mk.witness_id > 0 and mk.delta_payload == 0:
                roots.add(mk.witness_id)
            cur = mk.next_mark
        return roots

    def compute_surface_affinity(self, node_i: int, node_j: int) -> int:
        """Seção 4.2: Afinidade bruta por profundidade de marcas compartilhadas E(i,j)."""
        self.total_genesis_firings["G_FRAG"] += 1
        marks_i = {}
        cur = self.nodes[node_i].first_mark
        while cur != -1:
            mk = self.marks[cur]
            if mk.witness_id > 0 and mk.delta_payload == 0:
                marks_i[mk.witness_id] = mk.depth_count
            cur = mk.next_mark

        overlap = 0
        cur = self.nodes[node_j].first_mark
        while cur != -1:
            mk = self.marks[cur]
            if mk.witness_id in marks_i and mk.delta_payload == 0:
                overlap += min(marks_i[mk.witness_id], mk.depth_count)
            cur = mk.next_mark
        return overlap

    def compute_contrastive_residual_affinity(self, node_i: int, node_j: int,
                                              marginal_node_totals: Optional[Dict[int, float]] = None,
                                              marginal_witness_totals: Optional[Dict[int, float]] = None,
                                              grand_total: Optional[float] = None) -> float:
        """
        Seção 4.2: Excedente Contrastivo Residual E^+(i,j) = sum_k min(d_{ik}, d_{jk}),
        usando os contadores marginais mantidos autonomamente pelo Gênesis G_FRAG.
        """
        self.total_genesis_firings["G_FRAG"] += 1
        m_node = marginal_node_totals if marginal_node_totals is not None else self._marginal_node_depth
        m_wit = marginal_witness_totals if marginal_witness_totals is not None else self._marginal_witness_depth
        g_tot = grand_total if grand_total is not None else self._grand_total_depth
        if g_tot <= 0:
            return 0.0

        res_i = {}
        tot_i = m_node.get(node_i, 0.0)
        cur = self.nodes[node_i].first_mark
        while cur != -1:
            mk = self.marks[cur]
            if mk.witness_id > 0 and mk.delta_payload == 0:
                e_ik = (tot_i * m_wit.get(mk.witness_id, 0.0)) / g_tot
                d_ik = max(0.0, float(mk.depth_count) - e_ik)
                if d_ik > 0:
                    res_i[mk.witness_id] = d_ik
            cur = mk.next_mark

        tot_j = m_node.get(node_j, 0.0)
        e_plus = 0.0
        cur = self.nodes[node_j].first_mark
        while cur != -1:
            mk = self.marks[cur]
            if mk.witness_id in res_i and mk.delta_payload == 0:
                e_jk = (tot_j * m_wit.get(mk.witness_id, 0.0)) / g_tot
                d_jk = max(0.0, float(mk.depth_count) - e_jk)
                e_plus += min(res_i[mk.witness_id], d_jk)
            cur = mk.next_mark
        return e_plus

    def propagate_localized_rays(self, active_pos_fragments: List[int],
                                 active_neg_fragments: List[int],
                                 in_slot0: int = 0, in_slot1: int = 0,
                                 max_hops: int = 6,
                                 energy_quanta: int = 100) -> Dict[str, Any]:
        """
        G_GATE (5) + G_POL (4): Propagação física localizada O(grau local) nas arenas mmap.
        Nenhuma varredura global O(N) ocorre. Se `energy_quanta <= 0` ou `ablation_suppress_all_rays`,
        nenhum raio se move.
        """
        t0 = time.perf_counter()
        self.last_query_rays_traversed = 0
        touched_nodes: Set[int] = set()
        certified_nodes: List[int] = []
        emitted_consequences: List[int] = []
        active_provenance: Set[int] = set()
        emitted_by_premise_sig: Dict[Tuple[Tuple[int, ...], Tuple[int, ...]], Set[int]] = {}
        active_investigators: List[Dict[str, Any]] = []

        if self.ablation_suppress_all_rays or energy_quanta <= 0:
            return {
                "emitted_fragments": [],
                "certified_morphons": [],
                "provenance_roots": set(),
                "bound_slot0": in_slot0,
                "bound_slot1": in_slot1,
                "rays_traversed": 0,
                "nodes_touched": 0,
                "epistemic_conflict": False,
                "active_investigations": [],
                "latency_us": round((time.perf_counter() - t0) * 1e6, 2)
            }

        self.nodes[5].energy_quanta += energy_quanta
        self.total_genesis_firings["G_GATE"] += 1
        self.total_genesis_firings["G_POL"] += 1

        frontier_pos = list(active_pos_fragments)
        frontier_neg = list(active_neg_fragments)
        seen_pos_rays: Set[Tuple[int, int]] = set()
        seen_neg_rays: Set[Tuple[int, int]] = set()
        cur_slot0 = in_slot0
        cur_slot1 = in_slot1

        for _hop in range(max_hops):
            next_frontier_pos: List[int] = []

            # 1. Propagar raios positivos (e decomposição de sub-fragmentos se houver)
            for frag_id in frontier_pos:
                if self.nodes[frag_id].flags & MFLAG_ABLATED:
                    continue
                e_idx = self.nodes[frag_id].first_out_edge
                while e_idx != -1:
                    edge = self.edges[e_idx]
                    self.last_query_rays_traversed += 1
                    if not edge.ablated:
                        dst_id = edge.dst_id
                        dst = self.nodes[dst_id]
                        if edge.role == PORT_SUBFRAGMENT and dst_id not in frontier_pos:
                            next_frontier_pos.append(dst_id)
                        elif edge.role in (PORT_PREMISE_POS, PORT_VERSION_CTX, PORT_TRANSITION):
                            if not (dst.flags & (MFLAG_ABLATED | MFLAG_OBSOLETE)):
                                if dst_id not in touched_nodes:
                                    touched_nodes.add(dst_id)
                                    dst.active = 0
                                    dst.certified = 0
                                    dst.ray_support = 0
                                    dst.cert_pos_hits = 0
                                    dst.cert_neg_hits = 0
                                if (frag_id, dst_id) not in seen_pos_rays:
                                    seen_pos_rays.add((frag_id, dst_id))
                                    dst.active = 1
                                    dst.ray_support += 1
                                    dst.cert_pos_hits += 1
                    e_idx = edge.next_out_edge

            # 2. Propagar raios negativos/ausências explícitas
            for frag_id in frontier_neg:
                if self.nodes[frag_id].flags & MFLAG_ABLATED:
                    continue
                e_idx = self.nodes[frag_id].first_out_edge
                while e_idx != -1:
                    edge = self.edges[e_idx]
                    self.last_query_rays_traversed += 1
                    if not edge.ablated and edge.role == PORT_PREMISE_NEG:
                        dst_id = edge.dst_id
                        dst = self.nodes[dst_id]
                        if not (dst.flags & (MFLAG_ABLATED | MFLAG_OBSOLETE)):
                            if dst_id not in touched_nodes:
                                touched_nodes.add(dst_id)
                                dst.active = 0
                                dst.certified = 0
                                dst.ray_support = 0
                                dst.cert_pos_hits = 0
                                dst.cert_neg_hits = 0
                            if (frag_id, dst_id) not in seen_neg_rays:
                                seen_neg_rays.add((frag_id, dst_id))
                                dst.active = 1
                                dst.ray_support += 1
                                dst.cert_neg_hits += 1
                    e_idx = edge.next_out_edge

            frontier_neg = []

            # 3. Avaliar certificação estrita O(1) apenas nos nós tocados pelo pulso
            for tid in list(touched_nodes):
                nd = self.nodes[tid]
                if nd.certified == 1 or nd.kind not in (KIND_FUNCTION, KIND_FACT_NODE, KIND_PRED_STATE, KIND_INTERFACE):
                    continue
                if nd.n_contra >= nd.n_confirm and nd.n_contra > 0:
                    continue

                total_req = nd.req_pos_count + nd.req_neg_count
                if total_req > 0 and nd.cert_pos_hits == nd.req_pos_count and nd.cert_neg_hits == nd.req_neg_count:
                    # Verificação de acoplamento multivariável (Teorema 1.5)
                    if (nd.flags & MFLAG_COUPLED_VARS) and cur_slot0 > 0 and cur_slot1 > 0:
                        pair_code = ((cur_slot0 & 0xFFFF) << 16) | (cur_slot1 & 0xFFFF)
                        pair_found = False
                        mk_idx = nd.first_mark
                        while mk_idx != -1:
                            if self.marks[mk_idx].witness_id == 0 and self.marks[mk_idx].delta_payload == pair_code:
                                pair_found = True
                                break
                            mk_idx = self.marks[mk_idx].next_mark
                        if not pair_found:
                            continue

                    nd.certified = 1
                    certified_nodes.append(tid)
                    active_provenance |= self.get_provenance_roots(tid)

                    if nd.slot0_val != 0 and cur_slot0 == 0:
                        cur_slot0 = nd.slot0_val
                    if nd.slot1_val != 0 and (cur_slot1 == 0 or (nd.flags & MFLAG_TRANSITIVE)):
                        if (nd.flags & MFLAG_TRANSITIVE) and cur_slot0 == nd.slot0_val:
                            cur_slot0 = nd.slot1_val
                            cur_slot1 = nd.slot1_val
                        elif cur_slot1 == 0:
                            cur_slot1 = nd.slot1_val

                    pos_sig = []
                    neg_sig = []
                    in_e = nd.first_in_edge
                    while in_e != -1:
                        ie = self.edges[in_e]
                        if ie.role in (PORT_PREMISE_POS, PORT_VERSION_CTX):
                            pos_sig.append(ie.src_id)
                        elif ie.role == PORT_PREMISE_NEG:
                            neg_sig.append(ie.src_id)
                        in_e = ie.next_in_edge
                    sig_tuple = (tuple(sorted(pos_sig)), tuple(sorted(neg_sig)))

                    out_e = nd.first_out_edge
                    while out_e != -1:
                        oe = self.edges[out_e]
                        self.last_query_rays_traversed += 1
                        if not oe.ablated and oe.role == PORT_CONSEQUENCE:
                            conseq_id = oe.dst_id
                            emitted_by_premise_sig.setdefault(sig_tuple, set()).add(conseq_id)
                            if conseq_id not in emitted_consequences:
                                emitted_consequences.append(conseq_id)
                                next_frontier_pos.append(conseq_id)
                        out_e = oe.next_out_edge

                elif nd.active == 1 and nd.cert_pos_hits >= 1 and nd.cert_pos_hits + nd.cert_neg_hits < total_req:
                    # Nó parcialmente ativado: registra porta faltante como candidata discriminante para Investigação Ativa
                    missing_pos = []
                    missing_neg = []
                    in_e = nd.first_in_edge
                    while in_e != -1:
                        ie = self.edges[in_e]
                        if ie.role == PORT_PREMISE_POS and (ie.src_id, tid) not in seen_pos_rays:
                            missing_pos.append(ie.src_id)
                        elif ie.role == PORT_PREMISE_NEG and (ie.src_id, tid) not in seen_neg_rays:
                            missing_neg.append(ie.src_id)
                        in_e = ie.next_in_edge
                    if missing_pos or missing_neg:
                        active_investigators.append({
                            "candidate_morphon": tid,
                            "missing_positive_ports": missing_pos,
                            "missing_negative_ports": missing_neg
                        })

            if not next_frontier_pos:
                break
            frontier_pos = next_frontier_pos

        self.last_query_nodes_touched = len(touched_nodes)
        conflict = any(len(outs) > 1 for outs in emitted_by_premise_sig.values())

        # Se houve conflito epistêmico {0,1} (Belnap), G_REVISE cria/ativa um Mórfon Investigador na arena
        if conflict:
            self.total_genesis_firings["G_REVISE"] += 1
            inv_id = self.alloc_node(KIND_INVESTIGATOR, core_law=LAW_REVISE, q_polar=POLAR_NEUTRAL)
            self.nodes[inv_id].epistemic_val = BELNAP_CONFLICT
            active_investigators.append({
                "investigator_morphon_id": inv_id,
                "status": "BELNAP_CONFLICT_DETECTED",
                "competing_outputs": [list(s) for s in emitted_by_premise_sig.values() if len(s) > 1]
            })

        # Reset O(nós tocados)
        for tid in touched_nodes:
            self.nodes[tid].active = 0
            self.nodes[tid].certified = 0
            self.nodes[tid].ray_support = 0
            self.nodes[tid].cert_pos_hits = 0
            self.nodes[tid].cert_neg_hits = 0

        return {
            "emitted_fragments": emitted_consequences,
            "certified_morphons": certified_nodes,
            "provenance_roots": active_provenance,
            "bound_slot0": cur_slot0,
            "bound_slot1": cur_slot1,
            "rays_traversed": self.last_query_rays_traversed,
            "nodes_touched": self.last_query_nodes_touched,
            "epistemic_conflict": conflict,
            "active_investigations": active_investigators,
            "latency_us": round((time.perf_counter() - t0) * 1e6, 2)
        }

    def ingest_episode_and_meet_locally(self, pos_frag_ids: List[int], neg_frag_ids: List[int],
                                        conseq_frag_id: Optional[int], prov_root_id: int,
                                        slot0: int = 0, slot1: int = 0,
                                        b_bits: int = 8, q_bits: int = 4, c_cost: int = 10) -> Dict[str, Any]:
        """
        G_INS (0) + G_MEET (2) + G_JOIN (3) + G_PROMOTE (6) + G_REVISE (7):
        Inscrição episódica e auto-organização funcional 100% local via caminhos de comprimento 2.
        """
        t0 = time.perf_counter()
        self.total_genesis_firings["G_INS"] += 1
        self.total_genesis_firings["G_MEET"] += 1

        ep_id = self.alloc_node(
            KIND_EPISODE, core_law=LAW_NONE,
            q_polar=POLAR_POS if conseq_frag_id is not None else POLAR_NEG
        )
        ep_node = self.nodes[ep_id]
        ep_node.slot0_val = slot0
        ep_node.slot1_val = slot1
        ep_node.epistemic_val = BELNAP_TRUE if conseq_frag_id is not None else BELNAP_FALSE
        self.inscribe_surface_mark(ep_id, witness_id=prov_root_id)

        for pf in pos_frag_ids:
            self.connect_port(pf, ep_id, PORT_PREMISE_POS, prov_root=prov_root_id)
            self.inscribe_surface_mark(pf, witness_id=prov_root_id)
        for nf in neg_frag_ids:
            self.connect_port(nf, ep_id, PORT_PREMISE_NEG, prov_root=prov_root_id)
        if conseq_frag_id is not None:
            self.connect_port(ep_id, conseq_frag_id, PORT_CONSEQUENCE, prov_root=prov_root_id)
            self.inscribe_surface_mark(conseq_frag_id, witness_id=prov_root_id)

        # G_MEET (ID 2): Descoberta local por caminhos de comprimento 2 (E_novo <- p -> E_antigo)
        witness_episodes: Dict[int, Set[int]] = {}
        candidate_functions_hit: Set[int] = set()

        for pf in pos_frag_ids:
            e_idx = self.nodes[pf].first_out_edge
            while e_idx != -1:
                edge = self.edges[e_idx]
                peer_id = edge.dst_id
                if peer_id != ep_id:
                    peer = self.nodes[peer_id]
                    if peer.kind == KIND_EPISODE and edge.role == PORT_PREMISE_POS:
                        witness_episodes.setdefault(peer_id, set()).add(pf)
                    elif peer.kind == KIND_FUNCTION and not (peer.flags & MFLAG_OBSOLETE):
                        candidate_functions_hit.add(peer_id)
                e_idx = edge.next_out_edge

        promoted_or_revised_id = None
        # G_REVISE (ID 7): Caso de contraexemplo (conseq_frag_id is None)
        if conseq_frag_id is None:
            self.total_genesis_firings["G_REVISE"] += 1
            pos_set_contra = set(pos_frag_ids)
            for fn_id in candidate_functions_hit:
                fn = self.nodes[fn_id]
                fn_pos_prems = set()
                ie = fn.first_in_edge
                while ie != -1:
                    if self.edges[ie].role == PORT_PREMISE_POS:
                        fn_pos_prems.add(self.edges[ie].src_id)
                    ie = self.edges[ie].next_in_edge
                if fn_pos_prems.issubset(pos_set_contra):
                    fn_roots = self.get_provenance_roots(fn_id)
                    common_neg_in_positives: Optional[Set[int]] = None
                    for peer_ep_id in witness_episodes.keys():
                        peer_roots = self.get_provenance_roots(peer_ep_id)
                        if peer_roots & fn_roots:
                            ep_negs = set()
                            ie2 = self.nodes[peer_ep_id].first_in_edge
                            while ie2 != -1:
                                if self.edges[ie2].role == PORT_PREMISE_NEG:
                                    ep_negs.add(self.edges[ie2].src_id)
                                ie2 = self.edges[ie2].next_in_edge
                            if common_neg_in_positives is None:
                                common_neg_in_positives = ep_negs
                            else:
                                common_neg_in_positives &= ep_negs
                    discriminant_negs = (common_neg_in_positives or set()) & pos_set_contra
                    if discriminant_negs:
                        fn.flags |= MFLAG_OBSOLETE
                        new_fn_id = self._create_specialized_function(fn_id, fn_pos_prems, discriminant_negs, fn_roots)
                        fn.superseded_by = new_fn_id
                        promoted_or_revised_id = new_fn_id
                    else:
                        fn.n_contra += 1
            return {
                "episode_id": ep_id,
                "revised_function_id": promoted_or_revised_id,
                "latency_us": round((time.perf_counter() - t0) * 1e6, 2)
            }

        # G_JOIN (ID 3): Antiunificação e acumulação de raízes no Semianel de Proveniência N[Z]
        self.total_genesis_firings["G_JOIN"] += 1
        matching_eps = [ep_id]
        common_pos_inter = set(pos_frag_ids)
        common_neg_inter = set(neg_frag_ids)
        union_roots = {prov_root_id}
        has_var = (slot0 != 0)
        observed_var_pairs: Set[Tuple[int, int]] = {(slot0, slot1)} if (slot0 > 0 and slot1 > 0) else set()
        min_positions = len(pos_frag_ids) + (1 if has_var else 0)

        for peer_id, shared_p_set in witness_episodes.items():
            peer = self.nodes[peer_id]
            peer_conseq = None
            oe = peer.first_out_edge
            while oe != -1:
                if self.edges[oe].role == PORT_CONSEQUENCE:
                    peer_conseq = self.edges[oe].dst_id
                    break
                oe = self.edges[oe].next_out_edge
            if peer_conseq != conseq_frag_id or (peer.slot0_val != 0) != has_var:
                continue

            matching_eps.append(peer_id)
            common_pos_inter &= shared_p_set
            peer_negs = set()
            peer_pos_total = 0
            ie = peer.first_in_edge
            while ie != -1:
                if self.edges[ie].role == PORT_PREMISE_NEG:
                    peer_negs.add(self.edges[ie].src_id)
                elif self.edges[ie].role == PORT_PREMISE_POS:
                    peer_pos_total += 1
                ie = self.edges[ie].next_in_edge
            common_neg_inter &= peer_negs
            union_roots |= self.get_provenance_roots(peer_id)
            if peer.slot0_val > 0 and peer.slot1_val > 0:
                observed_var_pairs.add((peer.slot0_val, peer.slot1_val))
            ep_m = peer_pos_total + (1 if has_var else 0)
            if ep_m < min_positions:
                min_positions = ep_m

        # G_PROMOTE (ID 6): Avaliação de Promoção Conservativa MDL (Teorema 5.4)
        n_indep = len(union_roots)
        if n_indep >= 2 and len(common_pos_inter) > 0:
            self.total_genesis_firings["G_PROMOTE"] += 1
            inv_count = len(common_pos_inter)
            v_vars = 1 if has_var else max(0, min_positions - inv_count)
            m_pos = max(2 if has_var else 1, inv_count + v_vars)
            delta_mdl = float(n_indep * ((m_pos - v_vars) * b_bits - q_bits) - c_cost)

            if delta_mdl > 0:
                existing_fn = None
                for fn_id in candidate_functions_hit:
                    fn = self.nodes[fn_id]
                    if (fn.flags & MFLAG_OBSOLETE) or bool(fn.flags & MFLAG_HAS_VARBIND) != has_var:
                        continue
                    fn_conseq = None
                    oe = fn.first_out_edge
                    while oe != -1:
                        if self.edges[oe].role == PORT_CONSEQUENCE:
                            fn_conseq = self.edges[oe].dst_id
                            break
                        oe = self.edges[oe].next_out_edge
                    if fn_conseq == conseq_frag_id:
                        existing_fn = fn_id
                        break

                var_flags = MFLAG_HAS_VARBIND if has_var else 0
                if observed_var_pairs:
                    d0 = {p[0] for p in observed_var_pairs}
                    d1 = {p[1] for p in observed_var_pairs}
                    if len(d0) >= 2 and len(d1) >= 2 and len(observed_var_pairs) == len(d0) * len(d1):
                        var_flags |= MFLAG_FACTORED_VARS
                    else:
                        var_flags |= MFLAG_COUPLED_VARS

                if existing_fn is not None:
                    fn = self.nodes[existing_fn]
                    fn.n_confirm = n_indep
                    fn.mdl_delta = delta_mdl
                    fn.flags = (fn.flags & ~(MFLAG_COUPLED_VARS | MFLAG_FACTORED_VARS)) | var_flags
                    for r_id in union_roots:
                        self.inscribe_surface_mark(existing_fn, witness_id=r_id)
                    for (s0, s1) in observed_var_pairs:
                        pair_code = ((s0 & 0xFFFF) << 16) | (s1 & 0xFFFF)
                        self.inscribe_surface_mark(existing_fn, witness_id=0, delta_payload=pair_code)
                    promoted_or_revised_id = existing_fn
                else:
                    fn_id = self.alloc_node(
                        KIND_FUNCTION, core_law=LAW_GATE, q_polar=POLAR_POS,
                        flags=MFLAG_PERSISTENT | var_flags
                    )
                    fn = self.nodes[fn_id]
                    fn.n_confirm = n_indep
                    fn.mdl_delta = delta_mdl
                    for pf in common_pos_inter:
                        self.connect_port(pf, fn_id, PORT_PREMISE_POS)
                    self.connect_port(fn_id, conseq_frag_id, PORT_CONSEQUENCE)
                    for r_id in union_roots:
                        self.inscribe_surface_mark(fn_id, witness_id=r_id)
                    for (s0, s1) in observed_var_pairs:
                        pair_code = ((s0 & 0xFFFF) << 16) | (s1 & 0xFFFF)
                        self.inscribe_surface_mark(fn_id, witness_id=0, delta_payload=pair_code)
                    promoted_or_revised_id = fn_id

        return {
            "episode_id": ep_id,
            "promoted_function_id": promoted_or_revised_id,
            "latency_us": round((time.perf_counter() - t0) * 1e6, 2)
        }

    def _create_specialized_function(self, old_fn_id: int, pos_prems: Set[int],
                                     neg_prems: Set[int], roots: Set[int]) -> int:
        old_fn = self.nodes[old_fn_id]
        conseq_id = None
        oe = old_fn.first_out_edge
        while oe != -1:
            if self.edges[oe].role == PORT_CONSEQUENCE:
                conseq_id = self.edges[oe].dst_id
                break
            oe = self.edges[oe].next_out_edge

        new_fn_id = self.alloc_node(
            KIND_FUNCTION, core_law=LAW_GATE, q_polar=POLAR_POS,
            flags=(old_fn.flags & ~MFLAG_OBSOLETE) | MFLAG_PERSISTENT
        )
        new_fn = self.nodes[new_fn_id]
        new_fn.n_confirm = old_fn.n_confirm
        new_fn.mdl_delta = old_fn.mdl_delta
        for pf in pos_prems:
            self.connect_port(pf, new_fn_id, PORT_PREMISE_POS)
        for nf in neg_prems:
            self.connect_port(nf, new_fn_id, PORT_PREMISE_NEG)
        if conseq_id is not None:
            self.connect_port(new_fn_id, conseq_id, PORT_CONSEQUENCE)
        for r_id in roots:
            self.inscribe_surface_mark(new_fn_id, witness_id=r_id)
        return new_fn_id

    def inscribe_or_revise_fact(self, schema_frag: int, key_frag: int,
                                version_gate_frag: int, value_frag: int,
                                prov_root_id: int,
                                previous_fact_node: Optional[int] = None) -> int:
        """G_INS + G_REVISE: Inscrição ou revisão de fato versionado certificado por portas."""
        self.total_genesis_firings["G_INS"] += 1
        fact_id = self.alloc_node(KIND_FACT_NODE, core_law=LAW_GATE, q_polar=POLAR_POS, flags=MFLAG_PERSISTENT)
        self.connect_port(schema_frag, fact_id, PORT_PREMISE_POS, prov_root=prov_root_id)
        self.connect_port(key_frag, fact_id, PORT_PREMISE_POS, prov_root=prov_root_id)
        self.connect_port(version_gate_frag, fact_id, PORT_VERSION_CTX, prov_root=prov_root_id)
        self.connect_port(fact_id, value_frag, PORT_CONSEQUENCE, prov_root=prov_root_id)
        self.inscribe_surface_mark(fact_id, witness_id=prov_root_id)

        if previous_fact_node is not None:
            self.total_genesis_firings["G_REVISE"] += 1
            prev = self.nodes[previous_fact_node]
            prev.flags |= MFLAG_OBSOLETE
            prev.superseded_by = fact_id
        return fact_id

    def pulse_temporal_transition_endogenous(self, observed_transitions: List[Tuple[Tuple[int, ...], int, int, Tuple[int, ...]]]) -> Dict[str, Any]:
        """
        TEOREMA 1.7 (NOVO): Indução Endógena de Estados Preditivos Mínimos (u ≡_D v) SEM ORÁCULO EXTERNO!
        A memória recebe apenas as transições empíricas vividas (h_t, ação_t, obs_t, h_{t+1}).
        1. G_INS inscreve cada nó histórico e conecta portas temporais `PORT_TRANSITION`.
        2. Raios retropropagados de 1 e 2 saltos pelas portas `PORT_TRANSITION` inscrevem na
           `SurfaceFaceArena` de cada história u o seu Espectro Temporal Observado Σ_D(u).
        3. G_MEET e G_JOIN fundem autonomamente os nós históricos com mesmo espectro Σ_D(u)
           em Mórfons de Estado Preditivo (`KIND_PRED_STATE`) na `NodeArena`!
        """
        self.total_genesis_firings["G_INS"] += 1
        self.total_genesis_firings["G_MEET"] += 1
        self.total_genesis_firings["G_JOIN"] += 1

        hist_to_ep_node: Dict[Tuple[int, ...], int] = {}
        for h, a, obs, h_next in observed_transitions:
            for ht in (h, h_next):
                if ht not in hist_to_ep_node:
                    nid = self.alloc_node(KIND_EPISODE, core_law=LAW_INS, sym_code=abs(hash(ht)) & 0xFFFFFFFF)
                    hist_to_ep_node[ht] = nid

            u_id = hist_to_ep_node[h]
            v_id = hist_to_ep_node[h_next]
            self.connect_port(u_id, v_id, PORT_TRANSITION, var_pos_idx=a, weight_pol=1 if obs > 0 else -1)
            # Marca de 1 passo inscrita diretamente na Face de u_id: (len=1, ação=a, saída=obs)
            sig_1step = (1 << 32) | ((a & 0xFF) << 16) | (obs & 0xFF)
            self.inscribe_surface_mark(u_id, witness_id=MARK_TEMP_SPECTRUM, depth_inc=1, delta_payload=sig_1step)

        # Propagação local de 2º salto pelas próprias arestas PORT_TRANSITION da arena (Zero Oráculo!)
        for h, u_id in hist_to_ep_node.items():
            e1 = self.nodes[u_id].first_out_edge
            while e1 != -1:
                ed1 = self.edges[e1]
                if ed1.role == PORT_TRANSITION:
                    a1 = ed1.var_pos_idx
                    o1 = 1 if ed1.weight_polarity > 0 else 0
                    mid_id = ed1.dst_id
                    e2 = self.nodes[mid_id].first_out_edge
                    while e2 != -1:
                        ed2 = self.edges[e2]
                        if ed2.role == PORT_TRANSITION:
                            a2 = ed2.var_pos_idx
                            o2 = 1 if ed2.weight_polarity > 0 else 0
                            sig_2step = (2 << 32) | ((a1 & 0xF) << 24) | ((o1 & 0xF) << 16) | ((a2 & 0xF) << 8) | (o2 & 0xF)
                            self.inscribe_surface_mark(u_id, witness_id=MARK_TEMP_SPECTRUM, depth_inc=1, delta_payload=sig_2step)
                        e2 = ed2.next_out_edge
                e1 = ed1.next_out_edge

        # G_JOIN: Agrupar histórias cujo espectro temporal completo na SurfaceFaceArena é idêntico
        spectrum_to_state_node: Dict[Tuple[int, ...], int] = {}
        hist_partition: Dict[str, int] = {}

        for h, u_id in sorted(hist_to_ep_node.items(), key=lambda x: len(x[0])):
            spec_set = set()
            mk_idx = self.nodes[u_id].first_mark
            while mk_idx != -1:
                mk = self.marks[mk_idx]
                if mk.witness_id == MARK_TEMP_SPECTRUM:
                    spec_set.add(mk.delta_payload)
                mk_idx = mk.next_mark
            # Considerar apenas histórias que possuem cobertura completa dos testes de 1 e 2 passos (6 continuações binárias)
            if len(spec_set) >= 6:
                spec_tuple = tuple(sorted(spec_set))
                if spec_tuple not in spectrum_to_state_node:
                    st_id = self.alloc_node(
                        KIND_PRED_STATE, core_law=LAW_GATE, q_polar=POLAR_POS,
                        sym_code=abs(hash(spec_tuple)) & 0xFFFFFFFF, flags=MFLAG_PERSISTENT
                    )
                    spectrum_to_state_node[spec_tuple] = st_id
                hist_partition[str(h)] = spectrum_to_state_node[spec_tuple]

        return {
            "minimal_predictive_states_count": len(spectrum_to_state_node),
            "state_morphon_ids": list(spectrum_to_state_node.values()),
            "history_partition": hist_partition,
            "oracle_used": False
        }

    def pulse_energy(self, stimulus: Dict[str, Any], energy_quanta: int = 100) -> Dict[str, Any]:
        """
        PORTA ÚNICA DE ENERGIA DO MOTOR AUTÔNOMO:
        O Python entrega apenas o estímulo bruto e os quanta de energia.
        Os 8 Mórfons Gênesis na arena executam autonomamente fragmentação, propagação,
        inferência, promoção MDL, revisão ou investigação!
        """
        pos_in_strs = stimulus.get("pos_in", [])
        neg_in_strs = stimulus.get("neg_in", [])
        conseq_str = stimulus.get("consequence", "__QUERY_ONLY__")
        prov_root = stimulus.get("prov_root", 0)
        slot0_code = self.encode_entity(stimulus.get("slot0"))
        slot1_code = self.encode_entity(stimulus.get("slot1"))

        pos_ids: List[int] = []
        for s in pos_in_strs:
            pos_ids.extend(self._genesis_frag_inscribe(s, prov_root=prov_root))
        neg_ids: List[int] = []
        for s in neg_in_strs:
            neg_ids.extend(self._genesis_frag_inscribe(s, prov_root=prov_root))

        # Se for uma experiência com desfecho observado (aprendizagem / contraexemplo na arena)
        if conseq_str != "__QUERY_ONLY__":
            conseq_id = self._genesis_frag_inscribe(conseq_str, prov_root=prov_root)[0] if conseq_str is not None else None
            learn_res = self.ingest_episode_and_meet_locally(
                pos_ids, neg_ids, conseq_id, prov_root_id=prov_root,
                slot0=slot0_code, slot1=slot1_code
            )
            return {"mode": "AUTONOMOUS_EXPERIENCE_INGESTION", "result": learn_res}

        # Caso contrário, propaga os raios com a energia fornecida
        prop_res = self.propagate_localized_rays(
            pos_ids, neg_ids, in_slot0=slot0_code, in_slot1=slot1_code,
            energy_quanta=energy_quanta
        )
        prop_res["emitted_symbols"] = [self.get_symbol_str(fid) for fid in prop_res["emitted_fragments"]]
        prop_res["bound_entity_0"] = self.decode_entity(prop_res["bound_slot0"])
        prop_res["bound_entity_1"] = self.decode_entity(prop_res["bound_slot1"])
        return {"mode": "AUTONOMOUS_RAY_PROPAGATION", "result": prop_res}

    def export_binary_snapshot_hex(self) -> Dict[str, Any]:
        """Exporta as células ativas das 3 arenas em formato hexadecimal auditável."""
        raw_nodes = ctypes.string_at(ctypes.byref(self.nodes), self.node_count * 64)
        raw_edges = ctypes.string_at(ctypes.byref(self.edges), self.edge_count * 32)
        raw_marks = ctypes.string_at(ctypes.byref(self.marks), self.mark_count * 32)
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "mark_count": self.mark_count,
            "total_ram_bytes": len(raw_nodes) + len(raw_edges) + len(raw_marks),
            "genesis_nodes_hex_sample": raw_nodes[:512].hex(),
            "edges_hex_sample": raw_edges[:256].hex(),
            "marks_hex_sample": raw_marks[:256].hex()
        }

    def close(self):
        self.nodes = None
        self.edges = None
        self.marks = None
        gc.collect()
        for mm in (self._node_mmap, self._edge_mmap, self._mark_mmap):
            try:
                mm.close()
            except BufferError:
                pass

# Alias de compatibilidade com scripts anteriores
UnifiedMorphMemory = AutonomousMorphMemory
