"""Replay auditável de uma interação integrada (sem alterar o núcleo original)."""
from evaluate import world,contexts,simulate
from integrated import InteractingMorphons

L=InteractingMorphons(4,2,3,max_degree=2,seed=0)
pool=[(x,a) for a in range(2) for x in contexts()]
for _ in range(22):
    available=[(x,a) for x,a in pool if len(L._faces(L.roots[a,0],'experience'))<11]
    chosen=L.choose_probe(available)
    x,a=chosen
    L.observe(x,a,world(0,x,a,0))
    pool.remove(chosen)
print('Aprendizagem: 22 episódios; núcleo congelado:',L.validate_invariants()['all_nuclei_constant'])
print('Número de faces (marcas recebidas):',L.validate_invariants()['interaction_faces'])

s=(0,1,0);last=1;goal=(1,0,0)
L.start_session(last)
plan,proof=L.choose_plan(s,L.current_history(),goal,max_depth=3)
print('Condição inicial:',s,'última ação:',last,'objetivo:',goal)
print('Plano deduzido das relações adquiridas:',plan)
assert plan is not None and len(plan)>=2
for i,action in enumerate(plan,1):
    before=s+(L.current_history(),)
    imagined,trace=L.query(before,action,record_imagination=True)
    actually=world(0,before,action,0)
    eid=L.observe(before,action,actually,live=True)
    print(f'{i}. Morfon-episódio={eid} estado={before} ação={action} '
          f'antecipado={imagined} observado={actually} prova={trace["marks"]}')
    s=actually
print('Condição final:',s,'objetivo atingido:',s==goal)
print('Pensamentos:',L.metrics['thoughts'],'episódios observados:',L.metrics['observations'])
print('Autoedições de Morfons:',sum(m['actor']==m['target'] for m in L.mutations))
assert s==goal
