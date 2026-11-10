# NEXO — Experimento 21: memória contínua, autoinspeção e aprendizagem por diálogo

**Data:** 08/11/2026. **Base:** memória e núcleo efetivos do Experimento 20, não um chatbot substituto.

## Rodar imediatamente

Na pasta extraída, com Python 3.11+:

```bash
python src/chat.py
```

A cada turno o programa grava o estado inteiro em `results/session_live.json`. Saia com `/sair`, reabra o mesmo comando e continue a conversa. Use `/memoria` para ver fatos, questões pendentes e perguntas internas persistidas. **Não use `--reset` a menos que queira descartar a sessão**.

Exemplos que agora funcionam como interações contínuas:

```text
Qual é meu nome?
Luan
Qual é meu nome?
Meu nome é outro nome.
Qual é meu nome?
Onde eu moro?
Moro em Recife.
Onde eu moro?
Minha hipótese é que o contexto influencia a interpretação.
Qual é minha hipótese?
Se a memória muda, então a interpretação pode mudar.
Considere que a memória muda.
O que se conclui?
Por quê?
/memoria
```

`src/continuous.py` contém o motor genérico de memória da conversa. Não há rótulos programados para `nome`, `cidade`, `mora`, `hipótese`, `livro` ou respostas prontas. Os exemplos de português usados no ensino estão **somente em `src/train_experiences.py` e `training/teacher_experiences.json`**, apartados do motor.

## Reproduzir todos os testes

```bash
python -m unittest discover -s tests -v
python src/evaluate.py
python src/evaluate_paraphrases.py
python src/adversarial.py
python src/demo_dialogue.py
```

`src/train_experiences.py` reconstrói a memória de ensino a partir da base 20 e de 216 exemplos, sem consultar os valores de avaliação. A memória já treinada está em `training/trained21.json` e a base congelada anterior em `training/base20_trained.json`.

## Quais resultados são concretos?

- **384/384 consultas inéditas** respondidas após observações novas, em 12 famílias de enunciados/consultas; palavras e valores de teste ausentes no ensino.
- **6/6 construções linguísticas inéditas** ensinadas interativamente por demonstrações, seguidas de generalização para novos valores.
- **175/175 consultas** de sete paráfrases que o sistema aprendeu a relacionar com vínculos preexistentes por feedback sobre fatos da própria memória.
- **173/173 verificações adversariais**, incluindo 80 consultas intercaladas, 25 correções de valor, 25 rejeições de fatos substituídos, 22 consultas episódicas, 20 inferências novas e uma operação binária antiga.
- **38/38 testes automatizados** de integração, integridade, revisão, autoquestões e persistência.
- **Estado exatamente igual** ao executar uma sequência sem interrupção ou interromper, salvar, restaurar e executar o restante.

Esses resultados NÃO representam diálogo filosófico livre. Perguntas fora do vocabulário aprendido continuam, na maioria dos casos, produzindo uma lacuna; agora essa lacuna é registrada e pode ser ensinada na conversa. Ver `RELATORIO_TECNICO.md` para os controles e erros corrigidos.

## Arquivos

- `src/base17/morfon.py`: núcleo dos Mórfons herdado, portas, raios e persistência.
- `src/nexo20.py`: inferências e memória do Experimento 20, acrescidas de revisão de fatos substituídos.
- `src/continuous.py`: aprendizagem lexical/relacional online, fatos, perguntas internas e inspeção.
- `src/chat.py`: console com gravação **após todo turno**, restauração e inspeção.
- `src/evaluate*.py`, `src/adversarial.py`, `src/demo_dialogue.py`: avaliadores e diálogo reproduzível.
- `training/`: memória de partida, memória ensinada e corpus externo de professor.
- `results/`: dados individuais, casos adversariais, memória usada na avaliação e transcrição literal.
- `figures/`: visualizações baseadas nas métricas reais.
- `tests/`: testes automatizados.
- `historico_Exp20.zip`: versão anterior completa, sem alterações.
- `MANIFEST_SHA256.json`: hashes individuais dos arquivos.
