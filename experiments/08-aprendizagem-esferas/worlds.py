"""Mundos artificiais ISOLADOS do aprendiz. Nomes das regras não são expostos ao modelo."""
import random

def generate_world(name,n,seed,start=0):
    rng=random.Random(seed)
    for _ in range(start): rng.random()  # not necessary; deterministic reserved
    for i in range(n):
        if name=='pares':
            x=tuple(int(rng.random()<.30) for _ in range(12))
            hidden=int((x[0] and x[4]) or (x[2] and x[9]))
        elif name=='trincas_e_ausencia':
            x=tuple(int(rng.random()<.41) for _ in range(11))
            hidden=int((x[0] and x[4] and not x[7]) or (x[1] and x[3] and x[8]))
        elif name=='coocorrencia_enganosa':
            x0=int(rng.random()<.38)
            x1=int(rng.random()<.38)
            # confounded copies: often match one driver, rarely important
            xs=[x0,x1]
            xs.extend([x0 if rng.random()<.82 else 1-x0,
                       x1 if rng.random()<.85 else 1-x1])
            xs.extend([int(rng.random()<.36) for _ in range(8)])
            x=tuple(xs)
            hidden=int(x[0] and x[1])
        elif name=='sem_relacao':
            x=tuple(int(rng.random()<.4) for _ in range(12))
            hidden=int(rng.random()<.15)
        else:raise ValueError(name)
        # Label noise is independent and never given to the learner.
        noise=(.018 if name!='sem_relacao' else 0.)
        y=hidden ^ int(rng.random()<noise)
        yield x,y


def metrics(pairs):
    tp=tn=fp=fn=0
    for pred,true in pairs:
        if true:
            if pred:tp+=1
            else:fn+=1
        elif pred:fp+=1
        else:tn+=1
    n=tp+tn+fp+fn
    precision=tp/(tp+fp) if tp+fp else 0
    recall=tp/(tp+fn) if tp+fn else 0
    f1=(2*precision*recall/(precision+recall)) if precision+recall else 0
    tnr=tn/(tn+fp) if tn+fp else 0
    return {'n':n,'accuracy':round((tp+tn)/n,4),
            'balanced_accuracy':round((recall+tnr)/2,4),
            'precision':round(precision,4),'recall':round(recall,4),'f1':round(f1,4),
            'tp':tp,'tn':tn,'fp':fp,'fn':fn}
