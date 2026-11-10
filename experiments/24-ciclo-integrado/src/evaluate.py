"""Mundo externo ao aprendiz: só o avaliador conhece os efeitos verdadeiros."""
from __future__ import annotations
from pathlib import Path
from itertools import product
from collections import Counter
import random,time,json,copy
from integrated import InteractingMorphons, monomials,monomial_mask,echelon
ROOT=Path(__file__).resolve().parents[1]


def world(kind,x,a,seed):
    """Quatro famílias, com permutações/inversões específicas da semente.

    As variantes são isomórficas (não contar como famílias independentes),
    mas as relações nos canais físicos diferem por semente. O aprendiz não
    importa esta função: ela é APENAS a física do simulador de avaliação.
    """
    u,v,w,h=map(int,x)
    if seed:
        rng=random.Random(1024+kind*911+seed*1777)
        perm=list(range(3));rng.shuffle(perm)
        invert=[rng.randrange(2) for _ in range(3)]
        invert_h=rng.randrange(2);invert_a=rng.randrange(2)
        inp=[x[perm[i]]^invert[i] for i in range(3)]+[h^invert_h]
        aa=a^invert_a
    else:
        perm=[0,1,2];invert=[0,0,0];inp=[u,v,w,h];aa=a
    u,v,w,h=map(int,inp)
    if kind==0:
        if aa==0:y=(u^1,v^(u&h),w^(u&v))
        else:y=(u^(v&h),v^1,w^h^(u&w))
    elif kind==1:
        if aa==0:y=(u^(v&w)^1,v^h,w^(u&h))
        else:y=(u^h,v^(u&w)^1,w^(v&h))
    elif kind==2:
        if aa==0:y=(u^(w&h),v^1,w^(u&v)^h)
        else:y=(u^1,v^(u&h),w^(v&h))
    elif kind==3:
        if aa==0:y=(u^1,v^(w&h),w^(u&v))
        else:y=(u^(v&w),v^1,w^(u&h))
    else:raise ValueError(kind)
    restored=[0,0,0]
    for i,j in enumerate(perm):restored[j]=y[i]^invert[i]
    return tuple(restored)


def contexts():
    return list(product((0,1),repeat=4))

def choose_inputs(rng,n_keep=12,nfeat=4,degree=2,active=True):
    samples=contexts();rng.shuffle(samples)
    if not active:return samples[:n_keep],samples[n_keep:]
    ms=monomials(nfeat,degree)
    selected=[];rank=0
    for s in samples:
        masks=[(monomial_mask(v,ms),0) for v in selected+[s]]
        piv=echelon(masks)
        if len(piv)>rank:
            rank=len(piv);selected.append(s)
    assert rank==len(ms),(rank,len(ms))
    if len(selected)>n_keep:raise AssertionError('insufficient budget')
    remaining=[s for s in samples if s not in selected]
    selected+=remaining[:n_keep-len(selected)]
    return selected,[s for s in samples if s not in selected]


def simulate(start,h,actions,kind,seed):
    state=tuple(start);hist=h
    for a in actions:
        state=world(kind,state+(hist,),a,seed);hist=a
    return state,hist


def evaluate_one(kind,seed,active=True,n_keep=11):
    rng=random.Random(85101+seed*119+kind*1009)
    task_rng=random.Random(935123+seed*203+kind*211)
    L=InteractingMorphons(4,2,3,max_degree=2,seed=seed)
    inputs={}
    if active:
        # A escolha é gerada pelo núcleo K usando marcas que outros Mórfons
        # inscreveram, não por uma ordem de amostras previamente programada.
        candidate_pool=[(x,a) for a in range(2) for x in contexts()]
        while any(len([e for e in L.events if any(True for f in L._faces(L.roots[a,0],'experience')
                       if f['payload']['episode']==e)])<n_keep for a in range(2)):
            # a disponibilidade do laboratório impede consultas a entradas
            # além das condições fisicamente resetáveis; aqui todas são.
            allowed=[(x,a) for x,a in candidate_pool
                     if len(L._faces(L.roots[a,0],'experience'))<n_keep]
            chosen=L.choose_probe(allowed)
            assert chosen is not None
            x,a=chosen
            L.observe(x,a,world(kind,x,a,seed))
            candidate_pool.remove((x,a))
        for a in range(2):
            used={tuple(f['payload']['before']) for f in L._faces(L.roots[a,0],'experience')}
            inputs[a]=([x for x in contexts() if x in used],[x for x in contexts() if x not in used])
    else:
        episodes=[]
        for a in range(2):
            train,test=choose_inputs(rng,n_keep=n_keep,active=False)
            inputs[a]=(train,test)
            episodes.extend((x,a,world(kind,x,a,seed)) for x in train)
        rng.shuffle(episodes)
        for x,a,y in episodes:L.observe(x,a,y)
    checks=[]
    for a,(train,test) in inputs.items():
        for x in test:
            got,proof=L.query(x,a);expect=world(kind,x,a,seed)
            checks.append({'x':x,'a':a,'expected':expect,'predicted':got,
                           'reason':proof['reason'],'correct':got==expect})
    # Uma ação real é escolhida, antecipada internamente, executada e observada.
    # Essa consequência volta para a MESMA memória, inclusive quando é holdout.
    # Selecionar uma tarefa com dois passos REALMENTE necessários no mundo.
    # A escolha é feita SOMENTE PELO AVALIADOR, não alimenta o aprendiz com o plano.
    candidates=[]
    for initial in contexts():
        s0,h0=initial[:3],initial[3]
        near={simulate(s0,h0,(a,),kind,seed)[0] for a in range(2)}
        farther={simulate(s0,h0,(a,b),kind,seed)[0]
                 for a in range(2) for b in range(2)}
        for g in sorted(farther-near-{s0}):candidates.append((s0,h0,g))
    if not candidates:raise AssertionError('No genuine 2-step task in fixture')
    live_s,live_h,live_target=task_rng.choice(candidates)
    L.start_session(live_h)
    live_plan,live_trace=L.choose_plan(live_s,L.current_history(),live_target,max_depth=3)
    live_steps=[]
    if live_plan is not None:
        for live_action in live_plan:
            before=live_s+(L.current_history(),)
            predicted,thought=L.query(before,live_action,record_imagination=True)
            actual=world(kind,before,live_action,seed)
            L.observe(before,live_action,actual,live=True)
            live_steps.append({'input':before,'action':live_action,
                               'predicted':predicted,'observed':actual,
                               'matched':predicted==actual})
            live_s=actual;live_h=L.current_history()
    # Atividade integrada: a entrada tem histórico do próprio motor (h),
    # ao simular, a mesma atividade atualiza esse histórico com a ação executada.
    plans=[]
    for _ in range(24):
        x=task_rng.choice(contexts());s=x[:3];h=x[3]
        actions=tuple(task_rng.randrange(2) for _ in range(task_rng.randint(1,3)))
        goal,_=simulate(s,h,actions,kind,seed)
        if goal==s:continue
        plan,trace=L.choose_plan(s,h,goal,max_depth=3)
        end,_=simulate(s,h,plan,kind,seed) if plan is not None else (s,h)
        plans.append({'start':s,'history':h,'goal':goal,'planned':plan,
                      'actual':end,'success':plan is not None and end==goal})
    # Sinal de consequência desejado sem alvo de estado completo.
    desires=[]
    for _ in range(12):
        x=task_rng.choice(contexts());s=x[:3];h=x[3]
        channel=task_rng.randrange(3);val=1-s[channel]
        p,trace=L.choose_for_signal(s,h,channel,val,max_depth=3)
        reached,_=simulate(s,h,p,kind,seed) if p is not None else (s,h)
        desires.append({'start':s,'hist':h,'channel':channel,'desired':val,
                        'plan':p,'success':p is not None and reached[channel]==val})
    # Causalidade das MARCAS: remove marca certificada e contrasta com marca não usada.
    ablations=[]
    for c in checks:
        if c['predicted'] is None:continue
        x,a=c['x'],c['a'];base=c['predicted']
        _,trace=L.query(x,a)
        if trace['marks']:
            got,_=L.query(x,a,ablate=[trace['marks'][0]])
            ablations.append({'active_mark_changed':got!=base,
                              'mark':trace['marks'][0],'before':base,'after':got})
        if len(ablations)>=4:break
    no_pulse,_=L.query(contexts()[0],0,block_pulses=True)
    invariants=L.validate_invariants()
    # Restaurar e repetir os holdouts
    restored=InteractingMorphons.restore(L.snapshot())
    roundtrip=all(restored.query(c['x'],c['a'])[0]==c['predicted'] for c in checks)
    # contexto de fato útil: caso existam entradas iguais em estado físico e ação,
    # mas diferentes h, que produzem consequências distintas.
    contrasted=sum(world(kind,tuple(s)+(0,),a,seed)!=world(kind,tuple(s)+(1,),a,seed)
                   for s in product((0,1),repeat=3) for a in range(2))
    # controle sem informação da história: ambiguidades reais nas mesmas ações.
    history_ambiguities=contrasted
    return {'kind':kind,'seed':seed,'active':active,'train':sum(len(inputs[a][0]) for a in range(2)),
      'holdout':len(checks),'correct':sum(c['correct'] for c in checks),
      'errors':sum(c['predicted'] is not None and not c['correct'] for c in checks),
      'abstentions':sum(c['predicted'] is None for c in checks),
      'plans':len(plans),'plans_success':sum(p['success'] for p in plans),
      'desires':len(desires),'desires_success':sum(p['success'] for p in desires),
      'context_sensitive_pairs':history_ambiguities,'faces':invariants['interaction_faces'],
      'nodes':len(L.mm.nodes),'no_self_edit':invariants['no_self_edits'],
      'constant_nucleus':invariants['all_nuclei_constant'],'snapshot_equal':roundtrip,
      'pulse_blocked':no_pulse is None,
      'ablated_marks':len(ablations),'ablation_effects':sum(z['active_mark_changed'] for z in ablations),
      'individual_tests':checks,'individual_plans':plans,'desire_tests':desires,
      'mutations_count':len(L.mutations),'model_faces':sum(len(L._faces(r,'model')) for r in L.roots.values()),
      'live_plan':live_plan,'live_steps':live_steps,'live_reached_goal':live_s==live_target,
      'questions':L.metrics['questions'],'thoughts':L.metrics['thoughts'],
      'feedback_experiences':len(live_steps)}


def run(n_seeds=6):
    rows=[];begin=time.perf_counter()
    for kind in range(4):
        for seed in range(n_seeds):
            for active in (True,False):
                r=evaluate_one(kind,seed,active)
                rows.append(r)
                print(kind,seed,'rank' if active else 'random',r['correct'],'/',r['holdout'],
                      'plans',r['plans_success'],'/',r['plans'],
                      'desires',r['desires_success'],'/',r['desires'],flush=True)
    summary={}
    for active in (True,False):
        ss=[r for r in rows if r['active']==active]
        summary['rank' if active else 'random']={k:sum(r[k] for r in ss) for k in
          ('train','holdout','correct','errors','abstentions','plans','plans_success',
           'desires','desires_success','context_sensitive_pairs','ablated_marks','ablation_effects',
           'questions','thoughts','feedback_experiences')}
        summary['rank' if active else 'random']['instances']=len(ss)
        summary['rank' if active else 'random']['all_nuclei_constant']=all(r['constant_nucleus'] for r in ss)
        summary['rank' if active else 'random']['all_no_self_edits']=all(r['no_self_edit'] for r in ss)
        summary['rank' if active else 'random']['all_snapshots_equal']=all(r['snapshot_equal'] for r in ss)
    data={'summary':summary,'elapsed_seconds':time.perf_counter()-begin,'instances':rows}
    out=ROOT/'results'/'integrated.json';out.write_text(json.dumps(data,indent=2,ensure_ascii=False))
    print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
    return data
if __name__=='__main__':
    import sys
    run(int(sys.argv[1]) if len(sys.argv)>1 else 6)
