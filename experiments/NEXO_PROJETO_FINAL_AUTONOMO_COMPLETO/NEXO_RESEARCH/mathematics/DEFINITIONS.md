# Definições Matemáticas Fundamentais da Arquitetura NEXO (V4.0 Autônoma)
**Referência Base:** Rosa, L. (2026). *NEXO: Arquitetura de memória relacional executável — fundamentos, demonstrações e resultados experimentais com auditoria causal (Version 1.0)*. Zenodo. https://doi.org/10.5281/zenodo.24094723

---

## Definição 1.1 — Memória Relacional Executável Autônoma ($\mathcal{M}$)
Uma Memória Relacional Executável Autônoma $\mathcal{M}$ é uma quádrupla dinâmica residente em três arenas binárias contíguas de memória (`mmap`):
$$\mathcal{M}_t = (V_t, E_t, \mathcal{F}_t, \mathcal{H}_t)$$
onde:
1. **$V_t$ (`NodeArena`, `MorphonNode` de 64 bytes):** Conjunto finito de unidades relacionais chamadas **Mórfons**. Os endereços físicos `0..7` são ocupados permanentemente pelos **8 Mórfons Gênesis** ($G_{\text{INS}}, G_{\text{FRAG}}, G_{\text{MEET}}, G_{\text{JOIN}}, G_{\text{POL}}, G_{\text{GATE}}, G_{\text{PROMOTE}}, G_{\text{REVISE}}$). Cada Mórfon $i \in V_t$ possui:
   - Núcleo operacional estável $K_i$;
   - Sinalização polar $q_i(t) \in \{-1, 0, +1\}$;
   - Ativação por único raio $a_i(t) = \mathbf{1}\{|R_i(t)| \ge 1\} \in \{0, 1\}$;
   - Sustentação contextual $s_i(t) = |R_i(t)| \in \mathbb{N}_0$;
   - Certificação estrita de portas $c_i(t) \in \{0, 1\}$;
   - Estado epistêmico no reticulado quaternário de Belnap $v_i(t) \in \{\emptyset, \{0\}, \{1\}, \{0,1\}\}$;
   - Espectro Estrutural Local $\Lambda_i \in \{0,1\}^{32}$ (atualizado incrementalmente em $O(1)$);
   - Quanta de energia operacional $E_i(t) \in \mathbb{N}_0$.

2. **$E_t$ (`EdgePortArena`, `PortEdge` de 32 bytes):** Conexões relacionais dirigidas implementadas como listas ligadas intrusivas (`first_out_edge`, `first_in_edge`) com papéis tipados (`PORT_PREMISE_POS`, `PORT_PREMISE_NEG`, `PORT_CONSEQUENCE`, `PORT_VAR_SLOT`, `PORT_VERSION_CTX`, `PORT_TRANSITION`, `PORT_SUBFRAGMENT`).

3. **$\mathcal{F}_t, \mathcal{H}_t$ (`SurfaceFaceArena`, `SurfaceFaceMark` de 32 bytes):** Faces modificáveis contendo o payload binário dos fragmentos emergentes, profundidade $c_{ik}$, raízes do Semianel de Proveniência $\mathbb{N}[Z]$, pares de variáveis acopladas e espectros temporais observados $\Sigma_D(u)$.
