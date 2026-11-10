from __future__ import annotations
import json,random,sys,time
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from grounded import ContextLearner,MorphGraph,tid,tok
from laboratorio import train,worlds,run_eval

ROOT=Path(__file__).resolve().parents[1]

def test_world(m,seed,mode='normal'):
    ep=worlds(seed,test=True);g=MorphGraph();rows=[]
    for text,*_ in ep['facts']:
        r=m.ingest(text,g)
        if mode=='swap_time' and r['kind']=='observed' and r['relation']=='zeta':
            orig=g.mem.nodes[r['node']];orig.facets[0]['current']=False
            g.add(r['subject'],r['relation'],r['value'],'fase0' if r['context']=='fase1' else 'fase1')
        if mode=='erase_facts' and r['kind']=='observed':
            g.mem.nodes[r['node']].facets[0]['current']=False
    for q,src,target,expect,cat in ep['questions']+ep['composed']+ep['followups']:
        if cat.startswith('contexto_sem_nome'):g.set_focus(src)
        a=m.ask(q,g)
        rows.append({'type':cat,'correct':tok(a['answer'] or '')==tok(expect),'answer':a['answer'],'reason':a['reason']})
    return rows

def summary(rows):
    agg={}
    for r in rows:
        x=agg.setdefault(r['type'],[0,0]);x[0]+=r['correct'];x[1]+=1
    return {'correct':sum(z['correct'] for z in rows),'total':len(rows),
            'by_type':{k:f'{v[0]}/{v[1]}' for k,v in sorted(agg.items())},
            'abstention':sum(z['answer'] is None for z in rows)}

def main():
    r=ROOT/'results';m=ContextLearner.load(r/'memoria_treinada.json')
    tests={}
    tests['normal']=summary([z for i in range(20) for z in test_world(m,50000+i)])
    tests['swap_time']=summary([z for i in range(20) for z in test_world(m,50000+i,'swap_time')])
    tests['erase_facts']=summary([z for i in range(20) for z in test_world(m,50000+i,'erase_facts')])
    refs=[n for n in m.mem.nodes.values() if n.kind=='reference_template']
    for n in refs:n.promoted=False
    tests['without_recursive_composition']=summary([z for i in range(20) for z in test_world(m,50000+i)])
    for n in refs:n.promoted=True
    tests['curve']=[]
    for n in [1,2,5,10,25,50,100,240]:
        t0=time.perf_counter();mod=ContextLearner();train(mod,n)
        ev=summary([z for i in range(10) for z in test_world(mod,70000+i)])
        tests['curve'].append({'worlds':n,'questions_supervised':mod.count['questions'],
                               'correct':ev['correct'],'total':ev['total'],'by_type':ev['by_type'],
                               'morphons':len(mod.mem.nodes),'time_seconds':round(time.perf_counter()-t0,2)})
    tests['hard_phrases']={}
    ep=worlds(123456,test=True);g=MorphGraph()
    for t,*_ in ep['facts']:m.ingest(t,g)
    person=ep['facts'][0][1]
    examples=['Poderia me informar a cidade onde mora '+person+'?',
              'Você sabe o endereço de '+person+'?',
              'O que '+person+' aprendeu sobre a chuva?',
              'Por que o ser humano interpreta contextos?',
              'Quanto é 17 mais 26?']
    for q in examples:tests['hard_phrases'][q]=m.ask(q,g)
    tests['unknown_entity']=m.ask('Onde mora PessoaFantasma',g)
    tests['scale']={}
    # repetir consulta com esferas irrelevantes que nao se conectam ao argumento
    first=ep['questions'][0][0]
    before=g.mem.metrics['edges_accessed'];base=m.ask(first,g);small=g.mem.metrics['edges_accessed']-before
    for i in range(10000):g.mem._atom((tid('distractor',i),1))
    before=g.mem.metrics['edges_accessed'];second=m.ask(first,g);large=g.mem.metrics['edges_accessed']-before
    tests['scale']={'edges_before':small,'edges_with_10000_disconnected':large,'same_answer':base['answer']==second['answer']}
    tests['training_without_output_supervision']={}
    bad=ContextLearner()
    for j in range(50):
        ep=worlds(14+1000*j);gg=MorphGraph();
        for text,s,rel,obj,ctx in ep['facts']:bad.sensor(text,s,rel,obj,ctx);gg.add(s,rel,obj,ctx)
        rand=random.Random(j+778)
        targets=[z[2] for z in ep['questions']]
        for q,s,correct,response,cat in ep['questions']:
            fake=rand.choice([t for t in targets if t!=correct])
            bad.question(q,s,fake,response,gg)
        for q,s,correct,response,cat in ep['followups']:
            gg.set_focus(s)
            fake=rand.choice([t for t in targets if t!=correct])
            bad.question(q,s,fake,response,gg)
        for phrase,s,correct in ep['references']:
            fake=rand.choice([t for t in targets if t!=correct])
            bad.teach_reference(phrase,s,fake,gg)
    badsummary=summary([z for i in range(15) for z in test_world(bad,81000+i)])
    tests['training_without_output_supervision']={'eval':badsummary,'training':bad.count}
    (r/'controles.json').write_text(json.dumps(tests,ensure_ascii=False,indent=2))
    print(json.dumps(tests,ensure_ascii=False,indent=2)[:16000])

if __name__=='__main__':main()
