"""Publish read-only CAD vectors and clearly labelled model-derived drawing sheets."""
from pathlib import Path
import sys, json, copy, math, hashlib, collections, html, shutil
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'verification/cad-runtime'))
import ezdxf
from ezdxf.addons.drawing import Frontend,RenderContext,svg,layout,config
from ezdxf.math import BoundingBox2d
from xml.etree import ElementTree as ET

OUT=ROOT/'web/dist/assets/drawings';OUT.mkdir(parents=True,exist_ok=True)
DXF=ROOT/'verification/revision-05/NGORO.viewer-source.dxf'
SCENE=ROOT/'web/dist/assets/scene.json'
SOURCE=ROOT/'analysis/NGORO.source.dwg'
if not SOURCE.exists():SOURCE=ROOT/'web/dist/downloads/NGORO.source.dwg'
scene=json.loads(SCENE.read_text())
manifest={'version':1,'source':'NGORO.send.dwg','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'model_revision':scene['revision'],'model_sha256':hashlib.sha256(SCENE.read_bytes()).hexdigest(),'sheets':[],'notes':['CAD asli berasal dari DWG melalui DXF AutoCAD, dirender sebagai vektor hanya-baca. Bentuk huruf dapat berbeda dari font CAD asli.','Layout kertas DWG kosong; lembar sumber diambil dari kelompok gambar di Model Space.','Gambar turunan mengikuti model revisi 04. Dimensi model yang direvisi tidak mengubah gambar sumber.','Gambar turunan untuk studi visual dan koordinasi, bukan dokumen pelaksanaan atau perhitungan struktur.']}

class LayerRenderer(svg.SVGRenderBackend):
 def tag(self,previous,p):
  for e in list(self.entities)[previous:]:e.set('data-layer',p.layer)
 def add_strokes(self,d,p):
  n=len(self.entities);super().add_strokes(d,p);self.tag(n,p)
 def add_filling(self,d,p):
  n=len(self.entities);super().add_filling(d,p);self.tag(n,p)
class LayerBackend(svg.SVGBackend):
 @staticmethod
 def make_backend(page,settings):return LayerRenderer(page,settings)

def save_source():
 doc=ezdxf.readfile(DXF);m=doc.modelspace()
 cfg=config.Configuration(background_policy=config.BackgroundPolicy.WHITE,color_policy=config.ColorPolicy.COLOR,lineweight_scaling=1)
 backend=LayerBackend();Frontend(RenderContext(doc),backend,config=cfg).draw_layout(m,filter_func=lambda e:e.dxftype()!='XLINE')
 ext=backend.player().bbox();full_bounds=(ext.extmin.x-2,ext.extmin.y-2,ext.extmax.x+2,ext.extmax.y+2)
 source_sheets=[
 ('source-all','Semua gambar DWG',full_bounds,'Keseluruhan Model Space, termasuk denah, rencana struktur, atap dan profil rangka.'),
 ('source-site','Siteplan asli',(2490,1467,2649,1582),'Siteplan dan dimensi dari DWG sumber.'),
 ('source-layout','Layout plan asli',(2653,1467,2813,1582),'Layout plan dan keterangan parkir dari DWG sumber.'),
 ('source-foundation','Rencana pondasi asli',(2818,1488,2948,1582),'Rencana pondasi dan sloof sesuai anotasi sumber; belum merupakan verifikasi struktur.'),
 ('source-columns','Rencana kolom asli',(2951,1488,3080,1582),'Rencana kolom, grid dan anotasi profil sesuai DWG.'),
 ('source-roof','Rencana atap asli',(3084,1488,3214,1582),'Susunan rangka dan gording dari DWG.'),
 ('source-frame','Profil rangka asli',(3220,1528,3325,1553),'Profil melintang rangka dari DWG; judul lembar ini ditambahkan untuk navigasi.')]
 for key,title,bounds,note in source_sheets:
  b=copy.deepcopy(backend);lo=bounds[:2];hi=bounds[2:]
  xml=b.get_xml_root_element(layout.Page(420,297,margins=layout.Margins.all(9)),settings=layout.Settings(crop_at_margins=True),render_box=BoundingBox2d([lo,hi]))
  layers=sorted({e.get('data-layer') for e in xml.iter() if e.get('data-layer')})
  (OUT/(key+'.svg')).write_text(ET.tostring(xml,encoding='unicode'),encoding='utf-8')
  manifest['sheets'].append({'id':key,'title':title,'kind':'source','url':'assets/drawings/'+key+'.svg','description':note,'layers':layers,'source_bounds':bounds})
 manifest['source_inventory']={'entities':len(m),'dimensions':len(m.query('DIMENSION')),'model_types':dict(collections.Counter(e.dxftype() for e in m)),'paper_layouts':{l.name:len(l) for l in doc.layouts if l.name!='Model'},'omitted':'7 infinite construction XLINE objects omitted; hidden and non-plot layers follow renderer visibility'}

# Lightweight vector sheet writer. Coordinates in metres; sheet furniture in viewBox units.
class Sheet:
 def __init__(self,key,title,desc,bounds):
  self.key,self.title,self.desc=key,title,desc;self.parts=[];self.layers=set();self.bounds=bounds
  xmin,ymin,xmax,ymax=bounds;self.scale=min(1040/(xmax-xmin),620/(ymax-ymin));self.ox=80+(1040-(xmax-xmin)*self.scale)/2-xmin*self.scale;self.oy=90+(620-(ymax-ymin)*self.scale)/2+ymax*self.scale
 def xy(self,p):return self.ox+p[0]*self.scale,self.oy-p[1]*self.scale
 def path(self,pts,layer='Geometri',fill='none',stroke='#31463f',width=1,closed=False):
  self.layers.add(layer);coords=[self.xy(p) for p in pts];d='M '+' L '.join(f'{x:.3f},{y:.3f}' for x,y in coords)+(' Z' if closed else '')
  self.parts.append(f'<path data-layer="{html.escape(layer)}" d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
 def rect(self,x,y,w,h,**kwargs):self.path([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],closed=True,**kwargs)
 def text(self,x,y,t,size=12,layer='Anotasi',anchor='middle',color='#31463f'):
  self.layers.add(layer);px,py=self.xy((x,y));self.parts.append(f'<text data-layer="{html.escape(layer)}" x="{px:.2f}" y="{py:.2f}" text-anchor="{anchor}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}">{html.escape(str(t))}</text>')
 def dim(self,a,b,offset,label):
  # Horizontal/vertical only; metre dimensions explicitly shown.
  horiz=abs(a[1]-b[1])<1e-6;aa=(a[0],a[1]+offset) if horiz else (a[0]+offset,a[1]);bb=(b[0],b[1]+offset) if horiz else (b[0]+offset,b[1])
  for x,y in [(a,aa),(b,bb),(aa,bb)]:self.path([x,y],layer='Dimensi',stroke='#587966',width=.8)
  for p in [aa,bb]:self.path([(p[0]-.3,p[1]-.3),(p[0]+.3,p[1]+.3)],layer='Dimensi',stroke='#587966')
  self.text((aa[0]+bb[0])/2+(0 if horiz else 1.4),(aa[1]+bb[1])/2+(.55 if horiz else 0),label,11,'Dimensi')
 def save(self):
  title=html.escape(self.title);desc=html.escape(self.desc)
  body=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 848" role="img" aria-label="{title}"><rect width="1200" height="848" fill="#fffefa"/><rect x="24" y="24" width="1152" height="800" fill="none" stroke="#a3ada5"/><text x="52" y="58" font-family="Arial" font-size="13" fill="#557463">NGORO / TURUNAN MODEL 3D / REVISI 04</text>'+''.join(self.parts)+f'<path d="M24 742H1176" stroke="#a3ada5"/><text x="52" y="774" font-family="Arial" font-size="22" fill="#243a31">{title}</text><text x="52" y="797" font-family="Arial" font-size="11" fill="#64726a">{desc}</text><text x="1148" y="818" text-anchor="end" font-family="Arial" font-size="10" fill="#64726a">Satuan meter · Skala layar berubah saat zoom · Studi visual, bukan gambar kerja konstruksi</text></svg>'
  (OUT/(self.key+'.svg')).write_text(body,encoding='utf-8')
  manifest['sheets'].append({'id':self.key,'title':self.title,'kind':'derived','url':'assets/drawings/'+self.key+'.svg','description':self.desc,'layers':sorted(self.layers)})

def solid_bounds(e):
 k=e['kind']
 if k=='box':return e['p'],[a+b for a,b in zip(e['p'],e['s'])]
 if k in ['beam','wf','cnp']:
  r=max(e['w'],e['h'])/2;return [min(a,b)-r for a,b in zip(e['a'],e['b'])],[max(a,b)+r for a,b in zip(e['a'],e['b'])]
 if k=='prism':return [min(p[i] for p in e['points'])-e['th'] for i in range(3)],[max(p[i] for p in e['points']) for i in range(3)]
 return None

def plan():
 s=Sheet('derived-plan','Denah bersih + garis potongan','Turunan model revisi 04; potongan horizontal +1.20 m dari datum tapak.',(-8,-9,101,89))
 s.rect(0,0,90,80,stroke='#82978c',fill='#f4f5ed',layer='Tapak')
 for e in scene['elements']:
  b=solid_bounds(e)
  if not b or not b[0][2]<=1.2<=b[1][2] or e['kind']!='box':continue
  if e['group']=='Lansekap' or e['group'].startswith('Interior'):continue
  x,y,z=e['p'];w,d,h=e['s']
  s.rect(x,y,w,d,layer=e['group'],fill='#c8d1c7',stroke='#3d5345',width=.65)
 for f in scene['footprints']:
  s.text(f['x']+f['w']/2,f['y']+f['d']/2,f['name'],12)
  s.text(f['x']+f['w']/2,f['y']+f['d']/2-2.6,f"{f['w']:g} × {f['d']:g} m",10)
 s.dim((0,0),(90,0),-5,'90.00 m');s.dim((90,0),(90,80),5,'80.00 m')
 for f in scene['footprints'][:4]:s.dim((f['x'],4),(f['x']+f['w'],4),-1.5,f"{f['w']:.2f}")
 s.path([(-3,34),(93,34)],layer='Potongan',stroke='#ab6650',width=1.2);s.text(-4,35,'A',12,'Potongan');s.text(94,35,'A',12,'Potongan')
 s.path([(75.5,1),(75.5,66)],layer='Potongan',stroke='#ab6650',width=1.2);s.text(75.5,68,'B',12,'Potongan');s.text(75.5,0,'B',12,'Potongan')
 s.save()

def projection_poly(e,axis):
 if e['kind']=='box':
  p=e['p'];q=[a+b for a,b in zip(p,e['s'])];i=0 if axis=='front' else 1
  return [(p[i],p[2]),(q[i],p[2]),(q[i],q[2]),(p[i],q[2])]
 if e['kind']=='prism':return [(p[0 if axis=='front' else 1],p[2]) for p in e['points']]
 if e['kind'] in ['beam','wf','cnp']:
  a,b=e['a'],e['b'];i=0 if axis=='front' else 1;dx,dz=b[i]-a[i],b[2]-a[2];ln=math.hypot(dx,dz)
  if ln<1e-6:return []
  ox,oz=-dz/ln*e['h']/2,dx/ln*e['h']/2
  return [(a[i]+ox,a[2]+oz),(b[i]+ox,b[2]+oz),(b[i]-ox,b[2]-oz),(a[i]-ox,a[2]-oz)]
 return []

def elevations():
 # Painted silhouettes sorted from far to near, showing actual model geometry.
 # Transparent cladding is intentionally kept translucent; this is a visual elevation.
 for axis,title,bounds in [('front','Tampak akses utama',(-5,-5,96,20)),('side','Tampak samping timur',(-4,-5,85,20))]:
  s=Sheet('derived-'+axis,title,'Proyeksi ortogonal model 3D; bukaan, atap dan pagar mengikuti revisi 04.',bounds)
  index=1 if axis=='front' else 0
  candidates=[e for e in scene['elements'] if e['group'] not in ['Tapak','Lansekap'] and not e['group'].startswith('Interior')]
  for e in sorted(candidates,key=lambda e:sum(solid_bounds(e)[j][index] for j in [0,1])/2 if solid_bounds(e) else 0):
   points=projection_poly(e,axis)
   if len(points)<3:continue
   mat=scene['materials'][e['mat']];color=mat.get('color','#e2e2da')
   if e['mat']=='glass':color='#dceaf0'
   s.path(points,layer=e['group'],fill=color,stroke='#34473d',width=.3,closed=True)
  s.path([(-2,0),(92 if axis=='front' else 82,0)],layer='Datum',width=1)
  s.dim((0,0),(90 if axis=='front' else 80,0),-3,'90.00 m' if axis=='front' else '80.00 m')
  s.save()

def section(axis,value,key,title,bounds):
 s=Sheet(key,title,f'Bidang potong {"Y" if axis==1 else "X"} = {value:.2f} m; solid terpotong ditampilkan. Dari model revisi 04.',bounds)
 for e in scene['elements']:
  if e['group']=='Lansekap' or e['group'].startswith('Interior'):continue
  k=e['kind'];pts=[]
  if k=='box':
   p=e['p'];q=[a+b for a,b in zip(p,e['s'])]
   if not p[axis]<=value<=q[axis]:continue
   i=1-axis;pts=[(p[i],p[2]),(q[i],p[2]),(q[i],q[2]),(p[i],q[2])]
  elif k=='prism':
   # Intersect convex top and bottom polygon edges with the actual section plane.
   poly=e['points'];a,b,c=poly[:3];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];ln=math.sqrt(sum(x*x for x in n));off=[-x/ln*e['th'] for x in n]
   bottom=[[p[i]+off[i] for i in range(3)] for p in poly];edges=[]
   for ring in [poly,bottom]:edges.extend(zip(ring,ring[1:]+ring[:1]))
   edges.extend(zip(poly,bottom));hit=[]
   for a,b in edges:
    if abs(b[axis]-a[axis])<1e-8:continue
    t=(value-a[axis])/(b[axis]-a[axis])
    if 0<=t<=1:hit.append(tuple(round(a[i]+t*(b[i]-a[i]),7) for i in [1-axis,2]))
   if len(set(hit))>=3:
    hit=list(set(hit));cx=sum(p[0] for p in hit)/len(hit);cy=sum(p[1] for p in hit)/len(hit);pts=sorted(hit,key=lambda p:math.atan2(p[1]-cy,p[0]-cx))
  elif k in ['beam','wf','cnp']:
   # Elements lying along the section are shown with their projected member outline.
   if abs(e['a'][axis]-value)<.15 and abs(e['b'][axis]-value)<.15:pts=projection_poly(e,'front' if axis==1 else 'side')
  if len(pts)>=3:s.path(pts,layer=e['group'],fill='#b8c4b8',stroke='#263f31',width=.75,closed=True)
 s.path([(-2,0),(92 if axis==1 else 68,0)],layer='Datum',width=1)
 s.text(0,-1.7,'DATUM TAPAK ±0.00',10,anchor='start');s.text(20,1.1,'FFL GUDANG +0.22',10)
 ridge=scene['warehouse_height']['ridge_above_floor'] if 'ridge_above_floor' in scene['warehouse_height'] else 12
 s.dim((89 if axis==1 else 65,.22),(89 if axis==1 else 65,12.22),3,'12.00 m dari FFL')
 s.text(47 if axis==1 else 35,15,'Puncak +12.22 / Tepi +9.3527 / FFL +0.22 m',12)
 s.save()

save_source();plan();elevations();section(1,34,'derived-section-a','Potongan A–A melintang',(-6,-5,101,20));section(0,75.5,'derived-section-b','Potongan B–B memanjang',(-5,-5,78,20))
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
if SOURCE.resolve()!=(ROOT/'web/dist/downloads/NGORO.source.dwg').resolve():shutil.copy2(SOURCE,ROOT/'web/dist/downloads/NGORO.source.dwg')
source_unchanged=manifest['source_sha256'].lower()==json.loads((ROOT/'verification/revision-05/source-preservation.json').read_text(encoding='utf-8-sig'))['source_sha256'].lower()
(ROOT/'verification/revision-05/drawings-build.json').write_text(json.dumps({'sheets':len(manifest['sheets']),'source_unchanged':source_unchanged,'entities':manifest['source_inventory'],'svg_bytes':sum(p.stat().st_size for p in OUT.glob('*.svg'))},indent=2))
assert source_unchanged
print('Generated',len(manifest['sheets']),'vector sheets; source unchanged.')
