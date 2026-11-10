#!/usr/bin/env python3
"""Confronta as principais alegações do README com resultados primários arquivados."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
def get(path): return json.loads((ROOT/'experiments'/path).read_text(encoding='utf8'))
def check(label, value, expected):
 ok=value==expected
 print(f'{"OK" if ok else "ERRO"} {label}: {value!r} (esperado {expected!r})')
 if not ok:raise AssertionError(label)

def main():
 d=get('17-raciocinio-contextual/results/metricas.json')
 check('Exp17, consultas corretas',d['correct'],2000);check('Exp17, consultas totais',d['total'],2000)
 check('Exp17, soma correta',d['arithmetic']['correct'],1000);check('Exp17, soma total',d['arithmetic']['total'],1000)
 check('Exp17, composições de 2-3 saltos inéditas',d['by_type']['dois_saltos']['total']+d['by_type']['tres_saltos_nunca_treinada']['total'],320)
 d=get('21-memoria-continua/results/summary.json')
 check('Exp21, consultas inéditas',d['holdout_queries'],384);check('Exp21, consultas corretas',d['holdout_correct'],384)
 check('Exp21, novos padrões ensinados',d['online_novel_correct'],6)
 d=get('21-memoria-continua/results/paraphrase_summary.json')
 check('Exp21, paráfrases corretas',d['correct'],175);check('Exp21, consultas de paráfrases',d['queries'],175)
 d=get('23-faces-funcionais/results/confirmatory.json')['summary']['spectral_quadratic']
 check('Exp23, previsões corretas',d['correct'],960);check('Exp23, consultas',d['holdout'],960)
 check('Exp23, objetivos',d['success'],962)
 d=get('24-ciclo-integrado/results/integrated.json')['summary']
 for key,vals in {'rank':(480,1034,576),'random':(328,942,559)}.items():
  a=d[key];check('Exp24 '+key+', corretas',a['correct'],vals[0]);check('Exp24 '+key+', planos',a['plans_success'],vals[1]);check('Exp24 '+key+', metas',a['desires_success'],vals[2]);check('Exp24 '+key+', holdout',a['holdout'],480)
 d=get('malhas-compartilhadas/results.json')
 check('Malhas, casos totais',d['metadata']['num_world_cases'],600)
 check('Malhas, grafos independentes',d['independent_bruteforce_graphs'],250)
 check('Malhas, economia modelo (bytes)',d['cost_model']['saving'],54320)
 e=d['evaluations']['shared_context'];print('Malhas, avaliação:',e)
 vals=[r for r in d['factorized_provenance'] if r['diamonds']==12][0]
 check('Malhas, caminhos',vals['explicit_proof_paths'],4096)
 check('Malhas, nós do DAG',vals['factorized_dag_nodes'],108)
 check('Malhas, inspeções fatoradas',vals['factorized_examined'],48)
 d=get('14-morfon-integrado/dados/consolidacao.json')['main']
 check('Exp14, quad integrado balanced accuracy',round(next(r['balanced_mean'] for r in d if r['world']=='quad' and r['variant']=='B_integrated'),4),1.0)
 check('Exp14, quad comparador balanced accuracy',round(next(r['balanced_mean'] for r in d if r['world']=='quad' and r['variant']=='ORIGINAL_08'),4),0.5)
 print('\nTodas as alegações selecionadas estão presentes nos registros primários.')
 return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except (AssertionError,KeyError,TypeError) as e:print('VERIFICAÇÃO FALHOU:',e,file=sys.stderr);raise SystemExit(1)
