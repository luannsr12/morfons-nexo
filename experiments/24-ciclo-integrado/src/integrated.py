"""NEXO Exp24: núcleo imutável, marcas recebidas em faces, escrita INTER-Mórfon.

Mórfon nÃO reescreve sua própria superfície. Cada evento, vindo de outra
unidade, inscreve uma face no receptor; a derivação relacional e a escolha de
operações genéricas pertencem à lei imutável de núcleo. O original morfon.py
continua preservado. GF(2) é uma álgebra declarada, não uma semântica de mundo.

Interações: fonte -> episódio; episódio (núcleo constante) -> faces das unidades
relacionais; unidade ativa -> previsão (outro Mórfon); previsão -> decisão -> ação
externa -> nova ocorrência. Nenhuma previsão alimenta o treino como observação.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys, json, copy, hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'originals'))
from morfon_exp21_original import MorphMemory,Config


def monomials(n, degree):
    return tuple(tuple(c) for d in range(degree+1) for c in combinations(range(n),d))

def monomial_mask(x, monos):
    return sum(1<<i for i,m in enumerate(monos) if all(x[j] for j in m))

def echelon(equations):
    pivots={}
    for mask,value in equations:
        y=int(value); q=mask
        while q:
            p=q.bit_length()-1
            if p in pivots:
                q^=pivots[p][0];y^=pivots[p][1]
            else:
                pivots[p]=(q,y);break
        if not q and y: return None
    return pivots

def coefficients(pivots):
    coeff=0
    for p in sorted(pivots):
        mask,y=pivots[p]
        if y^((mask&coeff).bit_count()%2):coeff|=1<<p
    return coeff

def identified(mask,pivots):
    y=0
    while mask:
        p=mask.bit_length()-1
        if p not in pivots:return None
        q,v=pivots[p];mask^=q;y^=v
    return y

@dataclass(frozen=True)
class Nucleus:
    """Função constante de todas as unidades deste laboratório.

    As rotinas genéricas NÃO conhecem as funções do mundo. Cada invocação usa
    actor distinto do target. Alterar o núcleo de um Mórfon não é permitido.
    """
    algebra: str='GF2-relational-v1'
    external_write_only: bool=True

    def inscribe(self,mm,actor,target,mark,log):
        assert actor!=target,'autorreforma proibida'
        assert actor in mm.nodes and target in mm.nodes
        face={'writer':actor,'receiver':target,'origin':mark['origin'],
              'role':mark['role'],'payload':copy.deepcopy(mark['payload']),
              'interaction_index':len(log)+1}
        mm.nodes[target].facets.append(face)
        log.append({'actor':actor,'target':target,'role':mark['role']})
        return len(mm.nodes[target].facets)-1

    def fit(self,observations,nf,max_degree):
        """Resolver relações sob diferentes graus, SEM fornecer coeficientes."""
        for degree in range(max_degree+1):
            ms=monomials(nf,degree)
            piv=echelon((monomial_mask(x,ms),y) for x,y in observations)
            if piv is not None:
                return {'degree':degree,'monomials':ms,'pivots':piv,
                        'coeff':coefficients(piv),'rank':len(piv)}
        return None

class InteractingMorphons:
    def __init__(self,n_features=4,n_actions=2,n_outputs=3,max_degree=2,seed=0):
        self.nf=n_features;self.na=n_actions;self.no=n_outputs;self.degree=max_degree;self.seed=seed
        self.mm=MorphMemory(Config(max_order=15,max_nodes=60000,max_relays=20000,
                                    propagation='completed',facet=False),seed=seed)
        self.K=Nucleus();self.cores={self.mm.ledger_uid:self.K};self.sources={};self.roots={};self.events=[]
        self.serial=0;self.mutations=[];self.metrics=Counter();self.session=None
        self._bootstrap()

    def _new(self,kind,ports=()):
        self.serial+=1
        n,ok=self.mm._create(kind,((950000000,self.serial),),tuple(ports))
        if not ok:raise RuntimeError('Mórfon allocation failed')
        self.cores[n.uid]=self.K # o núcleo é imutável; não faz parte das faces
        return n.uid

    def _bootstrap(self):
        for j in range(self.nf):
            for bit in (0,1):self.sources['sensor',j,bit]=self._new('sensor')
        for a in range(self.na):self.sources['action',a]=self._new('action-source')
        for j in range(self.no):self.sources['output',j]=self._new('output-source')
        self.session=self._new('ongoing-session')
        # Mórfons receptores existentes, NÃO novas faces a cada contradição.
        for a in range(self.na):
            for j in range(self.no):
                r=self._new('relation',(self.sources['action',a],self.sources['output',j]))
                self.roots[a,j]=r
                self.K.inscribe(self.mm,self.sources['action',a],r,
                  {'origin':'genesis','role':'identity','payload':{'action':a,'output':j}},self.mutations)

    def _source_uids(self,x,a):
        return [self.sources['sensor',j,int(bit)] for j,bit in enumerate(x)]+[self.sources['action',a]]

    def _faces(self,uid,role=None):
        return [f for f in self.mm.nodes[uid].facets if role is None or f['role']==role]

    def _last_model(self,root):
        models=self._faces(root,'model')
        return models[-1]['payload'] if models else None

    def start_session(self,history):
        assert history in range(self.na)
        actor=self.sources['action',int(history)]
        self.K.inscribe(self.mm,actor,self.session,
              {'origin':'observed','role':'session-start',
               'payload':{'last_action':int(history)}},self.mutations)

    def current_history(self):
        faces=[f for f in self.mm.nodes[self.session].facets
               if f['role'] in ('session-start','last-action')]
        return faces[-1]['payload']['last_action'] if faces else None

    def observe(self,x,a,y,live=False):
        x=tuple(int(v) for v in x);y=tuple(int(v) for v in y)
        assert len(x)==self.nf and len(y)==self.no and 0<=a<self.na
        src=self._source_uids(x,a)
        # O acontecimento é um Mórfon distinto. Seu núcleo inscreve marcas
        # exclusivamente NAS SUPERFÍCIES DOS OUTROS MÓRFONS.
        episode=self._new('observed-episode',tuple(src))
        pulse=self.mm.pulse_units(src)
        assert episode in pulse['certified_ids']
        for j,target in enumerate(y):
            root=self.roots[a,j]
            self.K.inscribe(self.mm,episode,root,
              {'origin':'observed','role':'experience',
               'payload':{'before':x,'observed_output':target,'episode':episode}},self.mutations)
            observations=[(tuple(face['payload']['before']),face['payload']['observed_output'])
                         for face in self._faces(root,'experience') if face['origin']=='observed']
            fit=self.K.fit(observations,self.nf,self.degree)
            previous=self._last_model(root)
            version=(previous['version']+1 if previous else 1)
            marks=[]
            # Marcas persistentes são REUSADAS quando seu significado relacional
            # não mudou. Nenhuma cópia a cada episódio, nenhuma autoescrita.
            previous_mark_ids=[]
            for old in self._faces(root,'model'):
                previous_mark_ids.extend(old['payload']['marks'])
            existing={}
            for mark_uid in previous_mark_ids:
                f=self._faces(mark_uid,'coefficient')
                if f:existing[tuple(f[-1]['payload']['monomial'])]=mark_uid
            if fit is not None:
                for bit,mono in enumerate(fit['monomials']):
                    if not (fit['coeff']>>bit)&1:continue
                    if mono in existing:
                        marks.append(existing[mono]);self.metrics['marks_reused']+=1
                        continue
                    m=self._new('acquired-mark',(root,)+tuple(self.sources['sensor',k,1] for k in mono))
                    self.K.inscribe(self.mm,episode,m,
                      {'origin':'derived','role':'coefficient',
                       'payload':{'parent':root,'monomial':mono,'version':version}},self.mutations)
                    marks.append(m)
                    self.metrics['marks_created']+=1
            model={'version':version,'consistent':fit is not None,
                   'degree':fit['degree'] if fit is not None else None,
                   'basis':[list(z) for z in fit['monomials']] if fit else [],
                   'pivots':{str(k):list(v) for k,v in fit['pivots'].items()} if fit else {},
                   'rank':fit['rank'] if fit else None,'marks':marks,
                   'training_count':len(observations)}
            self.K.inscribe(self.mm,episode,root,
                      {'origin':'derived','role':'model','payload':model},self.mutations)
            self.metrics['refits']+=1
            if fit is None:self.metrics['inconsistencies']+=1
        self.events.append(episode);self.metrics['observations']+=1
        if live:
            self.K.inscribe(self.mm,episode,self.session,
                  {'origin':'observed','role':'last-action',
                   'payload':{'last_action':int(a)}},self.mutations)
        return episode

    def query(self,x,a,ablate=(),block_pulses=False,record_imagination=False):
        x=tuple(int(v) for v in x); assert len(x)==self.nf
        if block_pulses:return None,{'reason':'pulses_suppressed'}
        src=self._source_uids(x,a)+[self.sources['output',j] for j in range(self.no)]
        pulse=self.mm.pulse_units(src)
        certified=set(pulse['certified_ids'])-set(ablate)
        out=[];proof=[]
        for j in range(self.no):
            root=self.roots[a,j]
            if root not in certified:return None,{'reason':'missing_relation','root':root}
            model=self._last_model(root)
            if model is None:return None,{'reason':'untrained'}
            if not model['consistent']:return None,{'reason':'inconsistent','root':root}
            basis=[tuple(m) for m in model['basis']]
            piv={int(k):tuple(v) for k,v in model['pivots'].items()}
            if identified(monomial_mask(x,basis),piv) is None:
                return None,{'reason':'insufficient_experience','root':root}
            # Output depends only on certified, still-current marks; no lookup
            # in a table of worlds, semântica ou resultados por estado.
            bit=0;active_marks=[]
            for mid in model['marks']:
                if mid in certified:
                    bit^=1;active_marks.append(mid)
            out.append(bit);proof.extend(active_marks)
        consequence=tuple(out)
        if record_imagination:
            actor=self.roots[a,0]
            thought=self._new('internal-prediction',(actor,))
            # ação do Mórfon que produziu a previsão SOBRE OUTRO MÓRFON
            self.K.inscribe(self.mm,actor,thought,
              {'origin':'internal','role':'anticipation',
               'payload':{'input':x,'action':a,'predicted':consequence,
                          'proof_mark_uids':proof}},self.mutations)
            self.metrics['thoughts']+=1
        return consequence,{'reason':'ok','marks':proof,'certified':len(certified),
                            'rays':pulse['rays'],'edges':pulse['edges']}

    def choose_plan(self,initial,history,goal,max_depth=3,allow_imagination=False):
        """Busca mecânica genérica no núcleo constante, usando SOMENTE marcas.

        history é a última ação VIVIDA, recuperada dos acontecimentos; não é
        um rótulo semântico de contexto inventado pelo motor.
        """
        initial=tuple(initial);goal=tuple(goal)
        assert len(initial)==self.no and len(goal)==self.no
        if initial==goal:return (),{'reason':'already_there'}
        frontier=[(initial,int(history),())];seen={(initial,int(history))}
        for depth in range(1,max_depth+1):
            next_queue=[]
            for s,h,seq in frontier:
                for a in range(self.na):
                    x=s+(h,)
                    out,trace=self.query(x,a,record_imagination=allow_imagination)
                    if out is None:continue
                    proposed=seq+(a,)
                    if out==goal:return proposed,{'reason':'found','depth':depth,'last_proof':trace}
                    ident=(out,a) # histórico seguinte é a ação acabada de viver
                    if ident not in seen:
                        next_queue.append((out,a,proposed));seen.add(ident)
            frontier=next_queue
            if not frontier:break
        return None,{'reason':'no_guaranteed_path','depth_limit':max_depth}

    def choose_probe(self,available):
        """Escolher uma entrada disponível que seja uma nova direção informacional.
        Candidatos podem incluir estado/ação; NÃO contém consequências. A escolha
        usa somente as MARCAS DE EXPERIÊNCIA recebidas por outros Mórfons.
        A entrada precisa ser fisicamente alcançável/resetável pelo laboratório.
        """
        basis=monomials(self.nf,self.degree)
        candidates=[]
        for x,a in available:
            x=tuple(int(v) for v in x)
            root=self.roots[a,0]
            past=[tuple(face['payload']['before']) for face in self._faces(root,'experience')]
            if x in past:continue
            before=echelon((monomial_mask(p,basis),0) for p in past)
            after=echelon((monomial_mask(p,basis),0) for p in past+[x])
            gain=int(len(after)>len(before))
            candidates.append((-gain,len(past),int(a),x))
        if not candidates:return None
        _,_,a,x=min(candidates)
        actor=self.roots[a,0]
        target=self._new('internal-question',(actor,))
        self.K.inscribe(self.mm,actor,target,
          {'origin':'internal','role':'investigation','payload':{'action':a,'input':x}},self.mutations)
        self.metrics['questions']+=1
        return x,a

    def choose_for_signal(self,initial,history,channel,value,max_depth=3):
        """Obter sinal desejado num canal observável, não um estado completo.
        Simula com marcas aprendidas e memória própria da última ação.
        """
        assert 0<=channel<self.no and value in (0,1)
        initial=tuple(initial)
        if initial[channel]==value:return (),{'reason':'already_there'}
        frontier=[(initial,int(history),())];seen={(initial,int(history))}
        for depth in range(1,max_depth+1):
            next_queue=[]
            for s,h,seq in frontier:
                for a in range(self.na):
                    out,trace=self.query(s+(h,),a)
                    if out is None:continue
                    proposed=seq+(a,)
                    if out[channel]==value:
                        # O Mórfon da relação inscreve a intenção noutro Mórfon.
                        actor=self.roots[a,channel]
                        decision=self._new('internally-decided-action',(actor,))
                        self.K.inscribe(self.mm,actor,decision,
                          {'origin':'internal','role':'decision','payload':{
                           'goal_channel':channel,'goal_value':value,
                           'sequence':proposed,'proof_marks':trace['marks']}},self.mutations)
                        self.metrics['decisions']+=1
                        return proposed,{'reason':'found','depth':depth,'decision':decision}
                    ident=(out,a)
                    if ident not in seen:
                        next_queue.append((out,a,proposed));seen.add(ident)
            frontier=next_queue
        return None,{'reason':'no_guaranteed_path'}

    def fingerprint(self):
        return hashlib.sha256(str((self.K.algebra,self.K.external_write_only)).encode()).hexdigest()

    def validate_invariants(self):
        assert self.K==Nucleus()
        assert len(self.cores)==len(self.mm.nodes)
        assert all(core is self.K for core in self.cores.values())
        assert all(x['actor']!=x['target'] for x in self.mutations)
        for uid,node in self.mm.nodes.items():
            for face in node.facets:
                assert face['writer']!=uid
                assert face['receiver']==uid
        return {'all_nuclei_constant':True,'no_self_edits':True,
                'interaction_faces':sum(len(n.facets) for n in self.mm.nodes.values())}

    def snapshot(self):
        return {'mm':self.mm.snapshot(),'nf':self.nf,'na':self.na,'no':self.no,
                'degree':self.degree,'seed':self.seed,'serial':self.serial,
                'sources':[[list(k),v] for k,v in self.sources.items()],
                'roots':[[list(k),v] for k,v in self.roots.items()],
                'events':self.events,'mutations':self.mutations,'metrics':dict(self.metrics),
                'session':self.session,
                'nucleus':{'algebra':self.K.algebra,'external_write_only':self.K.external_write_only}}

    @classmethod
    def restore(cls,payload):
        obj=cls(payload['nf'],payload['na'],payload['no'],payload['degree'],payload['seed'])
        obj.mm=MorphMemory.restore(payload['mm'])
        obj.serial=payload['serial']
        obj.sources={tuple(k):v for k,v in payload['sources']}
        obj.roots={tuple(k):v for k,v in payload['roots']}
        obj.events=list(payload['events'])
        obj.session=payload['session']
        obj.mutations=list(payload['mutations'])
        obj.metrics=Counter(payload['metrics'])
        assert payload['nucleus']=={'algebra':obj.K.algebra,'external_write_only':obj.K.external_write_only}
        obj.cores={uid:obj.K for uid in obj.mm.nodes}
        obj.validate_invariants()
        return obj
