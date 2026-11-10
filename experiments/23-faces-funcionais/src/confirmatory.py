"""Bateria confirmatória: sementes 2..13 não usadas no desenvolvimento inicial.
Mundos e episódios idênticos por condição; fontes de verdade no simulador.
"""
from __future__ import annotations
import json,time
from pathlib import Path
from evaluate import evaluate_one as tree_run
from evaluate_spectral import evaluate_one as harmonic_run

def run(seeds=range(2,14)):
    summary={};raw=[];start=time.perf_counter()
    names=('toggle_cond','context','parity','asym','history')
    variants=('root_only','greedy','mdl_optimal','spectral_linear','spectral_quadratic')
    for name in names:
        for seed in seeds:
            funcs={
                'root_only':lambda:tree_run(name,seed,False),
                'greedy':lambda:tree_run(name,seed,True),
                'mdl_optimal':lambda:tree_run(name,seed,True,optimal=True),
                'spectral_linear':lambda:harmonic_run(name,seed,1),
                'spectral_quadratic':lambda:harmonic_run(name,seed,2),
            }
            for variant in variants:
                result=funcs[variant]();result['variant']=variant
                raw.append(result)
            print('checked',name,seed,'accuracy',[(v,raw[-5+i]['correct']) for i,v in enumerate(variants)],flush=True)
    for variant in variants:
        sub=[z for z in raw if z['variant']==variant]
        keys=['train','holdout','correct','answered','errors','abstentions','plans','found','success']
        summary[variant]={k:sum(z[k] for z in sub) for k in keys}
        summary[variant]['instances']=len(sub)
        summary[variant]['mean_nodes']=round(sum(z['nodes'] for z in sub)/len(sub),2)
        summary[variant]['mean_faces_or_marks']=round(sum(z.get('live_marks',z.get('face_count',0)) for z in sub)/len(sub),2)
    out={'seeds':list(seeds),'worlds':list(names),'summary':summary,
         'elapsed_seconds':time.perf_counter()-start,'instances':raw}
    path=Path(__file__).resolve().parents[1]/'results'/'confirmatory.json'
    path.write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
    return summary
if __name__=='__main__':run()
