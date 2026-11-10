from __future__ import annotations
import json,random
from pathlib import Path
from evaluate import world,all_states,N,A
from spectral_faces import SpectralFaces

def run_one(name,seed):
    rng=random.Random(72031+seed*17+sum(map(ord,name)))
    L=SpectralFaces(N,A,max_degree=2,seed=seed)
    states=all_states();splits={}
    for a in range(A):
        q=states[:];rng.shuffle(q);splits[a]=(q[:24],q[24:])
    obs=[(s,a,world(name,s,a)) for a in range(A) for s in splits[a][0]]
    rng.shuffle(obs)
    for s,a,t in obs:L.observe(s,a,t)
    stats={'world':name,'seed':seed,'queries':0,'without_rays':0,
           'ablated_active_mark_changed':0,'active_mark_tests':0,
           'ablated_inactive_mark_unchanged':0,'inactive_mark_tests':0,
           'face_deleted_blocks':0}
    for a in range(A):
        for s in splits[a][1]:
            out,p=L.query(s,a)
            assert out==world(name,s,a)
            stats['queries']+=1
            without,_=L.query(s,a,rays=False)
            stats['without_rays']+=int(without is None)
            root=L.roots[(a,0)]
            deleted,_=L.query(s,a,ablate_face=root)
            stats['face_deleted_blocks']+=int(deleted is None)
            for j,used in enumerate(p['marks']):
                if not used:continue
                m=used[0];got,_=L.query(s,a,ablate_mark=m)
                stats['active_mark_tests']+=1
                stats['ablated_active_mark_changed']+=int(got!=out)
            live=[u for r in L.roots.values() for u in L.mm.nodes[r].facets[0]['marks']]
            active=set(u for j in p['marks'] for u in j)
            inactive=next((u for u in live if u not in active),None)
            if inactive is not None:
                got,_=L.query(s,a,ablate_mark=inactive)
                stats['inactive_mark_tests']+=1
                stats['ablated_inactive_mark_unchanged']+=int(got==out)
    return stats

def run():
    rows=[]
    for name in ['toggle_cond','context','parity','asym','history']:
        for seed in range(3):rows.append(run_one(name,seed))
    keys=['queries','without_rays','active_mark_tests','ablated_active_mark_changed',
         'inactive_mark_tests','ablated_inactive_mark_unchanged','face_deleted_blocks']
    summary={k:sum(d[k] for d in rows) for k in keys}
    dest=Path(__file__).resolve().parents[1]/'results'/'causal_ablations.json'
    dest.write_text(json.dumps({'summary':summary,'cases':rows},ensure_ascii=False,indent=2))
    print('SUMMARY',json.dumps(summary,ensure_ascii=False))
    return summary
if __name__=='__main__':run()
