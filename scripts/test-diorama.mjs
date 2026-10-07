import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync, readFileSync} from 'node:fs';
import * as T from '../web/dist/vendor/three.module.js';
import vm from 'node:vm';

const moduleUrl = new URL('../web/dist/diorama.js', import.meta.url);
test('diorama presentation exists as a separate reversible layer', async () => {
  assert.ok(existsSync(moduleUrl), 'Diorama presentation module is not implemented');
  const {createDiorama} = await import(moduleUrl);
  const scene = new T.Scene();
  const concrete = new T.MeshStandardMaterial({color:'#b9b8af', roughness:.84});
  const before = concrete.color.getHex();
  const effect = createDiorama(scene, {concrete}, {reduced:true});
  assert.equal(effect.group.visible, false);
  effect.setActive(true);
  assert.equal(effect.group.visible, true);
  assert.notEqual(concrete.color.getHex(), before);
  assert.ok(concrete.roughness < .84);
  effect.setActive(false);
  assert.equal(concrete.color.getHex(), before);
  assert.equal(concrete.roughness, .84);
  assert.equal(effect.group.visible, false);
});

test('miniature base covers the existing road without changing model coordinates', async () => {
  assert.ok(existsSync(moduleUrl), 'Diorama base is not implemented');
  const {createDiorama} = await import(moduleUrl);
  const scene = new T.Scene(), building = new T.Mesh(new T.BoxGeometry(23,12,60));
  building.position.set(29.5,6,-35); scene.add(building);
  const before = building.matrix.toArray();
  const effect = createDiorama(scene, {}, {reduced:true});
  const base = effect.group.getObjectByName('Diorama plinth');
  const bounds = new T.Box3().setFromObject(base);
  assert.ok(bounds.min.x <= -12 && bounds.max.x >= 102);
  assert.ok(bounds.min.z <= -92.3 && bounds.max.z >= 0);
  assert.ok(bounds.max.y < -.55);
  effect.setActive(true); effect.update(.03);
  assert.deepEqual(building.matrix.toArray(), before);
  assert.equal(building.parent, scene);
  assert.ok(effect.group.children.length <= 10, 'Keep additional draw calls bounded');
});

test('rain pauses for reduced motion and remains bounded for lightweight quality', async () => {
  assert.ok(existsSync(moduleUrl), 'Diorama atmosphere is not implemented');
  const {createDiorama} = await import(moduleUrl);
  const effect = createDiorama(new T.Scene(), {}, {reduced:true});
  effect.setActive(true);
  assert.equal(effect.rain.visible, false);
  const moving = createDiorama(new T.Scene(), {}, {reduced:false});
  moving.setActive(true); moving.setQuality(true);
  assert.ok(moving.rain.geometry.drawRange.count <= 280);
  const initial=moving.rain.geometry.attributes.position.array.slice();
  moving.update(.02);
  assert.notDeepEqual(moving.rain.geometry.attributes.position.array, initial);
  moving.setActive(false);
  const paused=moving.rain.geometry.attributes.position.array.slice();
  moving.update(.02);
  assert.deepEqual(moving.rain.geometry.attributes.position.array, paused);
});

test('presentation control is accessible and model/CAD navigation remains available', () => {
  const html=readFileSync(new URL('../web/dist/index.html',import.meta.url),'utf8');
  assert.match(html,/id="presentation"/);
  assert.match(html,/>Diorama malam</);
  for(const id of ['walk-mode','roof','interiors','toggle-door-1','toggle-door-2','toggle-door-3','drawing-sheet']) assert.ok(html.includes(`id="${id}"`));
  assert.match(html,/data-workspace="cad"/);
  assert.match(html,/data-workspace="sheets"/);
});

test('changing presentation exits walk before setting the new orbit lens', () => {
  const app=readFileSync(new URL('../web/dist/app.js',import.meta.url),'utf8');
  const source=app.slice(app.indexOf('function setPresentation('),app.indexOf("$('presentation').onchange"));
  const state={walkMode:'first',ready:true},camera=new T.PerspectiveCamera(58);
  const experience={setMode(mode){if(state.walkMode!=='orbit')camera.fov=32;state.walkMode=mode;}};
  const scene=new T.Scene();scene.background=new T.Color();scene.fog=new T.FogExp2();
  const context={state,camera,controls:{},experience,scene,ground:{},sky:{},diorama:null,document:{body:{classList:{toggle(){}}}},$(){return {};},setTime(){},hemi:new T.HemisphereLight(),sun:new T.DirectionalLight(),renderer:{},dynamicLights:[],setView(){experience.setMode('orbit');}};
  vm.runInNewContext(source+';setPresentation("studio",false);',context);
  assert.equal(state.walkMode,'orbit');
  assert.equal(camera.fov,42);
  state.walkMode='first';camera.fov=58;
  vm.runInNewContext(source+';setPresentation("studio",true);',context);
  assert.equal(camera.fov,42);
});

test('overview framing contains the whole plinth on desktop and portrait screens', async () => {
  const module=await import(moduleUrl);
  assert.equal(typeof module.fitDioramaView,'function','Full miniature camera fitting is missing');
  for(const aspect of [16/9,1,390/844,320/844]){
    const camera=new T.PerspectiveCamera(32,aspect,.12,1800),target=new T.Vector3(45,1,-42),eye=new T.Vector3(137,110,-157);
    camera.position.copy(module.fitDioramaView(camera,eye,target));camera.lookAt(target);camera.updateMatrixWorld();
    for(const x of [-15,105])for(const y of [-4.5,14])for(const z of [-97,9]){
      const projected=new T.Vector3(x,y,z).project(camera);
      assert.ok(Math.abs(projected.x)<.81 && Math.abs(projected.y)<.81,`Clipped miniature at aspect ${aspect}: ${projected.toArray()}`);
    }
  }
});
