"""Generate mapper labels from disk descriptions using the disk's text routines.
No editorial game-world labels or translated text expansion are stored here.
"""
from pathlib import Path
import json,re
from cpu import CPU
from reference import display
HERE=Path(__file__).resolve().parent
if HERE.name!='work' or HERE.parent.parent.name!='build':
    raise SystemExit('Run scripts/build.py; generated artifacts must stay under private build/<variant>/work/.')
memory=(HERE/'startup.bin').read_bytes()
labels=[]
for room in range(139):
    pointer=memory[0x812c+room]+256*memory[0x80a1+room]
    if memory[pointer] in (33,93,37):pointer+=1
    cpu=CPU(memory);cpu.hooks[0xc0e]=display
    cpu.m[0x10]=pointer&255;cpu.m[0x11]=pointer>>8;cpu.output=[]
    cpu.run(0x2159);cpu.run(0x2439)
    text=''.join(' ' if c==13 else chr(c-128) if 193<=c<=218 else chr(c+32) if 65<=c<=90 else chr(c) if 32<=c<=126 else '' for c in cpu.output)
    text=' '.join(text.split())
    # Generic editorial shortening; the description itself comes only from disk.
    title=re.split(r'[.!?]',text,1)[0].strip()[:60].strip()
    if not title:title='Location'
    labels.append({'room':room,'title':title+' ['+str(room+1)+']','description':text})
(HERE/'room_titles.json').write_text(json.dumps(labels,indent=2)+'\n')
print('Generated 139 disk-derived mapper labels.')
