"""NEXO | Protótipo isolado de esferas observacionais e aprendizagem estrutural.

Sem semântica codificada: a memória inicia vazia. Sensores são tokens opacos
(ex.: (8, 0) significa um valor binário explicitamente observado, NÃO uma
interpretação). A consequência Y é observada depois da previsão.

Regras:
  - Um raio ativa a esfera; o peso de ativação = quantidade de raios.
  - Somente a coincidência completa de entradas de uma candidata serve como
    evidência de uma condição preditiva. Ativação != previsão.
  - Candidatas são propostas por experiências, testadas em eventos posteriores
    e descartadas se não agregarem evidência preditiva suficiente.
  - Ligações de índice fragmento->esferas permitem ativação sem scan global.
  - Expandir pares promissores em trincas = descoberta estrutural incremental.
"""
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
import math
import json
from pathlib import Path
from collections import deque


def wilson_lower(success, total, z=1.28):
    if total <= 0: return 0.0
    p=success/total; z2=z*z
    return (p+z2/(2*total)-z*math.sqrt((p*(1-p)+z2/(4*total))/total))/(1+z2/total)


@dataclass
class Sphere:
    parts: tuple
    birth: int
    hits: int=0
    positives: int=0
    state: int=0
    rays: int=0
    useful: bool=False
    def confidence(self):
        return self.positives/self.hits if self.hits else 0


class NexoSphereLearner:
    def __init__(self, max_order=3, max_candidates=2500, max_rays_per_event=24,
                 min_evidence=14, min_confidence=0.89, min_gain=0.27,
                 prune_after=120, cooldown=160, expand_min=12,
                 prune=True):
        self.max_order=max_order
        self.max_candidates=max_candidates
        self.max_rays_per_event=max_rays_per_event
        self.min_evidence=min_evidence
        self.min_confidence=min_confidence
        self.min_gain=min_gain
        self.prune_after=prune_after
        self.cooldown=cooldown
        self.expand_min=expand_min
        self.prune=prune
        self.spheres={}
        self.reverse_index=defaultdict(set)
        self.cooldowns={}
        self.expiry_queue=deque()
        self.review_due=defaultdict(set)
        self.expired_uncertain=0
        self.blocked_proposals=0
        self.t=0; self.positive_total=0
        self.created=0; self.deleted=0; self.promoted=0; self.demoted=0
        self.redundant_removed=0
        self.rays_visited=0; self.max_candidates_seen=0
        self.last_active={}  # temporary and only for the last observation
        self.prequential={'correct':0,'total':0,'tp':0,'fp':0,'fn':0,'tn':0}

    @staticmethod
    def tokens_from_vector(x):
        # An explicit zero is an observed value, not an absent activation.
        return frozenset((i,int(v)) for i,v in enumerate(x))

    def create(self, parts):
        key=tuple(sorted(parts))
        if len(key) != len(set(key)) or not key or len(key)>self.max_order:
            return False
        if len({p[0] for p in key})!=len(key):  # no contradictory sensor values
            return False
        if key in self.spheres: return False
        if len(self.spheres)>=self.max_candidates:
            self.blocked_proposals+=1
            return False
        if self.cooldowns.get(key,0)>self.t:
            return False
        obj=Sphere(parts=key,birth=self.t)
        self.spheres[key]=obj
        for p in key:
            self.reverse_index[p].add(key)
        self.created+=1
        self.review_due[self.t+self.prune_after].add(key)
        self.max_candidates_seen=max(self.max_candidates_seen,len(self.spheres))
        return True

    def remove(self,key,redundant=False):
        obj=self.spheres.pop(key,None)
        if not obj:return
        for p in key:
            self.reverse_index[p].discard(key)
        self.deleted+=1
        self.redundant_removed+=int(redundant)
        self.cooldowns[key]=self.t+self.cooldown
        self.expiry_queue.append((self.t+self.cooldown,key))

    def activate(self,tokens):
        # Rays only for spheres reachable from tokens in THIS experience.
        rays=defaultdict(int)
        for token in tokens:
            for key in self.reverse_index.get(token,()):
                rays[key]+=1
                self.rays_visited+=1
        for key in self.last_active:
            if key in self.spheres:
                s=self.spheres[key]; s.state=0;s.rays=0
        for key,n in rays.items():
            s=self.spheres[key];s.state=1;s.rays=n
        self.last_active=rays
        return rays

    def predict(self,tokens):
        rays=self.activate(tokens)
        completed=[self.spheres[k] for k,c in rays.items() if c==len(k) and self.spheres[k].useful]
        if not completed:
            return 0, None
        # Focus: max rays. For ties, prefer strongest observed confidence, then smallest.
        best=max(completed,key=lambda s:(s.rays,wilson_lower(s.positives,s.hits),-len(s.parts)))
        return 1,best.parts

    def step(self,x,y,train=True):
        tokens=self.tokens_from_vector(x)
        if len(tokens)>self.max_rays_per_event:
            raise ValueError('Evento excede o orçamento local de fragmentos observados')
        prediction,focus=self.predict(tokens)
        if not train:
            return prediction,focus
        y=int(y)
        self.prequential['total']+=1
        self.prequential['correct']+=(prediction==y)
        self.prequential[('tp' if y and prediction else 'fp' if prediction else 'fn' if y else 'tn')]+=1
        self.t+=1;self.positive_total+=y
        # pre-existing candidates only; newly created after the update CANNOT
        # use this example to inflate confidence (avoids selection bias).
        completed=[]
        for k,n in self.last_active.items():
            if n==len(k):
                s=self.spheres[k]
                s.hits+=1;s.positives+=y
                completed.append(s)
        baseline=self.positive_total/self.t
        for s in completed:
            old=s.useful
            low=wilson_lower(s.positives,s.hits)
            s.useful=(s.hits>=self.min_evidence
                      and s.confidence()>=self.min_confidence
                      and low>=max(.62,baseline+self.min_gain))
            if s.useful and not old:self.promoted+=1
            if old and not s.useful:self.demoted+=1
        # Remove configurations whose positive prediction is already supported
        # by a smaller reliable sphere. Search through subsets and incident
        # connections only, never across all memory.
        if self.prune:
            for s in completed:
                if s.useful and s.parts in self.spheres:
                    self.prune_redundant(s)
        # Make new hypotheses ONLY from positive observed experiences.
        # Signals are opaque; this policy is a general discovery mechanism.
        if y:
            for tok in sorted(tokens): self.create((tok,))
            for p in combinations(sorted(tokens),2):self.create(p)
            if self.max_order>=3:
                # Expand only pairs demonstrating some predictive signal but
                # not yet a sufficiently precise full rule. No enumeration of
                # all triples or global scan of candidates.
                promising=[s for s in completed if len(s.parts)==2
                           and s.hits>=self.expand_min
                           and baseline+.10<s.confidence()<self.min_confidence]
                promising.sort(key=lambda s:(-s.confidence(),-s.hits,s.parts))
                for s in promising[:12]:
                    for tok in sorted(tokens):
                        if tok not in s.parts:
                            self.create((*s.parts,tok))
        if self.prune:
            self.review_candidates_due()
        while self.expiry_queue and self.expiry_queue[0][0]<=self.t:
            due,key=self.expiry_queue.popleft()
            if self.cooldowns.get(key)==due: del self.cooldowns[key]
        return prediction,focus

    def prune_redundant(self,s):
        from itertools import combinations
        parts=s.parts
        for length in range(1,len(parts)):
            for sub in combinations(parts,length):
                parent=self.spheres.get(sub)
                if parent and parent.useful and parent.hits>=s.hits and parent.confidence()+.04>=s.confidence():
                    self.remove(parts,redundant=True)
                    return
        if parts not in self.spheres:return
        incident=list(self.reverse_index.get(parts[0],()))
        pset=set(parts)
        for key in incident:
            if len(key)<=len(parts) or key not in self.spheres:continue
            child=self.spheres[key]
            if child.useful and pset.issubset(key) and s.hits>=child.hits and s.confidence()+.04>=child.confidence():
                self.remove(key,redundant=True)

    def review_candidates_due(self):
        """Poda por agenda (time-wheel), sem varrer toda a memória.

        Candidatas com pouca evidência não são rotuladas como ruins; após
        6 janelas sem sustentação suficiente expiram por limite de orçamento.
        """
        baseline=self.positive_total/max(1,self.t)
        for key in self.review_due.pop(self.t,set()):
            s=self.spheres.get(key)
            if s is None or s.useful:continue
            age=self.t-s.birth
            if s.hits>=self.min_evidence and s.confidence()<=baseline+.08:
                self.remove(key)
            elif age>=6*self.prune_after and s.hits<self.min_evidence:
                self.expired_uncertain+=1
                self.remove(key)
            else:
                self.review_due[self.t+self.prune_after].add(key)

    def save_learned_memory(self, path):
        """Serializa SOMENTE esferas comprovadas, sem dados brutos de treino.

        Esta é uma foto para INFERÊNCIA. Estatísticas online das candidatas
        descartadas não são preservadas; não é um checkpoint de treino.
        """
        committed=[s for s in self.spheres.values() if s.useful]
        data={'format':'nexo-sphere-memory-v0.1','semantics':'opaque-binary-literals',
              'sphere_rule':'one-ray-active, full-coincidence-for-evidence',
              'spheres':[{'parts':[list(p) for p in s.parts],
                          'hits':s.hits,'positives':s.positives}
                         for s in sorted(committed,key=lambda s:(len(s.parts),s.parts))]}
        Path(path).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
        return len(committed)

    @classmethod
    def from_learned_memory(cls,path):
        data=json.loads(Path(path).read_text(encoding='utf-8'))
        if data.get('format')!='nexo-sphere-memory-v0.1':
            raise ValueError('Formato de memória incompatível')
        m=cls(max_order=max((len(s['parts']) for s in data['spheres']),default=1),
              max_candidates=max(2500,len(data['spheres'])))
        for item in data['spheres']:
            key=tuple(tuple(x) for x in item['parts'])
            m.create(key)
            s=m.spheres[tuple(sorted(key))]
            s.hits=int(item['hits']);s.positives=int(item['positives']);s.useful=True
        return m

    def audit(self):
        useful=[s for s in self.spheres.values() if s.useful]
        # Prune redundant subset/superset only in reporting, not in causal
        # online learning. The underlying model still retains all true rules.
        minimal=[]
        for s in sorted(useful,key=lambda z:(len(z.parts),z.parts)):
            if any(set(m.parts).issubset(s.parts) for m in minimal):continue
            minimal.append(s)
        return {
          'n_experiences':self.t,'n_candidates_live':len(self.spheres),
          'n_useful':len(useful),'n_minimal_useful':len(minimal),
          'minimal_useful':[{'parts':list(s.parts),'seen':s.hits,'positives':s.positives,
                              'confidence':round(s.confidence(),3)} for s in minimal[:20]],
          'created':self.created,'discarded':self.deleted,
          'promoted':self.promoted,'demoted':self.demoted,
          'redundant_removed':self.redundant_removed,
          'max_candidates_seen':self.max_candidates_seen,
          'rays_visited_total':self.rays_visited,
          'prequential':self.prequential,
          'index_edges':sum(map(len,self.reverse_index.values())),
          'cooldowns':len(self.cooldowns),
          'expired_uncertain':self.expired_uncertain,
          'blocked_proposals':self.blocked_proposals
        }
