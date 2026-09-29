import json,urllib.request,zipfile,io,concurrent.futures,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RES='1K' if '--1k' in sys.argv else '2K'
OUT=ROOT/('web/dist/assets/textures-1k' if RES=='1K' else 'web/dist/assets/textures');OUT.mkdir(parents=True,exist_ok=True)
data=json.loads((ROOT/'analysis/materials-api.json').read_text())
def fetch(a):
 aid=a['assetId']; dl=next(x for x in a['downloadFolders']['default']['downloadFiletypeCategories']['zip']['downloads'] if x['attribute']==RES+'-JPG')
 req=urllib.request.Request(dl['downloadLink'],headers={'User-Agent':'NGORO Visualization/1.0'})
 z=zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(req,timeout=90).read()))
 files={}
 for n in z.namelist():
  for kind in ['Color','NormalGL','Roughness']:
   if n.endswith('_'+kind+'.jpg'):
    target=OUT/(aid+'_'+kind+'.jpg');target.write_bytes(z.read(n));files[kind]=target.name
 return {'id':aid,'source':a['shortLink'],'license':'CC0','size_m':[a.get('dimensionX',200)/100,a.get('dimensionY',200)/100],'maps':files}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: result=list(pool.map(fetch,data['foundAssets']))
(ROOT/'web/dist/assets/material-sources.json').write_text(json.dumps(result,indent=2))
print('Downloaded',len(result),RES,'PBR materials;',sum(p.stat().st_size for p in OUT.iterdir()),'bytes')
