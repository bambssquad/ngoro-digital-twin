"""Revision 02: targeted landscape, entrance, shutters and guardhouse edits."""
import math

def apply_revision(scene):
    elems=scene['elements']
    remove={'Batang pohon','Tajuk pohon','Plinth pagar depan','Tiang pagar','Rel pagar','Piket pagar','Pilar gerbang','Daun gerbang digeser','Rel pintu rolling','Pintu rolling terangkat','Bilah pintu'}
    # IDs of all retained elements stay exactly as in the approved model.
    nextid=max(e['id'] for e in elems)+1
    scene['elements']=[e for e in elems if e['name'] not in remove and not(e['name']=='Dinding pos' and e['p'][0]==48)]
    E=scene['elements']; motions=[]
    def add(kind,name,mat,group,**kw):
        nonlocal nextid
        e=dict(id=nextid,kind=kind,name=name,mat=mat,group=group,**kw);nextid+=1;E.append(e);return e
    def box(n,p,s,m,g,**kw):return add('box',n,m,g,p=p,s=s,**kw)
    def beam(n,a,b,w,h,m,g,**kw):return add('beam',n,m,g,a=a,b=b,w=w,h=h,**kw)
    def poly(n,pts,m,g,th=.018):return add('prism',n,m,g,points=pts,th=th)
    def cylinder(n,p,r,h,m,g):return add('cylinder',n,m,g,p=p,r=r,h=h)
    scene['materials'].update(palm_leaf={'color':'#416c39','roughness':.79},palm_leaf_light={'color':'#779443','roughness':.86},palm_trunk={'color':'#9a8c70','roughness':.93},galvanized={'color':'#a5b3b7','metalness':.78,'roughness':.34},gate_finish={'color':'#34484a','metalness':.63,'roughness':.4})
    # Slender palms. Each arching frond has a rachis and paired tapered leaflets.
    positions=[(x+.4,y) for x in [1,88.1] for y in [8,20,32,44,56,70]]+[(x+.9,77.3) for x in [7,16,56,76]]
    for k,(x,y) in enumerate(positions):
        h=6.1+(k%4)*.38;g='Lansekap';crown=h-.4
        for j in range(10):
            z=.1+j*crown/10;r=.115+(1-j/10)*.048
            cylinder('Palm batang beruas',[x+.035*math.sin(j/10),y,z],r,crown/10+.015,'palm_trunk',g)
            cylinder('Palm bekas pelepah',[x+.035*math.sin(j/10),y,z+.015],r+.009,.027,'bark',g)
        cylinder('Palm crownshaft',[x+.03,y,crown-.25],.12,.65,'palm_leaf_light',g)
        for f in range(11):
            angle=f*math.tau/11+k*.47;length=1.75+.18*(f%3)
            dx,dy=math.cos(angle),math.sin(angle);sx,sy=-dy,dx
            def at(t):return [x+.03+dx*length*t,y+dy*length*t,crown+.25+1.18*math.sin(math.pi*t*.87)-.8*t]
            for j in range(8):beam('Palm tulang pelepah',at(j/8),at((j+1)/8),.018,.018,'palm_leaf_light',g)
            for j in range(1,9):
                t=j/10;start=at(t);end=at(t+.075);leaflen=.48*math.sin(math.pi*t)**.6
                for side in [-1,1]:
                    tip=[start[0]+sx*side*leaflen+dx*.20,start[1]+sy*side*leaflen+dy*.20,start[2]-.22-.12*t]
                    poly('Palm anak daun',[start,end,tip],'palm_leaf' if (j+f)%3 else 'palm_leaf_light',g,.012)
    # Front wall has plinth, coping, piers, recessed joints and an open gate bay.
    g='Pagar depan'
    for x,w in [(0,36),(48,42)]:
        box('Tembok depan plester',[x,79.8,.1],[w,.24,2],'plaster',g)
        box('Sokel tembok',[x,79.77,.1],[w,.30,.32],'concrete',g)
        box('Coping tembok',[x-.03,79.75,2.1],[w+.06,.34,.075],'concrete',g)
        for xx in range(x,x+w+1,3):
            box('Kolom praktis pagar',[xx-.07,79.77,.1],[.14,.30,2.0],'plaster',g)
            box('Capping kolom pagar',[xx-.10,79.74,2.1],[.20,.36,.09],'concrete',g)
    for x in [35.72,47.94]:
        box('Pilar gate beton',[x,79.57,.1],[.34,.58,2.55],'concrete',g)
        box('Pilar gate plester',[x-.018,79.55,.40],[.376,.62,2.23],'plaster',g)
        box('Topi pilar gate',[x-.06,79.5,2.63],[.46,.72,.08],'trim',g)
        box('Lampu pilar gate',[x+.095,80.18,1.95],[.15,.075,.28],'light',g)
    # Heavy sliding gate: welded frame, mesh infill, rack drive and guide hardware.
    g='Gerbang utama';mid='gate-main';x0=36.12;w=11.76;y=79.50;z=.29;h=2.02
    motions.append(dict(id=mid,label='Gerbang utama',kind='slide',delta=[-11.86,0,0],anchor=[42,80,.1],bounds=[x0,y-.03,z,w,.18,h]))
    moving={'motion':mid}
    for zz in [z,z+h-.12]:box('Gate rangka horizontal',[x0,y,zz],[w,.12,.12],'gate_finish',g,**moving)
    for i in range(7):
        xx=x0+i*w/6;box('Gate rangka vertikal',[xx,y,z],[.07,.12,h],'gate_finish',g,**moving)
    for i in range(1,79):box('Gate kisi baja',[x0+i*w/79,y+.033,z+.12],[.023,.052,h-.24],'gate_finish',g,**moving)
    box('Gate kickplate',[x0,y-.012,z+.12],[w,.016,.36],'gate_finish',g,**moving)
    for i in range(6):beam('Gate pengaku diagonal',[x0+i*w/6,y+.065,z+.48],[x0+(i+1)*w/6,y+.065,z+h-.12],.032,.032,'gate_finish',g,**moving)
    box('Gate rack gear',[x0,y-.05,.38],[w,.045,.032],'galvanized',g,**moving)
    for i in range(3):
        xx=x0+.55+i*(w-1.1)/2
        box('Gate rumah roda',[xx-.18,y-.025,.2],[.36,.17,.20],'trim',g,**moving)
        # Horizontal wheel axes, represented by capped circular disks.
        add('wheel','Gate roda V','galvanized',g,p=[xx,y+.06,.20],r=.095,d=.075,motion=mid)
    box('Gate rel tanah',[24.1,y+.035,.112],[23.82,.042,.032],'galvanized',g)
    box('Gate fondasi motor',[35.10,79.01,.1],[.58,.52,.16],'concrete',g)
    box('Gate motor gearbox',[35.19,79.10,.26],[.40,.35,.41],'trim',g)
    box('Gate tutup motor',[35.16,79.07,.65],[.46,.41,.075],'gate_finish',g)
    box('Gate lampu peringatan',[35.32,79.22,.73],[.12,.12,.12],'amber',g)
    for xx in [35.89,48.11]:
        box('Gate sensor photocell',[xx-.035,79.47,.72],[.07,.06,.11],'rubber',g)
        box('Gate roller guide bracket',[xx-.13,79.34,2.1],[.26,.22,.055],'galvanized',g)
    box('Gate stopper buka',[24.16,79.40,.12],[.10,.25,.22],'rubber',g)
    # Rolling shutters: interlocked slats, edge seals, hood, guides, drive and controls.
    for num,cx in [(3,29.5),(2,52.5),(1,75.5)]:
        g=f'Pintu Gudang {num}';mid=f'door-{num}';left=cx-3;floor=.22;top=5.02
        motions.append(dict(id=mid,label=f'Pintu Gudang {num}',kind='roll',travel=4.94,top=5.04,anchor=[cx,65,.22],bounds=[left,63.98,floor,6,.14,4.8]))
        for xx in [left-.12,left+6]:
            box('Rolling guide channel',[xx,63.94,floor],[.12,.20,4.9],'galvanized',g)
            box('Rolling guide seal',[xx+.035,64.12,floor],[.05,.026,4.82],'rubber',g)
            for j in range(7):
                box('Rolling wall bracket',[xx-.025,63.84,.55+j*.67],[.17,.14,.07],'galvanized',g)
                cylinder('Rolling anchor bolt',[xx+.06,63.92,.56+j*.67],.009,.018,'steel',g)
        for j in range(60):
            zz=floor+j*.08
            box('Rolling slat galvanis',[left+.025,64.025,zz],[5.95,.036,.077],'galvanized',g,motion=mid,slat=j)
            box('Rolling lip interlock',[left+.025,64.061,zz+.064],[5.95,.018,.010],'steel',g,motion=mid,slat=j)
        box('Rolling bottom rail',[left+.018,64.007,floor],[5.964,.082,.092],'gate_finish',g,motion=mid,slat=0)
        box('Rolling bottom seal',[left+.028,64.012,floor-.007],[5.944,.072,.023],'rubber',g,motion=mid,slat=0)
        for xx in [left+.20,left+5.63]:box('Rolling handle',[xx,64.09,.43],[.17,.055,.045],'trim',g,motion=mid,slat=2)
        # Four hood plates form a real enclosure rather than an oversized solid block.
        box('Rolling hood front',[left-.18,64.39,5.06],[6.36,.055,.62],'blue',g)
        box('Rolling hood top',[left-.18,63.87,5.68],[6.36,.575,.055],'blue',g)
        for xx in [left-.18,left+6.12]:box('Rolling hood endplate',[xx,63.87,5.06],[.06,.575,.62],'blue',g)
        beam('Rolling barrel shaft',[left-.08,64.12,5.35],[left+6.08,64.12,5.35],.13,.13,'steel',g)
        for i in range(13):box('Rolling hood fixing',[left+i*.5,64.454,5.57],[.018,.012,.018],'galvanized',g)
        box('Rolling motor enclosure',[left+6.22,63.89,4.85],[.25,.30,.52],'trim',g)
        box('Rolling pushbutton box',[left+6.37,64.07,1.18],[.17,.09,.28],'trim',g)
        for j,m in enumerate(['palm_leaf','red','amber']):box('Rolling pushbutton',[left+6.42,64.165,1.36-j*.066],[.065,.014,.041],m,g)
        for side in [-1,1]:
            xx=cx+side*3.36;cylinder('Bollard pelindung pintu',[xx,64.62,.1],.082,.91,'amber',g)
            for zz in [.27,.53,.79]:cylinder('Bollard strip hitam',[xx,64.62,zz],.085,.085,'rubber',g)
    # West wall aperture and eastward roof drainage, preserving source footprint.
    g='Pos';x=48;ya=76.2;yb=78.25;z0=.22;bottom=1.1;top=2.4
    box('Pos barat pier selatan',[x,75.5,z0],[.18,ya-75.5,2.9],'plaster',g)
    box('Pos barat pier utara',[x,yb,z0],[.18,79-yb,2.9],'plaster',g)
    box('Pos barat ambang bawah',[x,ya,z0],[.18,yb-ya,bottom],'plaster',g)
    box('Pos barat lintel',[x,ya,z0+top],[.18,yb-ya,2.9-top],'plaster',g)
    box('Jendela barat kaca',[47.99,ya+.055,z0+bottom+.05],[.035,yb-ya-.11,top-bottom-.10],'glass',g)
    for yy in [ya,(ya+yb)/2-.025,yb-.05]:box('Jendela barat mullion',[47.96,yy,z0+bottom],[.09,.05,top-bottom],'trim',g)
    for zz in [z0+bottom,z0+top-.05]:box('Jendela barat frame',[47.96,ya,zz],[.09,yb-ya,.05],'trim',g)
    box('Jendela barat sill',[47.88,ya-.07,z0+bottom-.06],[.35,yb-ya+.14,.06],'concrete',g)
    box('Jendela barat handle',[47.92,(ya+yb)/2+.075,1.73],[.035,.035,.17],'galvanized',g)
    scene['openings'].append(dict(name='Jendela barat pos',x=48,y=ya,z=z0+bottom,w=yb-ya,h=top-bottom,axis='y',group=g))
    roof=next(e for e in E if e['name']=='Atap pos');roof['points']=[[47.6,75.1,3.4],[51.4,75.1,3.2],[51.4,79.4,3.2],[47.6,79.4,3.4]]
    for j in range(9):beam('Pos standing seam',[47.6,75.12+j*.53,3.418],[51.4,75.12+j*.53,3.218],.018,.027,'galvanized','Atap')
    box('Pos talang timur',[51.35,75.1,3.14],[.16,4.3,.10],'trim','Atap')
    cylinder('Pos downpipe timur',[51.43,75.57,.15],.047,3.08,'trim',g)
    scene['motions']=motions;scene['revision']=2
    scene['assumptions'].append('Revision 02 approved A/A/C: slender palms 6-8m; 2m plaster wall; steel sliding gate and rolling shutters; east-falling guardhouse roof and west window; first/third-person browser walk with collision and touch joystick. Hardware dimensions are visual detailing assumptions.')
    return scene
