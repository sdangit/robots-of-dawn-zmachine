#!/usr/bin/env python3
"""Compare fresh Z5/Z8 trace builds with original-code execution (requires local build)."""
import argparse,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--c64',type=Path,required=True)
p.add_argument('--apple2',type=Path,help='Optional image identity check; gameplay reference is C64')
p.add_argument('--inform6',required=True)
p.add_argument('--dfrotz',default='dfrotz')
a=p.parse_args()
from build import input_paths,input_environment
hashes=json.loads((ROOT/'disk-hashes.json').read_text())
env=input_environment(input_paths(a.c64,a.apple2,hashes))
os.environ.pop('ROBOTS_APPLE_DISK',None)
os.environ.update(env,INFORM6=str(Path(a.inform6).resolve()))
work=ROOT/'build/faithful/work'
if not (work/'memory.bin').exists():p.error('Run scripts/build.py first.')
sys.path.insert(0,str(work))
from reference import start,command
memory=(work/'memory.bin').read_bytes()
commands=['look','inventory','west','west','south','look','north','east','look','wait','inventory','north','south','east','west','look','northeast','southwest','northwest','southeast','look','wait','inventory','look']
results=[]
for seed in (0,1,2,3,31,63,127,128,192,254,255):
 c=start(memory,seed)
 expected=[(bytes(c.output),bytes(c.m[0x3b59:0x3e11]))]
 for cmd in commands:
  command(c,cmd);expected.append((bytes(c.output),bytes(c.m[0x3b59:0x3e11])))
 for version in (5,8):
  out=ROOT/'build/tests'/f'seed-{seed}-z{version}'
  subprocess.run([sys.executable,str(work/'build_story.py'),'--out',str(out),'--trace','--seed',str(seed),'--version',str(version)],check=True)
  result=subprocess.run([a.dfrotz,'-q','-m','-w','200','-Z','3',str(out/f'robots-trace.z{version}')],input='\n'.join(commands+['quit'])+'\n',text=True,capture_output=True,timeout=90,check=True)
  chunks=result.stdout.split('PORT_INPUT>')[:-1]
  assert len(chunks)==len(expected),(seed,version,len(chunks))
  for i,(chunk,(text,state)) in enumerate(zip(chunks,expected)):
   output,tail=chunk.split('PORT_STATE:')
   assert bytes.fromhex(''.join(output.split()))==text,(seed,version,i,'text')
   assert bytes.fromhex(''.join(tail.split('PORT_SEED:')[0].split()))==state,(seed,version,i,'state')
  results.append(dict(seed=seed,version=version,commands=len(commands),exact_text_and_696_byte_state_checks=len(expected),passed=True))
(ROOT/'build/tests/results.json').write_text(json.dumps(results,indent=2)+'\n')
print(f'Passed {len(results)} runs, {len(results)*len(commands)} commands, {len(results)*len(expected)} exact output/state comparisons.')
