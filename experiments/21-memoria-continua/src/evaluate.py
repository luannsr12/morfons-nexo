"""Avaliação de conversas CONTÍNUAS em informações não presentes no ensino."""
from __future__ import annotations
import json,random,time,sys
from collections import Counter
from pathlib import Path
from continuous import ContinuousNexo
from train_experiences import FAMILIES

ROOT=Path(__file__).resolve().parents[1]
TRAIN=ROOT/'training'/'trained21.json'

def experiment():
    rows=[];start=time.perf_counter(); n=ContinuousNexo.load(TRAIN,'avaliacao')
    initial_nodes=len(n.mem.nodes)
    for group,(statement,question,has_subject) in enumerate(FAMILIES):
        for i in range(32):
            val=f'Vezara{group}x{i}'
            subj=f'Moraia{group}x{i}'
            s=statement.format(s=subj,v=val)
            q=question.format(s=subj,v=val)
            # Teste de ausência de fato numa sessão nova já treinada em idioma
            # e de consulta imediatamente após a observação ainda inédita.
            obs=n.answer(s)
            ans=n.answer(q)
            rows.append({'category':group,'trial':i,'utterance':s,'question':q,
                         'expected':val,'answer':ans.get('answer'),'correct':ans.get('answer')==val,
                         'observed_reason':obs['reason'],'answer_reason':ans['reason'],
                         'fact':ans.get('fact_uid'),'rays':ans.get('rays'),'morphons':len(n.mem.nodes)})
    correct=sum(r['correct'] for r in rows)
    # Ensinando construções não presentes no treinamento, DURANTE a conversa;
    # o professor externo oferece uma tripla por turno, não regras ao motor.
    novel=[
        ('Minha ferramenta favorita é {v}.','Qual é minha ferramenta favorita?'),
        ('Minha descoberta recente é {v}.','Qual é minha descoberta recente?'),
        ('Minha conclusão provisória é {v}.','Qual é minha conclusão provisória?'),
        ('O formato de {s} é {v}.','Qual é o formato de {s}?'),
        ('O tamanho de {s} é {v}.','Qual é o tamanho de {s}?'),
        ('O mineral {s} contém {v}.','O que o mineral {s} contém?'),
    ]
    live=[];before_schemas=len(n._schemas)
    for f,(sa,qa) in enumerate(novel):
        lesson=[]
        for j in range(3):
            key=f'Povaro{f}t{j}';val=f'Elidia{f}t{j}'
            s=sa.format(s=key,v=val);q=qa.format(s=key,v=val)
            a=n.answer(s);b=n.answer(q);c=n.answer(val)
            lesson.append((a['reason'],b['reason'],c['reason']))
        s=sa.format(s=f'Taliko{f}',v=f'Cerium{f}')
        q=qa.format(s=f'Taliko{f}',v=f'Cerium{f}')
        a=n.answer(s);b=n.answer(q)
        live.append({'kind':f,'question':q,'expected':f'Cerium{f}',
                     'answer':b.get('answer'),'correct':b.get('answer')==f'Cerium{f}',
                     'schema_count':len(n._schemas),'lessons':lesson,
                     'reason':b.get('reason')})
    # Uma única situação de raciocínio filosófico, construída com fatos novos
    # da conversa; usa o raciocinador treinado no experimento anterior.
    logic=[]
    for text in ['Minha hipótese é que a revisão de uma hipótese requer novas evidências.',
                 'Qual é minha hipótese?',
                 'Se meu nome é Rubia, então a pessoa se identifica como Rubia.',
                 'Meu nome é Rubia.',
                 'O que se conclui?', 'Por quê?',
                 'Meu nome é Valeria.',
                 'Isso permite concluir que meu nome é Rubia?',
                 'Qual é meu nome?',
                 'Isso permite concluir que meu nome é Valeria?']:
        result=n.answer(text)
        logic.append({'user':text,'nexo':result.get('answer'),'reason':result.get('reason'),
                      'trace':result.get('trace')})
    before=n.introspect()
    state=ROOT/'results'/'trained_and_live_state.json'
    n.save(state)
    restored=ContinuousNexo.load(state)
    post=restored.answer('Qual é meu nome?')
    after=restored.introspect()
    summary={'training_examples':len(json.loads((ROOT/'training'/'teacher_experiences.json').read_text())),
             'learned_schemas_before_interaction':before_schemas,
             'new_schemas':len(n._schemas)-before_schemas,
             'holdout_queries':len(rows),'holdout_correct':correct,
             'online_novel_queries':len(live),'online_novel_correct':sum(x['correct'] for x in live),
             'initial_morphons':initial_nodes,'after_morphons':len(n.mem.nodes),
             'restored_name':post.get('answer'),'last_response':post.get('reason'),
             'turns_before_restart':before['turns'],'turns_after_restart':after['turns'],
             'persisted_self_questions':before['self_question_morphons'],
             'elapsed_seconds':round(time.perf_counter()-start,3)}
    for fname,content in [('holdout.json',rows),('online_induction.json',live),
                          ('philosophical_continuity.json',logic),('summary.json',summary)]:
        (ROOT/'results'/fname).write_text(json.dumps(content,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print('logic:')
    for e in logic:print(e['user'],'=>',e['nexo'],'(',e['reason'],')')
    return summary

if __name__=='__main__':experiment()
