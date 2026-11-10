from __future__ import annotations
import json,random,sys,time
from pathlib import Path
from evaluate import world,all_states,plans,N,A
from spectral_faces import SpectralFaces

def evaluate_one(kind,seed,max_degree=2):
    rng=random.Random(72031+seed*17+sum(ord(c) for c in kind))
    L=SpectralFaces(N,A,max_degree=max_degree,seed=seed)
    states=all_states();splits={}
    for a in range(A):
        seq=states[:];rng.shuffle(seq)
        splits[a]=[seq[:24],seq[24:]]
    episodes=[(s,a,world(kind,s,a)) for a in range(A) for s in splits[a][0]]
    rng.shuffle(episodes)
    for s,a,t in episodes:L.observe(s,a,t)
    tests=[]
    for a in range(A):
        for s in splits[a][1]:
            out,proof=L.query(s,a);want=world(kind,s,a)
            tests.append({'action':a,'state':list(s),'expected':list(want),
                          'predicted':list(out) if out is not None else None,
                          'correct':out==want,'reason':proof['reason']})
    jobs=[]
    for _ in range(35):
        s=rng.choice(states)
        actions=tuple(rng.randrange(A) for _ in range(rng.choice((1,2,3))))
        goal=s
        for a in actions:goal=world(kind,goal,a)
        if s==goal:continue
        plan,pr=plans(L,s,goal)
        reached=s
        if plan is not None:
            for a in plan:reached=world(kind,reached,a)
        jobs.append({'start':list(s),'goal':list(goal),'plan':plan,'found':plan is not None,
                     'success':plan is not None and reached==goal})
    marks=[]
    for a in range(A):
        for j in range(N):
            f=L.mm.nodes[L.roots[(a,j)]].facets[0]
            marks.append({'action':a,'channel':j,'degree':f['degree'],
                    'rank':f.get('rank'),'terms':len(f['basis']),
                    'nonzero_marks':len(f['marks'])})
    ablations=[]
    for a in range(A):
        for s in splits[a][1]:
            out,trace=L.query(s,a)
            if out is None:continue
            ablated=None
            for j,uids in enumerate(trace['marks']):
                if not uids:continue
                ablated,_=L.query(s,a,ablate_mark=uids[0]);
                if ablated!=out:
                    ablations.append({'action':a,'state':list(s),'mark':uids[0],
                        'baseline':list(out),'ablation':list(ablated),'channel':j})
                    break
            if len(ablations)>=4:break
        if len(ablations)>=4:break
    return {'world':kind,'seed':seed,'degree_bound':max_degree,'train':len(episodes),
        'holdout':len(tests),'correct':sum(t['correct'] for t in tests),
        'answered':sum(t['predicted'] is not None for t in tests),
        'errors':sum(t['predicted'] is not None and not t['correct'] for t in tests),
        'abstentions':sum(t['predicted'] is None for t in tests),
        'plans':len(jobs),'found':sum(j['found'] for j in jobs),
        'success':sum(j['success'] for j in jobs),'nodes':len(L.mm.nodes),
        'live_marks':L.count_live_marks(),'fit_diagnostics':marks,
        'ablations':ablations,'test_cases':tests,'plan_cases':jobs}

def run(seeds=5):
    data=[];start=time.perf_counter()
    for name in ['toggle_cond','context','parity','asym','history']:
        for seed in range(seeds):
            for degree in (1,2):
                row=evaluate_one(name,seed,degree)
                data.append(row)
                print(name,seed,'degree',degree,'test',row['correct'],'/',row['holdout'],
                    'answer',row['answered'],'plans',row['success'],'/',row['plans'],
                    'marks',row['live_marks'],'nodes',row['nodes'],flush=True)
    summary={}
    for degree in (1,2):
        sub=[x for x in data if x['degree_bound']==degree]
        summary[str(degree)]={k:sum(x[k] for x in sub) for k in
            ('train','holdout','correct','answered','errors','abstentions','plans','found','success','live_marks')}
        summary[str(degree)]['instances']=len(sub)
    path=Path(__file__).resolve().parents[1]/'results'/'spectral_eval.json'
    path.write_text(json.dumps({'summary':summary,'elapsed_seconds':time.perf_counter()-start,
        'instances':data},indent=2,ensure_ascii=False))
    print('SUMMARY',json.dumps(summary,ensure_ascii=False))
    return summary
if __name__=='__main__':run(int(sys.argv[1]) if len(sys.argv)>1 else 5)
