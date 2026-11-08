"""Execute supplied game bytes; only input/output platform boundaries are adapted."""
from cpu import CPU

def display(cpu):
    value=cpu.a; cpu.output.append(value); cpu.m[0x6f]=value
    if value==13: cpu.m[0xd3]=0
    elif 32<=value<=126 or 193<=value<=218: cpu.m[0xd3]=(cpu.m[0xd3]+1)%40
    cpu.nz(value); cpu.ret(); return True

def start(memory, seed):
    cpu=CPU(memory); cpu.hooks[0xc0e]=display; cpu.m[0xd5]=39; cpu.m[0xa2]=seed
    cpu.run(0xd4d,stop=0xcab,limit=500000)
    return cpu

def command(cpu,text):
    data=' '.join(text.upper().split()).encode('ascii')+b' \0'
    if len(data)>256: raise ValueError('Command too long')
    cpu.current_pc=None; cpu.m[0x800:0x900]=bytes(256);cpu.m[0x800:0x800+len(data)]=data
    cpu.a=0;cpu.s=1;cpu.output=[];cpu.reads.clear();cpu.writes.clear()
    cpu.run(0xe18,stop=0xcab,limit=1500000)
    return cpu
