import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync,readFileSync} from 'node:fs';
import * as T from '../web/dist/vendor/three.module.js';
import vm from 'node:vm';
import {fitDioramaView} from '../web/dist/diorama.js';
const moduleUrl=new URL('../web/dist/construction.js',import.meta.url);
const data=JSON.parse(readFileSync(new URL('../web/dist/assets/scene.json',import.meta.url)));
const load=async()=>{assert.ok(existsSync(moduleUrl),'Construction playback is not implemented');return import(moduleUrl);};

test('every existing Ngoro element has a bounded illustrative stage',async()=>{
 const {stageForElement,STAGES}=await load();
 assert.equal(STAGES.length,8);
 const before=JSON.stringify(data),counts=Array(8).fill(0);
 for(const e of data.elements){const stage=stageForElement(e);assert.ok(Number.isInteger(stage)&&stage>=0&&stage<8,e.name);counts[stage]++;}
 assert.ok(counts.every(n=>n>0));assert.equal(counts.reduce((a,b)=>a+b),9972);
 assert.equal(stageForElement({group:'Pondasi',name:'Pedestal'}),1);
 assert.equal(stageForElement({group:'Struktur',name:'Kolom WF250'}),2);
 assert.equal(stageForElement({group:'Struktur',name:'Rafter WF250'}),3);
 assert.equal(stageForElement({group:'Atap',name:'Penutup atap Gudang 1'}),4);
 assert.equal(JSON.stringify(data),before);
});

test('stage scrub hides future instances, reveals completed work and restores exact matrices',async()=>{
 const {createConstruction}=await load();
 const elements=[{id:1,group:'Pondasi',name:'Pedestal'},{id:2,group:'Struktur',name:'Kolom WF250'}];
 const mesh=new T.InstancedMesh(new T.BoxGeometry(),new T.MeshStandardMaterial(),2);
 mesh.setMatrixAt(0,new T.Matrix4().makeTranslation(10,1,20));mesh.setMatrixAt(1,new T.Matrix4().makeTranslation(10,5,20));
 const initial=mesh.instanceMatrix.array.slice(),parent=new T.Group();parent.visible=false;parent.add(mesh);
 const c=createConstruction([{mesh,elements}],{elements,parents:[parent]});
 c.setActive(true);c.setStage(1);
 assert.equal(parent.visible,true);assert.equal(c.inspect().visible,1);
 assert.equal(mesh.instanceMatrix.array[16],0);assert.equal(mesh.instanceMatrix.array[0],1);
 c.setStage(2);assert.deepEqual(mesh.instanceMatrix.array,initial);assert.equal(c.inspect().visible,2);
 c.setStage(0);assert.equal(c.inspect().visible,0);
 c.setActive(false);assert.deepEqual(mesh.instanceMatrix.array,initial);assert.equal(mesh.instanceColor,null);assert.equal(parent.visible,false);
 c.setActive(true);c.setStage(7);c.setActive(false);assert.deepEqual(mesh.instanceMatrix.array,initial);
});

test('playback pauses, stops at completion, restarts and never counts WF parts twice',async()=>{
 const {createConstruction}=await load();
 const elements=[{id:5,group:'Struktur',name:'Rafter WF250'}];
 const mesh=new T.InstancedMesh(new T.BoxGeometry(),new T.MeshStandardMaterial(),3);
 const c=createConstruction([{mesh,elements:[elements[0],elements[0],elements[0]]}],{elements,parents:[]});
 c.setActive(true);c.setPlaying(true);c.update(5.1);assert.equal(c.inspect().stage,1);
 c.setPlaying(false);c.update(100);assert.equal(c.inspect().stage,1);
 c.setStage(7);assert.equal(c.inspect().visible,1);assert.equal(c.inspect().playing,false);
 c.setPlaying(true);assert.equal(c.inspect().stage,0);c.update(40);assert.equal(c.inspect().stage,7);assert.equal(c.inspect().playing,false);
 c.setActive(false);c.setPlaying(true);assert.equal(c.inspect().playing,false);
});

test('merged meshes and labels respect their phase and restore shared materials',async()=>{
 const {createConstruction}=await load();const original=new T.MeshStandardMaterial({color:'#abcabc'});
 const mesh=new T.Mesh(new T.BoxGeometry(),original),label=new T.Mesh(new T.PlaneGeometry(),original);
 const e={id:9,group:'Atap',name:'Atap kantor'};
 const c=createConstruction([{mesh,elements:[e]},{mesh:label,elements:[],stage:7}],{elements:[e],parents:[]});
 c.setActive(true);c.setStage(3);assert.equal(mesh.visible,false);assert.equal(label.visible,false);
 c.setStage(4);assert.equal(mesh.visible,true);assert.notEqual(mesh.material,original);
 c.setActive(false);assert.equal(mesh.material,original);assert.equal(label.visible,true);
});

test('public UI exposes an illustrative timeline and retains both existing visual modes',()=>{
 const html=readFileSync(new URL('../web/dist/index.html',import.meta.url),'utf8');
 assert.match(html,/value="construction"/);assert.match(html,/id="construction-stage"/);
 assert.match(html,/id="construction-play"/);assert.match(html,/Urutan ilustratif/);
 assert.match(html,/value="diorama"/);assert.match(html,/value="studio"/);
 assert.doesNotMatch(html,/142\.5|484 bolts|24.week|10.ton/i);
});

test('soil is temporarily hidden so below-grade foundations can be inspected',async()=>{
 const mod=await load();assert.equal(typeof mod.isElementVisible,'function');
 const soil={id:1,group:'Tapak',name:'Tanah tapak 90 x 80'},foundation={id:2,group:'Pondasi',name:'Pondasi plat 1.50'};
 assert.equal(mod.isElementVisible(soil,0),true);assert.equal(mod.isElementVisible(soil,1),false);
 assert.equal(mod.isElementVisible(foundation,1),true);assert.equal(mod.isElementVisible(soil,5),true);
});

test('pre-existing per-instance colours survive repeated construction-mode visits',async()=>{
 const {createConstruction}=await load();const e={id:1,group:'Struktur',name:'Kolom WF250'};
 const mesh=new T.InstancedMesh(new T.BoxGeometry(),new T.MeshStandardMaterial(),1);
 mesh.setColorAt(0,new T.Color('#f5a322'));const before=mesh.instanceColor.array.slice();
 const c=createConstruction([{mesh,elements:[e]}],{elements:[e],parents:[]});
 for(let i=0;i<3;i++){c.setActive(true);c.setStage(2);c.setActive(false);assert.deepEqual(mesh.instanceColor.array,before);}
});

test('repeated construction resizes do not accumulate zoom and keep the scene in frame',()=>{
 const app=readFileSync(new URL('../web/dist/app.js',import.meta.url),'utf8');
 const code=app.slice(app.indexOf("window.addEventListener('resize'"),app.indexOf(";controls.addEventListener('start'"));
 const camera=new T.PerspectiveCamera(36,16/9,.12,1800);camera.position.set(137,110,-157);
 const target=new T.Vector3(45,1,-42);let resize;
 const context={camera,controls:{target},state:{ready:true,presentation:'construction',walkMode:'orbit',view:'overview'},fitDioramaView,renderer:{setSize(){}},window:{addEventListener(_name,fn){resize=fn;}},innerWidth:1440,innerHeight:810,transition:null};
 vm.runInNewContext(code,context);resize();const first=camera.position.clone();
 for(let i=0;i<10;i++)resize();assert.ok(camera.position.distanceTo(first)<1e-8);
 for(const [w,h] of [[390,844],[1440,810],[390,844],[1440,810]]){
  context.innerWidth=w;context.innerHeight=h;resize();camera.lookAt(target);camera.updateMatrixWorld();
  assert.ok(camera.position.distanceTo(target)<1600);
  for(const x of [-15,105])for(const y of [-4.5,14])for(const z of [-97,9]){const p=new T.Vector3(x,y,z).project(camera);assert.ok(Math.abs(p.x)<.9&&Math.abs(p.y)<.9);}
 }
 assert.ok(camera.position.distanceTo(first)<1e-8);
});

test('opening model details pauses construction without restarting it on close',async()=>{
 const {createConstruction}=await load(),construction=createConstruction([],{elements:[],parents:[]});construction.setActive(true);construction.setPlaying(true);
 const app=readFileSync(new URL('../web/dist/app.js',import.meta.url),'utf8');
 const code=app.slice(app.indexOf("$('info').onclick"),app.indexOf(";document.querySelector('.close')"));
 const info={},details={showModal(){this.open=true;}};
 vm.runInNewContext(code,{construction,$:id=>id==='info'?info:details});info.onclick();construction.update(20);
 assert.equal(details.open,true);assert.equal(construction.inspect().playing,false);assert.equal(construction.inspect().stage,0);
});

test('opening a drawing workspace pauses playback and preserves the chosen stage',async()=>{
 const {createConstruction}=await load(),construction=createConstruction([],{elements:[],parents:[]});construction.setActive(true);construction.setStage(3);construction.setPlaying(true);
 const app=readFileSync(new URL('../web/dist/app.js',import.meta.url),'utf8');
 const code=app.slice(app.indexOf("for(const b of document.querySelectorAll('[data-workspace]')"),app.indexOf("document.addEventListener('visibilitychange'"));
 let click;vm.runInNewContext(code,{construction,document:{querySelectorAll(){return [{addEventListener(_event,fn){click=fn;}}]}}});click();construction.update(20);
 assert.equal(construction.inspect().playing,false);assert.equal(construction.inspect().stage,3);
});
