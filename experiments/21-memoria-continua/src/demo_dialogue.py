"""Uma conversa literal, executada por um modelo restaurado; sem respostas escritas no script."""
from pathlib import Path
from continuous import ContinuousNexo
import json
ROOT=Path(__file__).resolve().parents[1]
START=ROOT/'training'/'trained21.json'
STATE=ROOT/'results'/'demonstration_state.json'

def main():
    n=ContinuousNexo.load(START,'conversa_demonstracao')
    records=[]
    chunks=[
        ['Qual é meu nome?','Íris','Qual é meu nome?',
         'Meu nome é Selma.','Qual é meu nome?',
         'Onde eu moro?','Moro em Recife','Onde eu moro?'],
        ['Minha hipótese é que as interpretações mudam com a experiência.',
         'Qual é minha hipótese?',
         'Se a memória muda, então a interpretação pode mudar.',
         'Considere que a memória muda.','O que se conclui?','Por quê?',
         'Isso permite concluir que toda interpretação é verdadeira?'],
        ['O símbolo recém-descoberto representa uma estrutura desconhecida.',
         'O que esse símbolo representa?'],
    ]
    for group,chunk in enumerate(chunks):
        if group:
            n.save(STATE);n=ContinuousNexo.load(STATE)
        for text in chunk:
            before=len(n.mem.nodes)
            res=n.answer(text)
            records.append({'turn':len(records)+1,'user':text,'nexo':res['answer'],
                            'reason':res['reason'],'new_morphons':len(n.mem.nodes)-before,
                            'fact_uid':res.get('fact_uid'),'goal_uid':res.get('goal_uid'),
                            'trace':res.get('trace')})
    n.save(STATE)
    inspection=n.introspect()
    (ROOT/'results'/'dialogue_literal.json').write_text(
        json.dumps({'turns':records,'introspection':inspection},ensure_ascii=False,indent=2),encoding='utf8')
    lines=[]
    for r in records:
        lines.extend([f"{r['turn']:02d} HUMANO: {r['user']}",f"   NEXO: {r['nexo']}",
                      f"   RASTRO: {r['reason']} / novas unidades {r['new_morphons']}",''])
    lines.extend(['AUTO-INSPEÇÃO FINAL:',json.dumps(inspection,ensure_ascii=False,indent=2)])
    (ROOT/'results'/'dialogue_literal.txt').write_text('\n'.join(lines),encoding='utf8')
    print('\n'.join(lines[:70]))

if __name__=='__main__':main()
