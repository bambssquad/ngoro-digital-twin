"""Verify revision 06 without pretending static checks are browser/GPU tests."""
from pathlib import Path
from xml.etree import ElementTree as ET
import hashlib, json, subprocess

root = Path(__file__).resolve().parents[1]
baseline = '2547e71ab06a16c35e3324de9a75ced9a53fcb33'
def git(*args):
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()

protected = ['web/dist/assets', 'web/dist/downloads', 'web/dist/experience.js',
             'web/dist/navigation.js', 'web/dist/drawings.js', 'web/dist/drawings.css']
files = git('ls-tree', '-r', '--name-only', baseline, '--', *protected).splitlines()
assert files, 'No protected model assets found'
for name in files:
    assert git('hash-object', name) == git('rev-parse', baseline + ':' + name), name

manifest=json.loads((root/'web/dist/assets/drawings/manifest.json').read_text())
assert len(manifest['sheets']) == 12
assert sum(s['kind']=='source' for s in manifest['sheets']) == 7
assert manifest['model_sha256'] == hashlib.sha256((root/'web/dist/assets/scene.json').read_bytes()).hexdigest()
assert manifest['source_sha256'] == hashlib.sha256((root/'web/dist/downloads/NGORO.source.dwg').read_bytes()).hexdigest()
for sheet in manifest['sheets']:
    svg = ET.parse(root/'web/dist'/sheet['url']).getroot()
    assert svg.tag.endswith('svg') and len(svg.attrib['viewBox'].split()) == 4
    assert {e.get('data-layer') for e in svg.iter() if e.get('data-layer')} == set(sheet['layers'])

for name in ['app.js','diorama.js','experience.js','navigation.js','drawings.js']:
    subprocess.run(['node','--check',str(root/'web/dist'/name)],check=True)
subprocess.run(['node','--test',str(root/'scripts/test-diorama.mjs')],check=True)
print(f'PASS: {len(files)} protected files byte-identical; 12 SVG sheets; 5 JavaScript syntax checks; diorama tests.')
print('Browser/GPU appearance and physical-device performance require separate verification.')
