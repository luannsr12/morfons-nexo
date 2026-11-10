from __future__ import annotations
import json,random,sys,time
from pathlib import Path
from spectral_faces import SpectralFaces,rm_decode_complete
from evaluate import world,all_states,N,A

def cubic_world(s,a):
    p,q,r,h,z=s;x=list(s)
    if a==0:x[0]=p^(q&r&h)
    else:x[1]=q^(p&r&h)
    return tuple(x)

def cubic_case(seed,ntrain,degree):
    rng=random.Random(1000+seed);states=all_states();L=SpectralFaces(N,A,max_degree=degree,seed=seed)
    trains={}
    for a in range(A):
        seq=states[:];rng.shuffle(seq);trains[a]=[seq[:ntrain],seq[ntrain:]]
    episodes=[(s,a,cubic_world(s,a)) for a in range(A) for s in trains[a][0]]
    rng.shuffle(episodes)
    for s,a,t in episodes:L.observe(s,a,t)
    results=[]
    for a in range(A):
        for s in trains[a][1]:
            guess,proof=L.query(s,a)
            results.append({'state':list(s),'action':a,'prediction':guess,
                   'expected':cubic_world(s,a),'correct':guess==cubic_world(s,a),
                   'reason':proof['reason']})
    return {'seed':seed,'ntrain_per_action':ntrain,'degree':degree,
         'correct':sum(z['correct'] for z in results),
         'answered':sum(z['prediction'] is not None for z in results),
         'holdout':len(results),'results':results}

def noisy_case(kind,seed,nflips=3):
    rng=random.Random(301+seed*19+sum(map(ord,kind)))
    L=SpectralFaces(N,A,max_degree=2,seed=seed,robust=True)
    originals={(a,i):world(kind,tuple((i>>j)&1 for j in range(N)),a) for a in range(A) for i in range(32)}
    noisy={key:list(value) for key,value in originals.items()}
    for a in range(A):
        for j in range(N):
            for i in rng.sample(list(range(32)),nflips):noisy[(a,i)][j]^=1
    episodes=[]
    for a in range(A):
        for i in range(32):
            s=tuple((i>>j)&1 for j in range(N))
            episodes.append((s,a,tuple(noisy[(a,i)])))
    rng.shuffle(episodes)
    for s,a,t in episodes:L.observe(s,a,t)
    predicted=[];corrections=[]
    for a in range(A):
        for i in range(32):
            s=tuple((i>>j)&1 for j in range(N))
            out,proof=L.query(s,a)
            predicted.append({'correct':out==originals[(a,i)],'answered':out is not None,
                              'proof':proof['reason']})
        for j in range(N):
            f=L.mm.nodes[L.roots[(a,j)]].facets[0]
            corrections.append({'degree':f['degree'],'distance':
                 (f['correction']['distance'] if f['correction'] else 0),
                 'corrected':len(f['correction']['corrected']) if f['correction'] and f['correction'].get('identified') else 0})
    return {'world':kind,'seed':seed,'corruptions_per_channel':nflips,
        'total_bit_corruptions':nflips*N*A,'correct':sum(z['correct'] for z in predicted),
        'answered':sum(z['answered'] for z in predicted),'holdout':len(predicted),
        'corrections':corrections}

def missing_context():
    L=SpectralFaces(2,1,max_degree=2)
    s=(1,0)
    L.observe(s,0,(1,0))
    L.observe(s,0,(1,1))
    answer,proof=L.query(s,0)
    return {'conflicting_same_input':answer is None,'reason':proof['reason'],
           'episodes_saved':len(L.episodes)}

def minimum_distance_check():
    # Enumerar as 65.535 funções não nulas da família RM(2,5)
    from spectral_faces import terms
    ms=terms(5,2); masks=[]
    for t in ms:
        mask=sum((int(all((i>>j)&1 for j in t))<<i) for i in range(32))
        masks.append(mask)
    best=32;word=0;grayold=0
    for i in range(1,1<<len(masks)):
        g=i^(i>>1);bit=(g^grayold).bit_length()-1
        word^=masks[bit];best=min(best,word.bit_count());grayold=g
    return {'n':32,'k':len(masks),'minimum_distance':best,'correctable':(best-1)//2}

def four_flip_failure():
    original=[0]*32
    # código x0*x1: peso 8, perturba 4 dos 8 pontos -> empate com o código zero
    target=[0]*32
    candidates=[i for i in range(32) if (i&3)==3]
    for i in candidates[:4]:target[i]=1
    decoded=rm_decode_complete(5,2,target)
    return {k:v for k,v in decoded.items() if k not in ('basis','coeff','corrected')}

def run():
    start=time.perf_counter();cubic=[]
    for degree in (2,3):
        for n in (24,30):
            for seed in range(4):
                c=cubic_case(seed,n,degree);cubic.append(c)
                print('CUBIC',degree,n,seed,c['correct'],'/',c['holdout'],'answered',c['answered'],flush=True)
    noise=[]
    for kind in ['toggle_cond','context','parity','asym','history']:
        for seed in range(3):
            z=noisy_case(kind,seed,3);noise.append(z)
            print('NOISE',kind,seed,z['correct'],'/',z['holdout'],'answered',z['answered'],flush=True)
    rec={'cubic':cubic,'noise':noise,'hidden_context':missing_context(),
        'distance':minimum_distance_check(),'four_flips':four_flip_failure(),
        'runtime':time.perf_counter()-start}
    path=Path(__file__).resolve().parents[1]/'results'/'adversarial.json'
    path.write_text(json.dumps(rec,indent=2,ensure_ascii=False))
    summary={'cubic':{},'noise':{'cases':len(noise),'correct':sum(c['correct'] for c in noise),
         'answered':sum(c['answered'] for c in noise),'total':sum(c['holdout'] for c in noise),
         'corrupted_bits':sum(c['total_bit_corruptions'] for c in noise)},
        'distance':rec['distance'],'four_flips':rec['four_flips'],'hidden_context':rec['hidden_context']}
    for degree in (2,3):
        for n in (24,30):
            sub=[c for c in cubic if c['degree']==degree and c['ntrain_per_action']==n]
            summary['cubic'][str((degree,n))]={'correct':sum(c['correct'] for c in sub),
                'answered':sum(c['answered'] for c in sub),'total':sum(c['holdout'] for c in sub)}
    print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
    return summary
if __name__=='__main__':run()
