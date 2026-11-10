from __future__ import annotations
import json,random
from pathlib import Path
from spectral_faces import SpectralFaces
from evaluate import all_states,N,A

def random_table_case(seed):
    rng=random.Random(99173+seed)
    table={(a,s):tuple(rng.randrange(2) for _ in range(N)) for a in range(A) for s in all_states()}
    L=SpectralFaces(N,A,max_degree=2,seed=seed)
    train=[];hold=[]
    for a in range(A):
        seq=all_states();rng.shuffle(seq)
        train.extend((s,a,table[(a,s)]) for s in seq[:24])
        hold.extend((s,a,table[(a,s)]) for s in seq[24:])
    rng.shuffle(train)
    for s,a,t in train:L.observe(s,a,t)
    rows=[]
    for s,a,t in hold:
        pred,why=L.query(s,a)
        rows.append({'reason':why['reason'],'predicted':pred,'truth':t,
                     'correct':pred==t,'answered':pred is not None})
    return {'seed':seed,'correct':sum(r['correct'] for r in rows),
            'answered':sum(r['answered'] for r in rows),'holdout':len(rows),
            'reasons':{z:sum(r['reason']==z for r in rows) for z in set(r['reason'] for r in rows)}}

def run():
    rows=[random_table_case(seed) for seed in range(20)]
    out={'instances':20,'train':20*48,'holdout':sum(r['holdout'] for r in rows),
         'correct':sum(r['correct'] for r in rows), 'answered':sum(r['answered'] for r in rows),
         'cases':rows}
    path=Path(__file__).resolve().parents[1]/'results'/'negative_controls.json'
    path.write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print('SUMMARY',json.dumps({k:v for k,v in out.items() if k!='cases'},ensure_ascii=False))
    return out
if __name__=='__main__':run()
