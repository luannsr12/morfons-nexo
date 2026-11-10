"""Execute a partir da raiz do pacote: python -m experimentos.run"""
import json,statistics,time
from pathlib import Path
from learner import NexoSphereLearner
from worlds import generate_world,metrics

WORLD_CONFIGS={
    'pares':(1100,1100,2),
    'trincas_e_ausencia':(1650,1100,3),
    'coocorrencia_enganosa':(1100,1100,2),
    'sem_relacao':(1100,1100,2),
}

def single(world,seed=2,method='composta'):
    train_n,test_n,max_order=WORLD_CONFIGS[world]
    train=list(generate_world(world,train_n,seed*101+13))
    test=list(generate_world(world,test_n,seed*101+71))
    if method=='atomica':max_order=1
    if method=='pares':max_order=min(2,max_order)
    learn=NexoSphereLearner(max_order=max_order,prune=(method!='sem_poda'))
    start=time.perf_counter()
    for x,y in train:learn.step(x,y)
    after_training=time.perf_counter()
    preds=[(learn.predict(learn.tokens_from_vector(x))[0],y) for x,y in test]
    after_test=time.perf_counter()
    # Training-only methods get the SAME streams, not supplied hidden rules.
    counts=learn.audit()
    counts['time_train_sec']=round(after_training-start,3)
    counts['time_test_sec']=round(after_test-after_training,3)
    return {'world':world,'seed':seed,'method':method,
            'test':metrics(preds),'base_all_zero':metrics([(0,y) for x,y in test]),
            'model':counts}

def run(seeds=(2,3,5,7,11)):
    results=[]
    for world in WORLD_CONFIGS:
        methods=['atomica','pares','composta','sem_poda'] if world=='trincas_e_ausencia' else ['atomica','composta','sem_poda']
        for seed in seeds:
            for method in methods:
                r=single(world,seed,method)
                results.append(r)
                print(f'{world:24s} {method:12s} seed={seed:2} BA={r["test"]["balanced_accuracy"]:.3f} '
                      f'F1={r["test"]["f1"]:.3f} nodes={r["model"]["n_candidates_live"]} '
                      f'pruned={r["model"]["discarded"]}',flush=True)
    summary={}
    for world in WORLD_CONFIGS:
        summary[world]={}
        for method in ('atomica','pares','composta','sem_poda'):
            subset=[x for x in results if x['world']==world and x['method']==method]
            if not subset:continue
            summary[world][method]={
               k:round(statistics.mean(item['test'][k] for item in subset),4)
                  for k in ('accuracy','balanced_accuracy','f1','precision','recall')}
            summary[world][method]['candidates_live_mean']=round(statistics.mean(item['model']['n_candidates_live'] for item in subset),1)
            summary[world][method]['created_mean']=round(statistics.mean(item['model']['created'] for item in subset),1)
            summary[world][method]['discarded_mean']=round(statistics.mean(item['model']['discarded'] for item in subset),1)
            summary[world][method]['baseline_balanced_accuracy']=round(statistics.mean(item['base_all_zero']['balanced_accuracy'] for item in subset),4)
    out={'design':'streaming prediction with sparse event-indexed spheres (positive rule mining)',
         'notes':['The generator defines hidden laws; the learner never sees these definitions.',
                  'Output labels are supplied AFTER each prediction as observations.',
                  'Sphere active with >=1 ray; only full support is a match for evidence.',
                  'No global scan in retrieval; proposed pairs use only event tokens.',
                  'Candidate generation is bounded and supervised by observed outcomes.',
                  'No causal inference or language learning claimed.'],
         'seed_set':list(seeds),'world_config':{k:list(v) for k,v in WORLD_CONFIGS.items()},
         'summary':summary,'runs':results}
    return out

if __name__=='__main__':
    out=run()
    dst=Path(__file__).resolve().parent.parent/'resultados.json'
    dst.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
    print('\nSaved',dst)
