"""Imagens derivadas das estruturas realmente consultadas; nao imagens conceituais."""
from __future__ import annotations
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,FancyArrowPatch
from grounded import MorphGraph,ContextLearner
ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)

def draw():
    m=ContextLearner.load(ROOT/'results/memoria_treinada.json');g=MorphGraph()
    for t in ['Hoje Mara mora em Recife','Mara guarda Caderno','Caderno fica em Olinda','Olinda pertence a Pernambuco']:
        m.ingest(t,g)
    q='Em que região fica o lugar onde fica o objeto que Mara guarda'
    v=m.ask(q,g,True)
    # Each edge corresponds to a world_fact Morphon selected by learned relation.
    used=[x for z in v['reference_trace'] for x in z['port_ids']]+v['nodes']
    labels=[]
    for uid in used:
        f=g.mem.nodes[uid].facets[0]
        labels.append((uid,g.entity_spelling[f['src']],g.entity_spelling[f['dst']]))
    fig,ax=plt.subplots(figsize=(11,3.75))
    layout={'Mara':(1,1.8),'Caderno':(3.6,1.8),'Olinda':(6.2,1.8),'Pernambuco':(8.8,1.8)}
    ax.set_xlim(0,10);ax.set_ylim(.45,3.1);ax.axis('off')
    for n,(name,(x,y)) in enumerate(layout.items()):
        ax.add_patch(Circle((x,y),.46,facecolor=plt.cm.tab10(n),edgecolor='black',alpha=.75,lw=1.5))
        ax.add_patch(Circle((x,y),.13,facecolor='white',edgecolor='black',lw=.7))
        ax.text(x,y-.78,name,ha='center',fontsize=12,weight='bold')
    for i,(uid,a,b) in enumerate(labels):
        x,y=layout[a];xx,yy=layout[b]
        ax.add_patch(FancyArrowPatch((x+.48,y),(xx-.48,yy),arrowstyle='->',mutation_scale=18,lw=2,color=plt.cm.tab10(i)))
        ax.text((x+xx)/2,2.25,f'Mórfon {uid} • 3 raios',ha='center',fontsize=9)
    ax.set_title('Caminho aprendido: 3 relações não vistas juntas no treinamento',fontsize=13)
    fig.tight_layout();fig.savefig(FIG/'01_morfons_em_cadeia.png',dpi=165);plt.close(fig)
    controls=json.loads((ROOT/'results/controles.json').read_text())
    x=['Completo','Sem composição','Tempo trocado','Sem fatos']
    y=[controls[v]['correct']/controls[v]['total']*100 for v in ['normal','without_recursive_composition','swap_time','erase_facts']]
    fig,ax=plt.subplots(figsize=(8,4))
    bars=ax.bar(x,y)
    ax.set_ylim(0,108);ax.set_ylabel('Respostas corretas (%)');ax.set_title('Ablações sobre as mesmas 1.000 consultas inéditas')
    for b,v in zip(bars,y):ax.text(b.get_x()+b.get_width()/2,v+2,f'{v:.1f}%',ha='center')
    fig.tight_layout();fig.savefig(FIG/'02_ablacoes.png',dpi=165);plt.close(fig)
    curve=controls['curve']
    fig,ax=plt.subplots(figsize=(8,4))
    ax.plot([z['worlds'] for z in curve],[100*z['correct']/z['total'] for z in curve],marker='o')
    ax.set_xscale('log');ax.set_xticks([1,2,5,10,25,50,100,240],['1','2','5','10','25','50','100','240'])
    ax.set_ylim(0,108);ax.set_xlabel('Mundos supervisionados');ax.set_ylabel('Respostas corretas (%)')
    ax.set_title('Mundo inicial deliberadamente ambíguo; novos exemplos discriminam rotas')
    fig.tight_layout();fig.savefig(FIG/'03_curva_aprendizagem.png',dpi=165);plt.close(fig)
if __name__=='__main__':draw()
