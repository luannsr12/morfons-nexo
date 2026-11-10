"""Console cumulativo: o estado é salvo APÓS CADA turno, não só no treino."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from continuous import ContinuousNexo

ROOT=Path(__file__).resolve().parents[1]
TRAIN=ROOT/'training'/'trained21.json'
DEFAULT=ROOT/'results'/'session_live.json'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--memory',type=Path,default=DEFAULT)
    parser.add_argument('--session',default='principal')
    parser.add_argument('--reset',action='store_true',help='recarrega explicitamente o treinamento, apagando esta sessão')
    args=parser.parse_args()
    if args.reset or not args.memory.exists():
        n=ContinuousNexo.load(TRAIN,args.session)
        n.save(args.memory)
    else:n=ContinuousNexo.load(args.memory,args.session)
    print('NEXO 21 | memoria continua. /memoria /salvar /sair')
    print('Diga algo novo, pergunte depois, corrija e reinicie: o estado sera mantido.')
    while True:
        try:phrase=input('Você > ').strip()
        except (EOFError,KeyboardInterrupt):break
        if phrase in ('/sair','/exit','quit'):break
        if phrase=='/memoria':
            print(json.dumps(n.introspect(),ensure_ascii=False,indent=2));continue
        if phrase=='/salvar':
            n.save(args.memory);print('Memória persistida em',args.memory);continue
        if not phrase:continue
        try:
            result=n.answer(phrase)
            # atomic save before confirming the turn to user
            n.save(args.memory)
            print('NEXO >',result.get('answer') or '[Sem conclusão]')
            print('         [memória:',result.get('reason'),'; prova:',result.get('trace') or
                  result.get('fact_uid') or result.get('goal_uid') or '-',']')
        except Exception as exc:
            n=ContinuousNexo.load(args.memory,args.session)  # desfaz alteracoes parciais em RAM
            print('Falha durante a transação; memoria anterior restaurada:',repr(exc))

if __name__=='__main__':main()
