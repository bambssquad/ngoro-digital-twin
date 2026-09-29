"""Revision 03: replace only the three rolling-shutter assemblies."""
def apply_sliding_doors(scene):
    E=scene['elements'];nextid=max(e['id'] for e in E)+1
    E[:]=[e for e in E if not(e['group'].startswith('Pintu Gudang') and e['name'].startswith('Rolling'))]
    scene['materials']['door_plate']={'color':'#526a75','roughness':.43,'metalness':.72}
    def add(kind,n,m,g,**kw):
        nonlocal nextid
        e=dict(id=nextid,kind=kind,name=n,mat=m,group=g,**kw);nextid+=1;E.append(e);return e
    def box(n,p,s,m,g,**kw):return add('box',n,m,g,p=p,s=s,**kw)
    def beam(n,a,b,w,h,m,g,**kw):return add('beam',n,m,g,a=a,b=b,w=w,h=h,**kw)
    motions=[m for m in scene['motions'] if not m['id'].startswith('door-')]
    for num,cx in [(3,29.5),(2,52.5),(1,75.5)]:
        g=f'Pintu Gudang {num}';mid=f'door-{num}';w=3.037;bottom=.225;height=4.790;travel=3.12
        # Interior-mounted tracks clear the existing canopy and its diagonal braces.
        bounds=[]
        for side,x in [(-1,cx-3.04),(1,cx+.003)]:
            kw={'motion':mid,'slideSide':side};bounds.append([x,63.60,bottom,w,.205,height])
            box('Sliding plat besi penuh 6mm',[x,63.755,bottom],[w,.006,height],'door_plate',g,**kw)
            for xx in [x+.025,x+w-.105]:box('Sliding rangka vertikal',[xx,63.665,bottom+.015],[.08,.09,height-.03],'gate_finish',g,**kw)
            for zz in [bottom+.015,1.78,3.36,bottom+height-.095]:box('Sliding rangka horizontal',[x+.025,63.665,zz],[w-.05,.09,.08],'gate_finish',g,**kw)
            # Welded edge beads preserve an unperforated solid exterior face.
            for xx in [x+.008,x+w-.014]:box('Sliding las tepi vertikal',[xx,63.761,bottom+.02],[.006,.003,height-.04],'steel',g,**kw)
            for zz in [bottom+.008,bottom+height-.014]:box('Sliding las tepi horizontal',[x+.008,63.761,zz],[w-.016,.003,.006],'steel',g,**kw)
            leading=x+w-.22 if side<0 else x+.16
            box('Sliding plat dudukan handle',[leading-.055,63.762,1.19],[.14,.012,.40],'trim',g,**kw)
            for zz in [1.23,1.49]:box('Sliding dudukan grip',[leading-.025,63.774,zz],[.065,.020,.045],'galvanized',g,**kw)
            box('Sliding handle tarik',[leading-.009,63.787,1.25],[.034,.018,.28],'galvanized',g,**kw)
            for xx in [x+.36,x+w-.36]:
                box('Sliding hanger plate',[xx-.05,63.63,4.96],[.10,.08,.33],'galvanized',g,**kw)
                add('wheel','Sliding trolley roda','steel',g,p=[xx,63.672,5.22],r=.085,d=.065,**kw)
                box('Sliding pengunci hanger',[xx-.07,63.616,5.265],[.14,.115,.028],'trim',g,**kw)
            # Bottom groove follows its flush floor guide; no floor step across entry.
            box('Sliding rel bawah daun',[x+.02,63.66,bottom],[w-.04,.095,.055],'steel',g,**kw)
        motions.append(dict(id=mid,label=f'Pintu Gudang {num}',kind='splitSlide',travel=travel,anchor=[cx,65,.22],leaves=bounds,bounds=[cx-3.04,63.60,bottom,6.08,.205,height]))
        for yy in [63.61,63.73]:box('Sliding rel atas C',[cx-6.23,yy,5.095],[12.46,.028,.17],'galvanized',g)
        box('Sliding bibir rel atas',[cx-6.23,63.61,5.095],[12.46,.148,.024],'galvanized',g)
        for k in range(9):
            xx=cx-6.15+k*1.5375
            box('Sliding bracket ke lintel',[xx-.055,63.735,5.12],[.11,.105,.26],'galvanized',g)
            for zz in [5.15,5.30]:box('Sliding anchor bolt',[xx-.012,63.73,zz],[.024,.018,.024],'steel',g)
        for xx in [cx-6.20,cx+6.12]:box('Sliding end stop karet',[xx,63.60,5.17],[.08,.16,.14],'rubber',g)
        for xx in [cx-3.04,cx+3.04]:box('Sliding floor guide',[xx-.035,63.62,.221],[.07,.12,.055],'galvanized',g)
        box('Sliding kunci pertemuan',[cx-.075,63.771,1.43],[.15,.03,.09],'galvanized',g,motion=mid,slideSide=-1)
    scene['motions']=motions;scene['revision']=3
    scene['assumptions'].append('Revision 03: all three warehouse shutters replaced with paired solid steel sliding leaves, nominal 6mm plate, approximately 3.04 x 4.79m per leaf, 3.12m travel each. Rails mount inside the facade to clear the unchanged canopy/braces. Plate thickness and hardware are visualization assumptions, not a fabrication design.')
    return scene
