# Arquivo experimental · NEXO

**Idioma:** [English](README.md) | **Português (Brasil)**

Este diretório preserva **linhas experimentais independentes**, e não uma aplicação única já integrada. O código, os testes, os relatórios e os resultados originais permanecem nas respectivas pastas, inclusive os documentos históricos em português.

[Visão geral](../README.pt-BR.md) · [Resultados](../docs/RESULTADOS.md) · [Reprodução](../docs/REPRODUCAO.md) · [Proveniência](../docs/PROVENIENCIA.md)

## Por onde começar

| Estudo | Pergunta investigada | Material |
| :-- | :-- | :-- |
| **08 · Aprendizagem estrutural** | Como observações binárias podem gerar e manter novas organizações? | [Experimento 08](../experiments/08-aprendizagem-esferas/) |
| **14 · Mórfon integrado** | Como raios, contexto, ordem, persistência e poda atuam no mesmo substrato? | [Experimento 14](../experiments/14-morfon-integrado/) |
| **17 · Raciocínio contextual** | Como compor referências e transições aprendidas em mundos inéditos? | [Experimento 17](../experiments/17-raciocinio-contextual/) |
| **21 · Memória contínua** | Como preservar fatos, ensinar paráfrases e revisar relações durante diálogos? | [Experimento 21](../experiments/21-memoria-continua/) |
| **23 · Faces funcionais** | As marcas nas faces realmente causam mudanças nas previsões? | [Experimento 23](../experiments/23-faces-funcionais/) |
| **24 · Ciclo integrado** | Como unir experiência, previsão, ação, feedback e revisão numa memória experimental? | [Experimento 24](../experiments/24-ciclo-integrado/) |
| **Malhas relacionais** | Como compartilhar identidades, compor relações e fatorar a proveniência? | [Estudo de malhas](../experiments/malhas-compartilhadas/) |
| **Arquivo V4.0 separado** | Investigação de arenas binárias e motores autônomos experimentais | [Pesquisa V4.0](../experiments/NEXO_PROJETO_FINAL_AUTONOMO_COMPLETO/NEXO_RESEARCH/) |

A numeração corresponde ao histórico da pesquisa. A existência de lacunas na sequência **não representa resultados não documentados**. O arquivo V4.0 não integra a contagem das sete suítes de regressão principais.

## Reprodução e preservação

Na raiz do repositório:

~~~bash
python -m pip install -r requirements-optional.txt
python scripts/test_all.py --no-save
python scripts/verify_results.py
python scripts/verify_source_hashes.py
~~~

A reexecução arquivada em 10/11/2026 registra **115 testes aprovados**. Os experimentos mais demorados podem sobrescrever arquivos de resultados; para executá-los, use uma cópia separada e consulte [Reprodução](../docs/REPRODUCAO.md).

**Aplicação relacionada:** [Morphons AI](https://morphons-ai.vercel.app/). Ela possui implementação e ciclo de treinamento próprios; não é a soma automática dos experimentos acima.
