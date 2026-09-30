from pathlib import Path
import json,hashlib,re,subprocess,urllib.request
from xml.etree import ElementTree as ET
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'web/dist/assets/drawings/manifest.json').read_text(encoding='utf-8'))
assert len(manifest['sheets'])==12
assert sum(s['kind']=='source' for s in manifest['sheets'])==7
assert manifest['source_inventory']['entities']==5053
assert manifest['source_inventory']['dimensions']==204
source=root/'analysis/NGORO.source.dwg'
if not source.exists():source=root/'web/dist/downloads/NGORO.source.dwg'
assert manifest['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
assert manifest['model_sha256']==hashlib.sha256((root/'web/dist/assets/scene.json').read_bytes()).hexdigest()
checks=[]
for s in manifest['sheets']:
 p=root/'web/dist'/s['url'];tree=ET.parse(p);r=tree.getroot()
 assert r.tag.endswith('svg') and len(r.attrib['viewBox'].split())==4
 layers={e.get('data-layer') for e in r.iter() if e.get('data-layer')}
 assert layers==set(s['layers']),s['id']
 assert len(layers)>0
 for e in r.iter():
  assert not e.tag.endswith(('script','foreignObject'))
  assert all(not k.lower().startswith('on') for k in e.attrib)
 checks.append({'id':s['id'],'bytes':p.stat().st_size,'layers':len(layers),'passed':True})
for f in ['app.js','drawings.js']:subprocess.run(['node','--check',str(root/'web/dist'/f)],check=True,capture_output=True)
baseline=root/'verification/revision-05/app-before.js'
before=baseline.read_bytes() if baseline.exists() else urllib.request.urlopen('https://raw.githubusercontent.com/bambssquad/ngoro-digital-twin/322c2a67a7661d6544a1a5c8660c2756f038a230/web/dist/app.js').read()
after=(root/'web/dist/app.js').read_bytes()
assert after==before.replace(b'previous=now;if(transition',b'previous=now;if(state.drawingMode){last=now;frames=0;return;}if(transition',1)
browser=json.loads((root/'verification/revision-05/browser-tests.json').read_text())
assert all(s['ready'] and not s['errors'] for s in browser['sheets'])
assert browser['interaction']['mobile']['result']['value']['overflow']==False
assert browser['interaction']['mobile']['result']['value']['pinchAfter']>1.49
assert browser['interaction']['layersOff']['result']['value']['visible']==0
files=['web/dist/index.html','web/dist/app.js','web/dist/drawings.js','web/dist/drawings.css','web/dist/downloads/NGORO.source.dwg','README.md','docs/cad-viewer.md','scripts/build_drawing_viewer.py','scripts/export_cad_source.ps1','scripts/verify_drawings.py']
files += [str(p.relative_to(root)).replace('\\','/') for p in (root/'web/dist/assets/drawings').glob('*')]
files += ['verification/revision-05/'+p for p in ['browser-tests.json','drawings-build.json','unchanged-3d.json','source-preservation.json']]
report={'passed':True,'sheets':checks,'source_unchanged':True,'model_unchanged':True,'app_change':'Only pause hidden Three.js rendering and reset FPS measurement during CAD mode','browser_passed':True}
(root/'verification/revision-05/verification.json').write_text(json.dumps(report,indent=2))
files.append('verification/revision-05/verification.json')
payload=[]
for name in files:
 b=(root/name).read_bytes()
 if name.endswith(('.js','.py','.ps1','.md','.json','.html','.css')):assert not re.search(rb'apikey_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}',b),name
 payload.append({'path':name,'size':len(b),'sha':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()})
(root/'verification/revision-05/upload-manifest.json').write_text(json.dumps(payload,indent=2))
print('PASS:',len(checks),'sheets; source/model unchanged; browser checks; selected',len(payload),'files for publication.')

