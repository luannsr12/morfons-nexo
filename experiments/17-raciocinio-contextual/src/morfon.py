"""NEXO 14: motor integrado experimental. Sem labels/semantica de mundo hardcoded.
Memoria: Morphon (atomos e compostos), com portas, marcas, coordenadas, contadores.
Indices reverse sao caches derivadas de portas, nao fonte de conhecimento.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict, deque
from itertools import combinations
from typing import Any
import math, hashlib, json, random


def wilson(s,n,z=1.28):
    if not n:return 0.
    p=s/n; z2=z*z
    return (p+z2/(2*n)-z*math.sqrt(p*(1-p)/n+z2/(4*n*n)))/(1+z2/n)

def stable_point(key,dim):
    b=hashlib.shake_256(repr(key).encode()).digest(8*dim)
    x=[int.from_bytes(b[8*i:8*i+8],'little')/(2**64-1)*2-1 for i in range(dim)]
    return x

def flat_lits(lits):
    return tuple(sorted((int(i),int(v)) for i,v in lits))

@dataclass
class Morphon:
    uid:int
    kind:str
    literals:tuple=()  # descriptors (sensor id, explicit observed bit), not class names
    ports:tuple=()     # source node IDs for direct incoming rays; can be nested children
    children:set=field(default_factory=set) # derived lookup cache? persisted as outgoing references
    xyz:list=field(default_factory=list)
    facets:list=field(default_factory=list)
    holes:dict=field(default_factory=dict)  # persistent observed port marks by id
    observations:int=0
    positives:int=0
    promoted:bool=False
    novel_pos:int=0
    novel_neg:int=0
    birth:int=0
    last_seen:int=0
    review_at:int=0
    rays:set=field(default_factory=set,repr=False) # transient, not persisted
    completed:bool=False  # transient
    # notes: a pulse from one connected node activates it even if incomplete
    @property
    def active(self):return int(bool(self.rays))
    @property
    def support(self):return len(self.rays)
    @property
    def rate(self):return self.positives/self.observations if self.observations else 0.
    def snapshot(self):
        return {'uid':self.uid,'kind':self.kind,'literals':list(self.literals),
                'ports':list(self.ports),'children':sorted(self.children),
                'xyz':self.xyz,'facets':self.facets,'holes':self.holes,
                'observations':self.observations,'positives':self.positives,
                'promoted':self.promoted,'novel_pos':self.novel_pos,'novel_neg':self.novel_neg,'birth':self.birth,'last_seen':self.last_seen,'review_at':self.review_at}
    @classmethod
    def load(cls,d):
        return cls(d['uid'],d['kind'],tuple(map(tuple,d['literals'])),tuple(d['ports']),
                   set(d.get('children',[])),list(d['xyz']),list(d['facets']),
                   {int(k):int(v) for k,v in d['holes'].items()},
                   d['observations'],d['positives'],d['promoted'],d.get('novel_pos',0),d.get('novel_neg',0),d['birth'],d['last_seen'],d.get('review_at',0))

@dataclass
class Config:
    max_order:int=3
    max_nodes:int=1800
    min_obs:int=10
    conf:float=.83
    lift:float=.19
    min_wilson:float=.63
    expand_min:int=8
    max_expansions:int=10
    learning:str='legacy'   # legacy / mdl
    nested:bool=False
    geometry_dim:int=3
    facet:bool=False
    faceted_focus:bool=False
    spectral:str='none'  # none, 1-hop, bandpass
    spectral_alpha:float=.30
    propagation:str='completed' # complete or all; user requirement activation unaffected
    coord_focus:bool=False
    hrr_dim:int=0
    max_relays:int=128
    facet_capacity:int=0 # 0 = no automatic subdividing
    spectral_proposal:bool=False
    prune_redundant:bool=True
    focus_rule:str="ray_first" # ray_first | evidence_first | evidence_ray
    require_novel_gain:bool=False
    order_controller:bool=False
    promotion_penalty:str="wilson" # wilson | multiplicity (conservative heuristic)
    periodic_prune:bool=False
    review_window:int=100

class MorphMemory:
    def __init__(self,config:Config,seed=0):
        self.cfg=config;self.seed=seed;self.rng=random.Random(seed)
        self.nodes={}; self.by_lits={};self.by_token={};self.step_no=0
        self.next_uid=0
        self.ledger_uid=self.next_uid;self.next_uid+=1
        self.nodes[self.ledger_uid]=Morphon(self.ledger_uid,'ledger',(),(),set(),
                                            [0.]*config.geometry_dim,[],{},birth=0)
        self.cache=defaultdict(set) # port node ID->parents, rebuildable
        self.last_pulsed=set();self.review_due=defaultdict(set);self.metrics={'created':0,'promoted':0,'demoted':0,'proposals':0,
                                             'rays':0,'edges_accessed':0,'spectral_edges':0,
                                             'nested_created':0,'max_candidates_seen':0,'over_budget':0,'pruned':0,'blocked_dependency':0}
        self.last_info={}
        self.controller_uid=None
        if self.cfg.order_controller:
            i=self.next_uid;self.next_uid+=1
            ctrl=Morphon(i,'controller',(),(),set(),[0.]*self.cfg.geometry_dim,
                         [{'order':k,'tested':0,'correct':0} for k in range(2,self.cfg.max_order+1)],{},birth=0)
            self.nodes[i]=ctrl;self.controller_uid=i
    @property
    def n_train(self):return self.nodes[self.ledger_uid].observations
    @n_train.setter
    def n_train(self,value):self.nodes[self.ledger_uid].observations=int(value)
    @property
    def total_positive(self):return self.nodes[self.ledger_uid].positives
    @total_positive.setter
    def total_positive(self,value):self.nodes[self.ledger_uid].positives=int(value)
    def _create(self,kind,literals,ports=()):
        literal_key=flat_lits(literals)
        if literal_key in self.by_lits:return self.nodes[self.by_lits[literal_key]],False
        if len(self.nodes)>=self.cfg.max_nodes:
            self.metrics['over_budget']+=1; return None,False
        # do not create contradictory literal values at same position
        if len({i for i,v in literal_key}) != len(literal_key):return None,False
        uid=self.next_uid; self.next_uid+=1
        xyz=stable_point((self.seed,'position',literal_key),self.cfg.geometry_dim)
        obj=Morphon(uid,kind,literal_key,tuple(ports),set(),xyz,[],{},birth=self.step_no)
        if self.cfg.facet:
            # persistent faces: one face per incoming port (and intersections later)
            obj.facets=[{'source':int(x),'order':k,'geometry':stable_point((uid,x,k),3)}
                        for k,x in enumerate(ports)]
        for pid in ports:
            obj.holes[int(pid)]=1
        self.nodes[uid]=obj;self.by_lits[literal_key]=uid
        if kind=='atom':
            self.by_token[literal_key[0]]=uid
        for pid in ports:
            self.nodes[pid].children.add(uid)
            self.cache[pid].add(uid)
        if kind!='atom' and self.cfg.periodic_prune:
            obj.review_at=self.step_no+self.cfg.review_window
            self.review_due[obj.review_at].add(uid)
        self.metrics['created']+=1
        if kind!='atom':self.metrics['proposals']+=1
        if kind=='nested':self.metrics['nested_created']+=1
        self.metrics['max_candidates_seen']=max(self.metrics['max_candidates_seen'],len(self.nodes))
        return obj,True
    def _atom(self,token):
        token=(int(token[0]),int(token[1]))
        if token in self.by_token:return self.nodes[self.by_token[token]]
        return self._create('atom',(token,))[0]
    def _choose_ports(self,lits,forced_nested=False):
        lits=flat_lits(lits)
        atoms=[self._atom(t).uid for t in lits]
        if not ((self.cfg.nested and len(lits)>=4) or (self.cfg.facet_capacity and len(lits)>self.cfg.facet_capacity) or forced_nested):
            return 'composite',tuple(atoms)
        # for 4 or 5 literals, attach to two pair subunits when available,
        # while preserving any unmatched single atom. Crucially candidates do not
        # get +1 evidence by creating child units on this very observation.
        if self.cfg.facet_capacity and len(lits)>self.cfg.facet_capacity:
            # split a large surface into independently addressable nested faces.
            # Split mechanics are general, not a known target relation.
            k=max(2,min(self.cfg.facet_capacity,len(lits)-1))
            parts=[lits[:k],lits[k:]]
            chosen=[]
            for part in parts:
                if len(part)==1:chosen.append(self.by_token[part[0]])
                else:
                    child,_=self.propose(part)
                    if child is None:return 'composite',tuple(atoms)
                    chosen.append(child.uid)
            return 'nested',tuple(sorted(chosen))
        chosen=[]; remaining=set(lits)
        keys=[(lits[i],lits[j]) for i in range(len(lits)) for j in range(i+1,len(lits))]
        options=[]
        for pair in keys:
            uid=self.by_lits.get(flat_lits(pair))
            if uid is not None and self.nodes[uid].kind!='atom':
                n=self.nodes[uid]; options.append((-n.observations, pair,uid))
        for _, pair, uid in sorted(options):
            if set(pair).issubset(remaining):
                chosen.append(uid);remaining.difference_update(pair)
        for tok in sorted(remaining):chosen.append(self.by_token[tok])
        if len(chosen)==len(lits):return 'composite',tuple(sorted(chosen))
        return 'nested',tuple(sorted(chosen))
    def propose(self,lits):
        lits=flat_lits(lits)
        if not lits or len(lits)>self.cfg.max_order:return None,False
        if lits in self.by_lits:return self.nodes[self.by_lits[lits]],False
        kind,ports=self._choose_ports(lits)
        return self._create(kind,lits,ports)
    def _remove_candidate(self,uid):
        n=self.nodes.get(uid)
        if n is None or n.kind=='atom' or n.promoted:return False
        if n.children:
            self.metrics['blocked_dependency']+=1;return False
        self.nodes.pop(uid);self.by_lits.pop(n.literals,None)
        for pid in n.ports:
            self.nodes[pid].children.discard(uid)
            self.cache[pid].discard(uid)
        self.last_pulsed.discard(uid)
        self.metrics['pruned']+=1
        return True
    def _review_candidates(self):
        for uid in self.review_due.pop(self.step_no,()):
            n=self.nodes.get(uid)
            if n is None:continue
            if n.promoted:
                n.review_at=0
                continue
            base=self.total_positive/max(1,self.n_train)
            old_enough=(self.step_no-n.birth>=6*self.cfg.review_window)
            discard=(n.observations>=self.cfg.min_obs and n.rate<=base+.08) or (old_enough and n.observations<self.cfg.min_obs)
            if not discard or not self._remove_candidate(uid):
                n.review_at=self.step_no+self.cfg.review_window
                self.review_due[n.review_at].add(uid)
    def pulse(self,tokens):
        # reset ONLY touched previously active; no traversal of all memory
        for uid in self.last_pulsed:
            n=self.nodes[uid];n.rays.clear();n.completed=False
        self.last_pulsed=set();certified=set(); rays_count=0;edges=0
        seen_tokens=flat_lits(tokens)
        queue=deque()
        for token in seen_tokens:
            pid=self.by_token.get(token)
            if pid is None: continue
            a=self.nodes[pid];a.rays.add(-1);a.completed=True
            self.last_pulsed.add(pid);certified.add(pid)
            queue.append((pid,1))
        processed=set()
        while queue:
            pid,depth=queue.popleft()
            if pid in processed:continue
            processed.add(pid)
            if depth>self.cfg.max_order+2:continue
            for uid in sorted(self.cache.get(pid,())):
                edges+=1
                parent=self.nodes[uid]
                old_active=parent.active
                if pid not in parent.rays:
                    parent.rays.add(pid);rays_count+=1
                    self.last_pulsed.add(uid)
                is_full=all(self.nodes[c].completed for c in parent.ports)
                if is_full and not parent.completed:
                    parent.completed=True;certified.add(uid)
                # activate at one ray always. Passing the signal to higher levels
                # is a separate policy; all-mode can cascade wildly.
                if (self.cfg.propagation=='all' and not old_active) or (self.cfg.propagation=='completed' and is_full):
                    queue.append((uid,depth+1))
                if edges>=self.cfg.max_relays*100:
                    break
            if edges>=self.cfg.max_relays*100:break
        self.metrics['rays']+=rays_count
        self.metrics['edges_accessed']+=edges
        comp=[self.nodes[uid] for uid in certified if self.nodes[uid].kind!='atom']
        if self.controller_uid is not None:
            ctrl=self.nodes[self.controller_uid];ctrl.rays.clear()
            ctrl.rays.update(n.uid for n in comp if n.promoted)
            if ctrl.rays:self.last_pulsed.add(self.controller_uid)
        self.last_info={'rays':rays_count,'edges':edges,'active':sum(self.nodes[i].active for i in self.last_pulsed),
                        'completed':len(comp),'certified_ids':[n.uid for n in comp]}
        return comp
    def _local_spectral(self,completed):
        # Local polynomial filter on incidence-derived adjacency of the candidate set.
        # No eigendecomposition; W*x and W^2*x are computed via shared ports.
        if self.cfg.spectral=='none':return {n.uid:0. for n in completed}
        q={n.uid for n in completed}
        input_to_nodes=defaultdict(list)
        for n in completed:
            for tok in n.literals:input_to_nodes[tok].append(n.uid)
        neigh=defaultdict(set)
        for uids in input_to_nodes.values():
            for i in uids:
                neigh[i].update(j for j in uids if j!=i)
        self.metrics['spectral_edges']+=sum(len(v) for v in neigh.values())
        x={n.uid:float(n.support) for n in completed}
        def W(vec):
            return {i:(sum(vec.get(j,0.) for j in neigh[i])/len(neigh[i]) if neigh[i] else 0.) for i in q}
        p1=W(x)
        if self.cfg.spectral=='1-hop':return p1
        p2=W(p1)
        return {i:p1[i]-p2[i] for i in q}
    def _chosen_order(self):
        if self.controller_uid is None:return self.cfg.max_order
        faces=self.nodes[self.controller_uid].facets
        # maximize empirical prequential accuracy, with deterministic preference
        # for lower complexity on ties. Model selection has no world labels.
        eligible=[f for f in faces if f['tested']>=30]
        if not eligible:return self.cfg.max_order
        return max(eligible,key=lambda f:(f['correct']/f['tested'], -f['order']))['order']
    def predict(self,x):
        tokens={(i,int(v)) for i,v in enumerate(x)}
        comp=self.pulse(tokens)
        cap=self._chosen_order()
        eligible=[n for n in comp if n.promoted and len(n.literals)<=cap]
        if not eligible:
            return 0,None
        spec=self._local_spectral(eligible)
        def key(n):
            # Every ray remains part of the instantaneous support. The variants
            # differ in how that support competes with durable experience.
            r=float(n.support)
            if self.cfg.spectral!='none':r+=self.cfg.spectral_alpha*spec[n.uid]
            if self.cfg.faceted_focus and self.cfg.facet:r+=.02*len(n.facets)
            if self.cfg.coord_focus:r+=.01/(1.+sum(t*t for t in n.xyz))
            c=wilson(n.positives,n.observations)
            if self.cfg.focus_rule=='ray_first':return (r,c,-len(n.literals),-n.uid)
            if self.cfg.focus_rule=='evidence_first':return (c,r,-len(n.literals),-n.uid)
            if self.cfg.focus_rule=='evidence_ray':return (c+.07*math.log1p(r),c,r,-n.uid)
            raise ValueError(self.cfg.focus_rule)
        chosen=max(eligible,key=key)
        return 1,chosen.uid
    def _promote(self,n):
        if n.observations<self.cfg.min_obs:return False
        base=self.total_positive/max(1,self.n_train)
        if self.cfg.learning=='legacy':
            bound=wilson(n.positives,n.observations)
            if self.cfg.promotion_penalty=='multiplicity':
                # Conservative penalty for many candidate hypotheses; do not
                # claim anytime-valid statistical guarantee (candidates adapt).
                M=max(2,self.metrics['proposals'])
                bound=max(0.,n.rate-math.sqrt(math.log(2*M/.05)/(2*n.observations)))
            accepted=(n.rate>=self.cfg.conf and bound>=max(self.cfg.min_wilson,base+self.cfg.lift))
        elif self.cfg.learning=='mdl':
            # A genuine contingency-table MDL rule, not a conditional-rate
            # likelihood that ignores misses on events where pattern is absent.
            # All four numbers can be calculated from counters on the candidate
            # morphon plus global observed event count, not truth labels.
            h=n.observations; a=n.positives
            b=h-a;c=self.total_positive-a;d=self.n_train-h-c
            if min(a,b,c,d)<0:raise AssertionError((a,b,c,d))
            table=[[a,b],[c,d]];N=self.n_train
            rows=[a+b,c+d];cols=[a+c,b+d]
            mi=0.
            for i in range(2):
                for j in range(2):
                    v=table[i][j]
                    if v>0 and rows[i] and cols[j]:mi+=(v/N)*math.log2(v*N/(rows[i]*cols[j]))
            # Cost of describing candidate identity + extra Bernoulli parameter.
            bits=.5*math.log2(max(2,N))+math.log2(max(2,self.metrics['proposals']))
            accepted=(n.rate>base+.04 and N*mi>bits)
        else:raise ValueError(self.cfg.learning)
        if accepted and self.cfg.require_novel_gain:
            # An increased compositional order must correct predictions that
            # its previously promoted STRICT subsets did not already solve.
            # This uses only post-birth observations, never a future oracle.
            accepted=(n.novel_pos>=5 and n.novel_pos>3*n.novel_neg)
        if not accepted or not self.cfg.prune_redundant:return accepted
        # Minimum nonredundancy: a larger explanation must offer something
        # that no already-promoted subset explains nearly as reliably.
        for order in range(2,len(n.literals)):
            for sub in combinations(n.literals,order):
                sid=self.by_lits.get(tuple(sub))
                if sid is not None:
                    s=self.nodes[sid]
                    if (s.promoted and s.observations>=n.observations and
                        s.rate>=n.rate-.04):return False
        return True
    def train_one(self,x,y):
        pred, focus=self.predict(x)
        # evaluate and update only candidates that existed BEFORE this example
        current=[self.nodes[i] for i in self.last_info['certified_ids']]
        # prequential comparison: all alternative decisions are made from the
        # SAME pre-update memory. The observed y is not seen until afterward.
        alternatives={k:int(any(n.promoted and len(n.literals)<=k for n in current))
                      for k in range(2,self.cfg.max_order+1)}
        self.step_no+=1;self.n_train+=1;self.total_positive+=int(y)
        if self.controller_uid is not None:
            ctrl=self.nodes[self.controller_uid]
            for face in ctrl.facets:
                k=face['order'];face['tested']+=1;face['correct']+=int(alternatives[k]==int(y))
        # freeze evidence of competing substructures before any updates from y
        promoted_pre={n.uid for n in current if n.promoted}
        for n in current:
            if n.kind!='atom':
                covered=any((m.uid in promoted_pre and m.uid!=n.uid and
                            len(m.literals)<len(n.literals) and
                            set(m.literals).issubset(n.literals)) for m in current)
                if not covered:
                    if y:n.novel_pos+=1
                    else:n.novel_neg+=1
            old=n.promoted;n.observations+=1;n.positives+=int(y);n.last_seen=self.step_no
            n.promoted=self._promote(n)
            self.metrics['promoted']+=int(n.promoted and not old)
            self.metrics['demoted']+=int(old and not n.promoted)
            # observed failure/success is persistently recorded in the node
            # no separate truth ledger stored as semantic memory
        if y:
            tokens=flat_lits((i,int(v)) for i,v in enumerate(x))
            for tok in tokens:self._atom(tok)
            for pair in combinations(tokens,2):self.propose(pair)
            if self.cfg.max_order>=3 and pred==0:
                # expanding pairs is a policy from Exp08; no world-specific relation names
                promising=[n for n in current if len(n.literals)==2 and n.observations>=self.cfg.expand_min
                           and (n.rate>self.total_positive/max(1,self.n_train)+.08)
                           and (not n.promoted)]
                if self.cfg.spectral_proposal:
                    # One-hop local incidence statistic: active neighboring patterns
                    # influencing proposal order; no global eigenvectors.
                    hit_count=defaultdict(int)
                    for n in promising:
                        for lit in n.literals:hit_count[lit]+=1
                    promising.sort(key=lambda n:(-n.rate-.04*sum(hit_count[t] for t in n.literals),-n.observations,n.uid))
                else:promising.sort(key=lambda n:(-n.rate,-n.observations,n.uid))
                for n in promising[:self.cfg.max_expansions]:
                    for tok in tokens:
                        if tok not in n.literals:
                            self.propose(n.literals+(tok,))
            if self.cfg.max_order>=4 and pred==0:
                # grow higher-order hypotheses from known composite structures
                trip=[n for n in current if len(n.literals)==3 and n.observations>=self.cfg.expand_min
                      and n.rate>self.total_positive/max(1,self.n_train)+.06 and not n.promoted]
                trip.sort(key=lambda n:(-n.rate,-n.observations,n.uid))
                for n in trip[:self.cfg.max_expansions]:
                    for tok in tokens:
                        if tok not in n.literals:self.propose(n.literals+(tok,))
        if self.cfg.periodic_prune:self._review_candidates()
        return pred,focus
    def fit(self,X,Y):
        for x,y in zip(X,Y):self.train_one(x,y)
    def evaluate(self,X,Y):
        from collections import Counter
        counts=Counter(); decisions=[]; cost=[];explanations=[]
        for x,y in zip(X,Y):
            p,f=self.predict(x); counts[(int(y),p)]+=1
            cost.append((self.last_info['edges'],self.last_info['rays'],self.last_info['active']))
            decisions.append((int(y),p,f))
            if f is not None:explanations.append(tuple(self.nodes[f].literals))
        tp=counts[(1,1)];fp=counts[(0,1)];tn=counts[(0,0)];fn=counts[(1,0)]
        bal=.5*((tp/(tp+fn) if tp+fn else 0)+(tn/(tn+fp) if tn+fp else 0))
        return {'accuracy':(tp+tn)/max(1,len(Y)),'balanced':bal,
                'precision':tp/max(1,tp+fp),'recall':tp/max(1,tp+fn),
                'tp':tp,'fp':fp,'fn':fn,'tn':tn,
                'nodes':len(self.nodes),'composites':sum(n.kind!='atom' for n in self.nodes.values()),
                'promoted':sum(n.promoted for n in self.nodes.values()),
                'selected_order':self._chosen_order(),
                'nested':sum(n.kind=='nested' for n in self.nodes.values()),
                'avg_edges':sum(z[0] for z in cost)/max(1,len(cost)),
                'avg_rays':sum(z[1] for z in cost)/max(1,len(cost)),
                'avg_active':sum(z[2] for z in cost)/max(1,len(cost)),
                'spectral_edges_total':self.metrics['spectral_edges'],
                'predictions':decisions,'explanations':explanations}
    def snapshot(self):
        return {'config':self.cfg.__dict__,'seed':self.seed,'step_no':self.step_no,
                'n_train':self.n_train,'total_positive':self.total_positive,'next_uid':self.next_uid,
                'metrics':self.metrics,
                'nodes':[self.nodes[k].snapshot() for k in sorted(self.nodes)]}
    @classmethod
    def restore(cls,blob):
        mm=cls(Config(**blob['config']),blob['seed']);mm.step_no=blob['step_no'];mm.n_train=blob['n_train'];
        mm.total_positive=blob['total_positive'];mm.next_uid=blob['next_uid']
        mm.metrics.update(blob.get('metrics',{}))
        for d in blob['nodes']:
            n=Morphon.load(d);mm.nodes[n.uid]=n
            if n.kind=='controller':mm.controller_uid=n.uid;continue
            if n.kind=='ledger':mm.ledger_uid=n.uid;continue
            mm.by_lits[n.literals]=n.uid
            if n.kind=='atom':mm.by_token[n.literals[0]]=n.uid
            for pid in n.ports:mm.cache[pid].add(n.uid)
        if mm.cfg.periodic_prune:
            for n in mm.nodes.values():
                if n.kind not in ('atom','controller','ledger') and n.review_at>mm.step_no:
                    mm.review_due[n.review_at].add(n.uid)
        return mm
    def assert_integrity(self):
        assert len(self.nodes)==len(self.by_lits)+1+(1 if self.controller_uid is not None else 0)
        for n in self.nodes.values():
            assert set(n.holes)==set(n.ports)
            assert len(n.xyz)==self.cfg.geometry_dim
            for pid in n.ports:
                assert n.uid in self.nodes[pid].children
                assert n.uid in self.cache[pid]
            assert len(n.literals)==len(set(n.literals))
            if n.kind=='nested':
                recomposed=tuple(sorted(set(t for pid in n.ports for t in self.nodes[pid].literals)))
                assert recomposed==n.literals
        return True
