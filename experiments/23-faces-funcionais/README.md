# NEXO — Experimento 23 (09/11/2026)

Laboratório com código, resultados individuais e testes **sobre o núcleo original** do NEXO. O objetivo é determinar se marcas nas faces dos Mórfons podem adquirir funções operacionais por observação e participar causalmente de previsão, ação e correção de erros.

**Resultado confirmatório:** 960/960 transições reservadas e 962/962 objetivos alcançados nos cinco mundos sintéticos com relações de grau até dois. **Testes adversariais:** 960/960 correções com 3 erros por bloco via Reed–Muller, 320 abstenções em tabelas aleatórias, resultados de terceiro grau e de observações contraditórias no relatório.

**Leia primeiro:** `RELATORIO_CIENTIFICO.md`. Imagens em `figures/`, dados individuais em `results/`, código-fonte do experimento em `src/` e testes em `tests/`.

**Núcleo:** `originals/morfon_exp21_original.py`, hash SHA-256 `842fffcbe268be3b7fc4bd311098c4dbb1b58a52e0291d7359f80434d6c70669`. Não foi editado. Os métodos `pulse_units`, `Morphon.facets`, `Morphon.ports`, `Morphon.rays` e `MorphMemory.snapshot/restore` são reutilizados.

**Reprodução:**

```bash
python -m unittest discover -s tests -v
python src/confirmatory.py
python src/adversarial.py
python src/negative_controls.py
python src/active_design.py
python src/causal_ablations.py
```

Nenhuma dependência externa necessária para executar os testes. As figuras fornecidas foram geradas com matplotlib, que é opcional para os testes.
