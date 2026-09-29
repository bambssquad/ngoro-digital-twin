require 'json'
root=NgoroBuild::ROOT;m=Sketchup.active_model
raise 'Wrong model' unless m.path.end_with?('NGORO_Detailed_SU2023.skp')
old=JSON.parse(File.read(root+'/verification/scene-before-stair.json'))['elements'].to_h{|e|[e['id'],e]}
scene=JSON.parse(File.read(root+'/web/dist/assets/scene.json'));now=scene['elements'].to_h{|e|[e['id'],e]}
changed=now.keys.select{|id|old[id]!=now[id]};removed=old.keys-now.keys
m.start_operation('Align office stair and entrance',true)
m.entities.grep(Sketchup::Group).each{|g|g.entities.to_a.each{|e|id=e.get_attribute('NGORO','id');e.erase! if id && (changed.include?(id)||removed.include?(id))}}
NgoroBuild.instance_variable_set(:@scene,scene)
changed.each{|id|NgoroBuild.build(now[id])}
m.options['PageOptions']['ShowTransition']=false
r=m.rendering_options
m.pages.each do |pg|
 m.pages.selected_page=pg;m.active_view.camera=pg.camera
 r['RenderMode']=3;r['Texture']=true;r['EdgeDisplayMode']=0;r['DrawSilhouettes']=false
 r['DrawGround']=false;r['DrawHorizon']=false;r['DisplaySketchAxes']=false;r['MaterialTransparency']=true
 r['BackgroundColor']=Sketchup::Color.new(234,233,224)
 m.shadow_info['DisplayShadows']=true;m.shadow_info['DisplayOnGround']=false
 m.shadow_info['Light']=85;m.shadow_info['Dark']=65
 m.styles.update_selected_style;pg.update
end
m.pages.selected_page=m.pages[0];m.active_view.camera=m.pages[0].camera
m.commit_operation;m.save
report=JSON.parse(File.read(root+'/verification/native-build.json'));report['elements']=now.length;report['stair_sync']={changed:changed.length,removed:removed.length};File.write(root+'/verification/native-build.json',JSON.pretty_generate(report))
m.active_view.write_image(filename:root+'/outputs/NGORO_SketchUp.png',width:2000,height:1400,antialias:true)
File.write(root+'/verification/native-sync.json',JSON.pretty_generate({changed:changed.length,removed:removed.length,saved:!m.modified?}))
