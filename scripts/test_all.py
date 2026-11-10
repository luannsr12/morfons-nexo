#!/usr/bin/env python3
"""Roda as sete suites originais isoladamente, sem modificar os experimentos."""
import argparse, json, re, subprocess, sys, datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TESTS={
 '08-aprendizagem-esferas':['-m','unittest','discover','-s','tests','-v'],
 '14-morfon-integrado':['-m','unittest','discover','-s','testes','-v'],
 '17-raciocinio-contextual':['-m','unittest','discover','-s','tests','-v'],
 '21-memoria-continua':['-m','unittest','discover','-s','tests','-v'],
 '23-faces-funcionais':['-m','unittest','discover','-s','tests','-v'],
 '24-ciclo-integrado':['-m','unittest','discover','-s','tests','-v'],
 'malhas-compartilhadas':['-m','unittest','-v','test_experiment'],
}
def main():
 p=argparse.ArgumentParser();p.add_argument('--no-save',action='store_true');args=p.parse_args()
 output=[];logs=[]
 for name,command in TESTS.items():
  cwd=ROOT/'experiments'/name
  result=subprocess.run([sys.executable,*command],cwd=cwd,capture_output=True,text=True)
  log=result.stdout+'\n'+result.stderr
  counts=re.findall(r'Ran (\d+) tests?',log)
  n=int(counts[-1]) if counts else 0
  ok=result.returncode==0 and bool(counts) and re.search(r'\nOK(?:\n|$)',log) is not None
  output.append({'experiment':name,'tests':n,'passed':ok,'exit_code':result.returncode})
  logs.append(f'===== {name} =====\n{log}')
  print(f'{"OK  " if ok else "FAIL"} {name:30} {n:3} testes',flush=True)
  if not ok: print('\n'.join(log.splitlines()[-18:]),file=sys.stderr)
 total=sum(v['tests'] for v in output);passed=all(v['passed'] for v in output)
 record={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'total_tests':total,'passed':passed,'suites':output}
 if not args.no_save:
  d=ROOT/'reproducibility'
  (d/'local_test_run.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  (d/'local_test_run.log').write_text('\n\n'.join(logs),encoding='utf8')
 print(f'\nTOTAL: {total} testes; {"todas aprovadas" if passed else "há falhas"}')
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
