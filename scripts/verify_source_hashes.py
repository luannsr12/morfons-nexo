#!/usr/bin/env python3
"""Audita SHA256 de todos os arquivos primários incluídos em experiments/."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'reproducibility/source_hashes.json').read_text(encoding='utf-8'))
fail=[]
for rel,sha in manifest['sha256'].items():
 p=ROOT/rel
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:fail.append(rel)
actual={p.relative_to(ROOT).as_posix() for p in (ROOT/'experiments').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
missing=actual-set(manifest['sha256'])
if fail or missing:
 print('Arquivos alterados/ausentes:',fail,'Arquivos sem manifesto:',sorted(missing));sys.exit(1)
print(f'OK: {len(manifest["sha256"])} arquivos originais verificados por SHA-256.')
