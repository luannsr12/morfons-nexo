"""NEXO Exp20: laboratorio de dialogo por hipoteses dentro da MESMA MorphMemory.
Sem chamadas de LLM ou respostas filosoficas codificadas.
A linguagem, regras de inferencia e modelos de resposta sao ensinados por exemplos
externos ao motor. Provas e seus pais sao Morfons com portas reais.
"""
from __future__ import annotations
import sys, json, hashlib, random, re
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'base17'))
from morfon import MorphMemory
from grounded import ContextLearner, MorphGraph, templ, match, tok, norm, tid


def canonical(premises, result):
    # Abstracao estrutural das referencias compartilhadas, sem vocabulario de dominio.
    ordered=tuple(sorted(premises,key=lambda x:(-len(x[1]),x[0],str(x[1]))))
    names={}
    def encode(f, allow_new=True):
        typ,vals=f
        seq=[]
        for val in vals:
            if val not in names:
                if not allow_new: return None
                names[val]=len(names)
            seq.append(names[val])
        return [typ,seq]
    inp=[encode(p) for p in ordered]
    out=encode(result,False)
    if out is None:return None
    return {'premises':inp,'result':out}


def instantiate(rule, facts):
    """Enumeracao local por tipos com unificacao de variaveis; independe de dominio."""
    assignments=[({},[])]
    for typ,roles in rule['premises']:
        new=[]
        for mapping,parents in assignments:
            for f in facts.get(typ,()):
                if f['uid'] in parents:continue
                if len(f['args'])!=len(roles):continue
                m=dict(mapping)
                for slot,value in zip(roles,f['args']):
                    if slot in m and m[slot]!=value:break
                    m[slot]=value
                else:new.append((m,parents+[f['uid']]))
        assignments=new
        if not assignments:return []
    results=[]
    for env,parents in assignments:
        try:args=tuple(env[x] for x in rule['result'][1])
        except KeyError:continue
        results.append((rule['result'][0],args,tuple(parents)))
    return results


class NexoDialogue:
    """Extensao cumulativa; o substrato anterior permanece disponivel e intacto."""
    def __init__(self,mem=None):
        if mem is None:
            raise ValueError('Forneca a MorphMemory real do NEXO19; nao crie memoria alternativa.')
        self.mem=mem
        self.context='mundo'
        self.last=None
        self.last_proof=[]
        self.pats=[];self.rules=[];self.responses=defaultdict(list)
        self.fact_cache=defaultdict(dict)
        self._lexical=None; self._worldgraph=None
        self._load_index()
    def _node(self,kind,key,ports=(),facet=None):
        hid=tid('nexo20',kind,repr(key))
        n,created=self.mem._create(kind,((-hid,1),),tuple(sorted(set(ports))))
        if n is None:raise MemoryError('Morfons capacity')
        n.promoted=True
        if facet is not None and created:n.facets=[facet]
        return n,created
    def _word_atom(self,word):
        a=self.mem._atom((tid('word',norm(word)),1))
        if not a.facets:a.facets=[{'word':word}]
        return a
    def _concept(self,label):
        key=norm(label).strip()
        tokens=tok(label)
        ports=[self._word_atom(w).uid for w in set(tokens)]
        n,created=self._node('reason_proposition',key,ports,{'surface':label,'key':key})
        return n
    def _relation_atom(self,rel):
        return self._word_atom('rel_'+rel)
    def _ctx_atom(self,ctx):
        n,_=self._node('reason_context',norm(ctx),(),{'surface':ctx})
        return n
    def _load_index(self):
        self.pats=[];self.rules=[];self.responses=defaultdict(list)
        for node in self.mem.nodes.values():
            if node.kind=='reason_pattern':self.pats.append(node)
            elif node.kind=='reason_rule':self.rules.append(node)
            elif node.kind=='reason_response':self.responses[node.facets[0]['mode']].append(node)
    def teach_utterance(self,text,slots,op):
        pat=templ(text,slots)
        if pat is None:raise ValueError((text,slots))
        ports=[self._word_atom(w).uid for w in pat if not w.startswith('{')]
        n,created=self._node('reason_pattern',(pat,op),ports,{'pattern':list(pat),'operation':op,'seen':0})
        n.observations+=1;n.facets[0]['seen']+=1
        if created:self.pats.append(n)
        return n
    def teach_response(self,mode,template):
        ports=[self._word_atom(w).uid for w in tok(template)]
        n,created=self._node('reason_response',(mode,template),ports,{'mode':mode,'text':template,'count':0})
        n.facets[0]['count']+=1
        if created:self.responses[mode].append(n)
        return n
    def teach_inference(self,premises,conclusion,valid=True,lesson_id=None):
        # Programador nao fornece uma regra logica. A maquina extrai a estrutura
        # das referencias em varios episodios e pode confirmar/desconfirmar regras.
        shape=canonical(premises,conclusion)
        if shape is None:return False
        # experiencia como Morfon no substrato, nao array externo de conhecimento.
        src=[]
        for typ,args in premises:
            src.append(self._concept(typ+':'+':'.join(args)).uid)
        target=self._concept('conclusion:'+conclusion[0]+':'+':'.join(conclusion[1])).uid
        lesson,_=self._node('reason_lesson',('lesson',lesson_id if lesson_id is not None else self.mem.next_uid),src+[target],
                             {'premises':[[k,list(a)] for k,a in premises],'conclusion':[conclusion[0],list(conclusion[1])],'valid':bool(valid)})
        rule,_=self._node('reason_rule',json.dumps(shape,sort_keys=True),[self._relation_atom(x[0]).uid for x in premises],
                          {'schema':shape,'positive':0,'negative':0,'lessons':[]})
        f=rule.facets[0]
        f['positive' if valid else 'negative']+=1
        f['lessons'].append(lesson.uid)
        rule.observations+=1;rule.positives+=int(valid)
        if rule not in self.rules:self.rules.append(rule)
        return True
    def teach_binary_truth(self,relation,inputs,result):
        """Tabela logica treinada em Morfons; a funcao nao esta no executor."""
        ports=[self._relation_atom(relation).uid]
        for i,bit in enumerate(inputs):
            ports.append(self._word_atom('bit_'+str(i)+'_'+str(int(bit))).uid)
        n,created=self._node('reason_truth_transition',(relation,tuple(inputs)),ports,
                             {'relation':relation,'inputs':list(map(int,inputs)),'output_counts':{}})
        counts=n.facets[0]['output_counts']
        result=str(int(result));counts[result]=counts.get(result,0)+1
        n.observations+=1
        return n
    def _truth(self,relation,inputs):
        key=(relation,tuple(map(int,inputs)))
        literal=((-tid('nexo20','reason_truth_transition',repr(key)),1),)
        uid=self.mem.by_lits.get(literal)
        if uid is None:return None
        n=self.mem.nodes[uid]
        ranked=sorted(n.facets[0]['output_counts'].items(),key=lambda z:z[1],reverse=True)
        if not ranked or (len(ranked)>1 and ranked[0][1]==ranked[1][1]):return None
        return int(ranked[0][0])
    def countermodel(self,target):
        """Procura uma testemunha que satisfaca tudo que foi observado e negue
        o alvo. Cada valor de uma implicacao vem de Morfon ensinado, nao de IF
        de linguagem Python que codifique o significado da implicacao.
        """
        known=self._facts(self.context)
        symbols=sorted(set(x for group in known.values() for f in group for x in f['args'])|{norm(target)})
        if len(symbols)>12:return {'status':'too_many_propositions','count':len(symbols)}
        index={x:i for i,x in enumerate(symbols)}
        viable=0;counter=None
        for bits in range(1<<len(symbols)):
            values={x:bool((bits>>i)&1) for x,i in index.items()}
            accepted=True
            for f in known.get('true',[]):
                if not values[f['args'][0]]:accepted=False;break
            if not accepted:continue
            for f in known.get('false',[]):
                if values[f['args'][0]]:accepted=False;break
            if not accepted:continue
            for f in known.get('if',[]):
                a,b=f['args']
                ok=self._truth('if',(values[a],values[b]))
                if ok is None:return {'status':'missing_learned_logic'}
                if not ok:accepted=False;break
            if not accepted:continue
            viable+=1
            if not values[norm(target)] and counter is None:counter=values
        if viable==0:return {'status':'inconsistent'}
        if counter is None:return {'status':'entailed','possible':viable}
        return {'status':'countermodel','possible':viable,'assignment':counter}
    def _parse(self,text):
        # o matching acontece sobre os Morfons de padrões efetivamente ativados
        # por palavras invariantes; captura por decomposicao estrutural.
        symbols=[(tid('word',w),1) for w in set(tok(text)) if (tid('word',w),1) in self.mem.by_token]
        self.mem.pulse(symbols)
        live=self.mem.last_pulsed
        matches=[]
        for n in self.pats:
            if n.uid not in live:continue
            pat=n.facets[0]['pattern']
            vals=match(tuple(pat),text)
            if vals is not None:
                fixed=sum(not s.startswith('{') for s in pat)
                matches.append((fixed,len(pat),n.observations,n.uid,vals))
        if not matches:return None
        matches.sort(reverse=True)
        top=matches[0]
        if len(matches)>1 and matches[1][:2]==top[:2] and self.mem.nodes[matches[1][3]].facets[0]['operation'] != self.mem.nodes[top[3]].facets[0]['operation']:
            return ('ambiguous',{})
        return self.mem.nodes[top[3]].facets[0]['operation'],top[-1]
    def _facts(self,context):
        # Ativacao LOCAL: a porta do Morfon de contexto indexa apenas fatos desse
        # contexto. Nao e feita varredura global sobre os Morfons da memoria.
        facts=defaultdict(list)
        cid=self._ctx_atom(context).uid
        for uid in self.mem.cache.get(cid,()):
            n=self.mem.nodes[uid]
            if n.kind!='reason_fact':continue
            f=n.facets[0]
            if not f.get('current',True):continue  # Exp21: revisoes mantem historia sem inferir de fatos antigos
            facts[f['relation']].append({'uid':n.uid,'args':tuple(f['args']),'source':f.get('source','observation')})
        return facts
    def add_fact(self,kind,args,context=None,source='dialogue'):
        ctx=norm(context or self.context)
        rawargs=tuple(str(a) for a in args)
        args=tuple(norm(a) for a in rawargs)
        ports=[self._relation_atom(kind).uid,self._ctx_atom(ctx).uid]+[self._concept(a).uid for a in rawargs]
        n,created=self._node('reason_fact',(ctx,kind,args),ports,
                             {'relation':kind,'args':list(args),'ctx':ctx,'source':source,'evidence':0})
        n.facets[0]['evidence']+=1;n.observations+=1
        self.fact_cache[ctx][(kind,args)]=n.uid
        self.last=('fact',(kind,args))
        return n
    def _set_discussion_focus(self,text):
        cid=self._ctx_atom(self.context).uid
        n,_=self._node('reason_discourse_focus',norm(self.context),[cid],{'proposition':None,'context':norm(self.context)})
        n.facets[0]['proposition']=norm(text)
        n.observations+=1
    def _pending_inquiry(self,entity=None):
        key=(-tid('nexo20','reason_discourse_focus',repr(norm(self.context))),1)
        uid=self.mem.by_lits.get((key,))
        if uid is None and entity is None:return None
        if uid is None:
            self._set_discussion_focus('')
            uid=self.mem.by_lits.get((key,))
        face=self.mem.nodes[uid].facets[0]
        if entity is not None:face['pending']=norm(entity)
        return face.get('pending')
    def _discussion_focus(self):
        key=(-tid('nexo20','reason_discourse_focus',repr(norm(self.context))),1)
        uid=self.mem.by_lits.get((key,))
        if uid is None:return None
        return self.mem.nodes[uid].facets[0].get('proposition')
    def _render(self,mode,**vals):
        variants=self.responses.get(mode,[])
        if not variants:return None
        n=max(variants,key=lambda m:(m.facets[0]['count'],-m.uid))
        text=n.facets[0]['text']
        for k,v in vals.items():text=text.replace('{'+k+'}',str(v))
        return text
    def closure(self,context=None,extra=(),commit=False):
        ctx=norm(context or self.context)
        facts=self._facts(ctx)
        existing={(kind,tuple(f['args'])):f for kind,vs in facts.items() for f in vs}
        # hipoteses sao factos transitorios, mas ainda usam as mesmas operacoes de inferencia.
        for kind,args in extra:
            args=tuple(norm(x) for x in args)
            # Um contrafactual alterna a premissa assumida na copia da consulta.
            # Ele nunca modifica o fato historico persistido no Morfon.
            inverse='false' if kind=='true' else 'true' if kind=='false' else None
            if inverse is not None:
                existing.pop((inverse,args),None)
            existing[(kind,args)]={'uid':-(len(existing)+1),'args':args,'source':'hypothesis'}
        proofs={key:[] for key in existing}
        for _ in range(7):
            by_type=defaultdict(list)
            for (kind,args),f in existing.items():by_type[kind].append(f)
            new=[]
            for rule in self.rules:
                face=rule.facets[0]
                if face['positive']<12 or face['negative']>face['positive']*.1:continue
                for typ,args,parents in instantiate(face['schema'],by_type):
                    key=(typ,args)
                    if key in existing or any(k==key for k,_ in new):continue
                    new.append((key,(rule.uid,parents)))
            if not new:break
            for key,(r,parents) in new:
                if commit:
                    # Consequencia como Morfon real: portas para o Morfon-regra
                    # e para as premissas observadas/derivadas. O núcleo é
                    # ativado com o primeiro raio; a conclusao so é certificada
                    # quando todos os portais esperados convergem.
                    ports=[r,*[p for p in parents if p>0]]
                    n,_=self._node('reason_derived',(ctx,key,tuple(sorted(ports))),ports,
                                   {'derived':list(key),'rule':r,'parents':list(parents),'context':ctx})
                    signal=self.mem.pulse_units(ports)
                    if not n.completed:raise AssertionError(('incomplete inference',key,ports,signal))
                    uid=n.uid
                else:uid=-(len(existing)+1)
                existing[key]={'uid':uid,'args':key[1],'source':'derived'}
                proofs[key]=[r,list(parents)]
        return existing,proofs
    def _best_consequences(self,existing,proofs):
        # somente conclusoes compostas por regras aprendidas
        derived=[(key,proofs[key]) for key in existing if proofs.get(key)]
        # prioriza a conclusao derivada mais recentemente (busca recursiva)
        return derived[-1] if derived else None
    def _wording(self,phrase):
        # usa o texto aprendido pela propria unidade; nao inventa semantica.
        uid=self.mem.by_lits.get(((-tid('nexo20','reason_proposition',repr(norm(phrase))),1),))
        if uid is not None:return self.mem.nodes[uid].facets[0]['surface']
        return phrase
    def _existing_capabilities(self,text):
        if self._lexical is None:
            self._lexical=ContextLearner()
            self._lexical.mem=self.mem
            self._lexical._reindex()
            self._worldgraph=MorphGraph()
            self._worldgraph.mem=self.mem
        numeric=self._lexical.ask_number(text)
        if numeric is not None:
            return {'answer':numeric.get('answer'),'reason':'retained_binary_transduction','trace':numeric}
        observed=self._lexical.ingest(text,self._worldgraph)
        if observed.get('kind')=='observed':
            return {'answer':'[relação observada]','reason':'retained_grounded_relation','node':observed['node']}
        query=self._lexical.ask(text,self._worldgraph)
        if query.get('answer'):
            return {'answer':query['answer'],'reason':'retained_relational_inference','trace':query}
        return {'answer':None,'reason':'no_learned_interpretation'}
    def _proof_sources(self,existing,proofs,key):
        by_id={v['uid']:k for k,v in existing.items()}
        sources=[];seen=set()
        def visit(item,depth=0):
            if depth>12 or item in seen:return
            seen.add(item)
            record=proofs.get(item)
            if not record:
                typ,args=item
                if typ=='if':sources.append('se '+self._wording(args[0])+' então '+self._wording(args[1]))
                elif typ=='true':sources.append(self._wording(args[0]))
                elif typ=='false':sources.append('não é verdade que '+self._wording(args[0]))
                return
            _,parents=record
            for uid in parents:
                p=by_id.get(uid)
                if p is not None:visit(p,depth+1)
        visit(key)
        return sources
    def answer(self,text):
        p=self._parse(text)
        if p is None:return self._existing_capabilities(text)
        op,vals=p
        if op=='ambiguous':return {'answer':None,'reason':'ambiguous_language'}
        if op in ('confirm_yes','confirm_no'):
            pending=self._pending_inquiry()
            if not pending:return {'answer':self._render('unknown',p='a pergunta anterior'),'reason':'no_pending_question'}
            fact=self.add_fact('true' if op=='confirm_yes' else 'false',(pending,),source='human_answer')
            self._pending_inquiry('')
            return {'answer':self._render('acknowledged'),'reason':'learned_from_human_reply','node':fact.uid}
        if op=='context':
            self.context=norm(vals['c']);self.last=None
            return {'answer':self._render('context',c=vals['c']),'reason':'context_selected'}
        if op=='implication':
            self.add_fact('if',(vals['p'],vals['q']))
            return {'answer':self._render('acknowledged'),'reason':'stored_implication'}
        if op in ('assert','deny'):
            self.add_fact('true' if op=='assert' else 'false',(vals['p'],))
            return {'answer':self._render('acknowledged'),'reason':'stored_observation'}
        if op in ('inference','check','missing','why','hypo','hypo_not','contradiction','counterexample','objection_focus'):
            extra=[]
            if op in ('hypo','hypo_not'):
                extra=[('true' if op=='hypo' else 'false',(vals['p'],))]
            # materiais anteriores nao sao modificados por uma hipotese de consulta
            known,proofs=self.closure(extra=extra,commit=not bool(extra))
            contrad=[args[0] for (typ,args) in known if typ=='true' and len(args)==1 and ('false',args) in known]
            if op=='contradiction':
                a=self._wording(contrad[0]) if contrad else ''
                return {'answer':self._render('conflict',p=a) if contrad else self._render('no_conflict'),
                        'reason':'context_conflict' if contrad else 'no_conflict'}
            if op=='check':
                key=norm(vals['p'])
                self._set_discussion_focus(key)
                yes=('true',(key,)) in known
                no=('false',(key,)) in known
                mode='both' if yes and no else 'yes' if yes else 'no' if no else 'unknown'
                if mode=='unknown':
                    prereqs=[f['args'][0] for f in self._facts(self.context)['if'] if f['args'][1]==key]
                    missing=[a for a in prereqs if ('true',(a,)) not in known and ('false',(a,)) not in known]
                    if missing:
                        asked=self._wording(missing[0]);self._pending_inquiry(asked)
                        return {'answer':self._render('request_fact',a=asked,p=vals['p']),
                                'reason':'chosen_human_observation','missing':asked}
                return {'answer':self._render(mode,p=vals['p']),'reason':mode,
                        'proof':proofs.get(('true',(key,))) or proofs.get(('false',(key,)))}
            if op in ('counterexample','objection_focus'):
                target=vals.get('p') if op=='counterexample' else self._discussion_focus()
                if not target:return {'answer':self._render('unknown',p='a conclusão anterior'),'reason':'missing_conversation_focus'}
                cm=self.countermodel(target)
                if cm['status']=='countermodel':
                    # Mostra condicoes relevantes que tornam o alvo nao necessario.
                    assignment=cm['assignment']
                    pieces=[self._wording(x)+' = '+('sim' if v else 'não') for x,v in assignment.items()]
                    return {'answer':self._render('counterexample',p=target,assignment='; '.join(pieces)),
                            'reason':'countermodel_from_learned_truth_table','model':cm}
                if cm['status']=='entailed':
                    return {'answer':self._render('no_counterexample',p=target),'reason':'no_countermodel'}
                return {'answer':self._render('unknown',p=target),'reason':cm['status']}
            if op=='missing':
                target=norm(vals['p'])
                self._set_discussion_focus(target)
                if ('true',(target,)) in known:
                    return {'answer':self._render('yes',p=vals['p']),'reason':'already_known'}
                # precondicao nao satisfeita: recua de consequencia ao antecedente.
                prereqs=[f['args'][0] for f in self._facts(self.context)['if'] if f['args'][1]==target]
                missing=[a for a in prereqs if ('true',(a,)) not in known]
                if missing:return {'answer':self._render('missing',p=vals['p'],a=self._wording(missing[0])),'reason':'identified_missing_premise'}
                return {'answer':self._render('unknown',p=vals['p']),'reason':'no_path'}
            if op=='why':
                if self.last_proof:
                    return {'answer':self._render('proof',p=self.last_proof[-1].get('conclusion',''),a=self.last_proof[-1].get('premise','')),
                            'reason':'learned_proof_trace','trace':self.last_proof[-1]}
                return {'answer':self._render('unknown',p='isso'),'reason':'no_proof'}
            best=self._best_consequences(known,proofs)
            if not best:
                return {'answer':self._render('unknown',p=vals.get('p','a hipótese')),'reason':'no_consequence'}
            key,(rule,parents)=best
            target=key[1][0] if key[1] else str(key)
            sources=[]
            # provenance por porta: recuperar as premissas concretas dos Morfons.
            for uid in parents:
                if uid>0 and uid in self.mem.nodes and self.mem.nodes[uid].kind=='reason_fact':
                    ff=self.mem.nodes[uid].facets[0]
                    sources.append((ff['relation'],ff['args']))
            proof_inputs=self._proof_sources(known,proofs,key)
            trace={'rule_morphon':rule,'parent_morphons':list(parents),'conclusion':self._wording(target),
                   'premise':'; '.join(proof_inputs), 'hypothesis':bool(extra), 'proof_sources':proof_inputs,
                   'ray_support':self.mem.nodes[known[key]['uid']].support if known[key]['uid']>0 else None}
            self.last_proof.append(trace)
            self._set_discussion_focus(target)
            mode='conditional_consequence' if extra else 'consequence'
            return {'answer':self._render(mode,p=self._wording(target)),'reason':'learned_inference',
                    'trace':trace,'derived':[(k[0],list(k[1])) for k in known if proofs.get(k)]}
        return {'answer':None,'reason':'operation_unimplemented','operation':op}
    def save(self,path):
        Path(path).write_text(json.dumps({'memory':self.mem.snapshot(),'context':self.context},ensure_ascii=False),encoding='utf-8')
    @classmethod
    def load(cls,path):
        blob=json.loads(Path(path).read_text(encoding='utf-8'))
        obj=cls(MorphMemory.restore(blob['memory']))
        obj.context=blob['context']
        return obj
