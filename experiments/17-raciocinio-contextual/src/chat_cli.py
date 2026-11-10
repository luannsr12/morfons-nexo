"""Conversa contextual com os Mórfons treinados, sem rede ou LLM."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).parent))
from grounded import ContextLearner,MorphGraph

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'results/memoria_treinada.json'
SAVE=ROOT/'results/sessao_interativa.json'

def main():
    model=ContextLearner.load(MODEL)
    graph=MorphGraph.restore(json.loads(SAVE.read_text(encoding='utf8'))) if SAVE.exists() else MorphGraph()
    print('NEXO | teste integrado de contexto (sem LLM).')
    print('Ensine com frases como: Hoje Mara mora em Recife / Mara guarda Caderno / Caderno fica em Olinda')
    print('Pergunte: Onde mora Mara? / E antes? / Onde fica o objeto que Mara guarda? / Quanto é 17 mais 26?')
    print('Comandos: /sair, /zerar, /estado')
    while True:
        try:line=input('Você> ').strip()
        except (EOFError,KeyboardInterrupt):break
        if not line:continue
        if line=='/sair':break
        if line=='/zerar':
            graph=MorphGraph();print('[Sessão zerada]');continue
        if line=='/estado':
            print(f'[Mórfons do mundo: {len(graph.mem.nodes)}, marcas/portas persistentes; foco: {graph.current_focus()}]');continue
        ans=model.ask(line,graph)
        if ans['answer'] is not None:
            print('NEXO>',ans['answer'],f"[passos={ans.get('hops')}, raios={ans.get('rays')}]")
        else:
            obs=model.ingest(line,graph)
            if obs.get('kind')=='observed':
                print('[Relação adicionada à memória; nenhuma resposta gerada]')
            else:print('NEXO> Não encontrei um caminho aprendido para responder a isso.',f"[{ans.get('reason')}]")
        SAVE.write_text(json.dumps(graph.snapshot(),ensure_ascii=False),encoding='utf8')
    SAVE.write_text(json.dumps(graph.snapshot(),ensure_ascii=False),encoding='utf8')

if __name__=='__main__':main()
