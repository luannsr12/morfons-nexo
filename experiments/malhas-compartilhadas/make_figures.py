import json
import matplotlib.pyplot as plt
x=json.load(open('results.json'))
fig,ax=plt.subplots(figsize=(12,6.2),constrained_layout=True)
names=['Identidade e contexto','Malhas isoladas','Sem contexto','Por nome','Nome e sem contexto']
modes=['shared_context','isolated','no_context','label_match','label_no_context']
y=[x['evaluations'][m]['accuracy']*100 for m in modes]
bars=ax.barh(names[::-1],y[::-1])
for bar,val in zip(bars,y[::-1]):
    ax.text(val+1,bar.get_y()+bar.get_height()/2,f'{val:.1f}%',va='center',fontsize=12)
ax.set_xlim(0,112);ax.set_xlabel('Consultas classificadas corretamente (%)',fontsize=12)
ax.set_title('Malhas compartilhadas: ablações de identidade e contexto',fontsize=16,pad=16)
ax.grid(axis='x',alpha=.18)
ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
ax.tick_params(axis='both',labelsize=11)
fig.savefig('figures/ablation_modes.svg',bbox_inches='tight')
fig.savefig('figures/ablation_modes.png',dpi=200,bbox_inches='tight')
plt.close(fig)

f=x['factorized_provenance']
fig,ax=plt.subplots(figsize=(12,6.2),constrained_layout=True)
ax.plot([z['diamonds'] for z in f],[z['explicit_proof_paths'] for z in f],'-o',linewidth=2.3,markersize=7,label='Provas expandidas')
ax.plot([z['diamonds'] for z in f],[z['factorized_dag_nodes'] for z in f],'-s',linewidth=2.3,markersize=7,label='Nós no DAG compartilhado')
ax.set_yscale('log',base=2)
ax.set_xlabel('Regiões de bifurcação e reencontro',fontsize=12)
ax.set_ylabel('Quantidade de estruturas (escala logarítmica)',fontsize=12)
ax.set_title('Proveniência compartilhada evita expansão dos caminhos',fontsize=16,pad=16)
ax.grid(alpha=.2)
ax.legend(fontsize=11)
ax.tick_params(axis='both',labelsize=11)
fig.savefig('figures/proof_factorization.svg',bbox_inches='tight')
fig.savefig('figures/proof_factorization.png',dpi=200,bbox_inches='tight')
plt.close(fig)
print('Duas figuras SVG/PNG produzidas.')
