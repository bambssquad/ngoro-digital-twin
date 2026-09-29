require 'json'
root='C:/Users/adigh/OneDrive/Documents/ChatGPT/ngoro-digital-twin';m=Sketchup.active_model
raise 'Wrong model' unless m.path.end_with?('NGORO_Detailed_SU2023.skp')
scene=JSON.parse(File.read(root+'/web/dist/assets/scene.json'))
byid=scene['elements'].to_h{|e|[e['id'],e]}
all=m.entities.grep(Sketchup::Group).flat_map{|g|g.entities.to_a}.select{|e|e.get_attribute('NGORO','id')}
m.start_operation('Close foliage meshes and finish scenes',true)
processed=[]
all.select{|e|e.get_attribute('NGORO','kind')=='sphere'}.each do |e|
 d=e.definition;next if processed.include?(d);processed<<d
 data=byid[e.get_attribute('NGORO','id')];s=data['s'];mat=m.materials['NGORO '+data['mat']]
 t=(1+Math.sqrt(5))/2;v=[[-1,t,0],[1,t,0],[-1,-t,0],[1,-t,0],[0,-1,t],[0,1,t],[0,-1,-t],[0,1,-t],[t,0,-1],[t,0,1],[-t,0,-1],[-t,0,1]]
 v.map!{|p|n=Math.sqrt(p.sum{|q|q*q});p.map{|q|q/n}}
 faces=[[0,11,5],[0,5,1],[0,1,7],[0,7,10],[0,10,11],[1,5,9],[5,11,4],[11,10,2],[10,7,6],[7,1,8],[3,9,4],[3,4,2],[3,2,6],[3,6,8],[3,8,9],[4,9,5],[2,4,11],[6,2,10],[8,6,7],[9,8,1]]
 cache={};mid=lambda{|a,b|key=[a,b].sort;cache[key]||=begin;p=v[a].zip(v[b]).map{|x,y|(x+y)/2};n=Math.sqrt(p.sum{|q|q*q});v<<p.map{|q|q/n};v.length-1;end}
 faces=faces.flat_map{|a,b,c|ab=mid.call(a,b);bc=mid.call(b,c);ca=mid.call(c,a);[[a,ab,ca],[b,bc,ab],[c,ca,bc],[ab,bc,ca]]}
 d.entities.clear!;mesh=Geom::PolygonMesh.new(v.length,faces.length)
 v.each{|p|mesh.add_point(Geom::Point3d.new(p.zip(s).map{|x,y|(x*y).m}))};faces.each{|f|mesh.add_polygon(f.map{|i|i+1})}
 d.entities.add_faces_from_mesh(mesh,12,mat,mat)
end
# Add a native office interior scene and keep all existing source scenes.
m.active_view.camera=Sketchup::Camera.new([84.m,76.m,5.55.m],[83.7.m,70.m,5.2.m],Z_AXIS,true);m.active_view.camera.fov=55
m.pages.add('08 — Interior kantor') unless m.pages.any?{|p|p.name=='08 — Interior kantor'}
m.pages.selected_page=m.pages[0];m.active_view.camera=m.pages[0].camera
m.commit_operation;m.save
all=m.entities.grep(Sketchup::Group).flat_map{|g|g.entities.to_a}.select{|e|e.get_attribute('NGORO','id')}
invalid=all.select{|e|e.respond_to?(:manifold?)&&!e.manifold?}.map{|e|e.get_attribute('NGORO','id')}
report={elements:all.length,nonmanifold_ids:invalid,scenes:m.pages.length,saved:!m.modified?,foliage_definitions_repaired:processed.length}
File.write(root+'/verification/native-final.json',JSON.pretty_generate(report))
m.active_view.write_image(filename:root+'/outputs/NGORO_SketchUp.png',width:2000,height:1400,antialias:true)
