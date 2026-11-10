"""Ambiente de testes: rotulos opacos, gerador separado do aprendiz.
Todos os nomes de relacao e textos de treino existem AQUI, nao no motor.
"""
from __future__ import annotations
import csv,json,random,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from grounded import ContextLearner,MorphGraph

TRAIN_PERSON=['Amira','Breno','Celia','Davi','Elisa','Fabio','Gilda','Heitor','Iara','Jonas','Katya','Luanio','Melina','Nara','Otavio','Paola','Rute','Sonia','Tales','Vera']
TRAIN_THING=['Carta','Chave','Fita','Moeda','Vaso','Pasta','Caderno','Caixa','Livro','Mapa','Relogio','Bola','Pente','Caneta','Pote','Tecido','Anel','Broche','Cordao','Vidro']
TRAIN_PLACE=['Recife','Olinda','Garanhuns','Carmo','Limoeiro','Petrolina','Caruaru','Paulista','Moreno','Igarassu','Goiana','Itamaraca','Jaboatao','Timbauba','Surubim','Pesqueira','Salgueiro','Arcoverde','Gravata','Lajedo']
REL={'lived':'zeta','holds':'tango','itemloc':'omega','region':'sigma','visits':'delta','origin':'eta'}
CTX={'past':'fase0','now':'fase1'}

def worlds(seed,test=False,trap=False):
    rng=random.Random(seed)
    if not test:
        people=rng.sample(TRAIN_PERSON,4);items=rng.sample(TRAIN_THING,4);places=rng.sample(TRAIN_PLACE,10)
    else:
        # nenhum nome/objeto/lugar existiu no treino; cada mundo tem lexemas diferentes
        base=seed*10
        people=[f'Zevira{base+i}' for i in range(4)]
        items=[f'Batifo{base+i}' for i in range(4)]
        places=[f'Vinala{base+i}' for i in range(10)]
    regions=[f'Terrava{seed*10+i}' for i in range(5)] if test else ['Nordalia','Sulavia','Oestina','Lestoria','Centuria']
    facts=[];queries=[];references=[];composed=[];followups=[]
    for i,loc in enumerate(places):
        reg=regions[i%len(regions)]
        facts.append((f'{loc} pertence a {reg}',loc,REL['region'],reg,CTX['now']))
        queries.append((f'Em que região fica {loc}',loc,reg,f'{loc} fica na região {reg}', 'regiao'))
    for i,p in enumerate(people):
        old=places[(2*i)%10];now=places[(2*i+1)%10];thing=items[i];site=places[(i+5)%10]
        visited=now if trap or rng.random()<.30 else rng.choice(places)
        origin=site if trap or rng.random()<.30 else rng.choice(places)
        facts += [(f'Antes {p} morava em {old}',p,REL['lived'],old,CTX['past']),
                  (f'Hoje {p} mora em {now}',p,REL['lived'],now,CTX['now']),
                  (f'{p} guarda {thing}',p,REL['holds'],thing,CTX['now']),
                  (f'{thing} fica em {site}',thing,REL['itemloc'],site,CTX['now']),
                  (f'{p} visita {visited}',p,REL['visits'],visited,CTX['now']),
                  (f'{thing} veio de {origin}',thing,REL['origin'],origin,CTX['now'])]
        queries += [(f'Onde mora {p}',p,now,f'{p} mora em {now}', 'agora'),
                    (f'Onde morava {p}',p,old,f'{p} morava em {old}', 'antes'),
                    (f'Onde está a coisa guardada por {p}',p,site,f'A coisa guardada por {p} está em {site}', 'dois_saltos'),
                    (f'Onde mora quem guarda {thing}',thing,now,f'Quem guarda {thing} mora em {now}', 'inverso_dois_saltos'),
                    (f'O que {p} guarda',p,thing,f'{p} guarda {thing}', 'objeto'),
                    (f'Onde fica {thing}',thing,site,f'{thing} fica em {site}','objeto_lugar')]
        followups.append(('E antes',p,old,f'{p} morava em {old}','contexto_sem_nome_antes'))
        followups.append(('E agora',p,now,f'{p} mora em {now}','contexto_sem_nome_agora'))
        references.append((f'o objeto que {p} guarda',p,thing))
        references.append((f'o lugar onde fica {thing}',thing,site))
        composed.append((f'Onde fica o objeto que {p} guarda',p,site,f'O objeto que {p} guarda fica em {site}','composicao_nunca_treinada'))
        reg=regions[places.index(site)%len(regions)]
        composed.append((f'Em que região fica o lugar onde fica o objeto que {p} guarda',p,reg,f'O lugar onde fica o objeto que {p} guarda fica na região {reg}','tres_saltos_nunca_treinada'))
    rng.shuffle(facts);rng.shuffle(queries)
    return {'facts':facts,'questions':queries,'references':references,'composed':composed,'followups':followups,'seed':seed}

def train(model,world_count=240,seed=14):
    logs=[];t0=time.perf_counter()
    for j in range(world_count):
        ep=worlds(seed+1000*j,trap=(j==0))
        g=MorphGraph()
        for statement,s,r,o,c in ep['facts']:
            model.sensor(statement,s,r,o,c)
            g.add(s,r,o,c)
        for question,source,target,response,cat in ep['questions']:
            model.question(question,source,target,response,g)
        for phrase,src,dst in ep['references']:
            model.teach_reference(phrase,src,dst,g)
        for question,src,target,response,cat in ep['followups']:
            g.set_focus(src)
            model.question(question,src,target,response,g)
        if j in (0,9,49,99,world_count-1):
            logs.append({'world':j+1,'patterns':len(model.fact_templates)+len(model.question_templates),
                         'morphons':len(model.mem.nodes),'training_questions':model.count['questions'],
                         'train_seconds':round(time.perf_counter()-t0,3)})
    return logs

def train_numeric(model,n=600,seed=7781):
    """Supervisao instrumental: o professor revela estados binarios intermediarios.
    Nao se transmite a formula de soma ao aprendiz, mas SIM a tabela de transicoes.
    """
    rng=random.Random(seed);traces=[]
    for k in range(n):
        a=rng.randrange(1,1024);b=rng.randrange(1,1024)
        if a==b:b+=1
        result=a+b # APENAS oraculo do ambiente
        carry=0
        for i in range(max(a.bit_length(),b.bit_length())+2):
            left=(a>>i)&1;right=(b>>i)&1
            value=left+right+carry # passo do PROFESSOR, nunca do aprendiz
            outbit=value&1;newstate=(value>>1)&1
            node=model.teach_bit_transition('operacao_0',left,right,carry,outbit,newstate)
            if k<4:traces.append({'source':k,'morphon':node.uid,'input':[left,right,carry],'result':[outbit,newstate]})
            carry=newstate
            if i>=max(a.bit_length(),b.bit_length()) and carry==0:break
        model.teach_numeric_phrase(f'Quanto e {a} mais {b}','operacao_0',a,b,result,f'O resultado é {result}')
    return traces

def eval_numeric(model,n=1000,seed=17729):
    rng=random.Random(seed);rows=[]
    for j in range(n):
        a,b=rng.randrange(0,2**21),rng.randrange(0,2**21)
        predicted=model.ask(f'Quanto e {a} mais {b}',MorphGraph())
        expected=a+b
        rows.append({'a':a,'b':b,'correct':predicted.get('result')==expected,
                     'expected':expected,'produced':predicted.get('result'),
                     'abstained':predicted.get('answer') is None,'steps':predicted.get('hops',0)})
    return rows,{'correct':sum(x['correct'] for x in rows),'total':n,
                 'abstained':sum(x['abstained'] for x in rows),
                 'maximum_steps':max(x['steps'] for x in rows)}

def run_eval(model,world_count=40,base_seed=999,rich=False):
    rows=[];t0=time.perf_counter()
    for i in range(world_count):
        ep=worlds(base_seed+i,test=True)
        graph=MorphGraph()
        for text,_,_,_,_ in ep['facts']:
            rec=model.ingest(text,graph)
            assert rec['kind']=='observed', (text,rec)
        for question,source,target,response,cat in ep['questions']+ep['composed']+ep['followups']:
            if cat.startswith('contexto_sem_nome'):graph.set_focus(source)
            predicted=model.ask(question,graph,with_trace=rich)
            rows.append({'world':i,'kind':cat,'question':question,'expected':response,
                         'predicted':predicted['answer'],'correct':tuple(__import__('grounded').tok(predicted['answer'] or ''))==tuple(__import__('grounded').tok(response)),
                         'literal_exact':predicted['answer']==response+'.',
                         'reason':predicted['reason'],'hops':predicted.get('hops',0),
                         'rays':predicted.get('rays',0),'path':predicted.get('path'),
                         'nodes':predicted.get('nodes')})
    from collections import defaultdict
    agg=defaultdict(lambda:[0,0])
    for r in rows:agg[r['kind']][0]+=int(r['correct']);agg[r['kind']][1]+=1
    summary={'correct':sum(r['correct'] for r in rows),'total':len(rows),'by_type':{k:{'correct':v[0],'total':v[1]} for k,v in sorted(agg.items())},
             'seconds':round(time.perf_counter()-t0,3)}
    return rows,summary

def dialogue(model,seed=90042):
    ep=worlds(seed,test=True)
    graph=MorphGraph();dialog=[]
    for statement,*_ in ep['facts']:
        rec=model.ingest(statement,graph)
        dialog.append({'type':'information','user':statement+'.','nexo':None,'process':rec})
    for question,source,target,expected,cat in ep['questions'][:7]+ep['composed'][:3]+ep['followups'][:2]:
        if cat.startswith('contexto_sem_nome'):graph.set_focus(source)
        out=model.ask(question,graph,True)
        dialog.append({'type':'question','user':question+'?','nexo':out['answer'],'expected':expected,'process':out})
    # atualizar um fato presente depois da observacao: deve diferenciar antes/agora
    target=ep['facts'][0][1];newcity=f'CidadeNova{seed}'
    statement=f'Hoje {target} mora em {newcity}'
    rec=model.ingest(statement,graph)
    dialog.append({'type':'correction','user':statement+'.','nexo':None,'process':rec})
    q=f'Onde mora {target}';out=model.ask(q,graph,True)
    dialog.append({'type':'question','user':q+'?','nexo':out['answer'],'expected':f'{target} mora em {newcity}.','process':out})
    for q in ['Quanto e 17 mais 26','O que aconteceu ontem com a chuva','Qual o sentido da vida']:
        out=model.ask(q,graph,True)
        dialog.append({'type':'unsupported','user':q+'?','nexo':out['answer'],'process':out})
    return dialog,graph

def main():
    root=Path(__file__).resolve().parents[1];res=root/'results';res.mkdir(exist_ok=True)
    model=ContextLearner();log=train(model)
    bit_examples=train_numeric(model)
    model.save(res/'memoria_treinada.json');model=ContextLearner.load(res/'memoria_treinada.json')
    rows,summary=run_eval(model)
    binary_rows,binary_summary=eval_numeric(model)
    (res/'operacoes_binarias_observadas.json').write_text(json.dumps(bit_examples,indent=2))
    (res/'avaliacao_numerica.json').write_text(json.dumps(binary_rows,indent=2))
    dialog,graph=dialogue(model)
    (res/'avaliacao_individual.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    (res/'dialogo_executado.json').write_text(json.dumps(dialog,ensure_ascii=False,indent=2))
    (res/'estado_de_uma_conversa.json').write_text(json.dumps(graph.snapshot(),ensure_ascii=False))
    (res/'curva.json').write_text(json.dumps(log,indent=2))
    summary.update({'arithmetic':binary_summary,'training':model.count,'model_morphons':len(model.mem.nodes),
                    'memory_bytes':(res/'memoria_treinada.json').stat().st_size})
    (res/'metricas.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print('---- CONVERSA ----')
    for r in dialog[-15:]:print(r['user'],'\nNEXO:',r['nexo'] or '[registrei / sem resposta verbal]','\n')

if __name__=='__main__':main()
