#!/usr/bin/env python3
"""Test generated startup states and Z-machine saves without checked-in game fixtures.

Requires scripts/build.py first. All generated test stories, dumps, and saves stay
in ignored build/tests/startup-saves/. The I/O page $D000-$DFFF is intentionally
not RAM in the host, so RAM comparisons cover all 61,440 modeled bytes.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTERS = ('a', 'x', 'y', 's', 'c', 'z', 'n', 'v', 'd')
DUMP = '''
[ Snapshot i;
 print "^TEST_RAM:";
 for(i=0:i~=$d000:i++)Hex(Read(i));
 for(i=$e000:i~=0:i++)Hex(Read(i));
 print "^TEST_REG:";
 Hex(ra);Hex(rx);Hex(ry);Hex(rs);Hex(fc);Hex(fz);Hex(fn);Hex(fv);Hex(fd);
 @log_shift pc (-8) i;Hex(i);Hex(pc);
 print "^TEST_END^";
];
'''
STARTUP = DUMP + '''
[ Main i;
 @buffer_mode 0;
 for(i=0:i<256:i++){
  print "^TEST_BEGIN:",i,"^";
  seed=i;indirect(startup_dispatch-->i);pc=$cab;Snapshot();
 }
 @quit;
];
'''
# Run the same native loop as production. Instrument only input boundaries;
# production Keyboard, save/restore routines, BootCase and opcodes are unchanged.
SESSION = DUMP + '''
[ Main;
 @buffer_mode 0;BootCase();
 while(1){
  if(pc==$c0e){Output();continue;}
  if(pc==$cab){Snapshot();Keyboard();continue;}
  if(pc==$d97){seed=FIXED_SEED;if(seed<0)seed=random(256)-1;Write($a2,seed);}
  if(pc==$7e66){SaveNative();continue;}
  if(pc==$7f51){RestoreNative();continue;}
  lastpc=pc;op=Fetch();indirect(dispatch-->op);
 }
];
'''


def compact_ram(memory):
    return bytes(memory[:0xd000] + memory[0xe000:])


def state(cpu):
    return compact_ram(cpu.m), bytes([getattr(cpu, key) for key in REGISTERS]) + cpu.pc.to_bytes(2, 'big')


def snapshots(output):
    return [(bytes.fromhex(''.join(ram.split())), bytes.fromhex(''.join(reg.split())))
            for ram, reg in re.findall(r'TEST_RAM:([\s\dA-F]+)TEST_REG:([\s\dA-F]+)TEST_END', output)]


def check(actual, expected, label):
    assert len(actual[0]) == 61440, (label, 'wrong RAM dump length', len(actual[0]))
    if actual != expected:
        diffs = [i if i < 0xd000 else i + 0x1000 for i, (a, b) in enumerate(zip(actual[0], expected[0])) if a != b]
        raise AssertionError((label, 'RAM differences', [hex(i) for i in diffs[:30]], 'registers', actual[1].hex(), expected[1].hex()))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--c64', type=Path, required=True)
    p.add_argument('--inform6', required=True)
    p.add_argument('--dfrotz', default='dfrotz')
    p.add_argument('--variant', choices=('faithful', 'mapper'), default='faithful')
    a = p.parse_args()
    from build import input_paths, input_environment
    env = input_environment(input_paths(a.c64, None, json.loads((ROOT/'disk-hashes.json').read_text())))
    compiler = shutil.which(a.inform6)
    if not compiler:
        p.error('Inform compiler not found')
    env.update(INFORM6=str(Path(compiler).resolve()), PYTHONDONTWRITEBYTECODE='1')
    work = ROOT/'build'/a.variant/'work'
    for name in ('memory.bin', 'startup.bin', 'startup.json'):
        if not (work/name).is_file():
            p.error('Run scripts/build.py first; missing ' + name)
    # Refuse stale copied source rather than silently test a different version.
    for path in (ROOT/'src').iterdir():
        if path.suffix in ('.py', '.inf'):
            assert (work/path.name).read_bytes() == path.read_bytes(), 'Rebuild first: stale ' + path.name
    sys.path.insert(0, str(work))
    from reference import start
    memory = (work/'memory.bin').read_bytes()
    prepared = (work/'startup.bin').read_bytes()
    artifact = json.loads((work/'startup.json').read_text())
    assert tuple(artifact['attributes']) == REGISTERS
    assert len(artifact['values']) == len(artifact['registers']) == len(artifact['outputs']) == 256
    expected = []
    for seed in range(256):
        boundaries = []
        def room_boundary(cpu):
            boundaries.append([len(cpu.output), cpu.m[0x3e04]])
            return False
        cpu = start(memory, seed, {0x249e: room_boundary})
        assert artifact['room_boundaries'][seed] == boundaries, (seed, 'startup room boundaries')
        reconstructed = bytearray(prepared)
        for address, value in zip(artifact['addresses'], artifact['values'][seed]):
            reconstructed[address] = value
        assert bytes(reconstructed) == bytes(cpu.m), (seed, 'full 64 KiB artifact mismatch')
        assert artifact['registers'][seed] == [getattr(cpu, key) for key in REGISTERS], (seed, 'artifact registers')
        assert bytes.fromhex(artifact['outputs'][seed]) == bytes(cpu.output), (seed, 'artifact output')
        expected.append((state(cpu), bytes(cpu.output)))
        if seed % 64 == 63:
            print(f'Validated {seed + 1}/256 native startup artifacts.', flush=True)
    out = ROOT/'build/tests/startup-saves'
    out.mkdir(parents=True, exist_ok=True)
    def build(name, unit, version, seed=-1):
        unit_path = out/(name+'.inf')
        unit_path.write_text(unit)
        dest = out/(name+'-z'+str(version))
        result = subprocess.run([sys.executable, str(work/'build_story.py'), '--unit', str(unit_path), '--out', str(dest), '--trace', '--seed', str(seed), '--version', str(version)], env=env, capture_output=True, text=True, check=True)
        (dest/'compile.log').write_text(result.stdout + result.stderr)
        return dest/f'robots-trace.z{version}'
    def run(story, commands, label):
        result = subprocess.run([a.dfrotz, '-q', '-m', '-w', '200', '-Z', '3', str(story)], input='\n'.join(commands)+'\n', text=True, capture_output=True, timeout=180, check=True, cwd=out)
        assert 'Unsupported native instruction' not in result.stdout
        (out/(label+'.log')).write_text(result.stdout + result.stderr)
        return result.stdout
    report = {'variant': a.variant, 'artifact_states': 256, 'exact_native_room_boundaries': True, 'artifact_ram_bytes': 65536, 'runtime_ram_bytes': 61440,
              'runtime_excluded_io_range': '$D000-$DFFF', 'registers': list(REGISTERS)+['pc'], 'formats': []}
    for version in (5, 8):
        story = build('all-startups', STARTUP, version)
        output = run(story, [], f'all-startups-z{version}')
        chunks = re.split(r'TEST_BEGIN:\s*(\d+)\s*', output)[1:]
        assert len(chunks) == 512, (version, 'startup count', len(chunks))
        for index in range(0, len(chunks), 2):
            seed, chunk = int(chunks[index]), chunks[index+1]
            assert seed == index//2
            dumps = snapshots(chunk)
            assert len(dumps) == 1
            check(dumps[0], expected[seed][0], (version, seed, 'startup'))
            emitted = bytes.fromhex(''.join(chunk.split('TEST_RAM:')[0].split()))
            assert emitted == expected[seed][1], (version, seed, 'startup text')
        sessions = []
        for seed in (0, 255):
            story = build(f'session-{seed}', SESSION, version, seed)
            # A fresh filename per run avoids overwrite prompts on repeated tests.
            import tempfile
            with tempfile.TemporaryDirectory(prefix='saves-', dir=out) as temporary:
                save = str((Path(temporary)/'checkpoint.qzl').relative_to(out))
                commands = ['look', 'inventory', 'save', save, 'west', 'look', 'restore', save, 'west', 'look', 'restart', 'look', 'inventory', 'quit']
                output = run(story, commands, f'session-{seed}-z{version}')
                assert 'Saved.' in output and 'Restored.' in output
                assert 'Save failed.' not in output and 'Restore failed.' not in output
                assert (out/save).is_file(), 'Interpreter did not create save'
                dumps = snapshots(output)
                assert len(dumps) == 10, (version, seed, 'session dump count', len(dumps))
                check(dumps[0], expected[seed][0], (version, seed, 'BootCase'))
                for left, right in ((3, 5), (4, 6), (0, 7), (1, 8), (2, 9)):
                    check(dumps[right], dumps[left], (version, seed, 'save/restart', left, right))
                # Restore in a new interpreter, proving the file is persistent.
                fresh = run(story, ['restore', save, 'west', 'look', 'quit'], f'fresh-restore-{seed}-z{version}')
                assert 'Restored.' in fresh and 'Restore failed.' not in fresh
                restored = snapshots(fresh)
                assert len(restored) == 3
                check(restored[1], dumps[3], (version, seed, 'fresh restore west'))
                check(restored[2], dumps[4], (version, seed, 'fresh restore look'))
            sessions.append({'seed': seed, 'same_process_restore': True, 'new_process_restore': True, 'restart': True, 'exact_state_comparisons': 8})
        report['formats'].append({'version': version, 'startup_states': 256, 'exact_startup_text': True, 'sessions': sessions})
        print(f'Z{version}: 256 full modeled-RAM/register/text startups; save/restore/restart seeds 0 and 255 passed.', flush=True)
    report['passed'] = True
    (out/'results.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Passed 256 fresh native artifact checks, 512 Z-machine startup checks, and 32 save/restart state comparisons.')


if __name__ == '__main__':
    main()
