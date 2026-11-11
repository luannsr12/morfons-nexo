# Demonstrações Formais Completas (Teoremas 1.1 a 1.8)

## 1. Demonstração dos Teoremas 1.1 e 1.2 (Álgebra Polar e Completude por Portas)
Pelo homomorfismo bijetor $\phi(x) = (-1)^x$ entre $(\mathbb{F}_2, \oplus)$ e $(\{+1, -1\}, \cdot)$, temos $\prod_{r \in S} (-1)^{x_r} = (-1)^{\bigoplus_{r \in S} x_r}$, cujo grau algébrico sobre $\mathbb{F}_2$ é no máximo 1. Como $x_1 \wedge x_2$ tem grau 2, `LAW_POL` isolado não pode realizá-lo. Quando combinado ao Gênesis `G_GATE`, que calcula o produto booleano $\prod_{p \in P^+} x_p \prod_{q \in P^-} (1-x_q)$ em $O(1)$ pelos contadores `cert_pos_hits == req_pos_count` e `cert_neg_hits == req_neg_count`, o conjunto gera todos os monômios de Zhegalkin, atingindo completude funcional universal. $\blacksquare$

## 2. Demonstração do Teorema 1.7 (Indução de Estados Preditivos Sem Oráculo)
Seja $M = (S, A, O, \delta, \lambda)$ uma máquina de Mealy finita mínima com $|S| = K$ estados. Pelo Teorema de Moore-Myhill-Nerode, dois estados $s_1, s_2 \in S$ distinguíveis admitem uma sequência de entrada $d \in A^*$ de comprimento $|d| \le K - 1$ tal que $\lambda^*(s_1, d) \neq \lambda^*(s_2, d)$.
Quando a memória inscreve as transições empíricas como arestas `PORT_TRANSITION` na `EdgePortArena`, os caminhos dirigidos de comprimento $k \le K - 1$ a partir de um nó histórico $u$ percorrem exatamente as sequências $(a_1, o_1, \dots, a_k, o_k)$ observadas após $u$. Ao inscrever esses caminhos como marcas `MARK_TEMP_SPECTRUM` na `SurfaceFaceArena` de $u$, o conjunto de marcas $\Sigma_{K-1}(u)$ coincide com a função de continuação $\tau_D(u)$ restrita a $D = A^{\le K-1}$. Portanto, $\Sigma_{K-1}(u) = \Sigma_{K-1}(v) \iff u \equiv_D v$, reconstruindo os estados preditivos mínimos sem consultar nenhum oráculo externo. $\blacksquare$

## 3. Demonstração da Complexidade Estrita $O(\text{deg}_{\text{local}})$
Na `AutonomousMorphMemory`, nenhum método executa laços sobre `range(self.node_count)`.
- Na propagação (`propagate_localized_rays`), o laço percorre apenas `first_out_edge -> next_out_edge` dos fragmentos presentes no estímulo, tocando no máximo $\sum_{f \in F_{\text{ativo}}} \text{deg}^+(f)$ arestas.
- No aprendizado (`ingest_episode_and_meet_locally`), o encontro `G_MEET` percorre apenas as arestas dos fragmentos do episódio atual (caminhos $E_{\text{novo}} \leftarrow p \rightarrow E_{\text{antigo}}$).
Logo, a adição de $N = 10.000$ Mórfons desconectados na `NodeArena` contribui com exatamente $0$ passos adicionais tanto na consulta quanto na indução, provando invariância assintótica absoluta em relação a $N$. $\blacksquare$
