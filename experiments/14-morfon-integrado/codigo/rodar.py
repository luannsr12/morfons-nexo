from __future__ import annotations
import argparse,sys,json,time,csv,statistics,copy,os
from pathlib import Path
from dataclasses import replace
sys.path.insert(0,str(Path(__file__).resolve().parent))
from morfon import MorphMemory,Config
from mundos import sample_world,WORLDS
from legado_exp08 import NexoSphereLearner
ROOT=Path(__file__).resolve().parent.parent

def variants():
    base=Config()
    return {
     'ORIGINAL_08':None,
     'A_flat_08_style':replace(base,max_order=3,nested=False,geometry_dim=3),
     'B_integrated':replace(base,max_order=4,nested=False),
     'C_nested':replace(base,max_order=4,nested=True),
     'D_facet':replace(base,max_order=4,facet=True,faceted_focus=True),
     'E_geo4d':replace(base,max_order=4,geometry_dim=4,coord_focus=True),
     'F_spectral_1':replace(base,max_order=4,spectral='1-hop'),
     'G_spectral_band':replace(base,max_order=4,spectral='bandpass'),
     'H_MDL':replace(base,max_order=4,learning='mdl'),
     'I_nested_MDL_spectral':replace(base,max_order=4,learning='mdl',nested=True,spectral='bandpass'),
     'J_all_propagation':replace(base,max_order=4,nested=True,propagation='all'),
     'K_without_4':replace(base,max_order=3,nested=False,facet=True,spectral='bandpass'),
     'L_spectral_proposals':replace(base,max_order=4,spectral_proposal=True),
     'M_split_faces':replace(base,max_order=4,facet=True,facet_capacity=2),
     'N_unscreened':replace(base,max_order=4,prune_redundant=False),
     'O_evidence_focus':replace(base,max_order=4,focus_rule='evidence_first'),
     'P_evidence_ray':replace(base,max_order=4,focus_rule='evidence_ray'),
     'Q_evidence_unpruned':replace(base,max_order=4,focus_rule='evidence_first',prune_redundant=False),
     'R_evidence_nested':replace(base,max_order=4,focus_rule='evidence_first',nested=True),
     'S_evidence_spectral':replace(base,max_order=4,focus_rule='evidence_ray',spectral='bandpass'),
     'T_novel_gain':replace(base,max_order=4,require_novel_gain=True),
     'U_novel_nested':replace(base,max_order=4,require_novel_gain=True,nested=True),
     'V_novel_spec':replace(base,max_order=4,require_novel_gain=True,spectral='bandpass'),
     'W_order_controller':replace(base,max_order=4,order_controller=True),
     'X_controller_nested':replace(base,max_order=4,order_controller=True,nested=True),
     'Y_controller_spectral':replace(base,max_order=4,order_controller=True,nested=True,spectral='bandpass'),
     'Z_controller_faceted4d':replace(base,max_order=4,order_controller=True,nested=True,facet=True,geometry_dim=4,coord_focus=True),
     'AA_order_20':replace(base,max_order=4,order_controller=True,min_obs=20),
     'AB_errorbudget':replace(base,max_order=4,order_controller=True,promotion_penalty='multiplicity'),
     'AC_errorbudget_nested':replace(base,max_order=4,order_controller=True,nested=True,promotion_penalty='multiplicity'),
     'AD_pruned_controller':replace(base,max_order=4,order_controller=True,periodic_prune=True),
     'AE_pruned_nested':replace(base,max_order=4,order_controller=True,periodic_prune=True,nested=True),
    }

def run_one(name,config,world,seed,n_train,n_test,snap=False):
    X,Y,Xt,Yt,meta=sample_world(world,seed,n_train,n_test)
    if name=='ORIGINAL_08':
        model=NexoSphereLearner(max_order=3,max_candidates=1800,max_rays_per_event=24)
        t0=time.perf_counter()
        for x,y in zip(X,Y):model.step(x,y,train=True)
        train_seconds=time.perf_counter()-t0
        t0=time.perf_counter();pairs=[(int(y),model.step(x,0,train=False)[0],None) for x,y in zip(Xt,Yt)]
        test_seconds=time.perf_counter()-t0
        tp=sum(y==1 and p==1 for y,p,_ in pairs);fp=sum(y==0 and p==1 for y,p,_ in pairs)
        fn=sum(y==1 and p==0 for y,p,_ in pairs);tn=sum(y==0 and p==0 for y,p,_ in pairs)
        bal=.5*(tp/max(1,tp+fn)+tn/max(1,tn+fp))
        return {'accuracy':(tp+tn)/len(Yt),'balanced':bal,'precision':tp/max(1,tp+fp),'recall':tp/max(1,tp+fn),
            'tp':tp,'fp':fp,'fn':fn,'tn':tn,'nodes':len(model.spheres),'composites':len(model.spheres),
            'promoted':sum(s.useful for s in model.spheres.values()),'nested':0,'avg_edges':float('nan'),
            'avg_rays':float('nan'),'avg_active':float('nan'),'spectral_edges_total':0,'selected_order':3,
            'variant':name,'world':world,'seed':seed,'train_seconds':train_seconds,'test_seconds':test_seconds,
            'n_train':n_train,'n_test':n_test,'created':model.created,'over_budget':model.blocked_proposals,
            'proposals':model.created,'rays_total':model.rays_visited}
    model=MorphMemory(config,seed=seed)
    t0=time.perf_counter();model.fit(X,Y);train_seconds=time.perf_counter()-t0
    assert model.assert_integrity()
    t0=time.perf_counter();res=model.evaluate(Xt,Yt);test_seconds=time.perf_counter()-t0
    # for memory, no cheating via holdout. predictions & explanation stored per run optionally
    predictions=res.pop('predictions'); explanations=res.pop('explanations')
    res.update({'variant':name,'world':world,'seed':seed,'train_seconds':train_seconds,
        'test_seconds':test_seconds,'n_train':n_train,'n_test':n_test,'created':model.metrics['created'],
        'over_budget':model.metrics['over_budget'],'proposals':model.metrics['proposals'],
        'rays_total':model.metrics['rays']})
    if snap and name!='ORIGINAL_08':
        full={'meta':meta,'config':config.__dict__,'snapshot':model.snapshot(),
              'inputs_test':Xt,'labels_test':Yt,'predictions':predictions,
              'explanations':explanations,'metrics':res}
        p=ROOT/'dados'/f'auditoria_{name}_{world}_{seed}.json'
        p.write_text(json.dumps(full,ensure_ascii=False),encoding='utf-8')
    return res

def main():
    pa=argparse.ArgumentParser();pa.add_argument('--seeds',type=int,default=5)
    pa.add_argument('--train',type=int,default=520);pa.add_argument('--test',type=int,default=260)
    pa.add_argument('--variants',nargs='*',default=None);pa.add_argument('--worlds',nargs='*',default=None)
    pa.add_argument('--prefix',default='resultados')
    args=pa.parse_args()
    vv=variants();sel=args.variants or list(vv);ws=args.worlds or WORLDS
    rows=[]
    for world in ws:
      for seed in range(args.seeds):
        for name in sel:
            row=run_one(name,vv[name],world,seed+41,args.train,args.test,snap=(seed==0 and name in ('B_integrated','C_nested','G_spectral_band','H_MDL')))
            rows.append(row)
            print(f'{world:19} {seed} {name:25} acc={row["accuracy"]:.3f} bal={row["balanced"]:.3f} nodes={row["nodes"]} nested={row["nested"]}',flush=True)
    out=ROOT/'dados';out.mkdir(exist_ok=True)
    (out/(args.prefix+'_individuais.json')).write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
    with (out/(args.prefix+'_individuais.csv')).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    summ=[]
    for world in ws:
      for name in sel:
        r=[x for x in rows if x['world']==world and x['variant']==name]
        summ.append({'world':world,'variant':name,'runs':len(r),
             **{metric+'_mean':round(statistics.mean(x[metric] for x in r),5)
                for metric in ['accuracy','balanced','precision','recall','nodes','promoted','nested','avg_edges','avg_active','train_seconds','test_seconds']}})
    (out/(args.prefix+'_resumo.json')).write_text(json.dumps(summ,indent=2),encoding='utf-8')
    return rows,summ
if __name__=='__main__':main()
