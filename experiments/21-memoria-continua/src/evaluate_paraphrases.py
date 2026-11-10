"""Transferência de paráfrase aprendida APENAS por interações observadas.
A equipe de teste gera frases; o motor recebe somente texto e feedback.
"""
import json
from pathlib import Path
from continuous import ContinuousNexo
ROOT=Path(__file__).resolve().parents[1]
TRAIN=ROOT/'training'/'trained21.json'

FAMILIES=[
 ('{s} mora em {v}.','Em qual cidade {s} reside?'),
 ('{s} mora em {v}.','Onde é o domicílio de {s}?'),
 ('{s} guarda {v}.','Qual artigo {s} mantém guardado?'),
 ('A cor de {s} é {v}.','Qual tom tem {s}?'),
 ('{s} prefere {v}.','O que {s} mais gosta?'),
 ('O livro {s} fica em {v}.','Em que lugar está o livro {s}?'),
 ('Meu nome é {v}.','Como eu sou chamado?'),
]

def run():
    n=ContinuousNexo.load(TRAIN,session='parafrase')
    training=[];evals=[]
    for i,(statement,question) in enumerate(FAMILIES):
        for j in range(3):
            key=f'Melora{i}k{j}'
            val=f'Loxia{i}v{j}'
            s=statement.format(s=key,v=val)
            q=question.format(s=key,v=val)
            lines=[s,q,val]
            outs=[n.answer(x) for x in lines]
            training.append({'group':i,'utterances':lines,'reasons':[r['reason'] for r in outs],
                             'new_aliases':outs[-1].get('new_aliases',0)})
        for j in range(25):
            key=f'Mandira{i}k{j}'
            val=f'Volita{i}v{j}'
            s=statement.format(s=key,v=val)
            q=question.format(s=key,v=val)
            n.answer(s)
            r=n.answer(q)
            evals.append({'group':i,'question':q,'expected':val,
                          'predicted':r['answer'],'correct':r['answer']==val,
                          'reason':r['reason']})
    summary={'families':len(FAMILIES),'demonstrations':len(training),
             'queries':len(evals),'correct':sum(e['correct'] for e in evals),
             'aliases':len(n._aliases),'morphons':len(n.mem.nodes)}
    for name,obj in [('paraphrase_training.json',training),('paraphrase_holdout.json',evals),
                     ('paraphrase_summary.json',summary)]:
        (ROOT/'results'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
    print(summary)
    for i in range(len(FAMILIES)):
        rows=[r for r in evals if r['group']==i]
        print(i,sum(r['correct'] for r in rows),'/',len(rows),rows[0]['reason'])

if __name__=='__main__':run()
