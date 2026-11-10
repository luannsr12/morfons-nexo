"""Exp23: laboratório isolado de morfologia causal em MorphMemory EXP21 original.

Nenhum código do núcleo foi alterado. Sem semântica de mundo no aprendiz.
As subdivisões são Mórfons normais, com portas dirigidas para pai e observação
espectral de face. Uma face existe enquanto os próprios Mórfons existem.
"""
from __future__ import annotations
import sys, math
from collections import Counter
from pathlib import Path
from dataclasses import dataclass
ORIGINAL=Path(__file__).resolve().parents[1]/'originals'
sys.path.insert(0,str(ORIGINAL))
from morfon_exp21_original import MorphMemory, Config

class FaceWorldLearner:
    def __init__(self, n_features: int, n_actions: int, *, morph: bool=True, seed: int=0):
        self.nf=n_features; self.na=n_actions; self.morph=morph
        self.mm=MorphMemory(Config(max_order=14,max_nodes=40000,max_relays=10000,
                propagation='completed',facet=True),seed=seed)
        self.serial=0;self.sources={};self.roots={};self.events=[];self.stats=Counter()
        for j in range(n_features):
            for bit in (0,1):self.sources[('sensor',j,bit)]=self._new('source',{'source':'sensor','channel':j,'bit':bit})
        for a in range(n_actions):self.sources[('action',a)]=self._new('source',{'source':'action','index':a})
        for j in range(n_features):self.sources[('target',j)]=self._new('source',{'source':'target','index':j})
    def _new(self,kind,meta,ports=()):
        self.serial+=1
        node,ok=self.mm._create(kind,((910000000,self.serial),),tuple(ports))
        if not ok:raise RuntimeError(('alloc',kind,self.serial))
        node.facets=[dict(meta)]
        return node.uid
    def _root(self,a,j):
        if (a,j) not in self.roots:
            fid=self._new('face',{'face_id':self.serial+1,'depth':0,'sector':[0.0,2*math.pi],
                'band':[-math.pi/2,math.pi/2],'split':None,'children':{},
                'examples':[],'output':None,'unresolved':False},
                (self.sources[('action',a)],self.sources[('target',j)]))
            self.roots[(a,j)]=fid;self.stats['roots']+=1
        return self.roots[(a,j)]
    def _face(self,uid):return self.mm.nodes[uid].facets[0]
    def _leaf(self,uid,s):
        while True:
            f=self._face(uid)
            if f['split'] is None:return uid
            uid=f['children'][int(s[f['split']])]
    def _reconcile(self, uid, depth=0):
        f=self._face(uid)
        if f['split'] is not None:return
        exps=[self._face(e) for e in f['examples']]
        ys={e['target_value'] for e in exps}
        if not ys:
            f['output']=None; f['unresolved']=False; return
        if len(ys)==1:
            f['output']=next(iter(ys)); f['unresolved']=False;return
        f['output']=None;f['unresolved']=True
        if not self.morph:
            counts=Counter(e['target_value'] for e in exps)
            f['output']=min((0,1),key=lambda k:(-counts[k],k))
            return
        ancestor_feats=set()
        cur=uid
        while True:
            meta=self._face(cur)
            if meta['depth']==0:break
            parent=self.mm.nodes[cur].ports[0]
            parentmeta=self._face(parent)
            ancestor_feats.add(parentmeta['split'])
            cur=parent
        candidates=[]
        n=len(exps)
        for j in range(self.nf):
            if j in ancestor_feats:continue
            groups={v:[e['target_value'] for e in exps if e['before'][j]==v] for v in (0,1)}
            if not all(groups.values()):continue
            # redução local da impureza; apenas episódios residentes nas faces
            gini=sum(len(g)/n*(1-sum((c/len(g))**2 for c in Counter(g).values())) for g in groups.values())
            candidates.append((gini,j))
        if not candidates:return
        _,j=min(candidates)
        lo,hi=f['sector'];mid=(lo+hi)/2.0
        children={}
        for b,rg in ((0,[lo,mid]),(1,[mid,hi])):
            sid=self.sources[('sensor',j,b)]
            child=self._new('face',{'face_id':self.serial+1,'depth':f['depth']+1,
              'sector':rg,'band':f['band'], 'split':None, 'children':{},
              'examples':[],'output':None,'unresolved':False}, (uid,sid))
            children[b]=child
        f['split']=j;f['children']=children;f['output']=None;f['unresolved']=False
        for eid in f['examples']:
            e=self._face(eid);self._face(children[e['before'][j]])['examples'].append(eid)
        self.stats['subdivisions']+=1
        # continuidade da área esférica da face original: ∫cos(lat)dlat dlon
        old_area=(hi-lo)*(math.sin(f['band'][1])-math.sin(f['band'][0]))
        new_area=sum((self._face(cid)['sector'][1]-self._face(cid)['sector'][0])*
                     (math.sin(f['band'][1])-math.sin(f['band'][0])) for cid in children.values())
        assert abs(old_area-new_area)<1e-10
        for child in children.values():self._reconcile(child,depth+1)
    def observe(self,s,a,next_s):
        assert len(s)==self.nf and len(next_s)==self.nf
        # estímulo + ação + consequência como Mórfon episódico persistente
        pre=[self.sources[('sensor',j,int(s[j]))] for j in range(self.nf)]
        event=self._new('episode',{'before':list(s),'action':int(a),'after':list(next_s)},
                        tuple(pre+[self.sources[('action',a)]]))
        self.events.append(event)
        for j in range(self.nf):
            root=self._root(a,j)
            eid=self._new('face-experience',{'before':list(s),'target_value':int(next_s[j]),
                'episode':event,'target':j},(event,self.sources[('target',j)]))
            face=root
            while True:
                f=self._face(face);f['examples'].append(eid)
                if f['split'] is None:break
                face=f['children'][s[f['split']]]
            self._reconcile(face)
        self.stats['observations']+=1
    def query(self,s,a,*,rays=True,ablation_face=None):
        if not rays:return None,{'reason':'no_rays'}
        src=[self.sources[('sensor',j,int(s[j]))] for j in range(self.nf)]
        src.append(self.sources[('action',a)])
        # os alvos são solicitações à mesma memória, não respostas recuperadas
        src.extend(self.sources[('target',j)] for j in range(self.nf))
        pulse=self.mm.pulse_units(src)
        # saída deve ser CERTIFICADA pelas portas; não ler memória de episódios
        completed=set(pulse['certified_ids']); outcomes=[];support=[];cert_faces=[]
        for j in range(self.nf):
            leaf=self._leaf(self._root(a,j),s)
            if ablation_face is not None and (j==ablation_face or leaf==ablation_face):
                return None,{'reason':'ablated','face':leaf,'target':j}
            n=self.mm.nodes[leaf]
            if leaf not in completed or not n.completed:
                return None,{'reason':'not_certified','leaf':leaf,'target':j,
                             'active':n.active,'support':n.support}
            f=n.facets[0]
            if f['output'] is None:return None,{'reason':'unresolved','leaf':leaf,'target':j}
            outcomes.append(int(f['output']));support.append(n.support);cert_faces.append(leaf)
        return tuple(outcomes),{'reason':'ok','faces':cert_faces,
            'support':support,'edges':pulse['edges'],'rays':pulse['rays']}


    def consolidate_optimal(self,penalty=2.6):
        """Indução MDL exata para cada face sobre até nf bits, a partir de episódios.
        Evita o erro da escolha gulosa irreversível; resultado reside nas faces
        de MorphMemory e somente pulsos podem recuperá-lo.
        A agenda da indução é mecânica externa, explicitamente auditada.
        """
        def kt_ids(ids):
            c=Counter(self._face(e)['target_value'] for e in ids)
            a,b=c[0],c[1]
            return (math.lgamma(a+b+1)-math.lgamma(a+.5)-math.lgamma(b+.5)
                    +2*math.lgamma(.5))/math.log(2)
        def optimize(ids,used,memo):
            key=(tuple(sorted(ids)),used)
            if key in memo:return memo[key]
            bestcost=kt_ids(ids);best=('leaf',)
            for j in range(self.nf):
                if used & (1<<j):continue
                groups=([e for e in ids if self._face(e)['before'][j]==0],
                        [e for e in ids if self._face(e)['before'][j]==1])
                if not all(groups):continue
                c0,t0=optimize(groups[0],used | (1<<j),memo)
                c1,t1=optimize(groups[1],used | (1<<j),memo)
                cand=c0+c1+penalty
                if cand<bestcost-1e-12:
                    bestcost=cand;best=('split',j,t0,t1)
            memo[key]=(bestcost,best)
            return memo[key]
        def overwrite(uid,tree):
            f=self._face(uid)
            if f['split'] is not None:
                f.setdefault('prior_subdivisions',[]).append({'feature':f['split'],
                    'children':list(f['children'].values())})
            f['children']={};f['split']=None
            vals=Counter(self._face(e)['target_value'] for e in f['examples'])
            f['output']=min((0,1),key=lambda k:(-vals[k],k)) if vals else None
            f['unresolved']=len(vals)>1
            if tree[0]=='leaf':return
            j=tree[1]
            lo,hi=f['sector'];mid=(lo+hi)/2
            children={}
            for b,rg,subtree in ((0,[lo,mid],tree[2]),(1,[mid,hi],tree[3])):
                child=self._new('face',{'face_id':self.serial+1,'depth':f['depth']+1,
                    'sector':rg,'band':f['band'],'split':None,'children':{},
                    'examples':[e for e in f['examples'] if self._face(e)['before'][j]==b],
                    'output':None,'unresolved':False},
                    (uid,self.sources[('sensor',j,b)]))
                children[b]=child
                overwrite(child,subtree)
            f['split']=j;f['children']=children;f['output']=None
            self.stats['optimal_subdivisions']+=1
        for root in self.roots.values():
            ids=self._face(root)['examples']
            _,tree=optimize(ids,0,{})
            overwrite(root,tree)

    def compress_faces(self,penalty=3.0):
        """Poda MDL/KT a partir de experiências residentes no próprio Mórfon.
        Uma edição de superfície modifica a árvore de faces; histórico preservado.
        L_KT=-log2(B(n0+1/2,n1+1/2)/B(1/2,1/2)).
        Não consulta o ambiente. A regra é genérica em qualquer canal.
        """
        def kt(samples):
            c=Counter(self._face(e)['target_value'] for e in samples)
            n0,n1=c[0],c[1]
            return (math.lgamma(n0+n1+1)-math.lgamma(n0+.5)
                -math.lgamma(n1+.5)+2*math.lgamma(.5)-math.lgamma(1))/math.log(2)
        def prune(uid):
            f=self._face(uid)
            leaf_cost=kt(f['examples'])
            if f['split'] is None:return leaf_cost
            children=f['children']
            cost=sum(prune(c) for c in children.values())+penalty
            if leaf_cost<=cost:
                f['split']=None;f['children']={};f['unresolved']=False
                vals=Counter(self._face(e)['target_value'] for e in f['examples'])
                f['output']=min((0,1),key=lambda k:(-vals[k],k))
                self.stats['pruned_faces']+=1
                return leaf_cost
            return cost
        for root in self.roots.values():prune(root)

    def face_count(self):return sum(n.kind=='face' for n in self.mm.nodes.values())
    def snapshot(self):return self.mm.snapshot()
