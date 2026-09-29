require 'json'
root='C:/Users/adigh/OneDrive/Documents/ChatGPT/ngoro-digital-twin'
$ngoro_reload=true;load root+'/scripts/build_native.rb'
m=Sketchup.active_model
raise 'Wrong model' unless m.path.end_with?('NGORO_Detailed_SU2023.skp')
raise 'Model has user changes; preserve before revision' if m.modified?
old=JSON.parse(File.read(root+'/verification/revision-04/scene-before.json'))['elements'].to_h{|e|[e['id'],e]}
scene=JSON.parse(File.read(root+'/web/dist/assets/scene.json'));now=scene['elements'].to_h{|e|[e['id'],e]}
changed=now.keys.select{|id|old[id]!=now[id]};removed=old.keys-now.keys
m.start_operation('NGORO revision 04: warehouse ridge height',true)
m.entities.grep(Sketchup::Group).each{|g|g.entities.to_a.each{|e|id=e.get_attribute('NGORO','id');e.erase! if id&&(changed.include?(id)||removed.include?(id))}}
materials={};scene['materials'].each do |name,s|
 mat=m.materials['NGORO '+name]||m.materials.add('NGORO '+name);mat.color=s['color'];mat.alpha=s.fetch('opacity',1);materials[name]=mat
end
groups=m.entities.grep(Sketchup::Group).to_h{|g|[g.name,g]}
scene['elements'].map{|e|e['group']}.uniq.each do |name|
 next if groups[name];g=m.entities.add_group;g.name=name;g.layer=m.layers.add('NGORO | '+name);groups[name]=g
end
NgoroBuild.instance_variable_set(:@m,m);NgoroBuild.instance_variable_set(:@materials,materials);NgoroBuild.instance_variable_set(:@groups,groups)
NgoroBuild.instance_variable_set(:@defs,{});NgoroBuild.instance_variable_set(:@count,0)
NgoroBuild.instance_variable_set(:@revision_items,changed.map{|id|now[id]});NgoroBuild.instance_variable_set(:@revision_index,0)
NgoroBuild.instance_variable_set(:@revision_errors,[]);NgoroBuild.instance_variable_set(:@revision_scene,scene)
NgoroBuild.instance_variable_set(:@revision_removed,removed.length)
module NgoroBuild
 def self.revision_batch
  last=[@revision_index+180,@revision_items.length].min
  while @revision_index<last
   e=@revision_items[@revision_index]
   begin;build(e);rescue=>ex;@revision_errors<<{id:e['id'],name:e['name'],error:ex.message};end
   @revision_index+=1
  end
  File.write(ROOT+'/verification/revision-04/native-progress.json',JSON.generate({done:@revision_index,total:@revision_items.length,errors:@revision_errors}))
  if @revision_index<@revision_items.length
   UI.start_timer(0.01,false){revision_batch}
  else
   raise 'Geometry errors; see report' unless @revision_errors.empty?
   @m.set_attribute('NGORO','revision',4);@m.set_attribute('NGORO','assumptions',@revision_scene['assumptions'].join("\n"))
   @m.commit_operation;ok=@m.save
   @m.active_view.write_image(filename:ROOT+'/outputs/NGORO_SketchUp.png',width:2000,height:1400,antialias:true)
   File.write(ROOT+'/verification/revision-04/native-sync.json',JSON.pretty_generate({saved:ok,changed:@revision_items.length,removed:@revision_removed,errors:@revision_errors}))
  end
 rescue=>ex
  @m.abort_operation
  File.write(ROOT+'/verification/revision-04/native-fatal.txt',ex.full_message)
 end
end
UI.start_timer(0.01,false){NgoroBuild.revision_batch}
{queued:changed.length,removed:removed.length}.to_json
