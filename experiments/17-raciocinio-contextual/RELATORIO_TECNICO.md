# Relatório técnico — Experimento 17

## 1. Hipótese e base filosófica

O livro *O Acontecer e o Intérprete*, de L. Rosa (2026), propõe uma dinâmica relacional situada de ocorrência, diferenciação, registro, modulação, seleção contextual e antecipação/ação (capítulo 3); caracteriza **contexto como história em atividade** (capítulo 5); e distingue o estado da memória da atividade que produz consequências e reorganiza a memória (capítulo 11). O próprio texto deixa em aberto as formas quantitativas dessas operações. A tradução para código neste ensaio **é hipótese computacional de pesquisa**, não uma equação que o livro tenha declarado.

Nos Experimentos 08–15, o NEXO já produziu relações, fragmentos, memória persistente e ativações. No Exp. 16, porém, frases semelhantes recuperavam respostas armazenadas e não utilizavam efetivamente o mundo relacional para derivar saídas. Esse foi o defeito que o Exp. 17 procurou isolar.

## 2. Contrato matemático preservado

Cada Mórfon possui portas, superfícies persistentes e um núcleo. A ativação **não** exige limiar de 2 ou mais: `a_i = 1[r_i > 0]`. A sustentação física temporária é `w_i = r_i`, onde `r_i` conta as fontes distintas de raios na ativação atual. Os Mórfons de fatos têm quatro portas: origem, tipo de relação opaco, destino e enquadramento contextual. Os Mórfons de padrões têm portas para os fragmentos lexicais invariantes. As conexões são reais e têm caches derivados de adjacência; salvar e restaurar preserva a estrutura.

A formação de pares/fragmentos do Exp15 não foi substituída; a nova camada usa seus Mórfons/portas/marcas e um problema diferente de supervisão lexical-relacional. **Não é correto dizer que a Fragmentação Contrastiva por Resíduos foi generalizada para tudo**. A descoberta de quais textos representam uma relação ocorre por ancoragens demonstradas (sujeito/objeto estruturados), não pelo indutor binário FCR. Isso é um limite atual explícito de integração com o aprendiz mais geral.

## 3. Duas operações que passaram a coexistir

### 3.1 Memória episódica e raciocínio relacional

Um exemplo observado tem um quádruplo opaco `(s,p,o,c)` e uma frase correspondente. O aprendiz observa diversos exemplos com substituição dos valores `s` e `o` e induz um padrão textual de invariantes e slots; registra uma ligação entre o padrão e `(p,c)`. A existência de nomes *não* é semântica hardcoded: nomes foram ancorados como entidades pelo professor.

Uma pergunta ensinada tem texto `q`, origem `s` e resultado observado `o`. O aprendiz percorre as conexões da memória situacional, buscando sequências de portas que terminem no resultado, e acumula evidência para a rota correspondente à forma textual da pergunta:

`p*(T) = argmax_p [ soma_{exemplos de T} credito(p | s, o, G) ]`.

**Atenção:** várias rotas podem explicar um único exemplo. Empate causa abstenção. Experiências novas desfazem coincidências do mundo inicial. A rota de uma pergunta *não* é hardcoded em `grounded.py`.

Para uma referência composta `R(X)`, aprendida separadamente de uma pergunta `Q(X)`, a inferência aplica caminhos sequenciais: `Q(R(X))`. Em perguntas inéditas com três saltos, `Q(R2(R1(X)))` foi reconstruída a partir das três operações elementares ensinadas separadamente. São consultas sobre dados **introduzidos após o treinamento**, não retorno de frases treinadas.

**O contexto** é distinguido por escopo explícito nas relações (passado/presente opacos) e por um foco armazenado no Mórfon de registro da sessão. Perguntas elípticas como “E antes?” recuperam a origem em foco, em vez de selecionar resposta por proximidade lexical.

A previsão exige evidência estrutural; uma pergunta sem caminho suficiente não produz resposta. Caso caminhos vigentes produzam destinos incompatíveis, a máquina se abstém e emite um motivo auditável. Ainda não há explicação discursiva espontânea: os códigos de motivo vêm do executor.

### 3.2 Transformações de bits dentro da mesma população de Mórfons

O professor fornece exemplos de transições `tau(x_i,y_i,c_i) = (z_i,c_(i+1))`, com bits e estado observados. O aprendiz armazena as oito combinações no mesmo substrato (`kind=bit_transition`), com quatro portas para operador, bit esquerdo, bit direito e estado.

Na inferência, um executor genérico percorre os dígitos binários de números recebidos, ativa uma transição por etapa, lê `z_i` e `c_(i+1)` da superfície, e constrói `resultado = Σ z_i 2^i`. A função concreta (a tabela de transição da adição) **não está escrita no código do aprendiz**. Mas o particionamento em colunas, a representação binária, o estado inicial e a leitura/escrita da resposta são convencionais e predefinidos. O treinamento **inclui o estado de transporte**: este ensaio não demonstra descobri-lo de exemplos de somas completas sem traços.

## 4. Protocolos e resultados reproduzidos

Os números exatos estão em `results/metricas.json`, `avaliacao_individual.json`, `avaliacao_numerica.json`, `controles.json`, `curva.json` e `results/chat_interativo_real.txt`.

- Treino: 240 mundos gerados por semente, 8.160 frases de ocorrência ancoradas, 10.080 perguntas com resposta demonstrada e 1.920 demonstrações de referências compostas. Adicional numérico: 600 exercícios de até 10 bits, com transições intermediárias e respostas do professor. São dois canais de aprendizagem na **mesma** memória de conhecimento, não um segundo chatbot.
- Teste: 40 mundos de entidades, itens, locais e regiões nunca nomeados no treino, num total de 2.000 consultas; 100% de acerto lexical-normalizado nessas 11 categorias. **O gerador, a gramática e o espaço de relações são delimitados**. Não é medição de conversação aberta.
- Composição inédita: 160 perguntas de duas etapas e 160 de três etapas **nunca demonstradas na forma completa**. 320/320, derivados de fragmentos ensinados separadamente.
- Operação numérica: 1.000/1.000 operações de soma com números até 21 bits por operando, jamais vistos integralmente no treino. Teste adicional específico: `17 + 26 = 43`.
- Com apenas um mundo inicial deliberadamente ambíguo, o aprendiz acerta 220/500; com um segundo mundo que diferencia as rotas candidatas, 500/500, mantendo o mesmo motor.
- Sem a composição recursiva, 160/1.000 perguntas deixam de funcionar e o resultado é 840/1.000, nos mesmos mundos.
- Com contextos de passado e presente trocados, cai a 600/1.000. O enquadramento não é decorativo.
- Sem os fatos observados, 0/1.000, todas abstenções — evidência de que não há respostas decoradas para nomes inéditos.
- Treinamento com respostas associadas a alvos errados: 0/750 no controle. O controle também gera abstenções e respostas incorretas; registradas separadamente.
- Recuperação local com 10.000 átomos desconectados: três conexões percorridas antes e depois para consulta selecionada. Isso não mede todos os padrões de escala.
- Parâmetros binários removidos: o modelo que conhece apenas a frase “Quanto é A mais B?” sem qualquer transição aprendida abstém-se; não existe soma numérica escondida no parser.
- 18 testes automatizados; incluindo serialização, raios, contradição, contexto e recuperação de novas informações.

## 5. Conversei realmente com a memória treinada

Transcrição literal do `chat_cli.py` executado por stdin no arquivo `results/chat_interativo_real.txt`. Forneci à conversa novas afirmações sobre Mara, Recife, Olinda e Caderno. Sem retreinar o modelo, obtive respostas corretas para `Onde mora Mara?`, `E antes?`, `Onde fica o objeto que Mara guarda?`, `Em que região fica o lugar onde fica o objeto que Mara guarda?`, e a operação `Quanto é 17 mais 26?`. Ao perguntar `Por que o mundo acontece?`, o agente não possuía operação linguística correspondente e se absteve. Não transformei essa ausência numa resposta fabricada.

**Nomes e lugares** da conversa de demonstração são fatos hipotéticos fornecidos na sessão. Isso não afirma nada sobre pessoas reais. Recife, Olinda e Pernambuco foram usados como termos reconhecíveis para facilitar o teste, sem acesso a serviços externos.

## 6. O que deu errado e por quê

1. A primeira rodada registrou **0/800** apesar de caminhos corretos, devido a uma falha na comparação literal (maiúsculas e ponto final). Auditoria confirmou as cadeias de tokens e o formato. Corrigi o verificador e mantive `literal_exact` e `correct` separados.
2. O primeiro código do renderizador utilizava `.capitalize()`, que coloca em minúsculas letras de nomes próprios após o primeiro token. Corrigi sem alterar o aprendiz.
3. O primeiro teste com dados contextualizados falhou porque a fixture escolheu o primeiro sujeito de uma lista embaralhada — às vezes uma cidade, não uma pessoa. O teste foi corrigido para escolher uma entidade própria da categoria examinada. Isso não foi contado como falha algorítmica.
4. Após permitir nomes com várias palavras, a generalização exigiu um comparador de spans. A primeira edição introduziu um erro de indentação, detectado pelo interpretador. Corrigi e executei novamente todas as verificações. Também corrigi a atualização do foco para entidades compostas.
5. A otimização do índice lexical tornou inválida a primeira ablação, que simplesmente apagava um índice auxiliar. A ablação passou a desativar os Mórfons referenciais reais; o efeito esperado de perda de composição voltou a ser observado.

Nenhum desses erros foi encoberto por uma mudança nos dados esperados. Os arquivos de log e testes documentam a versão funcional final.

## 7. Limites materiais e próximos requisitos científicos

- **Ensino estruturado**: a origem e o destino de eventos são fornecidos durante a supervisão. Não há descoberta autônoma de entidades/percepções a partir de pixels, sons ou texto cru.
- **Padrões textuais**: aparecem em uma gramática curta, embora slots já aceitem várias palavras e referências aninhadas. Perguntas diferentes do que foi ensinado (paráfrases livres) frequentemente produzem abstenção, inclusive questões filosóficas do próprio livro. O NEXO não consegue ainda conversar livremente sobre o livro só por tê-lo lido.
- **Traços para aritmética**: o mecanismo conhece as transições porque o professor demonstrou estados binários; não há indução da regra de estado oculto a partir de casos completos.
- **Sessão relacional**: um mesmo predicado/contexto é tratado como funcional (novo valor substitui o antigo); isso não cobre relações multivaloradas. Essa pressuposição deve ser aprendida ou representada explicitamente em modelos posteriores.
- **Ainda não demonstrados**: planejamento geral sobre fatos aprendidos, escolha de perguntas próprias, aquisição de semântica livre, causalidade ampla e auto-organização autônoma do vocabulário. A memória de episódios cresce conforme novos acontecimentos são preservados. O experimento anterior de fragmentação continua pertinente para eventual compactação de fatos.
- **Escalabilidade**: para cada consulta, padrão textual é recuperado pelos tokens fixos que ativam as portas; fatos são percorridos pelos vizinhos do objeto ativo. A criação de novos nós por observação é O(1) em número de fragmentos envolvidos (a busca de arestas do sujeito cresce com o seu grau). Nenhuma prova de custo sublinear no pior caso com hubs gigantescos. Não há treinamento distribuído nem atualização incremental de regras linguísticas com ruído de transcrição.

## 8. Comparação com pesquisa externa

A leitura de *Compositional Generalization with Grounded Language Models* (Wold et al., Findings of ACL, 2024, https://aclanthology.org/2024.findings-acl.205/) fundamentou a exigência de avaliar composições inéditas sobre grafos que não coincidam com os dados do treinamento. *Recursive Algorithmic Reasoning* (Jürß et al., Learning on Graphs 2024, https://proceedings.mlr.press/v231/jurss24a.html) motivou o controle explícito de profundidade da resolução recursiva. São referências de contexto, não cópia de arquitetura. O código do aprendiz não requer nem chama esses modelos.

## 9. Conclusão sem maquiagem

**Neste laboratório**, o NEXO deixou de responder apenas por similaridade de frase. Ele utiliza relações fornecidas pela experiência, recupera caminhos aprendidos, produz informação nova combinando estruturas e reutiliza uma função binária observada. O aumento de exemplos não converte automaticamente esse sucesso em compreensão geral: a curva mostra que a gramática é curta e dois mundos informativos são suficientes. Demonstramos **generalização composicional dentro de um universo ancorado**, não inteligência conversacional geral. A linha correta de investigação posterior é ampliar o modo como palavras e situações ganham ancoragem, preservando os Mórfons, e não acrescentar respostas fixas para perguntas do usuário.
