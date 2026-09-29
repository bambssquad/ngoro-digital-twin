require 'json'
root='C:/Users/adigh/OneDrive/Documents/ChatGPT/ngoro-digital-twin';m=Sketchup.active_model
scene=JSON.parse(File.read(root+'/web/dist/assets/scene.json'))
all=m.entities.grep(Sketchup::Group).flat_map{|g|g.entities.to_a}.select{|e|e.get_attribute('NGORO','id')}
ids=all.map{|e|e.get_attribute('NGORO','id')};want=scene['elements'].map{|e|e['id']}
bad=all.select{|e|e.respond_to?(:manifold?)&&!e.manifold?}
textures=m.materials.select{|mat|mat.name.start_with?('NGORO')&&mat.texture}.map{|mat|{name:mat.name,width:mat.texture.image_width,height:mat.texture.image_height}}
stairs=all.select{|e|e.name=='Anak tangga kantor'};landing=all.find{|e|e.name=='Landing kantor'};floor=all.select{|e|e.name=='Pelat kantor'}.max_by{|e|e.bounds.max.z}
top=stairs.map{|e|e.bounds.max.z.to_m}.max;ff=floor.bounds.max.z.to_m
report={path:m.path,version:Sketchup.version,reopened:true,elements:all.length,missing_ids:want-ids,extra_ids:ids-want,duplicate_ids:ids.length-ids.uniq.length,nonmanifold:bad.length,embedded_textures:textures,scenes:m.pages.length,stair_top_m:top,upper_ffl_m:ff,landing_top_m:landing.bounds.max.z.to_m,modified:m.modified?}
report[:pass]=report[:missing_ids].empty?&&report[:extra_ids].empty?&&bad.empty?&&textures.length==7&&report[:scenes]==8&&(top-ff).abs<0.005&&!m.modified?
File.write(root+'/verification/native-reopened.json',JSON.pretty_generate(report))
m.active_view.write_image(filename:root+'/outputs/NGORO_SketchUp.png',width:2000,height:1400,antialias:true)
