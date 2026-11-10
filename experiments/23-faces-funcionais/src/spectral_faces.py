"""Experimento 23b: marcas harmônicas discretas nas faces da MorphMemory original.

O espectro é sobre GF(2) (soma XOR), não um campo eletromagnético;
coeficientes do espectro e grau são induzidos de episódios observados.
Os termos aprendidos são Mórfons com portas de entrada reais e ficam em
facetas do Mórfon-pai. Sem armazenamento de tabelas de transição no executor.
O motor externo realiza apenas operações algébricas universais (eliminação GF2)
e o escalonamento de pulsos; decisão de capacidade é causalmente certificada.
"""
from __future__ import annotations
import sys,math
from pathlib import Path
from itertools import combinations
from collections import Counter
ORIGINAL=Path(__file__).resolve().parents[1]/'originals'
sys.path.insert(0,str(ORIGINAL))
from morfon_exp21_original import MorphMemory,Config


def terms(n,degree):
    return tuple(tuple(z) for k in range(degree+1) for z in combinations(range(n),k))

def phi(s,monos):
    v=0
    for i,term in enumerate(monos):
        if all(s[j] for j in term):v|=1<<i
    return v

def eliminate(rows):
    """Pivot máximo. Retorna base de pares (máscara de entradas, bit observado).
    Nenhuma informação de domínio: aplica eliminação Gaussiana exata GF(2).
    """
    piv={}
    for m,y in rows:
        q=m;b=int(y)
        while q:
            p=q.bit_length()-1
            if p in piv:q^=piv[p][0];b^=piv[p][1]
            else:piv[p]=(q,b);break
        if q==0 and b:return None
    return piv

def solve(piv):
    coefficients=0
    for p in sorted(piv):
        mask,y=piv[p]
        b=y^(((mask&coefficients).bit_count())&1)
        if b:coefficients|=1<<p
    return coefficients

def rm_decode_complete(n,degree,observations,max_correctable=None):
    """Decodificação exata por código RM(r,n) em n<=5: nearest Hamming.
    Codifica todas as possíveis polinomiais de grau <=degree, usando Gray code.
    Este enumerador é laboratório, NÃO é algoritmo escalável para n grande.
    """
    if n>5:raise ValueError('Exhaustive decoder restricted to <=5 sensors')
    ms=terms(n,degree);k=len(ms)
    if k>18:raise ValueError('Codebook too large for this laboratory')
    if len(observations)!=(1<<n):return None
    word=sum(int(observations[i])<<i for i in range(1<<n))
    monos=[]
    for mono in ms:
        mask=0
        for i in range(1<<n):
            if all((i>>j)&1 for j in mono):mask|=1<<i
        monos.append(mask)
    best=1<<n;best_gray=None;ties=0;cw=0;old_gray=0
    for z in range(1<<k):
        gray=z^(z>>1)
        if z:
            changed=gray^old_gray;bit=changed.bit_length()-1
            cw^=monos[bit]
        d=(cw^word).bit_count()
        if d<best:best=d;best_gray=gray;ties=1
        elif d==best:ties+=1
        old_gray=gray
    cap=(2**(n-degree)-1)//2 if max_correctable is None else max_correctable
    if best>cap or ties!=1:return {'identified':False,'distance':best,'ties':ties,'capacity':cap}
    return {'identified':True,'distance':best,'ties':1,'capacity':cap,
            'coeff':best_gray,'basis':ms,
            'corrected':[i for i in range(1<<n) if ((sum(((best_gray>>j)&1) and all((i>>v)&1 for v in mono)
                        for j,mono in enumerate(ms))&1) != observations[i])]}


def uniquely_determined(mask,piv):
    y=0
    while mask:
        p=mask.bit_length()-1
        if p not in piv:return None
        m,b=piv[p];mask^=m;y^=b
    return y

class SpectralFaces:
    def __init__(self,n_features,n_actions,*,max_degree=2,seed=42,robust=False):
        self.nf=n_features;self.na=n_actions;self.max_degree=max_degree;self.robust=robust
        self.mm=MorphMemory(Config(max_order=14,max_nodes=40000,max_relays=10000,
                                    propagation='completed',facet=True),seed=seed)
        self.serial=0;self.src={};self.roots={};self.episodes=[];self.stats=Counter()
        for j in range(n_features):
            for b in (0,1):self.src[('sensor',j,b)]=self._new('source',{'channel':j,'value':b,'type':'sensor'})
        for a in range(n_actions):self.src[('action',a)]=self._new('source',{'index':a,'type':'action'})
        for j in range(n_features):self.src[('target',j)]=self._new('source',{'index':j,'type':'target'})
    def _new(self,kind,meta,ports=()):
        self.serial+=1
        n,ok=self.mm._create(kind,((930000000,self.serial),),tuple(ports))
        if not ok:raise RuntimeError('Allocation failed')
        n.facets=[dict(meta)]
        return n.uid
    def _root(self,a,j):
        if (a,j) not in self.roots:
            uid=self._new('spectral-face',{'action':a,'channel':j,'sector':[0,2*math.pi],
                'shell':[-math.pi/2,math.pi/2],'degree':None,'marks':[],
                'pivots':{},'basis':[],'training_count':0,'version':0},
                (self.src[('action',a)],self.src[('target',j)]))
            self.roots[(a,j)]=uid
        return self.roots[(a,j)]
    def observe(self,s,a,out):
        assert len(s)==self.nf and len(out)==self.nf
        sources=tuple(self.src[('sensor',j,int(s[j]))] for j in range(self.nf))
        uid=self._new('episode',{'before':list(s),'after':list(out),'action':a,
                 'origin':'observed'}, sources+(self.src[('action',a)],))
        self.episodes.append(uid)
        for j in range(self.nf):self._fit(a,j)
    def _fit(self,a,j):
        root=self._root(a,j)
        meta=self.mm.nodes[root].facets[0]
        episodes=[self.mm.nodes[e].facets[0] for e in self.episodes if self.mm.nodes[e].facets[0]['action']==a]
        candidate=None
        for d in range(self.max_degree+1):
            ms=terms(self.nf,d)
            rows=[(phi(z['before'],ms),z['after'][j]) for z in episodes]
            piv=eliminate(rows)
            if piv is not None:
                candidate=(d,ms,piv);break
        corrected=None
        if candidate is None and self.robust and len(episodes)==(1<<self.nf):
            by_input={tuple(z['before']):int(z['after'][j]) for z in episodes}
            if len(by_input)==(1<<self.nf):
                y=[by_input[tuple((i>>k)&1 for k in range(self.nf))] for i in range(1<<self.nf)]
                corrected=rm_decode_complete(self.nf,self.max_degree,y)
                if corrected and corrected['identified']:
                    d=self.max_degree;ms=corrected['basis']
                    pred_rows=[(phi(tuple((i>>k)&1 for k in range(self.nf)),ms),
                                (sum(((corrected['coeff']>>z)&1)*int(all((i>>v)&1 for v in mono))
                                     for z,mono in enumerate(ms)))&1)
                                 for i in range(1<<self.nf)]
                    piv=eliminate(pred_rows)
                    assert piv is not None
                    candidate=(d,ms,piv)
        for uid in meta['marks']:
            self.mm.nodes[uid].facets[0]['live']=False
        meta['marks']=[];meta['version']+=1;meta['training_count']=len(episodes)
        meta['correction']=corrected
        if candidate is None:
            meta['degree']=None;meta['basis']=[];meta['pivots']={}
            self.stats['contradictions']+=1
            return
        d,ms,piv=candidate;coeff=corrected['coeff'] if corrected and corrected.get('identified') else solve(piv)
        meta['degree']=d;meta['basis']=[list(z) for z in ms]
        meta['pivots']={str(p):[int(v[0]),int(v[1])] for p,v in piv.items()}
        meta['rank']=len(piv)
        # Marca espectral persistente como Mórfon ligado ao centro e às faces/sensores
        for bit,mono in enumerate(ms):
            if not ((coeff>>bit)&1):continue
            ports=(root,)+tuple(self.src[('sensor',i,1)] for i in mono)
            angle=(bit+.5)/len(ms)*2*math.pi
            uid=self._new('face-harmonic',{'parent_face':root,'monomial':list(mono),
                'order':len(mono),'azimuth':angle,'live':True,
                'version':meta['version']},ports)
            meta['marks'].append(uid)
        self.stats['refits']+=1
    def query(self,s,a,*,rays=True,ablate_mark=None,ablate_face=None):
        if not rays:return None,{'reason':'no_rays'}
        src=[self.src[('sensor',j,int(s[j]))] for j in range(self.nf)]
        src.append(self.src[('action',a)])
        src.extend(self.src[('target',j)] for j in range(self.nf))
        pulse=self.mm.pulse_units(src);certified=set(pulse['certified_ids'])
        result=[];used=[]
        for j in range(self.nf):
            rid=self._root(a,j);f=self.mm.nodes[rid].facets[0]
            if ablate_face==rid:return None,{'reason':'face_ablation'}
            if rid not in certified:return None,{'reason':'root_not_certified'}
            if f['degree'] is None:return None,{'reason':'contradiction'}
            ms=[tuple(m) for m in f['basis']]
            piv={int(k):(v[0],v[1]) for k,v in f['pivots'].items()}
            guaranteed=uniquely_determined(phi(s,ms),piv)
            if guaranteed is None:return None,{'reason':'unidentified','channel':j,'rank':len(piv)}
            bit=0;channel_marks=[]
            for uid in f['marks']:
                if uid==ablate_mark:continue
                if uid in certified:
                    bit^=1;channel_marks.append(uid)
            # confirmação: emissão é produto das portas/marcas ativas; consulta
            # espectral garante apenas que a resposta é identificável da memória.
            # Se ablação altera bit, NÃO usaremos o valor de guaranteed para corrigir.
            if ablate_mark is None and bit!=guaranteed:
                raise AssertionError(('Face pulse mismatch',a,j,s,bit,guaranteed))
            result.append(bit);used.append(channel_marks)
        return tuple(result),{'reason':'ok','marks':used,'certified':len(certified),
                              'edges':pulse['edges']}

    def imagine(self,s,a):
        """Representação interna da consequência, ligada às marcas que a produziram.
        NÃO cria episódio observado, não confirma a própria previsão.
        """
        predicted,trace=self.query(s,a)
        if predicted is None:return None,trace
        proof=[uid for group in trace['marks'] for uid in group]
        parent=[self.src[('action',a)]]
        parent+=list(dict.fromkeys(proof))
        node=self._new('internal-imagination',{'before':list(s),'action':int(a),
             'anticipated':list(predicted),'origin':'internal',
             'proof_marks':proof},tuple(parent))
        return predicted,{'node':node,'proof':trace}

    @classmethod
    def restore(cls,blob,n_features,n_actions,max_degree=2,seed=42,robust=False):
        obj=cls(n_features,n_actions,max_degree=max_degree,seed=seed,robust=robust)
        obj.mm=MorphMemory.restore(blob)
        obj.src={};obj.roots={};obj.episodes=[];obj.stats=Counter()
        obj.serial=0
        for node in obj.mm.nodes.values():
            if node.literals and node.literals[0][0]==930000000:
                obj.serial=max(obj.serial,node.literals[0][1])
            if not node.facets:continue
            f=node.facets[0]
            if node.kind=='source':
                if f['type']=='sensor':key=('sensor',f['channel'],f['value'])
                elif f['type']=='action':key=('action',f['index'])
                elif f['type']=='target':key=('target',f['index'])
                else:continue
                obj.src[key]=node.uid
            elif node.kind=='spectral-face':obj.roots[(f['action'],f['channel'])]=node.uid
            elif node.kind=='episode':obj.episodes.append(node.uid)
        assert len(obj.roots)<=n_actions*n_features
        return obj

    def count_faces(self):
        return sum(n.kind=='spectral-face' for n in self.mm.nodes.values())
    def count_live_marks(self):
        return sum(len(self.mm.nodes[r].facets[0]['marks']) for r in self.roots.values())
