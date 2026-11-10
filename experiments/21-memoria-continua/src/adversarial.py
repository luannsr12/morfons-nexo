"""Ablações e verificações de diálogo intercalado/continuidade com a MESMA MorphMemory."""
from pathlib import Path
import json, tempfile
from continuous import ContinuousNexo
from nexo20 import NexoDialogue
ROOT=Path(__file__).resolve().parents[1]
TRAIN=ROOT/'training'/'trained21.json';BASE=ROOT/'training'/'base20_trained.json'

def main():
    agent=ContinuousNexo.load(TRAIN,'adversarial')
    rows=[]
    def record(case,expected,actual):
        rows.append({'case':case,'expected':expected,'actual':actual,'ok':expected==actual})
    # Teste de aprendizado distribuído: 40 entidades, duas propriedades,
    # observacoes intercaladas antes de fazer QUALQUER pergunta.
    for i in range(40):
        agent.answer(f'Velaria{i} mora em Regio{i}.')
        agent.answer(f'Velaria{i} guarda volume{i}.')
    for i in reversed(range(40)):
        record('delayed_location',f'Regio{i}',agent.answer(f'Onde Velaria{i} mora?')['answer'])
        record('delayed_possession',f'volume{i}',agent.answer(f'O que Velaria{i} guarda?')['answer'])
    # Revisão: hipótese antiga deixa de ser premissa para novas inferências.
    for i in range(25):
        a,b=f'Vistia{i}',f'Salim{i}'
        agent.answer(f'Meu nome é {a}.')
        agent.answer(f'Meu nome é {b}.')
        record('revision_latest',b,agent.answer('Qual é meu nome?')['answer'])
        record('revision_old_not_true',False,agent.answer(f'Isso permite concluir que meu nome é {a}?')['reason']=='yes')
    # A falta de conhecimento cria uma pergunta interna, que permanece na memória.
    questions=[]
    for i in range(22):
        q=f'Qual é a origem de mineral{i}?'
        r=agent.answer(q)
        questions.append({'question':q,'reason':r['reason'],'goal':r.get('goal_uid')})
        agent.answer(f'Fonte{i}')
        again=agent.answer(q)
        record('episodic_recall',f'Fonte{i}',again['answer'])
    # Mantém cálculo e inferência antigos; nenhum caso é de treino lexical.
    record('old_binary_arithmetic',True,'43' in str(agent.answer('Quanto é 17 mais 26?')['answer']))
    for i in range(20):
        p=f'a campainha alfa{i} toca'
        q=f'o corredor beta{i} abre'
        agent.answer(f'Se {p}, então {q}.')
        agent.answer(f'Considere que {p}.')
        ans=agent.answer(f'Isso permite concluir que {q}?')
        record('new_philosophical_inference','yes',ans['reason'])
    # Um conjunto de perguntas abertas nao deve ser apresentado como entendimento.
    unsupported=[]
    for q in ['Por que as minhas escolhas mudam conforme meu passado?',
              'O que torna uma crença justificada?',
              'Você acha que o contexto cria significado?',
              'Se existem duas interpretações, como decidir entre elas?',
              'O que você pensa sobre a origem da consciência?']:
        r=agent.answer(q)
        unsupported.append({'question':q,'reason':r['reason'],'answer':r['answer']})
    summary={'cases':len(rows),'correct':sum(x['ok'] for x in rows),
             'by_case':{k:{'n':sum(x['case']==k for x in rows),
                           'ok':sum(x['case']==k and x['ok'] for x in rows)}
                        for k in sorted(set(x['case'] for x in rows))},
             'unsupported_free_questions':unsupported,'unknown_episodes':questions,
             'morphons':len(agent.mem.nodes),'introspection':agent.introspect()}
    (ROOT/'results'/'adversarial_cases.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'results'/'adversarial_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print('total',summary['correct'],'/',summary['cases'])
    print('bycase',summary['by_case'])
    print('unknown',[(a['question'],a['reason']) for a in unsupported])
    return summary

if __name__=='__main__':main()
