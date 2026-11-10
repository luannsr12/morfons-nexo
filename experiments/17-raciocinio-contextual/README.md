# NEXO — Experimento 17: contexto, inferência e conversação por Mórfons

## O que foi efetivamente feito

Evolução isolada do Experimento 16, usando **o mesmo `morfon.py`** do núcleo integrado anterior (copiado sem alterar suas operações de portas/raios/núcleos). A extensão `grounded.py` aprende **templates lexicais**, **rotas de relações**, **referências composicionais** e **transições binárias**, conservando-as como Mórfons e utilizando Mórfons também para armazenar os acontecimentos de uma conversa.

**A entrada de ensino é supervisionada e multimodal/estruturada.** O professor apresenta um acontecimento estruturado (IDs opacos de sujeito, relação, objeto e contexto) junto de uma frase portuguesa e demonstra a resposta de perguntas. O aprendiz não recebe uma gramática pronta de português, mas recebe ancoragem sensorial e feedback. Portanto, **não aprende português livre a partir de textos crus**. Há gerador e oráculo específicos no arquivo `src/laboratorio.py`, nunca importados por `src/grounded.py`.

## Teste principal

- 240 mundos de treinamento, com oito relações entre entidades e contextos, 8.160 enunciados ancorados, 10.080 perguntas demonstradas e 1.920 demonstrações de fragmentos referenciais.
- 40 mundos inéditos, nomes/objetos/lugares inéditos; 2.000 consultas reservadas, incluindo 320 perguntas de sintaxe composicional **inteiramente ausente no treino** (160 de dois e 160 de três saltos). Resultado: **2.000/2.000**, no ambiente gerado, regular e limitado.
- Uma primeira experiência intencionalmente ambígua contém pistas concorrentes. Com um único mundo, 220/500 consultas; após um segundo mundo discriminante, 500/500. Isso mostra a dependência do feedback, mas também a simplicidade do universo de teste.
- Uma função binária **ensinada por traços intermediários** de operações inteiras produz oito Mórfons de transição. 1.000 cálculos inteiros inéditos: **1.000/1.000**, inclusive magnitudes acima do treinamento. O executor de colunas binárias é **programado genericamente**; a tabela de saída e de estado seguinte é aprendida. Não declarar que o NEXO inventou o algoritmo de soma.
- Console real executado: `results/chat_interativo_real.txt`. O NEXO responde a perguntas sobre eventos inseridos após o treinamento e calcula `17 + 26 = 43`, mas ainda **não conversa sobre assuntos arbitrários**. Frases/paráfrases sem padrões aprendidos levam a abstenção.

## Como reproduzir

Na pasta principal (requer Python 3.10+):

```bash
python src/laboratorio.py
python src/controles.py
python -m unittest discover -s tests -v
python src/chat_cli.py
```

O código de treino, inferência e testes utiliza só biblioteca padrão. `python src/figuras.py` é opcional e requer matplotlib. A sessão do CLI fica no arquivo `results/sessao_interativa.json`; `/zerar` limpa a memória da conversa, não o aprendizado do modelo.

## Arquivos

- `src/morfon.py`: motor preservado de portas, raios, ativação, marcas e serialização.
- `src/grounded.py`: camada aprendida de linguagem/contexto/caminhos/transformações binárias, sem LLM, rede, embeddings nem rótulos de domínio hardcoded.
- `src/laboratorio.py`: mundos/oráculo/treinamento/supervisão/avaliação, separado do aprendiz.
- `src/controles.py`: ablações, corruptores de ensino, curva e escalabilidade.
- `src/chat_cli.py`: conversa interativa realmente executável.
- `tests/`: verificações comportamentais e invariantes de Mórfons.
- `results/`: dados individuais, memória treinada, controlo, diálogo, console e logs reais.
- `figures/`: gráficos derivados das estruturas e decisões realmente observadas.
- `corpus/`: amostras literais da supervisão efetivamente utilizada.
- `RELATORIO_TECNICO.md`: equações, interpretação, limites e controvérsias experimentais.

## A principal diferença do Experimento 16

Antes: `frase -> frase parecida armazenada`. Agora: `texto -> padrão aprendido -> ativações -> rota relacional aprendida -> atualização/consulta à memória de eventos -> frase construída`. Para composições inéditas, a operação de resolução de referência é aplicada recursivamente, sem resposta pronta no corpus.

Não substituir o NEXO completo por este protótipo. Há ganho medido em raciocínio relacional situado, mas a aprendizagem de categorias/observáveis brutos, a compreensão linguística irrestrita e uma política de exploração autônoma não foram demonstradas.
