# Reprodução e auditoria

**Requisitos:** Python 3.11 ou posterior. Biblioteca padrão para o motor. Matplotlib apenas para regenerar gráficos (os PNGs já estão incluídos).

A memória inicial (`training/base20_trained.json`) é uma cópia exata da memória de 9.102 Mórfons do Exp20. O ensino conversacional contém 216 demonstrações completas em `training/teacher_experiences.json`. A memória resultante de 10.215 Mórfons está em `training/trained21.json` (o adaptador pode criar a unidade de sessão ao carregar, resultando em 10.216 antes da primeira conversa).

Comandos, a partir da pasta raiz extraída:

```
python -m unittest discover -s tests -v
python src/evaluate.py
python src/evaluate_paraphrases.py
python src/adversarial.py
python src/demo_dialogue.py
python src/chat.py
```

`python src/train_experiences.py` reaprende os esquemas a partir da memória Exp20; o ensino está fora do módulo `continuous.py`, de forma que cada alteração no motor possa ser testada com o MESMO material de ensino.

Os avaliadores usam nomes/valores formados por cadeias distintas das cadeias do professor. Os resultados são produzidos por `agent.answer(...)` depois do ensino e ficam em arquivos JSON individuais. Os exemplos de filosofia da demonstração não estão no professor lexical e não se tornam respostas hardcoded.

A réplica salva/restaura um estado no meio do diálogo; o teste `TestExactReproducibility` compara os snapshots de todos os Mórfons após as duas execuções, sem ignorar facetas, nós ou portas. `TestParaphraseLearning` verifica aprendizagem efetiva de uma nova forma de perguntar e um caso com fonte ambígua. `TestPendingVsObservation` impede que uma afirmação posterior seja forçosamente usada como resposta a uma pergunta anterior.

Cada arquivo consta em `MANIFEST_SHA256.json` com SHA-256; o próprio manifesto está fora de sua lista para evitar circularidade. O ZIP é testado por `zipfile.testzip`, extração em pasta limpa e execução repetida de todas as 38 provas automatizadas.
