# Contribuições ao acervo científico NEXO

**Idioma:** [English](CONTRIBUTING.md) | **Português (Brasil)**

Contribuições especialmente úteis: **reprodução independente de experimentos, identificação de falhas, perguntas metodológicas e correções precisas na documentação**.

Antes de propor mudanças, consulte [Reprodução](docs/REPRODUCAO.md), [Resultados](docs/RESULTADOS.md) e [Proveniência](docs/PROVENIENCIA.md).

## Ao relatar um resultado

Abra uma issue no GitHub, informando a **pasta experimental**, **SHA do commit**, **versão do Python/ambiente**, **comandos**, **saída obtida**, **saída esperada** e, quando possível, **menor entrada capaz de reproduzir o problema**. Para questionar uma métrica, identifique seu arquivo de origem e a condição de teste.

## Preservação

O material em `experiments/` pertence ao acervo histórico verificado por SHA-256. Evite alterações silenciosas em dados, códigos ou relatórios originais. Se houver uma correção experimental, apresente **nova versão identificada**, com os próprios testes e resultados. Melhorias nos índices, guias, traduções, figuras editoriais e acessibilidade são bem-vindas.

Comandos sugeridos:

~~~bash
python scripts/verify_source_hashes.py
python scripts/verify_results.py
python scripts/test_all.py --no-save
~~~

Distinga hipóteses de resultados testados, documente falhas e preserve os caminhos para as evidências.

O [Morphons AI](https://morphons-ai.vercel.app/) é uma aplicação relacionada, desenvolvida em outro repositório.
