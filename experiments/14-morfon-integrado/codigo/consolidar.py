import json,statistics as st,collections,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
D=ROOT/'dados'
main=[]
for s in ('principal_a','principal_b','principal_c'):
    main.extend(json.loads((D/(s+'_individuais.json')).read_text()))
poda=json.loads((D/'poda_robustez_individuais.json').read_text())
secondary=[]
for s in ('secundarios_a','secundarios_noisy'):
    secondary.extend(json.loads((D/(s+'_individuais.json')).read_text()))
hrr=json.loads((D/'hrr_vinculacao.json').read_text());digits=json.loads((D/'digitos_reais.json').read_text())

def group(rows,keys):
    d=collections.defaultdict(list)
    for x in rows:d[tuple(x[k] for k in keys)].append(x)
    output=[]
    for k,v in sorted(d.items()):
        z={keys[i]:k[i] for i in range(len(k))};z['n']=len(v)
        for metric in ('balanced','accuracy','nodes','avg_edges','avg_active','nested','selected_order','snapshot_bytes','score'):
            try:
                a=[float(x[metric]) for x in v if metric in x and math.isfinite(float(x[metric]))]
                if a:z[metric+'_mean']=st.mean(a)
            except (ValueError,TypeError):pass
        output.append(z)
    return output
out={'main_n':len(main),'main':group(main,['world','variant']),
     'poda_n':len(poda),'poda':group(poda,['world','variant']),
     'secondary_n':len(secondary),'secondary':group(secondary,['world','variant']),
     'hrr':group(hrr,['dim','superposed_pairs']),
     'digits':group(digits,['variant']),
     'geometry':group(json.loads((D/'geometria_3d_4d.json').read_text()),['dim']),
     'scaling':json.loads((D/'escala_indices.json').read_text()),
     'spectral':json.loads((D/'filtro_polinomial_local.json').read_text()),
     'replication':json.loads((D/'controle_replicacao.json').read_text())}
(D/'consolidacao.json').write_text(json.dumps(out,indent=2,ensure_ascii=False))
for gname in ('main','poda','secondary','hrr','digits'):
 print('\n'+gname)
 for r in out[gname]:print(r)
