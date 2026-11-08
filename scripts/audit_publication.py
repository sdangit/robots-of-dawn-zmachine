#!/usr/bin/env python3
"""Check Git's publishable files for accidental binary/generated content."""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
ALLOWED_ROOT={'.gitignore','.gitattributes','README.md','LICENSE','NOTICE.md','disk-hashes.json','Makefile'}
ALLOWED_DIR={'docs','scripts','src','tests'}
FORBIDDEN_SUFFIX={'.d64','.do','.prg','.bin','.z5','.z8','.qzl','.sav','.zip','.gz','.pdf','.jpg','.png'}

def check(path,data):
    p=Path(path)
    problems=[]
    if p.parts[0]=='src' and (len(p.parts)!=2 or p.name not in {'extract.py','prepare_startup.py','cpu.py','reference.py','mos6502.py','build_story.py','runtime.inf','prepare_labels.py'}): problems.append('source file is not on the reviewed allowlist')
    if p.suffix=='.json' and path!='disk-hashes.json': problems.append('generated or unreviewed JSON')
    if len(p.parts)==1 and p.name not in ALLOWED_ROOT:problems.append('unreviewed root file')
    if len(p.parts)>1 and p.parts[0] not in ALLOWED_DIR:problems.append('unreviewed top-level directory')
    if p.suffix.lower() in FORBIDDEN_SUFFIX:problems.append('binary/input/archive extension')
    if any(x in ('out','inputs','extracted','__pycache__') for x in p.parts):problems.append('generated/input directory')
    if p.name in ('robots.inf','room_titles.json','fasttext.inf','source-provenance.json'):problems.append('generated game content')
    if b'\0' in data:problems.append('binary content')
    if b'Array ram ->' in data and p.suffix=='.inf':problems.append('embedded game memory')
    return problems

def audit_repo(root):
    errors=[]
    # Inspect actual index blobs, not just current worktree bytes.
    entries=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=root).decode().split('\0')
    for entry in filter(None,entries):
        header,name=entry.split('\t',1)
        mode,oid,stage=header.split()
        if mode not in ('100644','100755'):
            errors.append(f'{name}: unsupported staged mode {mode}')
        data=subprocess.check_output(['git','cat-file','blob',oid],cwd=root)
        for reason in check(name,data):errors.append(f'{name} (index): {reason}')
    files=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=root).decode().split('\0')
    count=0
    for name in sorted(set(filter(None,files))):
        p=root/name
        if p.is_symlink():errors.append(f'{name}: symlink is not publishable');continue
        if not p.exists():continue  # Already checked index if tracked.
        count+=1
        for reason in check(name,p.read_bytes()):errors.append(f'{name}: {reason}')
    # Check all reachable historical blobs as well as current index/worktree.
    refs=subprocess.check_output(['git','rev-list','--all','--objects'],cwd=root,text=True).splitlines()
    for entry in refs:
        fields=entry.split(' ',1)
        if len(fields)!=2: continue
        oid,name=fields
        kind=subprocess.check_output(['git','cat-file','-t',oid],cwd=root,text=True).strip()
        if kind!='blob': continue
        data=subprocess.check_output(['git','cat-file','blob',oid],cwd=root)
        for reason in check(name,data): errors.append(f'{name} (history {oid}): {reason}')
    return count,errors

def main():
    count,errors=audit_repo(ROOT)
    if errors:raise SystemExit('\n'.join(errors))
    print(f'Publication audit passed for {count} tracked/unignored files and staged blobs. Ignored build products are not a release payload.')

if __name__=='__main__':main()
