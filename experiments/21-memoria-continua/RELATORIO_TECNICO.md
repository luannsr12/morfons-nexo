# NEXO — Experimento 21: auditoria causal da memória contínua

## Problema concreto encontrado

O Exp20 continuava usando `MorphMemory` para premissas, provas e relações, mas seu interpretador só reconhecia construções previamente ensinadas, o console não ensinava padrões novos durante a conversa e parte do estado de justificativa (`last_proof`) era mantida em uma lista transitória de Python. Por exemplo, `Meu nome é X` não construía um fato consultável, e uma pergunta não interpretada não estabelecia uma operação de aprendizado posterior. A resposta vazia do experimento anterior não demonstrava falta de capacidade matemática do Mórfon, mas falta de um **ciclo de interpretação/observação/atualização** ligado à conversa.

A correção foi executada no MESMO substrato que contém as 9.102 unidades iniciais do Exp20, sem programar respostas por assunto.

## Operação de aprendizagem linguística

O professor fornece apenas episódios textuais `(afirmação, pergunta, resposta)`. O sistema:

1. Verifica se a resposta aparece na afirmação. Essa é a âncora observacional inicial, não um slot de significado fornecido pelo programador.
2. Compara afirmações e perguntas entre experiências e identifica tokens invariantes e regiões variáveis, alinhando regiões variáveis que aparecem tanto na afirmação quanto na pergunta.
3. Conserva as unidades de exemplo e os padrões aprendidos em Mórfons `dialogue_example` e `dialogue_schema` com portas para os termos invariantes e evidências observadas.
4. Só generaliza um novo slot depois de experiências discriminantes: uma única substituição lexical contradizendo 18 observações não autoriza generalização irrestrita.
5. Cada novo turno é um Mórfon de episódio; observações interpretadas viram `dialogue_fact`, com portas para contexto, estrutura aprendida, variáveis e valor. O fato mais novo pode substituir a vigência anterior; ambos continuam serializados.
6. Consultas percorrem os vínculos locais reconstruídos de portas (`MorphMemory.cache` é índice derivado, não memória semântica). Um raio ativa; raios adicionais dão sustentação. Consultas desconhecidas geram `dialogue_goal` e `dialogue_self_question` permanentes, vinculados à observação e a seu contexto.
7. Quando alguém ensina um valor à pergunta pendente, o Mórfon da lacuna é marcado como resolvido. Respostas pontuais persistem mesmo antes de serem generalizadas em um padrão; a generalização é verificada separadamente.
8. Uma pergunta nova pode virar paráfrase de uma antiga se seu valor for **confirmado pela observação humana** e corresponder a um fato único já presente. Três experiências distintas promovem um Mórfon `dialogue_alias` com a forma da pergunta aprendida; o sistema não recebe uma lista codificada de sinônimos.
9. Fatos novos são inscritos simultaneamente como premissas do antigo raciocinador, também na mesma `MorphMemory`. Ao corrigir uma observação, fatos substituídos permanecem na história, mas deixam de atuar como premissas atuais.

O estado da sessão, os episódios, a autoinspeção, as dúvidas e os vínculos com suas fontes são facetas de Mórfons. Índices temporários e listas em Python são reconstruídos a partir dessas facetas. A gravação JSON é a serialização física da memória dos Mórfons, não uma segunda base de conhecimento.

### Critério de meta-observação

Quando uma consulta encontra uma lacuna, a própria consulta, a lacuna e a reflexão tornam-se Mórfons ligados; a unidade de autoquestão é ativada por raios e pode ser examinada em `/memoria`. Quando um enunciado não é interpretável, uma autoquestão de observação sem estrutura também é preservada. O estado `resolvido` depende de uma evidência adquirida, não apenas de imprimir uma resposta genérica. Isso implementa **autoinspeção restrita da própria memória**, não a descoberta arbitrária de novos procedimentos de raciocínio.

## Baterias executadas

| Prova | Resultado | Auditoria |
|---|---:|---|
| Ensino inicial | 216 exemplos, 11 padrões aprendidos | `training/teacher_experiences.json`, `results/training_schemas.log` |
| Fatos inéditos em 12 construções | 384/384 | `results/holdout.json` |
| Novas construções ensinadas no diálogo | 6/6 | `results/online_induction.json` |
| 7 tipos de pergunta-paráfrase, exemplos novos | 175/175 | `results/paraphrase_holdout.json` |
| Memória intercalada/corrigida/inferência | 173/173 | `results/adversarial_cases.json` |
| Unidade, integração, regressões | 38/38 | `results/unittest.log` |
| Conversa interrompida e restaurada | Memórias finais idênticas | `tests/test_regression_extended.py` |

Bateria principal: a memória passou de 10.216 para 15.082 Mórfons em 844 turnos, com 384 observações e consultas e mais seis lições de idioma. Isso é crescimento real; nenhum número de Mórfons foi inventado a partir das frases de avaliação. O máximo de nós configurável cresce quando necessário, por uma regra de alocação, sem mudar a política de aprendizagem.

A comparação com a base Exp20 é factual: a entrada `Meu nome é Zefira` era interpretada como `no_learned_interpretation` na memória antiga; na nova, após o ensino de padrões, um valor novo é armazenado e recuperado. As duas versões usam a mesma classe `MorphMemory`.

## Erros encontrados e corrigidos neste mesmo experimento

1. **Pergunta pendente engolia uma nova afirmação:** `Meu nome é Y` podia ser tratado como resposta curta a outra pergunta. Corrigido dando precedência a construções reconhecidas.
2. **Generalização induzida por uma única exceção:** 18 exemplos de uma construção e um de outra criavam um slot superamplo. Corrigido exigindo diversidade recorrente antes de alterar a estrutura.
3. **Recordação de resposta antiga bloqueava novo ensino:** após a primeira associação a `Como eu sou chamado?`, o sistema repetia um nome antigo e não solicitava nova observação. Corrigido mantendo a proveniência da resposta episódica e verificando se o fato que a justificava ainda está vigente; a prova de paráfrase passou de 150/175 para 175/175.
4. **Demonstrações diferentes deduplicadas:** três experiências da mesma pergunta sem variável de sujeito eram colapsadas em uma porque o identificador ignorava o valor; corrigido para utilizar o valor observado na identidade da experiência.
5. **Observações desconhecidas consumidas como resposta:** uma frase nova e completa podia fechar incorretamente uma lacuna pendente. Corrigida a priorização de observações; a incerteza é conservada quando a relação não foi determinada.
6. **Elipse não recuperada:** `Onde eu moro?` seguido de `Moro em Recife` memorizava a frase inteira como valor. Agora o Mórfon de consulta usa a parte invariável aprendida para reconhecer o prefixo elíptico e isolar `Recife`; mantém essa experiência para posterior aprendizagem da variante gramatical.
7. **Estado de prova se perdia no reinício:** `Por quê?` após reiniciar não reconstruía `last_proof`. O rastro da prova foi persistido como faceta do Mórfon de sessão e restaurado.
8. **Capacidade estática de nós:** a memória tinha limite de alocação configurado para um laboratório finito. A capacidade agora cresce antes do esgotamento, sem alterar a estrutura relacional ou a evidência.

Nenhum erro acima foi 'resolvido' simplesmente renomeando a avaliação; todos geraram alterações de código, novos testes e reexecução do experimento.

## Experimento de conversa com raciocínio e revisão

`results/dialogue_literal.txt` contém 17 turnos, incluindo pergunta de nome sem informação inicial, ensino humano, nome corrigido, local de residência expresso sem pronome, hipótese textual, implicação aprendida anteriormente, conclusão, justificativa, pergunta não demonstrada e autoinspeção da memória com o estado da dúvida. O texto apresentado é a saída literal do processo.

## Dados ausentes / escopo demonstrado

A aprendizagem da sintaxe de pergunta/afirmação utiliza **216 episódios de ensino construídos externamente**, todos presentes no pacote, e novas lições posteriores. Isso não equivale a interpretar frases inteiramente livres ou aprender sintaxe apenas ouvindo uma única frase. Perguntas filosóficas livres não ensinadas podem continuar sem resolução, mas agora não encerram a experiência: deixam Mórfons de dúvida e permitem novo ensino. Os 5 exemplos adversariais abertos estão registrados em `results/adversarial_summary.json`.

O código do motor não contém respostas específicas sobre o mundo, nomes ou opiniões filosóficas. Contém sim mecanismos de correspondência de palavras, escolha de foco, prioridade de observações, requisitos de evidência e apresentação de mensagens; eliminar tais operações significaria eliminar o algoritmo, e não retirar hardcodes de conteúdo.

## Relação com *O Acontecer e o Intérprete*

O capítulo 5 descreve o contexto como *história em atividade*: o significado depende das relações adquiridas, não apenas da frase isolada. O capítulo 6 considera a pergunta como uma estrutura que pode continuar disponível quando o acontecimento original terminou. O experimento aproxima duas propriedades implementáveis dessas ideias: fatos contextuais persistentes/revisáveis e uma representação durável de dúvidas, reativada ao longo da interação. Esse paralelo é uma hipótese de engenharia; não é demonstração da teoria filosófica inteira.

## Decisão técnica

Preservar a arquitetura cumulativa. A forma mínima comprovada do ciclo é **acontecimento → Mórfon de episódio → estruturação da observação → memória persistente → consulta/inferência → lacuna representada por Mórfon → nova observação → atualização**. O mesmo substrato contém fatos e provas, sem substituir o NEXO por um serviço de chatbot, recuperação por embeddings externos ou respostas filosóficas pré-escritas.
