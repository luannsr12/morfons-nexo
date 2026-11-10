"""Escala 6 dimensões observadas (5 ambientais + último ato)."""
from pathlib import Path
import random,json,time
from itertools import product
from integrated import InteractingMorphons, monomials,monomial_mask
ROOT=Path(__file__).resolve().parents[1]

def environment(seed):
    rng=random.Random(seed+4451)
    basis=monomials(6,2)
    functions={}
    for a in range(2):
        for j in range(5):
            # duas a quatro interações de ordem <=2 por saída, incluindo
            # história em alguma saída; informações só no simulador externo.
            possible=list(range(1,len(basis)))
            chosen=rng.sample(possible,rng.randint(2,4))
            if j==a:chosen[0]=basis.index((5,))
            coeff=sum(1<<i for i in set(chosen))
            functions[a,j]=coeff
    def world(x,a):
        mask=monomial_mask(x,basis)
        return tuple((mask&functions[a,j]).bit_count()%2 for j in range(5))
    return world,functions

def run(seeds=6):
    records=[];beg=time.perf_counter()
    cases=list(product((0,1),repeat=6))
    for seed in range(seeds):
        true,coeff=environment(seed)
        L=InteractingMorphons(6,2,5,2,seed=seed+300)
        pool=[(x,a) for x in cases for a in range(2)]
        while any(len(L._faces(L.roots[a,0],'experience'))<22 for a in range(2)):
            allow=[(x,a) for x,a in pool if len(L._faces(L.roots[a,0],'experience'))<22]
            choice=L.choose_probe(allow)
            assert choice is not None
            x,a=choice
            L.observe(x,a,true(x,a))
            pool.remove(choice)
        found=[]
        for x,a in pool:
            pred,_=L.query(x,a)
            found.append({'state':x,'action':a,'pred':pred,'expected':true(x,a)})
        summary={'seed':seed,'train':44,'holdout':len(found),
                 'correct':sum(p['pred']==p['expected'] for p in found),
                 'abstentions':sum(p['pred'] is None for p in found),
                 'errors':sum(p['pred'] is not None and p['pred']!=p['expected'] for p in found),
                 'nodes':len(L.mm.nodes),'faces':L.validate_invariants()['interaction_faces'],
                 'marks_created':L.metrics['marks_created'],
                 'marks_reused':L.metrics['marks_reused'],
                 'cases':found}
        records.append(summary)
        print(seed,summary['correct'],'/',summary['holdout'],
              'nodes',summary['nodes'],'marks new',summary['marks_created'],
              'reused',summary['marks_reused'],flush=True)
    aggregated={key:sum(r[key] for r in records) for key in
                ('train','holdout','correct','abstentions','errors','nodes','faces','marks_created','marks_reused')}
    aggregated['instances']=len(records)
    data={'summary':aggregated,'records':records,'elapsed_seconds':time.perf_counter()-beg}
    (ROOT/'results'/'scale.json').write_text(json.dumps(data,indent=2,ensure_ascii=False))
    print('SUMMARY',json.dumps(aggregated))
    return data
if __name__=='__main__':run()
