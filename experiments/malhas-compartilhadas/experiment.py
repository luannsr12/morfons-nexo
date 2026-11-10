"""NEXO: local overlap of Morphon meshes (isolated experiment, Python >=3.10).

Tests path composition, context intersection, canonical identity, rays,
provenance, exact conservative motif reconstruction and structural cost.
No domain knowledge, NLP, learned Genesis controller or automatic persistence is claimed.
"""
from __future__ import annotations
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from itertools import product
from typing import FrozenSet, Dict, List, Tuple
import json, random, time, statistics

C0 = frozenset((0,1,2))
CORE_LAW = ('immutable', (-1, 0, +1), 'activate_if_at_least_one_distinct_ray')

@dataclass
class Morphon:
    uid: str
    display: str
    memberships: set = field(default_factory=set)
    faces: dict = field(default_factory=dict)
    persistent: bool = False
    @property
    def core(self):
        # The law is read-only; learning changes faces and membership, never this law.
        return CORE_LAW

@dataclass(frozen=True)
class Relation:
    src: str
    dst: str
    tag: str
    layer: int
    scope: FrozenSet[int]
    evidence: str
    sign: int = +1

class MeshMemory:
    def __init__(self):
        self.nodes = {}
        self.by_src_tag = defaultdict(list)
        self.all_facts = []
        self.by_display_src_tag = defaultdict(list)
        self.negative = defaultdict(list)
        self.membership = defaultdict(set)

    def genesis_create(self, uid, display=None, persistent=False, config=None):
        # Genesis receives the mutable configuration before allocating a unit.
        if uid in self.nodes:
            raise ValueError('duplicate exact identity')
        self.nodes[uid] = Morphon(uid, display if display is not None else uid,
                                 faces=dict(config or {}), persistent=persistent)

    def genesis_edit_face(self, uid, key, value):
        self.nodes[uid].faces[key] = value

    def genesis_promote(self, uid):
        self.nodes[uid].persistent = True

    def genesis_remove(self, uid):
        if self.nodes[uid].persistent:
            raise ValueError('persistent Morphon is not removable')
        if any(f.src == uid or f.dst == uid for f in self.all_facts):
            raise ValueError('referenced Morphon requires explicit relation revision first')
        del self.nodes[uid]

    def add_fact(self, src, tag, dst, layer, scope, evidence, sign=+1):
        for uid in (src,dst):
            if uid not in self.nodes:
                raise ValueError('unknown fragment; Genesis must allocate it first')
        assert sign in (-1,+1) and scope
        rel = Relation(src, dst, tag, layer, frozenset(scope), evidence, sign)
        self.all_facts.append(rel)
        self.membership[layer].update((src,dst))
        self.nodes[src].memberships.add(layer)
        self.nodes[dst].memberships.add(layer)
        # Retain factual configuration as mutable peripheral marks.
        self.nodes[src].faces.setdefault('out',[]).append(evidence)
        if sign == +1:
            self.by_src_tag[(src,tag)].append(rel)
            self.by_display_src_tag[(self.nodes[src].display,tag)].append(rel)
        else:
            self.negative[(src,tag,dst)].append(rel)

    def query(self, start, tags, context=None, allowed_layers=None,
              match_display=False, ignore_context=False):
        """Only relevant postings are traversed, no global iteration over all facts.
        Returns target->list[proof], rays, and number of examined facts.
        """
        if start not in self.nodes:
            return {}, {}, 0
        rays=defaultdict(set)
        rays[start].add('stimulus:'+start)
        state = [(start, C0, frozenset(), (), frozenset())]
        examined = 0
        for tag in tags:
            nxt = []
            for uid, allowed, prov, path, conflicted in state:
                key = (self.nodes[uid].display, tag) if match_display else (uid,tag)
                index = self.by_display_src_tag if match_display else self.by_src_tag
                for rel in index.get(key,()):
                    examined += 1
                    if allowed_layers is not None and rel.layer not in allowed_layers:
                        continue
                    scope = C0 if ignore_context else allowed.intersection(rel.scope)
                    if context is not None and not ignore_context:
                        scope = scope.intersection((context,))
                    if not scope:
                        continue
                    # Physical rays are counted by distinct emitting fragment identity.
                    rays[rel.dst].add('fragment:'+rel.src)
                    negs = [n.evidence for n in self.negative.get((rel.src,rel.tag,rel.dst),())
                            if bool(n.scope.intersection(scope))]
                    nxt.append((rel.dst,scope,prov.union((rel.evidence,)),
                                path + (rel.evidence,), conflicted.union(negs)))
            state = nxt
            if not state:
                break
        result=defaultdict(list)
        for uid,scope,provenance,path,conflicted in state:
            result[uid].append({'scope':sorted(scope),'provenance':sorted(provenance),
                                'path':list(path),'opposed_evidence':sorted(conflicted)})
        return dict(result),dict(rays),examined

    def remove_provenance(self, ev):
        """Rebuild derived postings after a real observed event is withdrawn."""
        kept=[r for r in self.all_facts if r.evidence!=ev]
        old_nodes=self.nodes
        # Keep Genesis nodes and their immutable nuclei; rebuild peripheral relations.
        self.by_src_tag.clear();self.by_display_src_tag.clear();self.negative.clear()
        self.membership.clear();self.all_facts=[]
        for node in old_nodes.values():
            node.memberships.clear()
            node.faces.pop('out',None)
        for r in kept:
            self.add_fact(r.src,r.tag,r.dst,r.layer,r.scope,r.evidence,r.sign)

    def structural_counts(self, node_bytes=64, membership_bytes=8, bridge_bytes=16):
        m=sum(len(s) for s in self.membership.values())
        u=len(set().union(*self.membership.values())) if self.membership else 0
        h=m-u # minimal cross-layer identity links needed for connectivity of copies
        explicit=m*node_bytes+h*bridge_bytes
        shared=u*node_bytes+m*membership_bytes
        return {'layer_occurrences':m,'distinct_used_units':u,
                'minimal_copy_bridges':h,'copied_cost':explicit,
                'shared_cost':shared,'saving':explicit-shared,
                'saving_pct':100*(explicit-shared)/explicit if explicit else 0}


def build_world(n=600, seed=1917, shared_prob=.75, aligned_prob=.70):
    rng=random.Random(seed)
    m=MeshMemory()
    cases=[]
    for i in range(n):
        shared=rng.random()<shared_prob
        aligned=rng.random()<aligned_prob
        ctx=rng.randrange(2)
        start=f's{i}'
        left=f'b{i}' if shared else f'b{i}_LEFT'
        right=f'b{i}' if shared else f'b{i}_RIGHT'
        mid=f'm{i}'; target=f't{i}'
        for uid,disp in [(start,start),(left,'b'+str(i)),(right,'b'+str(i)),
                         (mid,mid),(target,target)]:
            if uid not in m.nodes:
                m.genesis_create(uid,disp,persistent=(i%7==0),
                                 config={'origin':'genesis','source':i})
        m.add_fact(start,'r0',left,0,{ctx},f'p{i}_0')
        m.add_fact(right,'r1',mid,1,{ctx if aligned else 1-ctx},f'p{i}_1')
        m.add_fact(mid,'r2',target,2,{ctx},f'p{i}_2')
        cases.append({'start':start,'target':target,'context':ctx,
                      'shared':shared,'aligned':aligned,'expected':shared and aligned})
    return m,cases


def evaluate_cases(mem, cases, mode):
    metrics=Counter()
    visited=[]
    truth_records=[]
    total_time=time.perf_counter()
    for c in cases:
        params={}
        if mode == 'isolated': params['allowed_layers']={0}
        elif mode == 'no_context': params['ignore_context']=True
        elif mode == 'label_match': params['match_display']=True
        elif mode == 'label_no_context':params={'match_display':True,'ignore_context':True}
        elif mode != 'shared_context':raise ValueError(mode)
        ans,rays,examined=mem.query(c['start'],('r0','r1','r2'),context=c['context'],**params)
        predicted=c['target'] in ans
        expected=c['expected']
        key='tp' if predicted and expected else 'fp' if predicted else 'fn' if expected else 'tn'
        metrics[key]+=1
        visited.append(examined)
        truth_records.append({'case':c['start'],'prediction':predicted,'expected':expected,
                              'examined_facts':examined})
    elapsed=(time.perf_counter()-total_time)*1000
    return {'mode':mode,**{k:metrics[k] for k in ('tp','fp','fn','tn')},
            'accuracy':(metrics['tp']+metrics['tn'])/len(cases),
            'precision':metrics['tp']/max(1,metrics['tp']+metrics['fp']),
            'recall':metrics['tp']/max(1,metrics['tp']+metrics['fn']),
            'mean_examined':round(statistics.mean(visited),3),
            'max_examined':max(visited),
            'elapsed_ms':round(elapsed,3)},truth_records


def antiunify(a,b):
    """Most specific generalization (first-order ordered tuple terms) with shared-variable identity.
    Each repeated same pair of mismatching subterms uses the same variable.
    """
    seen={}
    def rec(x,y):
        if x==y:return x
        if isinstance(x,tuple) and isinstance(y,tuple) and len(x)==len(y):
            return tuple(rec(i,j) for i,j in zip(x,y))
        key=(x,y)
        if key not in seen:seen[key]=('VAR',len(seen))
        return seen[key]
    return rec(a,b)

def match_pattern(pattern,term):
    mapping={}
    def rec(p,t):
        if isinstance(p,tuple) and len(p)==2 and p[0]=='VAR' and isinstance(p[1],int):
            if p in mapping and mapping[p]!=t:return False
            mapping[p]=t; return True
        if isinstance(p,tuple):
            if not isinstance(t,tuple) or len(p)!=len(t):return False
            return all(rec(a,b) for a,b in zip(p,t))
        return p==t
    return mapping if rec(pattern,term) else None

def instantiate(pattern,mapping):
    if isinstance(pattern,tuple) and len(pattern)==2 and pattern[0]=='VAR' and isinstance(pattern[1],int):
        return mapping[pattern]
    if isinstance(pattern,tuple):return tuple(instantiate(p,mapping) for p in pattern)
    return pattern

def motif_test():
    triples=[(f'u{i}',f'u{i}') for i in range(3)]
    unrelated=[(f'u{i}',f'v{i}') for i in range(3)]
    p=antiunify(triples[0],triples[1])
    q=antiunify(unrelated[0],unrelated[1])
    assert p==(('VAR',0),('VAR',0)),p
    assert q==(('VAR',0),('VAR',1)),q
    for xs,pattern in ((triples,p),(unrelated,q)):
        for t in xs:
            bind=match_pattern(pattern,t)
            assert bind is not None and instantiate(pattern,bind)==t
    def saving(n,m,v,b=8,q=4,c=10):return n*((m-v)*b-q)-c
    assert saving(2,2,1)==-2 and saving(3,2,1)==2
    assert saving(3,2,2)==-22
    new='new_fragment'
    generalized=(new,new)
    assert match_pattern(p,generalized) is not None
    assert match_pattern(q,generalized) is not None
    return {'identity_pattern':str(p),'unrelated_pattern':str(q),
            'identity_savings_n2':saving(2,2,1),
            'identity_savings_n3':saving(3,2,1),
            'unrelated_savings_n3':saving(3,2,2),
            'novel_identity_input':new,'novel_identity_output':new,
            'exact_reconstructions':len(triples)+len(unrelated)}


class ProofFactory:
    """Shared directed acyclic proof expressions (OR = alternatives, AND = joint facts).

    DAG nodes are stored once; evaluation can be redone after an evidence retraction
    without enumerating every derivation.
    """
    def __init__(self):
        self.nodes=[('false',()),('true',())]
        self.intern={self.nodes[0]:0,self.nodes[1]:1}

    def node(self, op, *args):
        key=(op,tuple(args))
        if key not in self.intern:
            self.intern[key]=len(self.nodes)
            self.nodes.append(key)
        return self.intern[key]

    def atom(self,evidence):return self.node('atom',evidence)

    def both(self,a,b):
        if a==0 or b==0:return 0
        if a==1:return b
        if b==1:return a
        return self.node('and',a,b)

    def either(self,a,b):
        if a==0:return b
        if b==0:return a
        if a==b:return a
        return self.node('or',a,b)

    def evaluate(self,root,active):
        cache={}
        def go(i):
            if i in cache:return cache[i]
            op,args=self.nodes[i]
            if op=='false':ans=False
            elif op=='true':ans=True
            elif op=='atom':ans=(args[0] in active)
            elif op=='and':ans=go(args[0]) and go(args[1])
            elif op=='or':ans=go(args[0]) or go(args[1])
            else:raise ValueError(op)
            cache[i]=ans
            return ans
        return go(root)


def factorized_query(mem,start,tags,context):
    """Context-scoped relational composition with a shared provenance DAG.

    In contrast to MeshMemory.query, it never enumerates distinct complete paths.
    This is a fixed-context finite-relational algorithm, not a learned Genesis policy.
    """
    factory=ProofFactory()
    active={start:1}
    visited=0
    for tag in tags:
        following={}
        for src,upstream in active.items():
            for rel in mem.by_src_tag.get((src,tag),()):
                visited+=1
                if context not in rel.scope:continue
                term=factory.both(upstream,factory.atom(rel.evidence))
                following[rel.dst]=factory.either(following.get(rel.dst,0),term)
        active=following
        if not active:break
    return active,factory,visited


def build_diamond_world(depth):
    mem=MeshMemory()
    for i in range(depth+1):mem.genesis_create('u'+str(i))
    for i in range(depth):
        a='x'+str(i)+'a';b='x'+str(i)+'b'
        mem.genesis_create(a);mem.genesis_create(b)
        for j,frag in enumerate((a,b)):
            mem.add_fact('u'+str(i),'split',frag,2*i,{0},f's{i}_{j}')
            mem.add_fact(frag,'merge','u'+str(i+1),2*i+1,{0},f'm{i}_{j}')
    return mem


def proof_factorization_test():
    rows=[]
    for depth in (1,2,3,5,8,10,12):
        mem=build_diamond_world(depth)
        path_tags=('split','merge')*depth
        t0=time.perf_counter()
        paths,rays,expanded=mem.query('u0',path_tags,context=0)
        enumerated_ms=(time.perf_counter()-t0)*1000
        t1=time.perf_counter()
        condensed,factory,examined=factorized_query(mem,'u0',path_tags,context=0)
        factorized_ms=(time.perf_counter()-t1)*1000
        goal='u'+str(depth)
        num=len(paths.get(goal,()))
        assert num==2**depth
        assert goal in condensed
        active={f.evidence for f in mem.all_facts}
        assert factory.evaluate(condensed[goal],active)
        assert factory.evaluate(condensed[goal],active-{'s0_0'})
        assert not factory.evaluate(condensed[goal],active-{'s0_0','s0_1'})
        assert len(rays[goal])==2  # 2 distinct incoming emitters, not 2^depth independent rays
        assert examined<=4*depth
        rows.append({'diamonds':depth,'evidence_facts':len(mem.all_facts),
                     'explicit_proof_paths':num,'explicit_examined':expanded,
                     'factorized_dag_nodes':len(factory.nodes),
                     'factorized_examined':examined,
                     'target_physical_rays':len(rays[goal]),
                     'enumerated_ms':round(enumerated_ms,4),
                     'factorized_ms':round(factorized_ms,4)})
    return rows


def chain_pattern_test():
    """Induce a reusable inter-mesh motif by antiunification of two observed paths."""
    def trace(a,b,c,d,contexts):
        k0,k1,k2=contexts
        return ('chain',('edge',0,'r0',a,b,k0),
                        ('edge',1,'r1',b,c,k1),
                        ('edge',2,'r2',c,d,k2))
    episodes=[trace('a1','b1','c1','d1',(0,0,0)),
              trace('a2','b2','c2','d2',(1,1,1))]
    pattern=antiunify(*episodes)
    for e in episodes:
        assignment=match_pattern(pattern,e)
        assert assignment is not None and instantiate(pattern,assignment)==e
    new=trace('newA','newB','newC','newD',(2,2,2))
    broken_identity=('chain',('edge',0,'r0','newA','newB',2),
                             ('edge',1,'r1','OTHER','newC',2),
                             ('edge',2,'r2','newC','newD',2))
    broken_context=trace('newA','newB','newC','newD',(2,1,2))
    assert match_pattern(pattern,new) is not None
    assert match_pattern(pattern,broken_identity) is None
    assert match_pattern(pattern,broken_context) is None
    return {'observed_complete_paths':2,
            'generalized_variables':len(match_pattern(pattern,new)),
            'new_unseen_path_matches':True,
            'broken_identity_rejected':True,
            'broken_context_rejected':True,
            'conservative_reconstructions':len(episodes),
            'pattern':repr(pattern)}


def test_ray_and_provenance():
    mem=MeshMemory()
    for x in ('s','b','m','m2','t'):
        mem.genesis_create(x,persistent=False,config={'role':'episode'})
    facts=[('s','r0','b',0,'a'),('b','r1','m',1,'b'),('m','r2','t',2,'c'),
           ('b','r1','m2',1,'d'),('m2','r2','t',2,'e')]
    for s,r,d,l,p in facts:mem.add_fact(s,r,d,l,{0},p)
    out,rays,_=mem.query('s',('r0','r1','r2'),0)
    assert len(out['t'])==2
    assert len(rays['t'])==2 and len(rays['m'])==1
    assert len(rays['b'])==1
    # An unrelated extra incident ray changes physical support, not path proof.
    rays['t'].add('unrelated_fragment')
    assert len(rays['t'])==3 and len(out['t'])==2
    mem.add_fact('m','r2','t',2,{0},'negative_c',sign=-1)
    out,_,_=mem.query('s',('r0','r1','r2'),0)
    assert any('negative_c' in proof['opposed_evidence'] for proof in out['t'])
    assert any(not proof['opposed_evidence'] for proof in out['t'])
    mem.remove_provenance('c')
    out,_,_=mem.query('s',('r0','r1','r2'),0)
    assert len(out['t'])==1 and out['t'][0]['path']==['a','d','e']
    assert all(node.core==CORE_LAW for node in mem.nodes.values())
    return {'initial_independent_paths':2,'initial_terminal_distinct_rays':2,
            'after_unrelated_ray':3,'remaining_proofs_after_retraction':1,
            'nucleus_unchanged':True}


def random_oracle_tests(seed=66,iterations=250):
    rng=random.Random(seed)
    verified=0
    for k in range(iterations):
        mem=MeshMemory()
        for i in range(8): mem.genesis_create('v'+str(i))
        for n in range(rng.randrange(5,25)):
            a='v'+str(rng.randrange(8));b='v'+str(rng.randrange(8))
            tag=rng.choice(('a','b','c'))
            mem.add_fact(a,tag,b,rng.randrange(3),{rng.randrange(3)},'ev'+str(n))
        start='v'+str(rng.randrange(8))
        tags=tuple(rng.choice(('a','b','c')) for _ in range(3))
        ctx=rng.randrange(3)
        got,_,_=mem.query(start,tags,context=ctx)
        # Independent brute-force 3-fold Cartesian-product oracle over positive facts.
        eligible=[[f for f in mem.all_facts if f.tag==tag and f.sign==1 and ctx in f.scope] for tag in tags]
        expected=defaultdict(list)
        for seq in product(*eligible):
            if seq[0].src==start and seq[0].dst==seq[1].src and seq[1].dst==seq[2].src:
                expected[seq[-1].dst].append(frozenset(f.evidence for f in seq))
        normalized={dst:sorted([frozenset(p['provenance']) for p in proofs],key=lambda s:sorted(s))
                    for dst,proofs in got.items()}
        want={dst:sorted(proofs,key=lambda s:sorted(s)) for dst,proofs in expected.items()}
        assert normalized==want,(k,tags,ctx,normalized,want)
        verified+=1
    return verified


def run():
    mem,cases=build_world()
    modes=['shared_context','isolated','no_context','label_match','label_no_context']
    evaluations={}
    records={}
    for mode in modes:
        m,r=evaluate_cases(mem,cases,mode)
        evaluations[mode]=m;records[mode]=r
    assert all(a['prediction']==a['expected'] for a in records['shared_context'])
    assert evaluations['isolated']['tp']==0
    assert evaluations['no_context']['fp']>0
    assert evaluations['label_match']['fp']>0
    costs=mem.structural_counts()
    # Alter only graph-size; no relevant posting can be added.
    probes=[cases[i] for i in (1,11,49,191,298,590)]
    touched_before=[mem.query(c['start'],('r0','r1','r2'),c['context'])[2] for c in probes]
    for i in range(20000):mem.genesis_create('noise'+str(i),config={'unrelated':True})
    touched_after=[mem.query(c['start'],('r0','r1','r2'),c['context'])[2] for c in probes]
    assert touched_before==touched_after
    result={
        'metadata':{'seeds':{'main':1917,'oracle':66},'num_world_cases':len(cases),
                    'notes':['Controlled finite relational worlds, deliberately constructed to test mechanisms',
                             'Generator supplies identities, relation tags and context scopes',
                             'No learning of shared identities or new Genesis policy is claimed']},
        'class_balance':{'shared_and_aligned':sum(c['expected'] for c in cases),
                         'shared_but_misaligned':sum(c['shared'] and not c['aligned'] for c in cases),
                         'split_but_aligned':sum(not c['shared'] and c['aligned'] for c in cases),
                         'split_and_misaligned':sum(not c['shared'] and not c['aligned'] for c in cases)},
        'evaluations':evaluations,'cost_model':{'node_unit_bytes':64,'node_layer_reference_bytes':8,
                                               'copy_bridge_bytes':16,**costs},
        'locality':{'extra_disconnected_nodes':20000,'probes_before':touched_before,'probes_after':touched_after},
        'motif':motif_test(),'cross_mesh_pattern':chain_pattern_test(),
        'factorized_provenance':proof_factorization_test(),
        'provenance_and_rays':test_ray_and_provenance(),
        'independent_bruteforce_graphs':random_oracle_tests()}
    with open('results.json','w',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False)
    with open('case_predictions.jsonl','w',encoding='utf-8') as f:
        for mode,rs in records.items():
            for row in rs:
                row=dict(row,mode=mode)
                f.write(json.dumps(row,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__':run()
