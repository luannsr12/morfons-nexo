"""Experimentos adversariais integrados; nenhum modelo verdadeiro entra no aprendiz."""
from __future__ import annotations
import json,random
from pathlib import Path
from itertools import product
from integrated import InteractingMorphons
from evaluate import world,contexts
ROOT=Path(__file__).resolve().parents[1]


def degree_three_world(x,a):
    u,v,w,h=x
    y=list(world(0,x,a,0))
    if a==0:y[0]^=u*v*h
    else:y[1]^=u*w*h
    return tuple(y)


def evolving_degree(seed):
    L=InteractingMorphons(4,2,3,max_degree=3,seed=seed)
    all_inputs=[(x,a) for x in contexts() for a in range(2)]
    phases=[]
    intervention=None
    for limit in (11,15):
        while min(len(L._faces(L.roots[a,0],'experience')) for a in range(2))<limit:
            available=[(x,a) for x,a in all_inputs
                       if len(L._faces(L.roots[a,0],'experience'))<limit]
            candidate=L.choose_probe(available)
            assert candidate is not None
            x,a=candidate
            L.observe(x,a,degree_three_world(x,a))
            all_inputs.remove((x,a))
        tested=[]
        for x,a in all_inputs:
            guess,reason=L.query(x,a)
            tested.append({'input':x,'action':a,'pred':guess,
                           'real':degree_three_world(x,a),
                           'reason':reason['reason']})
        phases.append({'examples_per_action':limit,
                       'tested':len(tested),
                       'correct':sum(v['pred']==v['real'] for v in tested),
                       'wrong':sum(v['pred'] is not None and v['pred']!=v['real'] for v in tested),
                       'abstain':sum(v['pred'] is None for v in tested),
                       'current_degrees':{str(a):[L._last_model(L.roots[a,j])['degree'] for j in range(3)] for a in range(2)},
                       'cases':tested})
        if limit==11:
            bad=next((v for v in tested if v['pred'] is not None and v['pred']!=v['real']),None)
            if bad:
                # Uma antecipação errada é confrontada com uma AÇÃO REAL:
                # o evento produzido pelo mundo modifica por outro Mórfon
                # as marcas do receptor original, não o seu núcleo.
                L.start_session(bad['input'][3])
                before=len(L.events)
                thought,_=L.query(bad['input'],bad['action'],record_imagination=True)
                L.observe(bad['input'],bad['action'],bad['real'],live=True)
                all_inputs.remove((bad['input'],bad['action']))
                intervention={'action':bad['action'],'input':bad['input'],
                              'prediction':thought,'observation':bad['real'],
                              'new_episodes':len(L.events)-before,
                              'current_history':L.current_history()}
    return {'seed':seed,'phases':phases,'intervention':intervention,
            'nucleus_unchanged':L.validate_invariants()['all_nuclei_constant']}


def contradictory_observation():
    L=InteractingMorphons(4,2,3,2,seed=101)
    x=(1,0,1,0);a=0;correct=world(0,x,a,0)
    L.observe(x,a,correct)
    initial=L.query(x,a)[0]
    changed=(correct[0]^1,correct[1],correct[2])
    L.observe(x,a,changed)
    after,trace=L.query(x,a)
    observations=L._faces(L.roots[a,0],'experience')
    assert observations[0]['payload']['observed_output']!=observations[1]['payload']['observed_output']
    return {'before':initial,'after':after,'reason':trace['reason'],
            'retained_conflicting_events':len(observations),
            'all_no_self_edits':L.validate_invariants()['no_self_edits']}


def physical_edge_ablation():
    L=InteractingMorphons(4,2,3,2,seed=102)
    from evaluate import choose_inputs
    rng=random.Random(110)
    holdout=[]
    for a in range(2):
        train,test=choose_inputs(rng,11,active=True)
        for x in train:L.observe(x,a,world(0,x,a,0))
        holdout.extend((x,a) for x in test)
    x,a=holdout[0]
    original,trace=L.query(x,a)
    assert original is not None
    uid=trace['marks'][0]
    root=L.mm.nodes[uid].ports[0]
    assert root in L.mm.nodes[uid].ports
    # Intervenção experimental DIRETAMENTE NO GRAFO DE PORTAS, não no output.
    L.mm.cache[root].discard(uid)
    damaged,trace2=L.query(x,a)
    L.mm.cache[root].add(uid)
    restored,trace3=L.query(x,a)
    # Perturbar conexão de uma marca que NÃO é usada na consulta.
    inactive=[]
    for r in L.roots.values():
        model=L._last_model(r)
        if model:
            inactive += [mid for mid in model['marks'] if mid not in trace['marks']]
    unused_changed=False
    if inactive:
        other=inactive[0];otherroot=L.mm.nodes[other].ports[0]
        L.mm.cache[otherroot].discard(other)
        unused_changed=L.query(x,a)[0]!=restored
        L.mm.cache[otherroot].add(other)
    return {'original':original,'without_required_edge':damaged,
            'after_restore':restored,'changed':original!=damaged,
            'restored_exactly':original==restored,'irrelevant_edge_changed_result':unused_changed,
            'edge':(root,uid)}


def context_lower_bound():
    # Mesmo presente físico + mesma ação -> dois resultados em histórias distintas.
    lower=[]
    for kind in range(4):
        disagreements=[]
        for bits in product((0,1),repeat=3):
            for a in range(2):
                p0=world(kind,bits+(0,),a,0)
                p1=world(kind,bits+(1,),a,0)
                if p0!=p1:disagreements.append({'state':bits,'action':a,'h0':p0,'h1':p1})
        lower.append({'kind':kind,'indistinguishable_without_history':len(disagreements),
                      'min_wrong_on_full_pairs':len(disagreements),
                      'examples':disagreements[:3]})
    return lower


def run():
    phases=[evolving_degree(i) for i in range(4)]
    results={'degree_three':phases,'contradiction':contradictory_observation(),
             'edge_ablation':physical_edge_ablation(),'history_collapse':context_lower_bound()}
    (ROOT/'results'/'adversarial.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
    print('DEGREE3',[(z['seed'],[(p['examples_per_action'],p['correct'],p['wrong'],p['abstain']) for p in z['phases']]) for z in phases])
    print('CONFLICT',results['contradiction'])
    print('EDGE',results['edge_ablation'])
    print('HISTORY',[(z['kind'],z['indistinguishable_without_history']) for z in results['history_collapse']])
    return results
if __name__=='__main__':run()
