"""Metre-based authoritative model shared by SketchUp and Three.js.
Source geometry is preserved; missing architectural details are explicit assumptions.
"""
import json,math,random,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];random.seed(27)
M={
 'concrete':dict(color='#b9b8af',texture='Concrete034',roughness=.84,tile=2),
 'floor':dict(color='#c8c9c4',texture='Concrete034',roughness=.55,tile=3),
 'asphalt':dict(color='#6e7477',texture='Asphalt012',roughness=.93,tile=3),
 'plaster':dict(color='#e7e2d7',texture='Concrete034',roughness=.8,tile=2),
 'roof':dict(color='#a8b5b9',texture='Metal032',roughness=.46,metalness=.6,tile=3),
 'steel':dict(color='#586b72',roughness=.45,metalness=.72),
 'trim':dict(color='#273b43',roughness=.38,metalness=.65),
 'blue':dict(color='#426478',roughness=.47,metalness=.4),
 'wood':dict(color='#b99b72',texture='Wood049',roughness=.65,tile=1.5),
 'glass':dict(color='#91b6bf',roughness=.13,metalness=.12,opacity=.34),
 'amber':dict(color='#e4a43a',roughness=.56),
 'white':dict(color='#eeeadc',roughness=.7),
 'rubber':dict(color='#252a2b',roughness=.93),
 'earth':dict(color='#77715d',roughness=1),
 'grass':dict(color='#69765b',roughness=1),
 'leaf':dict(color='#526d45',roughness=.95),
 'leaf2':dict(color='#768559',roughness=.97),
 'bark':dict(color='#77604c',texture='Wood049',roughness=1,tile=1),
 'light':dict(color='#fff4d3',roughness=.2,emissive='#ffe1a0'),
 'red':dict(color='#a74736',roughness=.5),
 'water':dict(color='#496a70',roughness=.16,metalness=.22),
}
E=[];labels=[];openings=[];lights=[]
def add(kind,name,mat,group,**kw):
 e=dict(id=len(E)+1,kind=kind,name=name,mat=mat,group=group,**kw);E.append(e);return e
def box(n,x,y,z,w,d,h,m='concrete',g='Tapak',**kw):
 return add('box',n,m,g,p=[x,y,z],s=[w,d,h],**kw)
def beam(n,a,b,w,h,m='steel',g='Struktur',**kw):
 return add('beam',n,m,g,a=a,b=b,w=w,h=h,**kw)
def cyl(n,x,y,z,r,h,m='steel',g='Tapak',**kw):return add('cylinder',n,m,g,p=[x,y,z],r=r,h=h,**kw)
def poly(n,pts,m,g,th=.08):return add('prism',n,m,g,points=pts,th=th)
def wf(n,a,b,g='Struktur'):
 # Capped I section, nominal WF250 with 125 mm flange; thickness is interpreted.
 add('wf',n,'steel',g,a=a,b=b,w=.125,h=.25,tw=.006,tf=.009)
def cnp(n,a,b,g='Struktur'):
 add('cnp',n,'steel',g,a=a,b=b,w=.05,h=.125,tw=.002,tf=.002)
def wall_y(n,x0,x1,y,z,h,m,g,apertures=[]):
 cursor=x0
 for lo,hi,bot,top in sorted(apertures):
  if lo>cursor:box(n,cursor,y,z,lo-cursor,.18,h,m,g)
  if bot>0:box(n+' sill',lo,y,z,hi-lo,.18,bot,m,g)
  if top<h:box(n+' lintel',lo,y,z+top,hi-lo,.18,h-top,m,g)
  openings.append(dict(name=n,x=lo,y=y,z=z+bot,w=hi-lo,h=top-bot,group=g))
  cursor=hi
 if cursor<x1:box(n,cursor,y,z,x1-cursor,.18,h,m,g)
def window(n,x,y,z,w,h,g):
 box(n+' glass',x,y+.04,z,w,.035,h,'glass',g)
 for xx in [x,x+w-.05,x+w/2-.025]:box(n+' mullion',xx,y,z,.05,.10,h,'trim',g)
 for zz in [z,z+h-.05]:box(n+' frame',x,y,zz,w,.10,.05,'trim',g)
 box(n+' sill',x-.07,y-.07,z-.07,w+.14,.26,.07,'concrete',g)
def table(x,y,z,w,d,g):
 box('Meja',x,y,z+.72,w,d,.05,'wood',g)
 for xx in [x+.06,x+w-.10]:
  for yy in [y+.06,y+d-.10]:box('Kaki meja',xx,yy,z,.04,.04,.72,'trim',g)
def chair(x,y,z,g):
 box('Kursi duduk',x,y,z+.43,.46,.48,.07,'blue',g);box('Sandaran',x,y+.43,z+.49,.46,.06,.45,'blue',g)
 for xx in [x+.03,x+.39]:
  for yy in [y+.03,y+.40]:box('Kaki kursi',xx,yy,z,.035,.035,.43,'trim',g)
def tree(x,y,h=4):
 cyl('Batang pohon',x,y,.1,.13,h*.58,'bark','Lansekap')
 for j in range(5):
  a=j*math.tau/5;cx=x+math.cos(a)*.55;cy=y+math.sin(a)*.55
  add('sphere','Tajuk pohon','leaf' if j%2 else 'leaf2','Lansekap',p=[cx,cy,h*.72+random.random()*.45],s=[1.35,1.25,1.35])
def car(x,y,color='white'):
 g='Kendaraan';box('Body mobil',x,y,.48,1.8,4.3,.64,color,g)
 box('Kabin',x+.13,y+1.02,1.12,1.54,2.22,.60,color,g)
 box('Kaca depan',x+.18,y+1.01,1.22,1.44,.025,.44,'glass',g)
 box('Kaca belakang',x+.18,y+3.23,1.22,1.44,.025,.44,'glass',g)
 for xx in [x-.02,x+1.8]:
  box('Kaca samping',xx,y+1.16,1.24,.02,1.87,.4,'glass',g)
  for yy in [y+.8,y+3.45]:
   beam('Ban mobil',[xx,yy,.43],[xx+(.18 if xx<x else -.18),yy,.43],.64,.64,'rubber',g)
 for xx in [x+.15,x+1.3]:box('Lampu mobil',xx,y-.015,.73,.35,.03,.19,'light',g)
def pallet(x,y,z,g):
 for yy in [y+.06,y+.48,y+.92]:box('Balok palet',x,yy,z,1.2,.09,.11,'wood',g)
 for i in range(6):box('Papan palet',x+i*.20,y,z+.11,.15,1.05,.025,'wood',g)
 box('Muatan karton',x+.06,y+.04,z+.14,1.07,.96,.85,'wood',g)
 for yy in [y+.17,y+.7]:box('Tali muatan',x+.055,yy,z+.14,1.08,.025,.86,'white',g)

# Site from source rectangle 2225, rebased at its southwest corner.
box('Tanah tapak 90 x 80',0,0,-.55,90,80,.5,'earth')
box('Pelataran beton',.15,.15,-.05,89.7,79.7,.15,'concrete')
box('Jalan depan',-12,80.3,-.10,114,12,.10,'asphalt')
for x in range(-10,102,7):box('Marka jalan',x,85.95,.015,3.4,.12,.015,'white')
for x in [0,89.8]:box('Dinding batas samping',x,0,.1,.2,80,2.1,'plaster')
box('Dinding batas belakang',0,0,.1,90,.2,2.1,'plaster')
for x,w in [(0,36),(48,42)]:
 box('Plinth pagar depan',x,79.8,.1,w,.2,.45,'concrete')
 for xx in range(int(x),int(x+w)+1,3):box('Tiang pagar',xx,79.8,.1,.14,.20,2.1,'trim')
 for z in [.85,1.5,2.1]:box('Rel pagar',x,79.84,z,w,.10,.06,'trim')
 for i in range(int(w/.3)):box('Piket pagar',x+i*.3,79.87,.55,.026,.026,1.6,'steel')
for x in [36,46,48]:box('Pilar gerbang',x-.15,79.85,.1,.3,.3,2.5,'plaster')
for x in range(37,46):box('Daun gerbang digeser',x,80,.3,.06,.07,1.8,'trim')
# Landscaping stays outside the source building footprints.
for x in [1.0,88.1]:
 box('Bed tanaman',x,2,.1,.8,75,.22,'grass','Lansekap')
 for y in [8,20,32,44,56,70]:tree(x+.4,y,3.6)
for x in [7,16,56,76]:
 box('Planter depan',x,76.4,.1,1.8,1.8,.3,'concrete','Lansekap');box('Tanah planter',x+.08,76.48,.4,1.64,1.64,.04,'earth','Lansekap');tree(x+.9,77.3,4.2)

# Foundations/steel grid match 6 m bays shown in structural plans.
for x in [3,18,41,64,87]:
 for y in range(4,65,6):
  box('Pondasi plat 1.50',x-.75,y-.75,-1.0,1.5,1.5,.4,'concrete','Pondasi')
  box('Pedestal',x-.23,y-.23,-.6,.46,.46,.82,'concrete','Pondasi')
  box('Baseplate',x-.17,y-.17,.22,.34,.34,.022,'steel','Struktur')
  for dx in [-.12,.12]:
   for dy in [-.12,.12]:cyl('Baut angkur',x+dx,y+dy,.242,.012,.055,'steel','Struktur')
  wf('Kolom WF250',[x,y,.24],[x,y,6.2 if x!=3 else 5.55])
  if y<64:box('Sloof 20x40',x-.10,y,-.25,.2,6,.4,'concrete','Pondasi')
for y in [4,64]:box('Sloof melintang',3,y-.1,-.25,84,.2,.4,'concrete','Pondasi')

for i,x in enumerate([18,41,64]):
 num=3-i;g=f'Gudang {num}';cx=x+11.5;eave=6.2;ridge=eave+11.5*.249328
 labels.append(dict(text=g,p=[cx,64.4,5.6]))
 box('Lantai '+g,x,4,.1,23,60,.12,'floor',g)
 for yy in range(10,64,6):box('Sambungan lantai',x+.15,yy,.222,22.7,.014,.004,'steel',g)
 for xx in [x+7.66,x+15.33]:box('Sambungan lantai',xx,4.1,.222,.014,59.8,.004,'steel',g)
 # Door is a true opening, with the roller shutter parked above it.
 wall_y('Fasad '+g,x,x+23,63.82,.22,5.98,'plaster',g,[(cx-3,cx+3,0,4.8),(x+1.5,x+2.5,0,2.2)])
 wall_y('Belakang '+g,x,x+23,4,.22,5.98,'plaster',g,[(x+4,x+8,4.4,5.5),(x+15,x+19,4.4,5.5)])
 for xx in [x+4,x+15]:window('Jendela belakang',xx,3.98,4.62,4,1.1,g)
 for xx in [cx-3.10,cx+3]:box('Rel pintu rolling',xx,64.04,.22,.10,.15,4.85,'trim',g)
 box('Pintu rolling terangkat',cx-3.03,64.02,5.1,6.06,.26,.62,'blue',g)
 for zz in [5.12+j*.08 for j in range(7)]:box('Bilah pintu',cx-3.03,64.28,zz,6.06,.025,.025,'steel',g)
 box('Daun pintu personel',x+1.51,63.88,.22,.98,.05,2.18,'blue',g)
 box('Gagang pintu',x+2.34,64.04,1.20,.035,.055,.24,'steel',g)
 for yy in [4,63.88]:poly('Dinding segitiga '+g,[[x,yy,eave],[x+23,yy,eave],[cx,yy,ridge]],'plaster',g,.12)
 for xx in [x,x+23] if i==0 else [x+23]:
  box('Dinding pemisah',xx-.09,4,.22,.18,60,5.98,'plaster',g)
 for xx in [x-.55,x+23.55]:
  box('Talang memanjang',xx-.09,3.45,eave-.05,.18,61.1,.18,'trim','Atap')
  for yy in [4,34,64]:cyl('Pipa air hujan',xx,yy,.25,.055,eave-.3,'trim',g)
 # Roofs are panels, with seams following pitch and 1.2 m purlins underneath.
 for side in [0,1]:
  xa,xb=(x-.55,cx) if side==0 else (cx,x+23.55)
  za,zb=(eave-.137,ridge) if side==0 else (ridge,eave-.137)
  poly('Penutup atap '+g,[[xa,3.45,za],[xb,3.45,zb],[xb,64.55,zb],[xa,64.55,za]],'roof','Atap',.055)
  for yy in [3.5+j*.75 for j in range(82)]:beam('Sambungan atap',[xa,yy,za+.025],[xb,yy,zb+.025],.023,.025,'roof','Atap')
  span=xb-xa
  for j in range(11):
   t=j/10;xx=xa+t*span;zz=za+t*(zb-za)
   cnp('Gording CNP125',[xx,4,zz-.15],[xx,64,zz-.15])
 beam('Nok atap',[cx,3.4,ridge+.03],[cx,64.6,ridge+.03],.32,.06,'trim','Atap')
 for yy in range(4,65,6):
  wf('Rafter WF250',[x,yy,eave-.15],[cx,yy,ridge-.15]);wf('Rafter WF250',[cx,yy,ridge-.15],[x+23,yy,eave-.15])
  for xx in [x,x+23]:
   beam('Haunch rafter',[xx,yy,eave-1.0],[xx+(1.5 if xx==x else -1.5),yy,eave+.1],.10,.20,'steel','Struktur')
  if yy in [4,16,40,58]:
   for xa,xb in [(x,cx),(cx,x+23)]:
    def zz(xx):return eave+(min(xx-x,x+23-xx))*.249328-.3
    beam('Ikatan angin silang',[xa,yy,zz(xa)],[xb,yy+6,zz(xb)],.016,.016,'steel','Struktur')
    beam('Ikatan angin silang',[xb,yy,zz(xb)],[xa,yy+6,zz(xa)],.016,.016,'steel','Struktur')
 # Front dock canopy shown 8 x 4 in layout.
 poly('Kanopi bongkar '+g,[[cx-4,64,4.95],[cx+4,64,4.95],[cx+4,68,4.5],[cx-4,68,4.5]],'roof','Atap',.07)
 for xx in [cx-3.7,cx+3.7]:beam('Penyangga kanopi',[xx,64,3.6],[xx,67.5,4.5],.10,.10,'steel',g)
 for xx in [cx-3.4,cx+3.4]:
  cyl('Bollard',xx,65,.1,.10,1.05,'amber',g);cyl('Bollard pita',xx,65,.68,.102,.18,'rubber',g)
 # Interior interpretation: pallet aisles, racking, escape access and luminaires.
 for rx in [x+3.2,x+16.8]:
  for ry in [9,19,29,39,49]:
   for dx in [0,2.7]:
    for dy in [0,1.2]:box('Upright rak',rx+dx,ry+dy,.22,.07,.07,4.4,'blue','Interior gudang')
   for z in [.55,1.95,3.35]:
    for dy in [0,1.2]:box('Balok rak',rx,ry+dy,z,2.77,.07,.12,'amber','Interior gudang')
    for px in [rx+.13,rx+1.45]:pallet(px,ry+.07,z+.12,'Interior gudang')
   beam('Diagonal rak',[rx,ry,.5],[rx,ry+1.2,4.5],.035,.035,'steel','Interior gudang')
 for yy in [12,24,36,48,60]:
  for xx in [x+6,cx,x+17]:
   cyl('Highbay housing',xx,yy,5.64,.22,.13,'trim','Interior gudang')
   cyl('Highbay diffuser',xx,yy,5.62,.18,.025,'light','Interior gudang');lights.append([xx,yy,5.56])
 for xx in [x+9,x+14]:box('Marka aisle',xx,6,.224,.08,56,.006,'amber',g)
 for yy in [14,32,50]:
  box('Alat pemadam kabinet',x+.22,yy,1.0,.16,.44,.75,'red',g)

# Open western shed follows the source rather than becoming a fourth warehouse.
box('Lantai sosoran',3,4,.1,15,60,.12,'floor','Sosoran')
poly('Atap sosoran',[[2.45,3.45,5.52],[18,3.45,6.15],[18,64.55,6.15],[2.45,64.55,5.52]],'roof','Atap',.055)
for yy in range(4,65,6):wf('Rafter sosoran',[3,yy,5.45],[18,yy,6.08])
for xx in [3+j*1.2 for j in range(13)]:cnp('Gording sosoran',[xx,4,5.35+(xx-3)*.042],[xx,64,5.35+(xx-3)*.042])
for yy in range(10,59,8):
 for xx in [5,8,11]:pallet(xx,yy,.22,'Interior sosoran')
labels.append(dict(text='SOSORAN',p=[10.5,64.5,4.8]))

# Office outline 6 x 12 m is fixed. Two-storey planning is inferred.
g='Kantor';ox,oy=81,66
for level in [0,1]:
 z=.15+level*3.6
 box('Pelat kantor',ox,oy,z,6,12,.15,'floor',g)
 apertures=[(82,84,1.0,2.8),(85,86.4,1.0,2.8)] if level else [(82,83.3,0,2.5),(84.1,86.3,.9,2.8)]
 wall_y('Fasad kantor',81,87,77.82,z+.15,3.45,'plaster',g,apertures)
 for lo,hi,b,t in apertures:window('Kaca kantor',lo,77.84,z+.15+b,hi-lo,t-b,g)
 wall_y('Belakang kantor',81,87,66,z+.15,3.45,'plaster',g,[(82,84.7,1,2.7)])
 window('Kaca belakang kantor',82,65.98,z+1.15,2.7,1.7,g)
 for xx in [81,86.82]:
  # Long side with continuous physical window slots between piers.
  box('Sill kantor',xx,66,z+.15,.18,12,1.0,'plaster',g)
  box('Spandrel kantor',xx,66,z+2.9,.18,12,.7,'plaster',g)
  for yy in [66,69,72,75,77.7]:box('Pier kantor',xx,yy,z+1.15,.18,.3,1.75,'plaster',g)
  for yy in [66.3,69.3,72.3,75.3]:
   box('Kaca samping kantor',xx+.06,yy,z+1.15,.03,2.7 if yy<75 else 2.4,1.75,'glass',g)
   for zz in [z+1.15,z+2.85]:box('Frame kantor',xx-.025,yy,zz,.23,2.7 if yy<75 else 2.4,.05,'trim',g)
 # Partitions leave circulation, stair opening in intermediate slab handled separately later.
 wall_y('Partisi kantor',81.2,86.8,70.6,z+.15,3.2,'plaster','Interior kantor',[(84.2,85.2,0,2.2)])
 for xx,yy in [(81.6,72),(81.6,74.4),(84.6,72),(84.6,74.4)]:
  table(xx,yy,z+.15,1.45,.7,'Interior kantor');chair(xx+.4,yy+.85,z+.15,'Interior kantor')
  box('Monitor',xx+.45,yy+.30,z+1.02,.55,.035,.36,'trim','Interior kantor')
 table(81.6,67,z+.15,2.2,1.1,'Interior kantor')
 for yy in [67.1,67.7]:chair(81.2,yy,z+.15,'Interior kantor')
 box('Lemari arsip',85.65,69,z+.15,.8,1.1,1.9,'wood','Interior kantor')
 for yy in [68,73,76]:box('Lampu kantor',83.7,yy,z+3.5,.6,.6,.035,'light','Interior kantor');lights.append([84,yy,z+3.3])
# Stair located on west outside of office footprint as an explicit access assumption.
for j in range(20):box('Anak tangga kantor',79.5,66+j*.28,.30+j*.18,1.45,.28,.18,'concrete','Tangga')
box('Landing kantor',79.5,71.6,3.75,1.5,1.2,.15,'concrete','Tangga')
for j in range(0,21,2):
 y=66+j*.28;z=.48+j*.18
 beam('Baluster tangga',[79.5,y,z],[79.5,y,z+1],.035,.035,'steel','Tangga')
beam('Handrail tangga',[79.5,66,1.48],[79.5,71.6,5.08],.05,.05,'steel','Tangga')
poly('Atap kantor',[[80.5,65.5,7.7],[87.5,65.5,7.7],[87.5,78.5,7.4],[80.5,78.5,7.4]],'roof','Atap',.12)
box('Kanopi pintu kantor',81.7,78,2.85,5.6,1.4,.14,'trim','Atap')
for z in [3.65,7.1]:box('Lis kantor',80.9,77.95,z,6.2,.16,.15,'trim',g)
labels.append(dict(text='KANTOR',p=[84,78.1,6.85]))

# Gatehouse from source: 3 x 3.5 m.
g='Pos';box('Lantai pos',48,75.5,.1,3,3.5,.12,'floor',g)
wall_y('Pos depan',48,51,78.82,.22,2.9,'plaster',g,[(48.5,50.6,1,2.25)]);window('Kaca pos',48.5,78.85,1.22,2.1,1.25,g)
wall_y('Pos belakang',48,51,75.5,.22,2.9,'plaster',g,[(48.3,49.2,0,2.2)])
for x in [48,50.82]:box('Dinding pos',x,75.5,.22,.18,3.5,2.9,'plaster',g)
poly('Atap pos',[[47.6,75.1,3.4],[51.4,75.1,3.4],[51.4,79.4,3.2],[47.6,79.4,3.2]],'roof','Atap',.08)
table(49,77,.22,1.5,.65,'Interior pos');chair(49.4,76.2,.22,'Interior pos')

# Parking rectangles from layout: cars 15 x 4, motorcycles 12 x 4.
for x,w,title in [(58.5,15,'Mobil'),(21,12,'Motor')]:
 box('Lantai parkir '+title,x,75,.1,w,4,.06,'concrete','Parkir')
 poly('Atap parkir '+title,[[x-.3,74.7,2.6],[x+w+.3,74.7,2.6],[x+w+.3,79.3,3.1],[x-.3,79.3,3.1]],'roof','Atap',.055)
 for xx in [x,x+w/2,x+w]:beam('Tiang parkir',[xx,78.8,.16],[xx,78.8,3.05],.1,.1,'steel','Parkir')
 for j in range(int(w/2.5)+1):box('Marka parkir',x+j*2.5,75,.166,.07,3.8,.012,'white','Parkir')
for x,c in [(59,'white'),(64,'blue'),(69,'trim')]:car(x,74.9,c)
for x in range(22,32,2):
 box('Motor body',x,76,.45,.52,1.5,.46,'trim','Kendaraan');box('Jok motor',x,76.45,.93,.5,.75,.12,'rubber','Kendaraan')
 for y in [76,77.5]:cyl('Roda motor',x+.25,y,.1,.22,.35,'rubber','Kendaraan')
# Site furniture, drainage and light poles.
for y in [2,65.3]:
 box('Saluran drainase',3,y,-.1,84,.24,.19,'trim','Tapak')
 for x in range(3,87):box('Grill drainase',x,y,.1,.035,.24,.025,'steel','Tapak')
for x,y in [(6,70),(25,70),(57,71),(77,70)]:
 cyl('Tiang lampu',x,y,.1,.07,6.0,'trim','Tapak');beam('Lengan lampu',[x,y,6.0],[x+1.2,y,6.0],.08,.08,'trim','Tapak')
 box('Lampu jalan',x+.7,y-.17,5.92,.8,.34,.10,'light','Tapak');lights.append([x+1.1,y,5.85])
for x in range(38,45):box('Penyeberangan',x,72,.11,.5,3,.01,'white','Tapak')
for cx in [29.5,52.5,75.5]:
 box('Marka loading',cx-4.1,64.4,.11,.08,5,.01,'amber','Tapak');box('Marka loading',cx+4,64.4,.11,.08,5,.01,'amber','Tapak')

# A real upper-storey side aperture connects the external stair landing to the office.
remove=set()
for e in E:
 if e['kind']!='box' or e['group']!='Kantor':continue
 x,y,z=e['p']
 if abs(x-81)<.001 and e['name']=='Sill kantor' and z>3:
  e['s'][1]=5.6
 if abs(x-81)<.001 and e['name']=='Pier kantor' and abs(y-72)<.001 and z>4:remove.add(e['id'])
 if x<81.2 and e['name'] in ['Kaca samping kantor','Frame kantor'] and z>4:
  if abs(y-69.3)<.001:e['s'][1]=2.3
  if abs(y-72.3)<.001:e['p'][1]=72.8;e['s'][1]=2.2
box('Sill kantor sesudah pintu',81,72.8,3.9,.18,5.2,1,'plaster','Kantor')
box('Pintu akses tangga kantor',81.02,71.65,3.9,.05,1.1,2.2,'glass','Kantor')
box('Lintel akses tangga',81,71.6,6.1,.18,1.2,.55,'plaster','Kantor')
for y in [71.6,72.75]:box('Frame pintu tangga',80.98,y,3.9,.24,.05,2.2,'trim','Kantor')
box('Frame atas pintu tangga',80.98,71.6,6.05,.24,1.2,.05,'trim','Kantor')
E=[e for e in E if e['id'] not in remove]
scene=dict(version=1,units='metres',origin_source=[2687.485976588833,1490.179689711849,0],materials=M,elements=E,labels=labels,lights=lights,openings=openings,
 footprints=[dict(name='Gudang '+str(3-i),x=x,y=4,w=23,d=60) for i,x in enumerate([18,41,64])]+[dict(name='Sosoran',x=3,y=4,w=15,d=60),dict(name='Kantor',x=81,y=66,w=6,d=12),dict(name='Pos',x=48,y=75.5,w=3,d=3.5)],
 assumptions=['1 drawing unit is 1 metre: confirmed against 23m spans, 60m length, WF250 geometry and 1.5m footings; INSUNITS flag is inconsistent.',
 'Site/layout governs plan; structural roof section is mirrored to put the western shed on the layout side.',
 'Warehouse finished floor +0.22m, steel eave +6.20m, roof rise 2.867m based on section slope; elevation datum interpreted.',
 'Office floor-to-floor 3.60m, facades, rooms, external stair, furniture, warehousing racks, doors and all finish selections are visualization assumptions.',
 'Landscape, vehicles, lighting and material weathering are presentation additions; no surveyed surrounding context.',
 'Structural members follow labels at nominal size; flange thickness and connections are illustrative, not an engineering design.'])
from revision_model import apply_revision
scene=apply_revision(scene)
from sliding_doors import apply_sliding_doors
scene=apply_sliding_doors(scene)
from warehouse_height import apply_warehouse_height
scene=apply_warehouse_height(scene)
(R/'web/dist/assets/scene.json').write_text(json.dumps(scene,separators=(',',':')))
(R/'outputs/model-manifest.json').write_text(json.dumps({k:v for k,v in scene.items() if k!='elements'},indent=2))
print('Scene:',len(scene['elements']),'elements;',dict(collections.Counter(e['group'] for e in scene['elements'])))
