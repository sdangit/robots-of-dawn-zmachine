#!/usr/bin/env python3
"""Hash-check user-owned inputs and generate private build products."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def verified(path, expected):
    path = path.expanduser().resolve(strict=True)
    data = path.read_bytes()
    if len(data) != expected['bytes'] or hashlib.sha256(data).hexdigest() != expected['sha256']:
        raise ValueError(f"Unsupported disk image: {path}. See disk-hashes.json; no build was started.")
    return path

def input_paths(c64, apple, hashes):
    paths = {'c64': verified(c64, hashes['c64'])}
    if apple is not None:
        paths['apple2'] = verified(apple, hashes['apple2'])
    return paths

def input_environment(paths, base=None):
    env = dict(os.environ if base is None else base)
    env['ROBOTS_C64_DISK'] = str(paths['c64'])
    # An inherited setting must not silently opt into the comparison.
    env.pop('ROBOTS_APPLE_DISK', None)
    if 'apple2' in paths:
        env['ROBOTS_APPLE_DISK'] = str(paths['apple2'])
    return env

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--c64', type=Path, required=True)
    p.add_argument('--apple2', type=Path, help='Optional hash-checked Apple II dictionary comparison input')
    p.add_argument('--inform6', default=os.environ.get('INFORM6', 'inform6'))
    p.add_argument('--version', choices=('5','8','both'), default='both')
    a = p.parse_args()
    a.variant = "faithful"
    hashes = json.loads((ROOT/'disk-hashes.json').read_text())
    paths = input_paths(a.c64, a.apple2, hashes)
    compiler = shutil.which(a.inform6)
    if not compiler:
        p.error('Inform 6 compiler not found. Supply --inform6 /absolute/path/to/inform6; see docs/BUILD.md.')
    work = ROOT/'build'/a.variant/'work'
    # Refresh handwritten sources only. Generated files stay in ignored build/.
    work.mkdir(parents=True,exist_ok=True)
    for name in ('extract.py','prepare_startup.py','cpu.py','reference.py','mos6502.py','build_story.py','runtime.inf'):
        shutil.copy2(ROOT/'src'/name,work/name)
    env = input_environment(paths)
    env.update(INFORM6=str(Path(compiler).resolve()), PYTHONDONTWRITEBYTECODE='1')
    def run(script, *args):
        subprocess.run([sys.executable,str(work/script),*map(str,args)],env=env,check=True)
    run('extract.py')
    run('prepare_startup.py')
    outputs=[]
    for version in ('5','8') if a.version == 'both' else (a.version,):
        out = ROOT/'build'/a.variant/f'z{version}'
        run('build_story.py','--out',out,'--version',version)
        story=out/f'robots.z{version}'
        outputs.append(dict(path=str(story.relative_to(ROOT)), bytes=story.stat().st_size, sha256=hashlib.sha256(story.read_bytes()).hexdigest()))
    report=dict(variant=a.variant, compiler=compiler, inputs={key: hashes[key] for key in paths}, apple_comparison='not performed; identity checked only' if 'apple2' in paths else 'skipped', outputs=outputs)
    (ROOT/'build'/a.variant/'build-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
