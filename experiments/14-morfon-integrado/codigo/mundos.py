"""Oraculos estritamente separados do motor. Todos recebem sementes, sem classes no aprendiz.
Mesmos episodios por variante; treino/teste separados, sem feedback no teste.
"""
import random

def sample_world(name, seed, n_train=520, n_test=260, n_features=9):
    rng=random.Random(seed+13007)
    X=[];Y=[]
    for t in range(n_train+n_test):
        a=[int(rng.random()<.5) for _ in range(n_features)]
        if name=='correlated':
            a[7]=a[0] if rng.random()<.85 else 1-a[0]
            a[8]=a[1] if rng.random()<.8 else 1-a[1]
        if name=='pair_or':
            y=(a[0] and a[1]) or (a[3] and a[4])
        elif name=='triple_absence':
            y=a[0] and a[1] and not a[2]
        elif name=='xor':
            y=a[0]!=a[1]
        elif name=='quad':
            y=a[0] and a[1] and a[2] and a[3]
        elif name=='context':
            y=(a[6] and a[0] and a[1]) or ((not a[6]) and a[3] and a[4])
        elif name=='correlated':
            y=a[0] and a[1]
        elif name=='noisy':
            y=(a[0] and a[1]) or (a[2] and not a[3])
            if rng.random()<.08:y=not y
        elif name=='null':
            y=rng.random()<.5
        elif name=='drift':
            y=(a[0] and a[1]) if t<n_train else (a[4] and a[5])
        else:raise ValueError(name)
        # Random anonymized feature permutation per world/seed; a separate seed
        # for each world avoids fixed associations to names/positions.
        X.append(a); Y.append(int(y))
    perm=list(range(n_features));random.Random(seed*101+len(name)*37).shuffle(perm)
    X=[[x[j] for j in perm] for x in X]
    return X[:n_train],Y[:n_train],X[n_train:],Y[n_train:],{'world':name,'seed':seed,'features':n_features,
                     'n_train':n_train,'n_test':n_test,'permutation':perm}

WORLDS=['pair_or','triple_absence','xor','quad','context','correlated','noisy','null','drift']
