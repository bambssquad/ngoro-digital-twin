import * as T from './vendor/three.module.js';

export function fitDioramaView(camera, eye, target) {
  const forward=target.clone().sub(eye).normalize();
  const right=new T.Vector3().crossVectors(forward,camera.up).normalize();
  const up=new T.Vector3().crossVectors(right,forward).normalize();
  const tanY=Math.tan(T.MathUtils.degToRad(camera.fov/2))*.78,tanX=tanY*camera.aspect;
  let distance=0;
  for(const x of [-15,105])for(const y of [-4.5,14])for(const z of [-97,9]){
    const delta=new T.Vector3(x,y,z).sub(target),depth=delta.dot(forward);
    distance=Math.max(distance,Math.abs(delta.dot(right))/tanX-depth,Math.abs(delta.dot(up))/tanY-depth);
  }
  return target.clone().addScaledVector(forward,-distance);
}

// Presentation-only layer. Model, collision data and exported drawings stay untouched.
export function createDiorama(scene, materials, {reduced=false}={}) {
  const group=new T.Group(); group.name='Diorama presentation'; group.visible=false; scene.add(group);
  const base=new T.Mesh(new T.BoxGeometry(120,3.2,106),new T.MeshStandardMaterial({color:'#142338',roughness:.48,metalness:.25}));
  base.name='Diorama plinth'; base.position.set(45,-2.3,-44); base.receiveShadow=true; group.add(base);
  const edge=new T.LineSegments(new T.EdgesGeometry(base.geometry),new T.LineBasicMaterial({color:'#526a81',transparent:true,opacity:.45}));
  edge.position.copy(base.position); group.add(edge);
  const foot=new T.Mesh(new T.BoxGeometry(116,.55,102),new T.MeshStandardMaterial({color:'#09111e',roughness:.7}));
  foot.position.set(45,-4.15,-44); group.add(foot);

  // Localized warm pools suggest rain-slick paving without a screen-space reflection pass.
  const glowMaterial=new T.ShaderMaterial({transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-1,
    uniforms:{tint:{value:new T.Color('#ffce8b')}},
    vertexShader:'varying vec2 vUv; void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
    fragmentShader:'varying vec2 vUv; uniform vec3 tint; void main(){float d=length((vUv-0.5)*2.0);float a=(1.0-smoothstep(0.05,1.0,d))*0.17;gl_FragColor=vec4(tint,a);\n#include <tonemapping_fragment>\n#include <colorspace_fragment>}',
  });
  for(const [x,z,w,d] of [[29.5,-70,15,13],[52.5,-70,15,13],[75.5,-70,15,13],[84,-78,10,10]]) {
    const glow=new T.Mesh(new T.PlaneGeometry(w,d),glowMaterial);glow.rotation.x=-Math.PI/2;glow.position.set(x,.112,z);group.add(glow);
  }

  const rainPositions=new Float32Array(420*6);let seed=23;
  const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
  for(let i=0;i<rainPositions.length;i+=6){const x=-12+random()*114,y=1+random()*34,z=5-random()*100;rainPositions.set([x,y,z,x-.14,y-.7,z+.08],i);}
  const rainGeometry=new T.BufferGeometry();rainGeometry.setAttribute('position',new T.BufferAttribute(rainPositions,3).setUsage(T.DynamicDrawUsage));
  const rain=new T.LineSegments(rainGeometry,new T.LineBasicMaterial({color:'#8fb3ca',transparent:true,opacity:.22,depthWrite:false}));
  rain.name='Fine rain';rain.frustumCulled=false;rain.visible=!reduced;group.add(rain);
  const saved=new Map(Object.entries(materials).map(([name,m])=>[name,{color:m.color.clone(),roughness:m.roughness,metalness:m.metalness,emissive:m.emissive.clone(),emissiveIntensity:m.emissiveIntensity,normalScale:m.normalScale.clone()}]));
  const palette={concrete:'#89959c',floor:'#a7acb2',asphalt:'#263748',plaster:'#c3c7c4',roof:'#597087',steel:'#566778',trim:'#172b3f',blue:'#40677f',earth:'#273745',grass:'#314b4d',leaf:'#385957',leaf2:'#536f68',palm_leaf:'#3d6663',palm_leaf_light:'#739487',galvanized:'#899ba9',gate_finish:'#263b4b',door_plate:'#425d73'};
  let active=false;
  function setActive(value){
    active=value;group.visible=value;
    for(const [name,m] of Object.entries(materials)){
      const original=saved.get(name);m.color.copy(original.color);m.roughness=original.roughness;m.metalness=original.metalness;m.emissive.copy(original.emissive);m.emissiveIntensity=original.emissiveIntensity;m.normalScale.copy(original.normalScale);
      if(!value)continue;
      if(palette[name])m.color.set(palette[name]);
      m.normalScale.multiplyScalar(.48);
      if(['concrete','asphalt','floor'].includes(name)){m.roughness=.27;m.metalness=.12;}
      if(name==='roof'){m.roughness=.42;m.metalness=.32;}
      if(name==='glass'){m.color.set('#dfd2ae');m.emissive.set('#f4bd71');m.emissiveIntensity=.52;}
      if(name==='light'){m.emissive.set('#ffd192');m.emissiveIntensity=2.6;}
    }
  }
  function setQuality(low){rainGeometry.setDrawRange(0,low?280:840);rain.visible=!reduced;}
  function update(dt){
    if(!active||reduced||!rain.visible)return;
    const amount=Math.min(Math.max(dt,0),.06)*13;
    for(let i=0;i<rainPositions.length;i+=6){rainPositions[i+1]-=amount;rainPositions[i+4]-=amount;if(rainPositions[i+1]<.8){rainPositions[i+1]+=34;rainPositions[i+4]+=34;}}
    rainGeometry.attributes.position.needsUpdate=true;
  }
  return {group,rain,setActive,setQuality,update};
}
