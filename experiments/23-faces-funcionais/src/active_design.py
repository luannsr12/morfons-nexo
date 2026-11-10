"""Laboratório de escolha ativa de experiências por aumento de posto relacional.
Acesso a estados iniciais reinicializáveis é uma capacidade DO LABORATÓRIO, não
uma capacidade de navegação no mundo atribuída ao aprendiz.
"""
from __future__ import annotations
import json,random
from pathlib import Path
from spectral_faces import SpectralFaces,terms,phi,eliminate,uniquely_determined
from evaluate import world,all_states,N,A

def pick_rank(learner,pairs):
    ms=terms(N,2);bases={}
    for a in range(A):
        eps=[learner.mm.nodes[e].facets[0] for e in learner.episodes if learner.mm.nodes[e].facets[0]['action']==a]
        bases[a]=eliminate([(phi(z['before'],ms),0) for z in eps]) or {}
    available=[]
    for s,a in pairs:
        row=phi(s,ms)
        novel=uniquely_determined(row,bases[a]) is None
        if novel:available.append((s,a))
    return min(available,key=lambda p:(p[1],p[0])) if available else None

def run_one(kind,seed,active):
    states=all_states();rng=random.Random(seed*9327+sum(map(ord,kind)))
    L=SpectralFaces(N,A,max_degree=2,seed=seed)
    candidates=[(s,a) for a in range(A) for s in states]
    for step in range(32):
        if active:
            pair=pick_rank(L,candidates)
            if pair is None:break
        else:
            pair=rng.choice(candidates)
        candidates.remove(pair)
        s,a=pair
        L.observe(s,a,world(kind,s,a))
    out=[]
    for a in range(A):
        for s in states:
            pred,proof=L.query(s,a)
            out.append((pred==world(kind,s,a),pred is not None))
    return {'world':kind,'seed':seed,'active':active,'episodes':len(L.episodes),
        'correct':sum(z[0] for z in out),'answered':sum(z[1] for z in out),'total':len(out)}

def run():
    all_rows=[]
    for w in ['toggle_cond','context','parity','asym','history']:
        for seed in range(10):
            for mode in (False,True):all_rows.append(run_one(w,seed,mode))
    summary={}
    for mode in (False,True):
        subset=[r for r in all_rows if r['active']==mode]
        summary[str(mode)]={k:sum(v[k] for v in subset) for k in ('episodes','correct','answered','total')}
        summary[str(mode)]['instances']=len(subset)
    outfile=Path(__file__).resolve().parents[1]/'results'/'active_design.json'
    outfile.write_text(json.dumps({'summary':summary,'cases':all_rows},indent=2,ensure_ascii=False))
    print('SUMMARY',json.dumps(summary,ensure_ascii=False))
    return summary
if __name__=='__main__':run()
