from pathlib import Path
import importlib.util,sys,subprocess,tempfile,types
r=Path(r'F:\Temp\iphone17-v30-topology-rebuild');e=Path(r'F:\Temp\iphone17-ticket140-continuation')
sys.path.insert(0,str(r/'tools'))
b=r'D:\Blender Foundation\Blender 5.2\blender.exe'
class ExportReached(Exception):pass
def check(source,label):
 m=types.ModuleType('build_'+label);m.__file__=str(r/'tools/build_iphone17_v30.py');exec(compile(source,m.__file__,'exec'),m.__dict__)
 seen=[]
 with tempfile.TemporaryDirectory(prefix='ticket140-failure-',dir=e) as tmp:
  device=Path(tmp);(device/'generate_low_v30.py').write_text("raise RuntimeError('TICKET140_INTENTIONAL_GENERATOR_FAILURE')\n")
  m.DEVICE=device;m.RUNTIME=device/'runtime/v30'
  original=m.run
  def guarded(*args):
   seen.append([str(x) for x in args])
   if len(seen)>1:raise ExportReached('export attempted after failed generator')
   original(*args)
  m.run=guarded
  old=sys.argv;sys.argv=['build_iphone17_v30.py','--blender',b,'--skip-previews']
  try:m.main();outcome='unexpected success'
  except subprocess.CalledProcessError as exc:outcome='generator-stopped-'+str(exc.returncode)
  except ExportReached:outcome='export-reached'
  finally:sys.argv=old
 print(label,outcome,'stages',len(seen),flush=True)
 return outcome,len(seen)
baseline=subprocess.check_output(['git','show','a8ad3a2:tools/build_iphone17_v30.py'],cwd=r,text=True)
assert check(baseline,'RED')==('export-reached',2)
assert check((r/'tools/build_iphone17_v30.py').read_text(),'GREEN')==('generator-stopped-7',1)
print('BUILD_FAILURE_REGRESSION_GREEN: actual Blender failure stops before export/package; no production writes')
