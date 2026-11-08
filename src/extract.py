"""Extract the matching user-supplied D64 into a private 64 KiB memory artifact."""
from pathlib import Path
import hashlib, json, os
HERE=Path(__file__).resolve().parent
if HERE.name!='work' or HERE.parent.parent.name!='build':
    raise SystemExit('Run scripts/build.py; generated artifacts must stay under private build/<variant>/work/.')

def extract(path):
    data=Path(path).read_bytes()
    def sector(track, number):
        if not 1 <= track <= 35: raise ValueError('Invalid track')
        sizes=[21 if t<=17 else 19 if t<=24 else 18 if t<=30 else 17 for t in range(1,36)]
        if not 0 <= number < sizes[track-1]: raise ValueError('Invalid sector')
        offset=(sum(sizes[:track-1])+number)*256
        return data[offset:offset+256]
    files={}; track,number=18,1; seen=set()
    while track:
        if (track,number) in seen: raise ValueError('Directory loop')
        seen.add((track,number)); block=sector(track,number)
        for i in range(8):
            entry=block[i*32:(i+1)*32]
            if not entry[2]: continue
            name=entry[5:21].rstrip(b'\xa0')
            t,s=entry[3:5]; payload=bytearray(); chain=set()
            while t:
                if (t,s) in chain: raise ValueError('File chain loop')
                chain.add((t,s)); part=sector(t,s)
                payload.extend(part[2:] if part[0] else part[2:part[1]+1]); t,s=part[:2]
            files[name]=payload
        track,number=block[:2]
    memory=bytearray(65536)
    # File load addresses are read from PRG headers. The final segment is relocated
    # to its execution address, matching the disk loader's memory layout.
    for name,relocated in [('LOADER',None),('ROBOTS1',None),('ROBOTS2',0xe000)]:
        payload=files[name.encode('ascii')]; address=int.from_bytes(payload[:2],'little') if relocated is None else relocated
        if address+len(payload)-2>65536: raise ValueError('Invalid load range')
        memory[address:address+len(payload)-2]=payload[2:]
    expected='ba24aab557e5f57f7bc8f687e6b11cf6cd4d82181aa11fd495f47b61dc59369c'
    if hashlib.sha256(memory).hexdigest()!=expected: raise ValueError('Unexpected memory image')
    return bytes(memory)

if __name__=='__main__':
    memory=extract(os.environ['ROBOTS_C64_DISK'])
    (HERE/'memory.bin').write_bytes(memory)
    (HERE/'extraction.json').write_text(json.dumps({'bytes':len(memory),'sha256':hashlib.sha256(memory).hexdigest()},indent=2)+'\n')
