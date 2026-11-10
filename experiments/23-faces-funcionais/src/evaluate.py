"""Avaliação pré-registrada no código: mundos e propriedades, sem passar função ao aprendiz."""
from __future__ import annotations
import json,random,sys,time
from pathlib import Path
from collections import Counter,deque
from facets import FaceWorldLearner

N=5;A=2

def world(kind,s,a,variant=0):
    x=list(s); p,q,r,h,z=s
    if kind=='toggle_cond':
        if a==0:x[0]=1-p
        else:x[1]=q^p
    elif kind=='context':
        if a==0:x[0]=p^(q&h)
        else:x[1]=q^(p^r)
    elif kind=='parity':
        if a==0:x[0]=p^q^r
        else:x[2]=r^p^q
    elif kind=='asym':
        if a==0:x[0]=p|q
        else:x[1]=p^q;x[2]=r^q
    elif kind=='history':
        if a==0:x[0]=p^(q&h)
        else:x[1]=q^(p&h)
    else:raise ValueError(kind)
    return tuple(x)

def all_states():return [tuple((i>>j)&1 for j in range(N)) for i in range(1<<N)]

def plans(learner,start,goal,max_steps=3):
    """Agendador mecânico: estados e transições exclusivamente da ativação de faces.
    Não vê world(), experiências nem tabelas; recebe apenas respostas certificadas.
    """
    if start==goal:return (), {'calls':0}
    frontier=deque([(start,())]);seen={start};calls=0
    while frontier:
        state,path=frontier.popleft()
        if len(path)>=max_steps:continue
        for a in range(A):
            out,proof=learner.query(state,a);calls+=1
            if out is None:continue
            seq=path+(a,)
            if out==goal:return seq,{'calls':calls,'proof':proof}
            if out not in seen:seen.add(out);frontier.append((out,seq))
    return None,{'calls':calls}

def evaluate_one(kind,seed,morph,*,compress=False,optimal=False):
    rng=random.Random(72031+seed*17+sum(ord(c) for c in kind))
    L=FaceWorldLearner(N,A,morph=morph,seed=seed)
    states=all_states();splits={};train_count=0
    for a in range(A):
        seq=states[:];rng.shuffle(seq)
        splits[a]=[seq[:24],seq[24:]]
    # intercalar ações e estados, sem agrupar para favorecer a aprendizagem
    episodes=[(s,a,world(kind,s,a)) for a in range(A) for s in splits[a][0]]
    rng.shuffle(episodes)
    for s,a,t in episodes:L.observe(s,a,t)
    assert len(episodes)==48
    if compress:L.compress_faces(penalty=3.0)
    if optimal:L.consolidate_optimal(penalty=2.6)
    tests=[]; evidence=[]
    for a in range(A):
        for s in splits[a][1]:
            out,proof=L.query(s,a)
            want=world(kind,s,a)
            tests.append({'action':a,'state':list(s),'expected':list(want),
                          'predicted':list(out) if out is not None else None,
                          'correct':out==want,'reason':proof['reason'],
                          'certified_faces':proof.get('faces',[])})
    assert len(tests)==16
    # um mesmo alvo de estados gerado somente pelo mundo externo, nunca dado ao aprendiz
    jobs=[];trials=0
    for _ in range(35):
        s=rng.choice(states)
        actions=tuple(rng.randrange(A) for _ in range(rng.choice((1,2,3))))
        target=s
        for a in actions:target=world(kind,target,a)
        if s==target:continue
        plan,info=plans(L,s,target)
        reached=s
        if plan is not None:
            for a in plan:reached=world(kind,reached,a)
        jobs.append({'start':list(s),'goal':list(target),'producing_actions':actions,
                     'plan':plan,'reached':list(reached),'found':plan is not None,
                     'success':plan is not None and reached==target,
                     'calls':info['calls']})
    correct=sum(t['correct'] for t in tests)
    answered=sum(t['predicted'] is not None for t in tests)
    coverage=answered/len(tests)
    # perturba a conclusão por remoção causal da face referenciada, num caso respondido
    ablations=[]
    for t in tests:
        if t['predicted'] is None:continue
        out1,trace=L.query(tuple(t['state']),t['action'])
        j=0;face_uid=trace['faces'][j]
        out2,_=L.query(tuple(t['state']),t['action'],ablation_face=face_uid)
        out3,_=L.query(tuple(t['state']),t['action'],rays=False)
        ablations.append({'face':face_uid,'baseline':list(out1),
                          'without_face':out2,'without_rays':out3})
        if len(ablations)>=4:break
    return {'world':kind,'seed':seed,'adaptive_faces':morph,'compressed':compress,'optimal':optimal,'optimal_subdivisions':L.stats['optimal_subdivisions'],
            'train':len(episodes),'holdout':len(tests),'correct':correct,'answered':answered,
            'errors':answered-correct,'abstentions':len(tests)-answered,
            'coverage':coverage,'face_count':L.face_count(),'subdivisions':L.stats['subdivisions'],
            'nodes':len(L.mm.nodes),'plans':len(jobs),'found':sum(j['found'] for j in jobs),
            'success':sum(j['success'] for j in jobs),'ablations':ablations,
            'test_cases':tests,'plan_cases':jobs}

def run(seeds=5):
    out=[];start=time.perf_counter()
    for world_name in ['toggle_cond','context','parity','asym','history']:
        for seed in range(seeds):
            for variant in (True,False):
                x=evaluate_one(world_name,seed,variant)
                out.append(x)
                print(world_name,seed,'morph',variant,'test',x['correct'],'/',x['holdout'],
                      'answered',x['answered'],'plans',x['success'],'/',x['plans'],
                      'faces',x['face_count'],'splits',x['subdivisions'],flush=True)
    summary={}
    for variant in (True,False):
        sub=[v for v in out if v['adaptive_faces']==variant]
        agg=lambda k:sum(v[k] for v in sub)
        summary[str(variant)]={'instances':len(sub),'train':agg('train'),'holdout':agg('holdout'),
                  'correct':agg('correct'),'answered':agg('answered'),'errors':agg('errors'),
                  'abstentions':agg('abstentions'),'plans':agg('plans'),
                  'found':agg('found'),'success':agg('success'),
                  'subdivisions':agg('subdivisions'),'face_count':agg('face_count')}
    path=Path(__file__).resolve().parents[1]/'results'/'evaluation.json'
    path.write_text(json.dumps({'summary':summary,'elapsed_seconds':time.perf_counter()-start,
                                'instances':out},indent=2,ensure_ascii=False))
    print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
    print('SAVED',path,flush=True)
    return summary

if __name__=='__main__':run(int(sys.argv[1]) if len(sys.argv)>1 else 5)
