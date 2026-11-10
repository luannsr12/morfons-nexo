"""NEXO 21: aprendizagem DURANTE a conversa na MorphMemory cumulativa.

O motor nao possui predicados ou respostas para nomes, cidades, livros ou
assuntos filosoficos. Os esquemas de enunciado/pergunta/valor sao inferidos
por alinhamento de exemplos linguísticos fornecidos pelo ambiente/professor.
Todos os fatos, turnos, duvidas, verificacoes e exemplos de ensino sao Morfons
persistentes na MESMA MorphMemory restaurada do NEXO20.
"""
from __future__ import annotations
from collections import defaultdict, Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json, re
from nexo20 import NexoDialogue
from grounded import norm, tok, tid, match

WORD = re.compile(r'[^\W_]+', re.UNICODE)


def tokens(s): return tok(s)


def answer_mask(statement, answer):
    s, a = tokens(statement), tokens(answer)
    if not s or not a: return None
    at = [i for i in range(len(s)-len(a)+1) if s[i:i+len(a)] == a]
    if len(at) != 1: return None
    pos = at[0]
    return tuple(s[:pos]+['@value']+s[pos+len(a):])


def similarity(example_a, example_b):
    sa, qa = example_a; sb, qb = example_b
    if len(sa) != len(sb) or len(qa) != len(qb): return 0.0
    eqs = sum(a==b for a,b in zip(sa,sb))
    eqq = sum(a==b for a,b in zip(qa,qb))
    return (eqs+eqq)/(len(sa)+len(qa))


def induce(examples):
    """Alinhamento contrastivo. A variavel resposta deve reaparecer no enunciado.
    Outras variaveis diferem entre exemplos e devem ser observadas na pergunta.
    Nenhum significado de palavras aparece aqui.
    """
    if len(examples) < 3: return None
    pairs = []
    for e in examples:
        sm = answer_mask(e['statement'],e['answer'])
        if sm is None: return None
        pairs.append((sm,tuple(tokens(e['question']))))
    first_s, first_q = pairs[0]
    if any(len(x)!=len(first_s) or len(y)!=len(first_q) for x,y in pairs):return None
    fixed_s = [len({p[0][j] for p in pairs})==1 for j in range(len(first_s))]
    fixed_q = [len({p[1][j] for p in pairs})==1 for j in range(len(first_q))]
    # O valor e um lugar especial identificado por repeticao no treino (resposta
    # consta no enunciado); a regra para esse lugar nao e uma ontologia de dominio.
    if '@value' not in first_s:return None
    vs = first_s.index('@value')
    s_pattern = list(first_s)
    q_pattern = list(first_q)
    variables = {}
    var_count = 0
    for j in range(len(s_pattern)):
        if j == vs: s_pattern[j]='{value}'; continue
        if fixed_s[j]: continue
        vals = tuple(p[0][j] for p in pairs)
        frequencies=Counter(vals)
        # Um unico contraexemplo nao justifica trocar uma palavra fixa
        # de 18 experiencias por um novo slot generico. Exigir pelo menos
        # tres valores distintos OU dois valores recorrentes tres vezes cada.
        if len(frequencies)<3 and (len(frequencies)<2 or min(frequencies.values())<3):return None
        matched = [k for k in range(len(q_pattern)) if not fixed_q[k]
                   and tuple(p[1][k] for p in pairs)==vals]
        if len(matched)!=1:return None
        var=f'{{key{var_count}}}'
        s_pattern[j]=var;q_pattern[matched[0]]=var
        variables[matched[0]]=var
        var_count+=1
    if any(not fixed_q[k] and k not in variables for k in range(len(q_pattern))):return None
    if sum(fixed_s)+sum(fixed_q)<2:return None
    return {'statement':s_pattern,'question':q_pattern,
            'keys':[f'key{k}' for k in range(var_count)],'number':len(examples)}


class ContinuousNexo:
    def __init__(self, base: NexoDialogue, session: str='principal'):
        self.base=base
        self.mem=base.mem
        self.session=norm(session)
        node, created=self._node('dialogue_session',self.session,(),{'step':0,'last_event':None,
                'unparsed_statement':None,'last_reason':None,'last_proof':[],
                'logic_context':'sessao:'+self.session,'session':self.session})
        self.base.context=node.facets[0].get('logic_context','sessao:'+self.session)
        self._schemas=self._all_schemas()
        self._aliases=self._all_aliases()

    @classmethod
    def from_state(cls,path,session='principal'):
        return cls(NexoDialogue.load(path),session)

    def _node(self,kind,key,ports=(),face=None):
        # a identidade canonica vive nas literais da propria MorphMemory
        return self.base._node(kind,(self.session,key) if kind in {
            'dialogue_session','dialogue_episode','dialogue_goal','dialogue_fact',
            'dialogue_reflection','dialogue_reply','dialogue_self_question'} else key,
            tuple(int(p) for p in ports),face)

    def _session_node(self):
        n,_=self._node('dialogue_session',self.session,(),{'step':0,'last_event':None,
                'unparsed_statement':None,'last_reason':None,'last_proof':[],
                'logic_context':'sessao:'+self.session,'session':self.session})
        return n

    def _session_atom(self):return self._session_node().uid

    def _atom(self,kind,value):
        return self.base._concept(f'{kind}:{norm(str(value))}')

    def _all_schemas(self):
        return [n for n in self.mem.nodes.values() if n.kind=='dialogue_schema']

    def _all_aliases(self):
        return [n for n in self.mem.nodes.values() if n.kind=='dialogue_alias']

    def _alias_mask(self,query,keys):
        words=list(tokens(query))
        for i,key in enumerate(keys):
            parts=tokens(key)
            hits=[j for j in range(len(words)-len(parts)+1) if words[j:j+len(parts)]==parts]
            if len(hits)!=1:return None
            j=hits[0];words[j:j+len(parts)]=['{key'+str(i)+'}']
        return tuple(words)

    def _learn_aliases(self):
        groups=defaultdict(list)
        for node in self.mem.nodes.values():
            if node.kind!='dialogue_alias_example':continue
            f=node.facets[0]
            mask=self._alias_mask(f['question'],f['keys'])
            if mask is not None:groups[(f['schema'],mask)].append(node)
        formed=0
        for (schema_uid,pattern),items in groups.items():
            # Evidencias independentes, nao repeticoes do mesmo par.
            if len({(tuple(n.facets[0]['keys']),norm(n.facets[0]['value'])) for n in items})<3:continue
            fixed=[w for w in pattern if not w.startswith('{')]
            ports=[schema_uid]+[self.base._word_atom(w).uid for w in sorted(set(fixed))]
            n,created=self._node('dialogue_alias',(schema_uid,pattern),ports,
                                 {'question':list(pattern),'target_schema':schema_uid,
                                  'evidence':len(items)})
            n.facets[0]['evidence']=max(len(items),n.facets[0]['evidence'])
            if created:formed+=1
        self._aliases=self._all_aliases()
        return formed

    def _observe_possible_paraphrase(self,goal,text):
        # Uma resposta humana serve como experiencia de equivalencia apenas
        # se ANTES ja existe um unico fato atual com esse mesmo valor e a
        # entidade da pergunta corresponde a sua chave. Sem essa evidencia,
        # nenhuma sinonimia é inferida.
        question=goal.facets[0]['question']
        qt=tokens(question)
        candidates=[]
        for uid in self.mem.cache.get(self._session_atom(),()):
            fnode=self.mem.nodes[uid]
            if fnode.kind!='dialogue_fact':continue
            f=fnode.facets[0]
            if not f['current'] or norm(f['value'])!=norm(text):continue
            if not all(any(qt[j:j+len(tokens(k))]==tokens(k)
                           for j in range(len(qt)-len(tokens(k))+1)) for k in f['key']):continue
            candidates.append(fnode)
        if len(candidates)!=1:return 0
        fact=candidates[0];fac=fact.facets[0]
        goal.facets[0]['linked_fact_uid']=fact.uid
        key=(norm(question),fac['schema'],tuple(fac['key']),norm(fac['value']))
        self._node('dialogue_alias_example',key,(goal.uid,fact.uid),
                   {'question':question,'schema':fac['schema'],'keys':fac['key'],
                    'value':fac['value'],'fact_uid':fact.uid})
        return self._learn_aliases()

    def _example(self, statement, question, answer, origin='teaching'):
        sm=answer_mask(statement,answer)
        if sm is None:return None
        entry={'statement':statement,'question':question,'answer':answer,'source':origin}
        key=(norm(statement),norm(question),norm(answer))
        ports=[self._atom('utterance',statement).uid,self._atom('question',question).uid,
               self._atom('value',answer).uid]
        n,created=self._node('dialogue_example',key,ports,entry)
        if created:
            n.observations=1
        return n

    def _learn_schemas(self):
        exs=[n.facets[0] for n in self.mem.nodes.values() if n.kind=='dialogue_example']
        groups=[]
        for e in exs:
            sm=answer_mask(e['statement'],e['answer'])
            if sm is None:continue
            signature=(sm,tuple(tokens(e['question'])))
            matches=[(similarity(signature,g['rep']),i) for i,g in enumerate(groups)]
            score,idx=max(matches,default=(0,None))
            if score>=.57:
                groups[idx]['rows'].append(e)
            else:groups.append({'rep':signature,'rows':[e]})
        formed=0
        for g in groups:
            if len(g['rows'])<3: continue
            schema=induce(g['rows'])
            if schema is None:continue
            key=(tuple(schema['statement']),tuple(schema['question']))
            # Canais de ativacao sao os termos invariantes aprendidos.
            fixed=[x for x in schema['statement']+schema['question'] if not x.startswith('{')]
            ports=[self.base._word_atom(w).uid for w in sorted(set(fixed))]
            n,created=self._node('dialogue_schema',key,ports,
                                 {'statement':schema['statement'],'question':schema['question'],
                                  'keys':schema['keys'],'evidence':len(g['rows']),
                                  'example_nodes':[]})
            n.facets[0]['evidence']=max(len(g['rows']),n.facets[0].get('evidence',0))
            n.observations=max(n.observations,len(g['rows']))
            if created:formed+=1
        self._schemas=self._all_schemas()
        return formed

    def _ensure_capacity(self):
        # Nao confundir limite de alocacao do prototipo com limite de memoria
        # aprendido pelo agente. O aumento altera apenas capacidade de nos.
        if len(self.mem.nodes)+256 >= self.mem.cfg.max_nodes:
            self.mem.cfg.max_nodes=max(self.mem.cfg.max_nodes*2,len(self.mem.nodes)+1024)

    def train(self,examples):
        for example in examples:
            self._ensure_capacity()
            self._example(example['statement'],example['question'],example['answer'])
        return self._learn_schemas()

    def _match(self,which,text):
        choices=[]
        for n in (self._schemas + self._aliases if which=='question' else self._schemas):
            p=n.facets[0][which]
            vals=match(tuple(p),text)
            if vals is None:continue
            fixed=sum(not x.startswith('{') for x in p)
            choices.append((fixed,n.facets[0]['evidence'],n.uid,vals))
        if not choices:return None
        choices.sort(reverse=True)
        if len(choices)>1 and choices[1][:2]==choices[0][:2] and choices[1][2]!=choices[0][2]:return None
        _,_,uid,vals=choices[0]
        n=self.mem.nodes[uid]
        if n.kind=='dialogue_alias':
            return self.mem.nodes[n.facets[0]['target_schema']],vals
        return n,vals

    def _key(self,schema,slots):
        return tuple(norm(slots[k]) for k in schema.facets[0]['keys'])

    def _surface_for(self,schema,key,value):
        # Uma proposicao observada e reconstruida SOMENTE do padrao textual
        # aprendido e de seus valores. Nao ha significado de dominio codificado.
        variables=dict(zip(schema.facets[0]['keys'],key))
        variables['value']=value
        return ' '.join(variables[x[1:-1]] if x.startswith('{') else x
                        for x in schema.facets[0]['statement'])

    def _fact(self,schema,key,value,origin='conversation',event_uid=None):
        ctx=self._session_atom()
        value=value.strip()
        # Para aprender mudancas, preserva historia e altera apenas corrente.
        previous=[]
        for uid in list(self.mem.cache.get(ctx,())):
            n=self.mem.nodes[uid]
            if n.kind!='dialogue_fact':continue
            f=n.facets[0]
            if f['schema']==schema.uid and tuple(f['key'])==tuple(key) and f['current']:
                previous.append(n)
        for n in previous:
            if norm(n.facets[0]['value'])!=norm(value):
                n.facets[0]['current']=False
                rid=n.facets[0].get('reason_uid')
                if rid in self.mem.nodes:self.mem.nodes[rid].facets[0]['current']=False
        idkey=(schema.uid,key,norm(value))
        ports=[ctx,schema.uid,self._atom('value',value).uid]
        ports.extend(self._atom('key',v).uid for v in key)
        n,created=self._node('dialogue_fact',idkey,ports,
                             {'schema':schema.uid,'key':list(key),'value':value,
                              'current':True,'evidence':0,'origin':origin,'events':[]})
        n.facets[0]['current']=True
        n.facets[0]['value']=value
        n.facets[0]['evidence']+=1
        if event_uid is not None:n.facets[0]['events'].append(event_uid)
        n.observations+=1
        # A observacao da linguagem entra tambem como premissa para o
        # raciocinador relacional ANTERIOR, na mesma MorphMemory.
        surface=self._surface_for(schema,key,value)
        premise=self.base.add_fact('true',(surface,),source='observed_live_dialogue')
        premise.facets[0]['current']=True
        n.facets[0]['reason_uid']=premise.uid
        self._resolve(schema,key,n.uid)
        return n

    def _lookup(self,schema,key):
        found=[]
        for uid in self.mem.cache.get(self._session_atom(),()):
            n=self.mem.nodes[uid]
            if n.kind=='dialogue_fact':
                f=n.facets[0]
                if f['schema']==schema.uid and tuple(f['key'])==tuple(key) and f['current']:
                    found.append(n)
        if not found:return None
        # O peso de sustentacao da busca provem das portas: contexto, regra e
        # componentes variaveis. Repeticoes da mesma fonte nao contam 2 vezes.
        sources=[self._session_atom(),schema.uid]+[self._atom('key',v).uid for v in key]
        self.mem.pulse_units(sources)
        return max(found,key=lambda n:(n.facets[0]['evidence'],n.observations,-n.uid))

    def _open_goals(self):
        out=[]
        for uid in self.mem.cache.get(self._session_atom(),()):
            n=self.mem.nodes[uid]
            if n.kind=='dialogue_goal' and n.facets[0]['state']=='open':out.append(n)
        return sorted(out,key=lambda x:x.facets[0]['at'])

    def _resolve(self,schema,key,fact_uid):
        for g in self._open_goals():
            f=g.facets[0]
            if f['schema']==schema.uid and tuple(f['key'])==tuple(key):
                f['state']='resolved';f['resolved_by']=fact_uid

    def _goal(self,query,schema=None,key=(),old_statement=None):
        sn=self._session_node()
        ports=[sn.uid,self._atom('question',query).uid]
        if schema is not None:ports.append(schema.uid)
        n,_=self._node('dialogue_goal',(norm(query),sn.facets[0]['step']),ports,
                       {'question':query,'schema':schema.uid if schema else None,
                        'key':list(key),'state':'open','at':sn.facets[0]['step'],
                        'origin_statement':old_statement,'resolved_by':None})
        return n

    def _event(self,text):
        sn=self._session_node()
        sn.facets[0]['step']+=1
        self.mem.step_no+=1
        eid=sn.facets[0]['step']
        previous=sn.facets[0]['last_event']
        ports=[sn.uid,self._atom('utterance',text).uid]
        if previous is not None:ports.append(previous)
        n,_=self._node('dialogue_episode',(eid,norm(text)),ports,
                       {'surface':text,'step':eid,'response':None,'reason':None})
        sn.facets[0]['last_event']=n.uid
        return n

    def _reflect(self,event,result,source_uids=()):
        sn=self._session_node()
        state={'step':sn.facets[0]['step'],'reason':result.get('reason'),
               'gaps':len(self._open_goals()),'answer_available':bool(result.get('answer') is not None and result.get('goal_uid') is None),
               'source_uids':list(source_uids)}
        ports=[event.uid,sn.uid]+list(source_uids)
        n,_=self._node('dialogue_reflection',sn.facets[0]['step'],ports,state)
        # A auto-observacao nao e uma string inventada: uma unidade persistente
        # observa quais fontes existem, se um resultado foi encontrado e se ha
        # uma lacuna; um Morfon de pergunta interna liga-se a lacunas ativas.
        if self._open_goals():
            goal=self._open_goals()[-1]
            inner,_=self._node('dialogue_self_question',(goal.uid,sn.facets[0]['step']),
                               (n.uid,goal.uid,sn.uid),{'needs':goal.uid,'step':sn.facets[0]['step'],
                                'source':'observed_gap'})
            self.mem.pulse_units([goal.uid,n.uid])
            state['self_question_uid']=inner.uid
        if result.get('reason')=='unparsed_observation':
            # Nao esperar alguem perguntar: investigar a propria falta de
            # esquema diante da observacao que acabou de receber.
            inner,_=self._node('dialogue_self_question',('unexplained',event.uid),
                               (n.uid,event.uid,sn.uid),{'needs':event.uid,
                                 'step':sn.facets[0]['step'],
                                 'source':'unexplained_observation','resolved_by':None})
            self.mem.pulse_units([event.uid,n.uid])
            state['self_question_uid']=inner.uid
        event.facets[0]['response']=result.get('answer')
        event.facets[0]['reason']=result.get('reason')
        sn.facets[0]['last_reason']=result.get('reason')
        sn.facets[0]['logic_context']=self.base.context
        trace=result.get('trace')
        if trace is not None:
            sn.facets[0]['last_proof']=self.base.last_proof[-8:]
        return result

    def _partial_observation_for_pending(self,text,event):
        goals=self._open_goals()
        if not goals:return None
        goal=goals[-1].facets[0]
        if goal['schema'] is None:return None
        schema=self.mem.nodes[goal['schema']]
        parts=schema.facets[0]['statement']
        keys=dict(zip(schema.facets[0]['keys'],goal['key']))
        if '{value}' not in parts:return None
        index=parts.index('{value}')
        def expand(items):
            out=[]
            for w in items:
                if w.startswith('{'):
                    name=w[1:-1]
                    if name not in keys:return None
                    out.extend(tokens(keys[name]))
                else:out.append(w)
            return out
        prefix=expand(parts[:index]);suffix=expand(parts[index+1:])
        if prefix is None or suffix is None:return None
        raw=WORD.findall(text);ts=[norm(x) for x in raw]
        # Reconhecer truncamentos de prefixo por pelo menos duas palavras
        # invariantes aprendidas. Nada depende da identidade de 'moro', 'nome' etc.
        for missed in range(1,min(3,len(prefix))):
            anchor=prefix[missed:]
            if len(anchor)<2 or ts[:len(anchor)]!=anchor:continue
            if suffix and ts[-len(suffix):]!=suffix:continue
            stop=len(ts)-len(suffix) if suffix else len(ts)
            value=' '.join(raw[len(anchor):stop]).strip()
            if not value or len(tokens(value))>12:continue
            fact=self._fact(schema,tuple(goal['key']),value,'partial_observation',event.uid)
            self._example(text,goal['question'],value,'partial_linguistic_experience')
            self._learn_schemas()
            return {'answer':'Aprendi uma observação parcial e atualizei a relação.',
                    'reason':'learned_from_partial_observation','fact_uid':fact.uid}
        return None

    def _handle_bare_answer(self,text,event):
        goals=self._open_goals()
        if not goals:return None
        goal=goals[-1]
        if text.rstrip().endswith('?') or len(tokens(text))>9:return None
        face=goal.facets[0]
        if face['schema'] is not None:
            schema=self.mem.nodes[face['schema']]
            fact=self._fact(schema,tuple(face['key']),text,'human_answer',event.uid)
            return {'answer':f'Aprendi com sua resposta: {text}.','reason':'learned_from_human',
                    'fact_uid':fact.uid}
        statement=face.get('origin_statement')
        if statement and answer_mask(statement,text):
            lesson=self._example(statement,face['question'],text,'live_interaction')
            formed=self._learn_schemas()
            if formed:
                parsed=self._match('statement',statement)
                if parsed:
                    schema,slots=parsed
                    self._fact(schema,self._key(schema,slots),slots['value'],'online_schema',event.uid)
                for uid in self.mem.cache.get(self._session_atom(),()):
                    node=self.mem.nodes[uid]
                    if node.kind=='dialogue_self_question' and node.facets[0].get('source')=='unexplained_observation' \
                       and node.facets[0].get('resolved_by') is None:
                        node.facets[0]['resolved_by']=schema.uid if parsed else None
            face['state']='resolved'
            self._session_node().facets[0]['unparsed_statement']=None
            face['direct_answer']=text
            return {'answer':'Registrei essa experiência e comparei sua estrutura com as anteriores.',
                    'reason':'online_linguistic_experience','formed_schemas':formed,'lesson_uid':lesson.uid}
        # Resposta direta continua disponivel na memoria da pergunta; nao e
        # tomada como prova de que um novo padrao geral foi aprendido.
        aliases=self._observe_possible_paraphrase(goal,text)
        face['state']='resolved'
        self._session_node().facets[0]['unparsed_statement']=None
        face['direct_answer']=text
        return {'answer':'Guardei sua resposta e comparei a pergunta com relações existentes.',
                'reason':'episodic_answer_not_general_rule','new_aliases':aliases}

    def answer(self,text):
        text=text.strip()
        if not text:return {'answer':None,'reason':'empty'}
        self._ensure_capacity()
        event=self._event(text)
        sn=self._session_node()
        # Uma afirmação nova tem precedência sobre responder a uma dúvida velha.
        # Sem isso, "Meu nome é Ana" seria engolido como resposta a qualquer
        # pergunta ainda pendente e a memoria deixaria de aprender a frase.
        stmt=self._match('statement',text)
        if stmt:
            schema,slots=stmt
            if 'value' in slots:
                fact=self._fact(schema,self._key(schema,slots),slots['value'],event_uid=event.uid)
                sn.facets[0]['unparsed_statement']=None
                return self._reflect(event,{'answer':'Registrei essa informação.',
                            'reason':'observed_relational_fact','fact_uid':fact.uid},[fact.uid,schema.uid])
        # Uma frase linguística já reconhecida pelo raciocinador antigo também
        # não pode ser confundida com a resposta elíptica a outra pergunta.
        has_reason_pattern=self.base._parse(text) is not None
        # Nao consumir uma nova frase declarativa completa como se fosse
        # automaticamente resposta a outra pergunta. Respostas multi-palavra
        # sem pontuacao continuam possiveis; casos ambiguos conservam a duvida.
        is_new_declaration=text.endswith('.') and len(tokens(text))>2
        if not has_reason_pattern and not text.endswith('?') and self._open_goals():
            partial=self._partial_observation_for_pending(text,event)
            if partial:return self._reflect(event,partial)
        if not has_reason_pattern and not is_new_declaration and not text.endswith('?') and len(tokens(text))<=9 and self._open_goals():
            learned=self._handle_bare_answer(text,event)
            if learned:return self._reflect(event,learned)
        query=self._match('question',text)
        if query:
            schema,slots=query
            key=self._key(schema,slots)
            fact=self._lookup(schema,key)
            if fact:
                return self._reflect(event,{'answer':fact.facets[0]['value'],
                            'reason':'recalled_from_live_memory','fact_uid':fact.uid,
                            'evidence':fact.facets[0]['evidence'],'rays':fact.support},[fact.uid,schema.uid])
            goal=self._goal(text,schema,key)
            return self._reflect(event,{'answer':'Ainda não sei. Você pode me contar a resposta?',
                        'reason':'self_identified_missing_fact','goal_uid':goal.uid},[goal.uid,schema.uid])
        # Os mecanismos anteriores de raciocinio e operacoes binárias continuam.
        self.base.last_proof=list(sn.facets[0].get('last_proof',[]))
        original=self.base.answer(text)
        if original['reason']!='no_learned_interpretation':
            return self._reflect(event,original)
        if text.endswith('?'):
            last_stmt=sn.facets[0]['unparsed_statement']
            # Uma resposta demonstrada anteriormente continua na memoria,
            # mesmo quando nao houve exemplos suficientes para induzir um
            # padrao. Se houve NOVA afirmacao sem interpretacao, nao reciclar
            # a resposta anterior como se ela ja descrevesse a nova situacao.
            if not last_stmt:
                related=[n for uid in self.mem.cache.get(sn.uid,())
                         if (n:=self.mem.nodes[uid]).kind=='dialogue_goal'
                         and norm(n.facets[0]['question'])==norm(text)
                         and n.facets[0]['state']=='resolved'
                         and n.facets[0].get('direct_answer')
                         and (not n.facets[0].get('linked_fact_uid') or
                              self.mem.nodes[n.facets[0]['linked_fact_uid']].facets[0]['current'])]
                if related:
                    g=max(related,key=lambda n:n.facets[0]['at'])
                    return self._reflect(event,{'answer':g.facets[0]['direct_answer'],
                        'reason':'recalled_specific_episode','goal_uid':None},[g.uid])
            goal=self._goal(text,old_statement=last_stmt)
            return self._reflect(event,{'answer':'Não conheço essa construção ainda. Você pode me ensinar a resposta?',
                        'reason':'self_identified_unparsed_question','goal_uid':goal.uid},[goal.uid])
        sn.facets[0]['unparsed_statement']=text
        return self._reflect(event,{'answer':'Observei isso. Ainda não sei como relacionar essa frase a outras experiências.',
                    'reason':'unparsed_observation'})

    def introspect(self):
        sn=self._session_node()
        questions=[{'uid':g.uid,'question':g.facets[0]['question'],
                    'schema':g.facets[0]['schema']} for g in self._open_goals()]
        facts=[n for uid in self.mem.cache.get(sn.uid,()) if (n:=self.mem.nodes[uid]).kind=='dialogue_fact']
        latest=[]
        for n in sorted(facts,key=lambda x:x.uid,reverse=True):
            f=n.facets[0]
            if f['current']:
                latest.append({'id':n.uid,'value':f['value'],'evidence':f['evidence'],
                               'schema':f['schema'],'key':f['key']})
            if len(latest)>=8:break
        self_questions=[self.mem.nodes[uid] for uid in self.mem.cache.get(sn.uid,())
                        if self.mem.nodes[uid].kind=='dialogue_self_question']
        recent_questions=[]
        for n in sorted(self_questions,key=lambda x:x.uid,reverse=True)[:5]:
            f=n.facets[0]
            what=self.mem.nodes.get(f['needs'])
            if what is None:surface=None
            elif what.kind=='dialogue_goal':surface=what.facets[0]['question']
            else:surface=what.facets[0].get('surface')
            recent_questions.append({'id':n.uid,'source':f['source'],
                        'question_or_observation':surface,
                        'closed':bool(f.get('resolved_by') or
                            (what is not None and what.kind=='dialogue_goal'
                             and what.facets[0]['state']=='resolved'))})
        return {'session':self.session,'turns':sn.facets[0]['step'],
                'facts_current':sum(n.facets[0]['current'] for n in facts),
                'stored_schemas':len(self._schemas),'learned_paraphrases':len(self._aliases),
                'unresolved_questions':questions,'recent_self_questions':recent_questions,
                'recent_facts':latest,'morphons':len(self.mem.nodes),
                'last_reason':sn.facets[0]['last_reason'],
                'self_question_morphons':len(self_questions)}

    def save(self,path):
        out=Path(path)
        # Gravacao atomica. A memoria logica e SEMPRE a MorphMemory inteira.
        blob={'memory':self.mem.snapshot(),'context':self.base.context,
              'continuous_session':self.session,'experiment':'21'}
        tmp=out.with_suffix('.tmp')
        tmp.write_text(json.dumps(blob,ensure_ascii=False),encoding='utf-8')
        tmp.replace(out)

    @classmethod
    def load(cls,path,session=None):
        blob=json.loads(Path(path).read_text(encoding='utf-8'))
        return cls(NexoDialogue.load(path),session or blob.get('continuous_session','principal'))
