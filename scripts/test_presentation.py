#!/usr/bin/env python3
"""Check normal mapper output against disk-executed text, with generated labels removed."""
from pathlib import Path
import argparse,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--inform6',required=True);p.add_argument('--dfrotz',default='dfrotz');a=p.parse_args()
work=ROOT/'build/mapper/work'
for source in (ROOT/'src').iterdir():
    if source.is_file() and source.read_bytes()!=(work/source.name).read_bytes():p.error('Staged sources differ; rebuild first.')
sys.path.insert(0,str(work));from reference import start,command
labels=json.loads((work/'room_titles.json').read_text())
assert len(labels)==139 and len({row['title'] for row in labels})==139
memory=(work/'memory.bin').read_bytes()
def rendered(raw):
    return ''.join('\n' if c==13 else chr(c-128) if 193<=c<=218 else chr(c+32) if 65<=c<=90 else chr(c) if 32<=c<=126 else '' for c in raw)
def normalize(value):return ' '.join(value.split())
commands=['look','inventory','west','west','south','look','north','east','look','wait','inventory','look']
events=[]
def boundary(cpu):
    events.append((len(cpu.output),cpu.m[0x3e04]));return False
cpu=start(memory,0,{0x249e:boundary});expected=rendered(cpu.output);rooms={cpu.m[0x3e04]}
assert events, 'Native startup did not reach a room-description boundary'
raw=bytes(cpu.output);previous=0;startup_order=''
for offset,room in events:
    startup_order+=rendered(raw[previous:offset])+'\n'+labels[room]['title']+'\n';previous=offset
startup_order+=rendered(raw[previous:])
for text in commands:
    command(cpu,text);expected+=rendered(cpu.output);rooms.add(cpu.m[0x3e04])
results=[]
for version in (5,8):
    out=ROOT/'build/tests'/f'presentation-z{version}'
    env=dict(os.environ,INFORM6=str(Path(a.inform6).resolve()),PYTHONDONTWRITEBYTECODE='1')
    subprocess.run([sys.executable,str(work/'build_story.py'),'--out',str(out),'--seed','0','--version',str(version)],env=env,check=True)
    result=subprocess.run([a.dfrotz,'-q','-m','-w','200','-Z','3',str(out/f'robots.z{version}')],input='\n'.join(commands+['quit'])+'\n',text=True,capture_output=True,check=True,timeout=90)
    output=result.stdout
    for room in rooms:assert labels[room]['title'] in output,('missing label',version,room)
    for row in labels:output=output.replace(row['title'],'')
    banner="SAVE and RESTORE use your interpreter's save files. QUIT exits; RESTART starts a new case."
    output=output.split(banner,1)[1].rsplit('Goodbye.',1)[0]
    output=output.replace('\n? ','\n')
    assert normalize(output)==normalize(expected),('native prose changed',version)
    # Isolate BootCase from upper-window status rendering to test exact startup order.
    order_out=ROOT/'build/tests'/f'presentation-order-z{version}'
    order_out.mkdir(parents=True,exist_ok=True)
    unit=order_out/'startup_order.inf';unit.write_text('[ Main; BootCase(); @quit; ];\n')
    subprocess.run([sys.executable,str(work/'build_story.py'),'--unit',str(unit),'--out',str(order_out),'--seed','0','--version',str(version)],env=env,check=True)
    ordered=subprocess.run([a.dfrotz,'-q','-m','-w','200','-Z','3',str(order_out/f'robots.z{version}')],input='',text=True,capture_output=True,check=True,timeout=90)
    assert normalize(ordered.stdout)==normalize(startup_order),('startup heading order',version)
    results.append({'version':version,'commands':len(commands),'encountered_rooms':len(rooms),'native_text_preserved':True,'generated_labels_present':True,'startup_heading_at_native_boundary':True})
(ROOT/'build/tests/presentation-results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
