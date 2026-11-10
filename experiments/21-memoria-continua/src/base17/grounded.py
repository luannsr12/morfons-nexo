"""NEXO 17: grounding textual, estado relacional e caminhos aprendidos.

Motor de Mórfons preservado do Exp14/15. A entrada supervisionada de treino
contém ancoragem sensorial (sujeito, relação opaca, objeto, contexto), mas o
processador NÃO conhece nomes de relações nem templates sem os exemplos.
As consultas aprendem sequências de portas (rotas) pelo resultado observado.
Não é modelo livre de linguagem; documentado no relatório.
"""
from __future__ import annotations
import hashlib, json, re, unicodedata
from collections import Counter
from pathlib import Path
from morfon import MorphMemory, Config


def norm(s):
    s=unicodedata.normalize('NFKD',s.casefold())
    return ''.join(c for c in s if not unicodedata.combining(c))

def tok(s):return re.findall(r'[^\W_]+',norm(s),flags=re.UNICODE)

def tid(*parts):
    b='\0'.join(map(str,parts)).encode('utf8')
    return int.from_bytes(hashlib.blake2b(b,digest_size=8).digest(),'big')

def templ(text,fields,preserve=False):
    """Substitui spans ancorados pelos sensores; ancoras ausentes sao possiveis
    (consultas elipticas como 'e antes'). O aprendiz nao conhece os nomes.
    """
    v=tok(text)
    display=re.findall(r'[^\W_]+',text,flags=re.UNICODE) if preserve else v
    matches=[]
    for name,value in fields.items():
        found=tok(value)
        if not found:return None
        positions=[i for i in range(len(v)-len(found)+1) if v[i:i+len(found)]==found]
        if len(positions)>1:return None
        if positions:matches.append((positions[0],positions[0]+len(found),name))
    matches.sort()
    if any(matches[i][1]>matches[i+1][0] for i in range(len(matches)-1)):
        return None
    for start,end,name in reversed(matches):display[start:end]=['{'+name+'}']
    return tuple(display)

def match(template,text):
    """Generalizacao estrutural de spans: slots podem ser palavras ou frases.
    Se houver mais de uma decomposicao, o algoritmo se abstém.
    """
    raw=re.findall(r'[^\W_]+',text,flags=re.UNICODE)
    ts=[norm(x) for x in raw]
    answers=[]
    def rec(pi,ti,env):
        if len(answers)>1:return
        if pi==len(template):
            if ti==len(ts):answers.append(env)
            return
        item=template[pi]
        if item.startswith('{') and item.endswith('}'):
            name=item[1:-1]
            for end in range(ti+1,min(len(ts),ti+12)+1):
                value=' '.join(raw[ti:end])
                if name in env and norm(env[name])!=norm(value):continue
                rec(pi+1,end,{**env,name:value})
        elif ti<len(ts) and item==ts[ti]:rec(pi+1,ti+1,env)
    rec(0,0,{})
    return answers[0] if len(answers)==1 else None

def render(template,source,target):
    # Slots da resposta sao aprendidos no proprio corpus de demonstracoes.
    return (lambda text: text[:1].upper()+text[1:]+'.')(' '.join(source if a=='{s}' else target if a=='{v}' else a for a in template))


class MorphGraph:
    """Fatos = Mórfons de 4 portas. Cache de adjacência é derivado das portas."""
    def __init__(self):
        self.mem=MorphMemory(Config(max_order=8,max_nodes=150000,propagation='completed',max_relays=500000))
        self.clock=0
        self.entity_spelling={}
        self.mem.nodes[self.mem.ledger_uid].facets=[{'focus':None,'turns':0}]
    def _atom(self,typ,value):
        a=self.mem._atom((tid(typ,norm(str(value))),1))
        if not a.facets:a.facets=[{'type':typ,'value':str(value)}]
        return a
    def add(self,subj,rel,obj,ctx):
        self.clock+=1
        s=self._atom('entity',subj);o=self._atom('entity',obj)
        r=self._atom('relation',rel);c=self._atom('context',ctx)
        self.entity_spelling[norm(subj)]=subj
        self.entity_spelling[norm(obj)]=obj
        # A estrutura antiga continua como memoria historica, com marca de vigente=0.
        for uid in tuple(self.mem.cache.get(s.uid,())):
            n=self.mem.nodes[uid]
            if n.kind!='world_fact':continue
            f=n.facets[0]
            if f['src']==norm(subj) and f['rel']==rel and f['ctx']==ctx:
                f['current']=False
        fingerprint=tid('fact',str(self.clock),norm(subj),str(rel),norm(obj),str(ctx))
        n,_=self.mem._create('world_fact',((-fingerprint,1),),tuple(sorted([s.uid,o.uid,r.uid,c.uid])))
        n.promoted=True;n.observations=1
        n.facets=[{'src':norm(subj),'dst':norm(obj),'rel':rel,'ctx':ctx,'current':True,'at':self.clock,'origin':'observed'}]
        self.set_focus(subj)
        self.mem.assert_integrity()
        return n
    def set_focus(self,entity):
        self._atom('entity',entity)
        led=self.mem.nodes[self.mem.ledger_uid]
        if not led.facets:led.facets=[{'focus':None,'turns':0}]
        led.facets[0]['focus']=norm(entity);led.facets[0]['turns']+=1
    def current_focus(self):
        led=self.mem.nodes[self.mem.ledger_uid]
        if not led.facets:return None
        return led.facets[0].get('focus')
    def neighbors(self,entity,select=None):
        key=(tid('entity',norm(entity)),1)
        eid=self.mem.by_token.get(key)
        if eid is None:return []
        # ativa apenas a regiao da entidade por raio; vizinhos nao conectados nao sao varridos
        self.mem.pulse([key])
        out=[]
        for uid in self.mem.last_pulsed:
            n=self.mem.nodes[uid]
            if n.kind!='world_fact' or not n.active:continue
            f=n.facets[0]
            if not f['current']:continue
            if f['src']==norm(entity):
                edge=(f['rel'],f['ctx'],1)
                if select is None or edge==select:
                    if select is not None:
                        n.rays.update((self._atom('relation',f['rel']).uid,self._atom('context',f['ctx']).uid))
                    out.append((f['dst'],edge,n.support,uid))
            if f['dst']==norm(entity):
                edge=(f['rel'],f['ctx'],-1)
                if select is None or edge==select:
                    if select is not None:
                        n.rays.update((self._atom('relation',f['rel']).uid,self._atom('context',f['ctx']).uid))
                    out.append((f['src'],edge,n.support,uid))
        return out
    def paths(self,src,target,max_hops=2):
        found=set(); queue=[(norm(src),(),frozenset([norm(src)]))]
        for _ in range(max_hops):
            nxt=[]
            for here,path,seen in queue:
                for there,step,_,_ in self.neighbors(here):
                    if there in seen:continue
                    np=path+(step,)
                    if there==norm(target):found.add(np)
                    nxt.append((there,np,seen|{there}))
            queue=nxt
        return sorted(found,key=repr)
    def follow(self,src,path):
        current=[(norm(src),[],0)]
        for rel,ctx,direction in path:
            nxt=[]
            for here,nids,support in current:
                for there,edge,weight,uid in self.neighbors(here,select=(rel,ctx,direction)):
                    nxt.append((there,nids+[uid],support+weight))
            current=nxt
            if not current:break
        # Dedupe distinct traversals, keep evidence provenance
        vals={}
        for dest,ids,s in current:
            if dest not in vals or s>vals[dest][1]:vals[dest]=(ids,s)
        return vals
    def snapshot(self):return {'memory':self.mem.snapshot(),'clock':self.clock,'spelling':self.entity_spelling}
    @classmethod
    def restore(cls,state):
        obj=cls();obj.mem=MorphMemory.restore(state['memory']);obj.clock=state['clock'];obj.entity_spelling=state['spelling'];return obj


class ContextLearner:
    """Uma memoria de Mórfons para templates de entrada, plano e verbalizacao.
    A estrutura de execucao de caminhos é instrucao matematica generica,
    a escolha do caminho (relacao/contexto/orientacao) é aprendida dos exemplos.
    """
    def __init__(self):
        self.mem=MorphMemory(Config(max_order=16,max_nodes=25000,propagation='completed',max_relays=50000))
        self.count={'sensors':0,'questions':0,'references':0,'unmatched':0}
        self._reindex()
    def _reindex(self):
        self.fact_templates={}
        self.question_templates={}
        self.reference_templates={}
        self.numeric_templates={}
        for n in self.mem.nodes.values():
            if n.kind=='fact_template':self.fact_templates[tuple(n.facets[0]['pattern'])]=n.uid
            if n.kind=='question_template':self.question_templates[tuple(n.facets[0]['pattern'])]=n.uid
            if n.kind=='reference_template':self.reference_templates[tuple(n.facets[0]['pattern'])]=n.uid
            if n.kind=='numeric_template':self.numeric_templates[tuple(n.facets[0]['pattern'])]=n.uid
    def _node(self,kind,pattern):
        key=tuple(pattern)
        idx={'fact_template':self.fact_templates,'question_template':self.question_templates,'reference_template':self.reference_templates,'numeric_template':self.numeric_templates}[kind]
        if key in idx:return self.mem.nodes[idx[key]]
        # portas das palavras invariantes: nodos atomicos persistentes
        pids=[]
        for word in pattern:
            if word.startswith('{'):continue
            a=self.mem._atom((tid('word',word),1))
            if not a.facets:a.facets=[{'word':word}]
            pids.append(a.uid)
        n,_=self.mem._create(kind,((-tid(kind,repr(key)),1),),tuple(sorted(set(pids))))
        n.promoted=True
        n.facets=[{'pattern':list(key),'counts':{},'reply_counts':{}}]
        idx[key]=n.uid
        return n
    def sensor(self,text,src,rel,dst,ctx):
        pattern=templ(text,{'s':src,'v':dst})
        if not pattern:return False
        n=self._node('fact_template',pattern)
        label=json.dumps((rel,ctx),ensure_ascii=False)
        d=n.facets[0]['counts'];d[label]=d.get(label,0)+1
        n.observations+=1;self.count['sensors']+=1
        return True
    def question(self,text,src,dst,response,graph,max_hops=2,kind='question_template'):
        pattern=templ(text,{'s':src})
        rpat=templ(response,{'s':src,'v':dst},preserve=True) if response is not None else None
        if not pattern or (kind=='question_template' and not rpat):
            self.count['unmatched']+=1;return False
        paths=graph.paths(src,dst,max_hops)
        if not paths:
            self.count['unmatched']+=1;return False
        n=self._node(kind,pattern)
        if '{s}' not in pattern and graph.current_focus()==norm(src):
            facet=n.facets[0];pol=facet.setdefault('source_policy',{})
            pol['focus']=pol.get('focus',0)+1
        # Cada rota que explica o exemplo recebe evidencia; contextos variados
        # desempatam caminhos espurios ao longo das demonstracoes.
        d=n.facets[0]['counts']
        for path in paths:
            key=json.dumps(path,ensure_ascii=False)
            d[key]=d.get(key,0)+1/len(paths)
        if rpat is not None:
            reply=n.facets[0]['reply_counts'];rk=json.dumps(rpat,ensure_ascii=False)
            reply[rk]=reply.get(rk,0)+1
        n.observations+=1
        self.count['questions' if kind=='question_template' else 'references']+=1
        return True
    def teach_reference(self,phrase,src,dst,graph):
        return self.question(phrase,src,dst,None,graph,kind='reference_template')
    def teach_bit_transition(self,op,left,right,state_in,out_bit,state_out):
        """Instrucao mecanica generica: relaciona bits observados na mesma memoria.
        O aprendiz NAO calcula out_bit/state_out; recebe-os do professor.
        """
        inputs=((tid('op',op),1),(tid('bit_left',left),1),
                (tid('bit_right',right),1),(tid('state_in',state_in),1))
        ports=[self.mem._atom(x).uid for x in inputs]
        key=((-tid('bit_transition',op,left,right,state_in),1),)
        n,_=self.mem._create('bit_transition',key,tuple(sorted(ports)))
        n.promoted=True;n.observations+=1
        if not n.facets:n.facets=[{'op':op,'left':left,'right':right,'state':state_in,'outputs':{}}]
        label=json.dumps((out_bit,state_out));counts=n.facets[0]['outputs']
        counts[label]=counts.get(label,0)+1
        return n
    def teach_numeric_phrase(self,text,op,a,b,result,response):
        pattern=templ(text,{'a':str(a),'b':str(b)})
        rpat=templ(response,{'r':str(result)},preserve=True)
        if pattern is None or rpat is None:return False
        n=self._node('numeric_template',pattern)
        cnt=n.facets[0]['counts'];cnt[op]=cnt.get(op,0)+1
        rr=n.facets[0]['reply_counts'];key=json.dumps(rpat,ensure_ascii=False)
        rr[key]=rr.get(key,0)+1
        n.observations+=1
        return True
    def _transduce(self,op,a,b):
        if min(a,b)<0:return None
        state=0;out=0;total_rays=0;steps=[]
        for i in range(max(a.bit_length(),b.bit_length())+2):
            x=(a>>i)&1;y=(b>>i)&1
            tokens=((tid('op',op),1),(tid('bit_left',x),1),
                    (tid('bit_right',y),1),(tid('state_in',state),1))
            self.mem.pulse(tokens)
            valid=[self.mem.nodes[uid] for uid in self.mem.last_pulsed
                   if self.mem.nodes[uid].kind=='bit_transition' and self.mem.nodes[uid].completed]
            if len(valid)!=1:return None
            n=valid[0];total_rays+=n.support
            results=sorted(n.facets[0]['outputs'].items(),key=lambda z:z[1],reverse=True)
            if len(results)>1 and results[0][1]==results[1][1]:return None
            outbit,newstate=json.loads(results[0][0]);out|=int(outbit)<<i
            steps.append({'morphon':n.uid,'rays':n.support,'input':[x,y,state],'output':[outbit,newstate]})
            state=int(newstate)
            if i>=max(a.bit_length(),b.bit_length()) and state==0:break
        if state!=0:return None
        return out,total_rays,steps
    def ask_number(self,text):
        candidates=self._match(text,'numeric_template')
        if not candidates:return None
        _,_,uid,vals=candidates[0]
        try:a=int(vals['a']);b=int(vals['b'])
        except (ValueError,KeyError):return {'answer':None,'reason':'numeric_arguments_missing'}
        node=self.mem.nodes[uid]
        ranked=sorted(node.facets[0]['counts'].items(),key=lambda z:z[1],reverse=True)
        if len(ranked)>1 and ranked[0][1]==ranked[1][1]:return {'answer':None,'reason':'ambiguous_operator'}
        result=self._transduce(ranked[0][0],a,b)
        if result is None:return {'answer':None,'reason':'unlearned_binary_transition'}
        number,weight,trace=result
        fmt=json.loads(max(node.facets[0]['reply_counts'].items(),key=lambda z:z[1])[0])
        sentence=' '.join(str(number) if t=='{r}' else t for t in fmt)
        return {'answer':sentence[:1].upper()+sentence[1:]+'.','reason':'learned_binary_transduction',
                'result':number,'rays':weight,'steps':trace,'hops':len(trace)}

    def _match(self,text,kind):
        # Padrões aprendidos admitem um slot de frase, que pode referir outro
        # Mórfon antes de fornecer o argumento ao Mórfon superior.
        idx={'fact_template':self.fact_templates,'question_template':self.question_templates,'reference_template':self.reference_templates,'numeric_template':self.numeric_templates}[kind]
        words=tok(text);raw=re.findall(r'[^\W_]+',text,flags=re.UNICODE)
        self.mem.pulse([(tid('word',word),1) for word in set(words)
                        if (tid('word',word),1) in self.mem.by_token])
        activated=self.mem.last_pulsed
        candidates=[]
        for uid in activated:
            node=self.mem.nodes[uid]
            if node.kind!=kind or not node.promoted:continue
            pat=tuple(node.facets[0]['pattern'])
            slots=[i for i,v in enumerate(pat) if v.startswith('{')]
            vals=match(pat,text)
            if vals is None:continue
            candidates.append((len(pat)-len(slots),node.observations,uid,vals))
        candidates.sort(reverse=True)
        return candidates

    def _resolve_entity(self,text,graph,depth=0):
        if depth>=4:return [],[]
        # Um nome atomico e um argumento; expressoes compostas sao resolvidas
        # por portais de referencia APRENDIDOS, sem regras de palavras.
        if (tid('entity',norm(text)),1) in graph.mem.by_token or len(tok(text))==1:return [text],[]
        for _,_,uid,vals in self._match(text,'reference_template'):
            src=vals.get('s')
            if src is None:continue
            bases,trace=self._resolve_entity(src,graph,depth+1)
            n=self.mem.nodes[uid]
            plans=sorted(n.facets[0]['counts'].items(),key=lambda z:z[1],reverse=True)
            if not plans:continue
            if len(plans)>1 and plans[0][1]==plans[1][1]:continue
            route=json.loads(plans[0][0]);answers={}
            for base in bases:
                for dest,val in graph.follow(base,route).items():answers[dest]=val
            if answers:return sorted(answers),trace+[{'reference_morphon':uid,'route':route,'rays':sum(v[1] for v in answers.values()),'port_ids':[p for v in answers.values() for p in v[0]]}]
        return [],[]
    def ingest(self,text,graph):
        candidates=self._match(text,'fact_template')
        if not candidates:return {'kind':'unknown','text':text}
        _,_,uid,vals=candidates[0]
        if 's' not in vals or 'v' not in vals:return {'kind':'unknown'}
        node=self.mem.nodes[uid]
        outcomes=sorted(node.facets[0]['counts'].items(),key=lambda x:x[1],reverse=True)
        if len(outcomes)>1 and outcomes[0][1]==outcomes[1][1]:return {'kind':'ambiguous_template'}
        rel,ctx=json.loads(outcomes[0][0])
        n=graph.add(vals['s'],rel,vals['v'],ctx)
        return {'kind':'observed','node':n.uid,'relation':rel,'context':ctx,'subject':vals['s'],'value':vals['v']}
    def ask(self,text,graph,with_trace=False):
        numeric=self.ask_number(text)
        if numeric is not None:return numeric
        candidates=self._match(text,'question_template')
        if not candidates:return {'answer':None,'reason':'no_language_pattern'}
        _,_,uid,vals=candidates[0]
        if 's' not in vals:
            policy=self.mem.nodes[uid].facets[0].get('source_policy',{})
            focus=graph.current_focus()
            if focus is None or not policy.get('focus'):
                return {'answer':None,'reason':'no_source'}
            vals['s']=graph.entity_spelling.get(focus,focus)
        roots,ref_trace=self._resolve_entity(vals['s'],graph)
        if not roots:return {'answer':None,'reason':'unknown_reference'}
        n=self.mem.nodes[uid]
        ranked=sorted(n.facets[0]['counts'].items(),key=lambda z:z[1],reverse=True)
        if len(ranked)>1 and ranked[0][1]==ranked[1][1]:return {'answer':None,'reason':'ambiguous_learned_route'}
        path=json.loads(ranked[0][0]);reached={}
        for root in roots:
            for dest,(ids,s) in graph.follow(root,path).items():reached[dest]=(ids,s)
        if not reached:return {'answer':None,'reason':'missing_relation','path':path}
        if len(reached)>1:return {'answer':None,'reason':'multiple_consistent_answers','alternatives':sorted(reached),'path':path}
        value,(ids,support)=next(iter(reached.items()))
        reply_ranked=sorted(n.facets[0]['reply_counts'].items(),key=lambda z:z[1],reverse=True)
        if not reply_ranked:return {'answer':None,'reason':'no_response_pattern'}
        reply=json.loads(reply_ranked[0][0])
        arg=graph.entity_spelling.get(norm(vals['s']),vals['s'])
        out={'answer':render(reply,arg,graph.entity_spelling.get(value,value)),
             'reason':'grounded_path','hops':len(path)+sum(len(x['route']) for x in ref_trace),
             'rays':support+sum(z['rays'] for z in ref_trace),'path':path,'reference_trace':ref_trace,'nodes':ids,'template_node':uid}
        if not with_trace:out.pop('nodes',None)
        if (tid('entity',norm(vals['s'])),1) in graph.mem.by_token:graph.set_focus(vals['s'])
        return out
    def save(self,path):
        Path(path).write_text(json.dumps({'memory':self.mem.snapshot(),'count':self.count},ensure_ascii=False),encoding='utf8')
    @classmethod
    def load(cls,path):
        v=json.loads(Path(path).read_text(encoding='utf8'));a=cls();a.mem=MorphMemory.restore(v['memory']);a.count=v['count'];a._reindex();return a
