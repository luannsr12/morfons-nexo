# Proveniência e integridade

Este repositório foi preparado a partir de **sete pacotes originais preservados**. Nenhum arquivo de código, teste, dados, relatório ou figura selecionado para `experiments/` foi reescrito. As cópias foram extraídas dos ZIPs originais e verificáveis por SHA-256.

- `reproducibility/source_archives.json`: nomes dos sete arquivos ZIP originais, respectivos hashes e inventário do que foi omitido por duplicação.
- `reproducibility/source_hashes.json`: hashes de **cada arquivo** efetivamente incluído em `experiments/`.
- `python scripts/verify_source_hashes.py`: confere os arquivos incluídos.
- `reproducibility/retest_2026-11-10.json`: resultados da reexecução atual das sete suítes originais.

Os ZIPs históricos **aninhados** (anteriores à série selecionada) e diretórios de cache não foram repetidos dentro da distribuição GitHub. Todos os artefatos experimentais primários dos sete diretórios selecionados permaneceram em `experiments/`. Os documentos editoriais do repositório (`README.md`, `docs/`, `assets/nexo-banner.svg` e `assets/arquitetura-nexo.svg`) foram criados para esta apresentação; os gráficos PNG da pasta `assets/` são cópias dos originais dos experimentos.

O repositório une **linhas de investigação que foram executadas e auditadas separadamente**. A inclusão conjunta não significa que seus motores foram fundidos num único programa. Os relatórios originais em cada diretório expõem parâmetros, mecanismos e condições de cada teste.
