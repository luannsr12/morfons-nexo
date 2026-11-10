"""Professor externo: apenas conversas demonstradas, sem esquemas/slots no aluno.
As frases aqui sao exemplos de idioma, nao predicados implementados no motor.
"""
from __future__ import annotations
import json, random
from pathlib import Path
from continuous import ContinuousNexo

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'training'/'base20_trained.json'

FAMILIES=[
 ('Meu nome é {v}.','Qual é meu nome?',False),
 ('Eu moro em {v}.','Onde eu moro?',False),
 ('Eu trabalho em {v}.','Onde eu trabalho?',False),
 ('{s} mora em {v}.','Onde {s} mora?',True),
 ('{s} guarda {v}.','O que {s} guarda?',True),
 ('{s} prefere {v}.','O que {s} prefere?',True),
 ('O livro {s} fica em {v}.','Onde fica o livro {s}?',True),
 ('A cor de {s} é {v}.','Qual é a cor de {s}?',True),
 ('O objeto {s} pertence a {v}.','A quem pertence o objeto {s}?',True),
 ('Meu projeto se chama {v}.','Como se chama meu projeto?',False),
 ('Eu estou estudando {v}.','O que estou estudando?',False),
 ('Minha hipótese é {v}.','Qual é minha hipótese?',False),
]

def teacher_data(seed=31,per_family=18):
    rng=random.Random(seed); triples=[]
    for family,(s,q,subject) in enumerate(FAMILIES):
        for i in range(per_family):
            # Nomes de treino são artificiais; nomes inéditos serão reservados.
            sub=f'zalor{family}t{i}'
            val=f'verila{family}t{i}'
            triples.append({'statement':s.format(s=sub,v=val),
                            'question':q.format(s=sub,v=val),'answer':val})
    rng.shuffle(triples)
    return triples

def train(path=None):
    agent=ContinuousNexo.from_state(BASE)
    examples=teacher_data()
    formed=agent.train(examples)
    to=Path(path or ROOT/'training'/'trained21.json')
    agent.save(to)
    (ROOT/'training'/'teacher_experiences.json').write_text(json.dumps(examples,ensure_ascii=False,indent=2),encoding='utf8')
    return agent,formed

if __name__=='__main__':
    n,f=train()
    print('formed:',f,'schemas:',len(n._schemas),'nodes:',len(n.mem.nodes))
    for sc in n._schemas:
        face=sc.facets[0]
        print(sc.uid,face['statement'],'--> ',face['question'],'evidence',face['evidence'])
