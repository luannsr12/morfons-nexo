"""Probes of mechanisms on the SAME trained integrated Morphon memory.
Only storage and processing variations: not claims of integrated gains in prediction.
"""
import json,random,sys,math,time,collections
from pathlib import Path
import numpy as np
from morfon import MorphMemory,Config
from mundos import sample_world
ROOT=Path(__file__).resolve().parent.parent

def trained(seed,world='quad',cfg=None):
    X,Y,Xt,Yt,_=sample_world(world,seed,520,260)
    m=MorphMemory(cfg or Config(max_order=4,order_controller=True,nested=True),seed)
    m.fit(X,Y)
    return m,Xt,Yt

def circular(a,b):return np.fft.ifft(np.fft.fft(a)*np.fft.fft(b)).real

def unbind(trace,known):return np.fft.ifft(np.fft.fft(trace)*np.conj(np.fft.fft(known))).real

def hrr_probe():
    rows=[]
    for seed in (41,42,43):
      m,_,_=trained(seed,'pair_or')
      pairs=sorted(set(n.literals for n in m.nodes.values() if len(n.literals)==2 and n.kind!='atom'))
      tokens=sorted(set(lit for pair in pairs for lit in pair))
      for d in (16,64,256):
        rng=np.random.default_rng(seed+d)
        v={t:rng.standard_normal(d)/math.sqrt(d) for t in tokens}
        for target_count in (1,4,8):
          # select bindings with distinct anchor and avoid repeating the answer.
          selected=[];anchors=set()
          for a,b in sorted(pairs,key=lambda q:hash((q,seed))):
            if a not in anchors and b not in anchors and a!=b:
              selected.append((a,b)); anchors.add(a)
            if len(selected)==target_count:break
          if len(selected)<target_count:continue
          trace=sum((circular(v[a],v[b]) for a,b in selected),np.zeros(d))
          correct=0
          for a,b in selected:
            recovered=unbind(trace,v[a]);scores={tok:float(np.dot(recovered,v[tok])) for tok in tokens}
            prediction=max(tokens,key=lambda t:(scores[t],t))
            correct+=int(prediction==b)
          rows.append({'seed':seed,'dim':d,'superposed_pairs':target_count,
                       'queries':len(selected),'correct':correct,'accuracy':correct/len(selected),
                       'exact_ports_accuracy':1.0,'storage_float_components':d,
                       'exact_port_references':2*len(selected)})
    return rows

def complexity_probe():
    rows=[]
    # Disconnected growth leaves local retrieval unchanged.
    m=MorphMemory(Config(max_nodes=50000),14)
    m.propose(((0,1),(1,1)))
    m.pulse([(0,1),(1,1)]);initial=m.last_info.copy()
    for i in range(10000):m._atom((i+10,1))
    m.pulse([(0,1),(1,1)]);after=m.last_info.copy()
    rows.append({'type':'10k_disconnected','nodes':len(m.nodes),
                 'edges_before':initial['edges'],'edges_after':after['edges'],
                 'ratio':after['edges']/max(1,initial['edges'])})
    # Opposite case: one highly connected atom makes event-local retrieval expensive.
    for fan in (100,1000,4000):
      n=MorphMemory(Config(max_nodes=10000),17)
      for j in range(fan):n.propose(((0,1),(j+10,1)))
      n.pulse([(0,1)])
      rows.append({'type':'high_degree','fanout':fan,'nodes':len(n.nodes),
                   'edges':n.last_info['edges'],'rays':n.last_info['rays'],
                   'active':n.last_info['active']})
    return rows

def geometry_probe():
    rows=[]
    for seed in (41,42,43):
      _,_,_=trained(seed,'quad')
      for d in (3,4):
        m,xt,yt=trained(seed,'quad',Config(max_order=4,nested=True,facet=True,geometry_dim=d,order_controller=True))
        result=m.evaluate(xt,yt)
        state=m.snapshot();raw=len(json.dumps(state).encode())
        rows.append({'seed':seed,'dim':d,'accuracy':result['accuracy'],'balanced':result['balanced'],
                     'nodes':result['nodes'],'nested':result['nested'],'snapshot_bytes':raw,
                     'avg_edges':result['avg_edges'],'avg_rays':result['avg_rays'],
                     'promoted':result['promoted']})
    return rows

def real_digits_probe():
    from sklearn.datasets import load_digits
    from sklearn.model_selection import train_test_split
    X=load_digits().data
    y=(load_digits().target%2).astype(int)
    rows=[]
    for seed in (41,42,43):
      train_idx,test_idx=train_test_split(np.arange(len(y)),test_size=.25,random_state=seed,stratify=y)
      xtr=X[train_idx];xte=X[test_idx]
      # No use of labels to pick sensors: top-variance pixels on training only.
      columns=np.argsort(xtr.var(axis=0))[-9:]
      xtr=np.asarray(xtr[:,columns]>8,dtype=int).tolist()
      xte=np.asarray(xte[:,columns]>8,dtype=int).tolist()
      for name,cfg in [('ORIGINAL_08',None),('integrated',Config(max_order=4,order_controller=True)),
                       ('nested',Config(max_order=4,order_controller=True,nested=True))]:
        if cfg is None:
          from legado_exp08 import NexoSphereLearner
          m=NexoSphereLearner(max_order=3,max_candidates=1800,max_rays_per_event=24)
          for a,b in zip(xtr,y[train_idx]):m.step(a,int(b),train=True)
          predictions=[m.step(a,0,train=False)[0] for a in xte]
          nn=len(m.spheres)
        else:
          m=MorphMemory(cfg,seed)
          m.fit(xtr,y[train_idx])
          predictions=[m.predict(a)[0] for a in xte]
          nn=len(m.nodes)
        tp=sum(p==1 and b==1 for p,b in zip(predictions,y[test_idx]));tn=sum(p==0 and b==0 for p,b in zip(predictions,y[test_idx]));
        fp=sum(p==1 and b==0 for p,b in zip(predictions,y[test_idx]));fn=sum(p==0 and b==1 for p,b in zip(predictions,y[test_idx]));
        bal=(tp/max(1,tp+fn)+tn/max(1,tn+fp))/2
        rows.append({'seed':seed,'variant':name,'accuracy':(tp+tn)/len(test_idx),'balanced':bal,
                     'tp':tp,'fp':fp,'fn':fn,'tn':tn,'nodes':nn,'pixels_train_only':columns.tolist(),
                     'train':len(train_idx),'test':len(test_idx)})
    return rows

def spectral_equivalence_probe():
    # Small exact proof of polynomial application without diagonalization,
    # using dense numpy only as evaluator, not the operational engine.
    m,xt,yt=trained(41,'pair_or',Config(max_order=4,order_controller=True,spectral='bandpass'))
    cases=[]
    for x in xt:
        cs=m.pulse((i,int(v)) for i,v in enumerate(x))
        chosen=[n for n in cs if n.promoted]
        cases.append((len(chosen),chosen))
    _,selected=max(cases,key=lambda x:x[0])
    assert len(selected)>=2, 'spectral probe must be genuinely nontrivial'
    alg=m._local_spectral(selected)
    N=len(selected);raw=np.array([n.support for n in selected],float)
    W=np.zeros((N,N))
    for i,n in enumerate(selected):
      for j,q in enumerate(selected):
        if i!=j and set(n.literals).intersection(q.literals):W[i,j]=1
      if W[i].sum()>0:W[i]/=W[i].sum()
    expected=(W-W@W)@raw
    observed=np.array([alg[n.uid] for n in selected]);error=np.max(np.abs(expected-observed)) if N else 0.
    assert error<1e-10
    return {'nodes':N,'max_abs_error':float(error),'equivalent':True,'dense_matrix_used_by_engine':False}

def main():
    root=ROOT/'dados'
    jobs=[('hrr_vinculacao',hrr_probe),('escala_indices',complexity_probe),
          ('geometria_3d_4d',geometry_probe),('digitos_reais',real_digits_probe),
          ('filtro_polinomial_local',spectral_equivalence_probe)]
    for name,fn in jobs:
      start=time.perf_counter();v=fn()
      (root/(name+'.json')).write_text(json.dumps(v,indent=2,ensure_ascii=False,default=lambda x:x.item() if hasattr(x,'item') else str(x)),encoding='utf8')
      print(name,'records=',len(v) if isinstance(v,list) else 1,'seconds=',round(time.perf_counter()-start,3),flush=True)
if __name__=='__main__':main()
