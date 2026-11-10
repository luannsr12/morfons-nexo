import json,statistics as st,math,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle,FancyArrowPatch,Polygon
from morfon import MorphMemory,Config
from mundos import sample_world
ROOT=Path(__file__).resolve().parent.parent
D=ROOT/'dados';F=ROOT/'figuras'
con=json.loads((D/'consolidacao.json').read_text());rows=con['main'];poda=con['poda']
def find(gr,w,v,key):
    return next(x[key+'_mean'] for x in gr if x.get('world')==w and x.get('variant')==v)

def main_comparison():
    ws=['pair_or','triple_absence','xor','quad','context','noisy','null','drift']
    names=['ORIGINAL_08','B_integrated','W_order_controller','X_controller_nested']
    labels=['Exp. 08 original','Integrado 4 níveis','Controle aprendido','Controle + aninhamento']
    xx=np.arange(len(ws));width=.20
    fig,ax=plt.subplots(figsize=(13,5.8))
    for j,(v,label) in enumerate(zip(names,labels)):
        vals=[find(rows,w,v,'balanced') for w in ws]
        ax.bar(xx+(j-1.5)*width,vals,width,label=label)
    ax.axhline(.5,ls='--',lw=1,c='gray',label='Referência 0,50')
    ax.set_xticks(xx,[{'pair_or':'Pares OR','triple_absence':'Trinca e zero','xor':'XOR',
                        'quad':'Quatro partes','context':'Contexto','noisy':'Ruído',
                        'null':'Mundo nulo','drift':'Mudança de mundo'}[w] for w in ws],rotation=18,ha='right')
    ax.set_ylim(0,1.08);ax.set_ylabel('Acurácia balanceada · média de 3 sementes')
    ax.set_title('NEXO Exp. 14 · comparação integrada, mesmos episódios')
    ax.legend(ncol=2,loc='upper center',fontsize=9);fig.tight_layout()
    fig.savefig(F/'01_integracao_vs_original.png',dpi=160);plt.close(fig)

def resource_comparison():
    ws=['pair_or','quad']
    names=['W_order_controller','AD_pruned_controller','AE_pruned_nested']
    labels=['Controle','Controle + poda','Controle + poda + aninhamento']
    xx=np.arange(len(ws));width=.25
    fig,ax=plt.subplots(figsize=(9,5.5))
    for j,(v,label) in enumerate(zip(names,labels)):
        y=[find(poda,w,v,'avg_edges') for w in ws]
        a=ax.bar(xx+(j-1)*width,y,width,label=label)
        for z in a:ax.text(z.get_x()+z.get_width()/2,z.get_height()+10,f'{z.get_height():.0f}',ha='center',fontsize=9)
    ax.set_xticks(xx,['Pares','Quatro componentes']);ax.set_ylabel('Conexões percorridas por evento')
    ax.set_title('A mesma tarefa, custos diferentes');ax.legend(loc='upper left')
    fig.tight_layout();fig.savefig(F/'02_custo_propagar.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5.3))
    for j,(v,label) in enumerate(zip(names,labels)):
        y=[find(poda,w,v,'nodes') for w in ws]
        a=ax.bar(xx+(j-1)*width,y,width,label=label)
        for z in a:ax.text(z.get_x()+z.get_width()/2,z.get_height()+6,f'{z.get_height():.0f}',ha='center',fontsize=9)
    ax.set_xticks(xx,['Pares','Quatro componentes']);ax.set_ylabel('Mórfons mantidos (média)')
    ax.set_title('Efeito da poda na memória persistente');ax.legend(loc='upper left')
    fig.tight_layout();fig.savefig(F/'03_tamanho_da_memoria.png',dpi=160);plt.close(fig)

def hrr():
    tab=con['hrr'];fig,ax=plt.subplots(figsize=(8,5))
    for K in (1,4,8):
        xx=[];yy=[]
        for d in (16,64,256):
            row=next(x for x in tab if x['dim']==d and x['superposed_pairs']==K)
            xx.append(d);yy.append(row['accuracy_mean'])
        ax.plot(xx,yy,marker='o',label=f'{K} associações sobrepostas')
    ax.axhline(1,ls='--',lw=.9,c='gray',label='Portas explícitas (exatas)')
    ax.set_xticks([16,64,256]);ax.set_ylim(0,1.07)
    ax.set_xlabel('Dimensões da assinatura holográfica');ax.set_ylabel('Recuperação do componente')
    ax.set_title('Compressão por convolução circular · dados do mesmo grafo')
    ax.legend();fig.tight_layout();fig.savefig(F/'04_compressao_hrr.png',dpi=160);plt.close(fig)

def shape_diagram():
    x,y,xt,yt,_=sample_world('quad',41,520,260)
    model=MorphMemory(Config(max_order=4,nested=True,facet=True,order_controller=True,periodic_prune=True),41)
    model.fit(x,y)
    candidates=[m for m in model.nodes.values() if m.kind=='nested' and m.promoted and len(m.literals)==4]
    if not candidates:
        candidates=[m for m in model.nodes.values() if m.kind=='nested' and len(m.literals)==4]
    if not candidates:raise RuntimeError('no nested substructure')
    p=candidates[0];parts=[model.nodes[c] for c in p.ports]
    fig,ax=plt.subplots(figsize=(10,6))
    ax.set_xlim(-5,6.2);ax.set_ylim(-3.5,4.4);ax.set_aspect('equal');ax.axis('off')
    # these coordinates visualize exact logical incidence; angles are display-only
    xparent=3.2; yparent=.5
    circle=Circle((xparent,yparent),1.1,fill=False,lw=2);ax.add_patch(circle)
    ax.add_patch(Circle((xparent,yparent),.26));ax.text(xparent,yparent,'M',ha='center',va='center',color='white',weight='bold')
    ax.text(xparent,2.,f'Mórfon composto {p.uid}',ha='center',fontsize=11)
    for j,c in enumerate(parts):
        theta=2*math.pi*j/max(1,len(parts))+math.pi/3
        px=-1.0+1.8*math.cos(theta);py=.5+1.65*math.sin(theta)
        rad=.47 if c.kind=='atom' else .76
        ax.add_patch(Circle((px,py),rad,fill=False,lw=1.8))
        ax.add_patch(Circle((px,py),.16))
        ax.text(px,py,f'{c.uid}',ha='center',va='center',color='white',weight='bold')
        ax.annotate('',xy=(xparent-.27,yparent),xytext=(px+.3,py),arrowprops={'arrowstyle':'->','lw':1.8})
        ax.text(px,py-rad-.25,f'{c.kind}\n{len(c.literals)} fragmentos',ha='center',va='top',fontsize=9)
    ax.text(3.2,-1.45,f'{len(p.ports)} portas diretas; {len(p.literals)} fragmentos na estrutura total',ha='center',fontsize=10)
    ax.text(.6,-3.,'Dados estruturais do modelo treinado; posições do diagrama são apenas de apresentação.',fontsize=9)
    fig.tight_layout();fig.savefig(F/'05_morfon_aninhado.png',dpi=180);plt.close(fig)
    return {'node_id':p.uid,'children':list(p.ports),'literal_count':len(p.literals),
            'port_count':len(p.ports),'promoted':p.promoted}

def main():
    F.mkdir(exist_ok=True)
    main_comparison();resource_comparison();hrr();value=shape_diagram()
    (D/'figura_topologia.json').write_text(json.dumps(value,indent=2))
    print('Five figures generated; structure',value)
if __name__=='__main__':main()
