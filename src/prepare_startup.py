"""Generate private startup snapshots by executing the user-supplied disk code."""
from pathlib import Path
import json
from reference import start
HERE=Path(__file__).resolve().parent
if HERE.name!='work' or HERE.parent.parent.name!='build':
    raise SystemExit('Run scripts/build.py; generated artifacts must stay under private build/<variant>/work/.')
memory=(HERE/'memory.bin').read_bytes()
attrs=('a','x','y','s','c','z','n','v','d')
snapshots=[]; outputs=[]; registers=[]; room_boundaries=[]
for seed in range(256):
    boundaries=[]
    def room_boundary(cpu):
        boundaries.append([len(cpu.output),cpu.m[0x3e04]])
        return False
    cpu=start(memory,seed,{0x249e:room_boundary})
    room_boundaries.append(boundaries)
    snapshots.append(bytes(cpu.m));outputs.append(bytes(cpu.output).hex())
    registers.append([getattr(cpu,name) for name in attrs])
    if seed%32==0: print(f'Executed startup seed {seed}',flush=True)
addresses=[i for i in range(65536) if any(state[i]!=snapshots[0][i] for state in snapshots[1:])]
artifact={'addresses':addresses,'values':[[state[i] for i in addresses] for state in snapshots],
          'registers':registers,'outputs':outputs,'attributes':attrs,'room_boundaries':room_boundaries}
(HERE/'startup.bin').write_bytes(snapshots[0])
(HERE/'startup.json').write_text(json.dumps(artifact,separators=(',',':'))+'\n')
print(f'Prepared 256 native startup states, {len(addresses)} variable addresses.',flush=True)
