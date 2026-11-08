import importlib.util
from pathlib import Path
import tempfile
import unittest
import hashlib
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
def module(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
build=module('build');audit=module('audit_publication')
class SafetyTests(unittest.TestCase):
 def test_hash_and_size(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'disk';p.write_bytes(b'fixture');expected={'bytes':7,'sha256':hashlib.sha256(b'fixture').hexdigest()}
   self.assertEqual(build.verified(p,expected),p.resolve())
   with self.assertRaises(ValueError):build.verified(p,dict(expected,bytes=8))
   p.write_bytes(b'changed')
   with self.assertRaises(ValueError):build.verified(p,expected)
 def test_publication_rejections(self):
  for name,data in [('src/disk.D64',b'abc'),('src/robots.inf',b'Array ram -> 1 2;'),('src/out/data.json',b'{}'),('build/output',b'data'),('src/memory.txt',b'a\0b')]:
   self.assertTrue(audit.check(name,data),name)
 def test_license_is_allowed(self):
  self.assertEqual(audit.check('LICENSE',(ROOT/'LICENSE').read_bytes()),[])
 def test_handwritten_source(self):
  self.assertEqual(audit.check('src/runtime.inf',b'[ Main; ];'),[])
 def test_optional_input_and_environment(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'c64';p.write_bytes(b'fixture')
   expected={'bytes':7,'sha256':hashlib.sha256(b'fixture').hexdigest()}
   hashes={'c64':expected,'apple2':expected}
   paths=build.input_paths(p,None,hashes)
   self.assertEqual(set(paths),{'c64'})
   self.assertNotIn('ROBOTS_APPLE_DISK',build.input_environment(paths,{'ROBOTS_APPLE_DISK':'stale'}))
   self.assertEqual(set(build.input_paths(p,p,hashes)),{'c64','apple2'})
   bad=Path(d)/'bad';bad.write_bytes(b'changed')
   with self.assertRaises(ValueError):build.input_paths(p,bad,hashes)
 def test_generated_artifacts_rejected(self):
  for name in ('src/startup.json','src/extraction.json','src/fasttext.inf','src/rooms.json','src/model.py'):
   self.assertTrue(audit.check(name,b'{}'),name)
 def test_source_stages_refuse_direct_execution(self):
  for name in ('extract.py','prepare_startup.py','build_story.py'):
   result=subprocess.run([sys.executable,str(ROOT/'src'/name)],capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0,name)
   self.assertIn('Run scripts/build.py',result.stderr,name)
 def test_history_is_checked(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);subprocess.run(['git','init','-q',str(root)],check=True)
   (root/'src').mkdir();p=root/'src/startup.json';p.write_text('{}')
   subprocess.run(['git','add','.'],cwd=root,check=True)
   subprocess.run(['git','-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','fixture'],cwd=root,check=True)
   subprocess.run(['git','rm','-q','src/startup.json'],cwd=root,check=True)
   subprocess.run(['git','-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','remove'],cwd=root,check=True)
   self.assertTrue(any('(history ' in issue for issue in audit.audit_repo(root)[1]))
 def test_staged_payload_is_checked(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);subprocess.run(['git','init','-q',str(root)],check=True)
   (root/'src').mkdir();p=root/'src/data.txt';p.write_bytes(b'game\0payload')
   subprocess.run(['git','add','src/data.txt'],cwd=root,check=True)
   p.write_text('clean worktree')
   self.assertTrue(any('(index)' in x for x in audit.audit_repo(root)[1]))
   p.unlink()
   self.assertTrue(any('(index)' in x for x in audit.audit_repo(root)[1]))
if __name__=='__main__':unittest.main()
