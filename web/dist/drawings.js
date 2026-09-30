// CAD remains read-only. All sheets and layer names come from the versioned manifest.
const $=id=>document.getElementById(id),NS='http://www.w3.org/2000/svg';
const canvas=$('drawing-canvas'),workspace=$('drawing-workspace');
let manifest=null,loading=null,mode='3d',sheet=null,content=null,fitBox=null,box=null,request=0;
const selections={cad:{kind:'source',id:'source-site'},sheets:{kind:'source',id:'source-foundation'}},cache=new Map(),hiddenLayers=new Map(),pointers=new Map();
let lastGesture=null;
const state=window.NGORO_DRAWINGS={ready:false,mode:'3d',errors:[],zoom:1,sheet:null,layers:[],hiddenLayers:[]};
const message=(text)=>{$('drawing-message').textContent=text;$('drawing-message').hidden=!text;};
function reflect(){if(!box)return;canvas.setAttribute('viewBox',box.join(' '));state.zoom=fitBox[2]/box[2];state.viewBox=[...box];$('drawing-zoom').textContent=Math.round(state.zoom*100)+'%';}
function fitted(){const r=canvas.getBoundingClientRect(),v=content.viewBox.baseVal;const aspect=r.width/r.height;let w=v.width*1.1,h=v.height*1.1;if(w/h<aspect)w=h*aspect;else h=w/aspect;return [v.x+(v.width-w)/2,v.y+(v.height-h)/2,w,h];}
function fit(){if(!content||workspace.hidden)return;fitBox=fitted();box=[...fitBox];reflect();}
function point(clientX,clientY){const m=canvas.getScreenCTM();if(!m)return null;return new DOMPoint(clientX,clientY).matrixTransform(m.inverse());}
function zoom(factor,clientX,clientY){if(!box)return;const r=canvas.getBoundingClientRect();const p=point(clientX??r.x+r.width/2,clientY??r.y+r.height/2);if(!p)return;const current=fitBox[2]/box[2],next=Math.min(200,Math.max(.3,current*factor)),f=current/next;box=[p.x+(box[0]-p.x)*f,p.y+(box[1]-p.y)*f,box[2]*f,box[3]*f];reflect();}
function resetGesture(){lastGesture=null;if(pointers.size===1){const p=[...pointers.values()][0];lastGesture={x:p.x,y:p.y,box:[...box]};}else if(pointers.size===2){const [a,b]=[...pointers.values()];lastGesture={x:(a.x+b.x)/2,y:(a.y+b.y)/2,distance:Math.hypot(a.x-b.x,a.y-b.y)};}}
canvas.addEventListener('wheel',e=>{if(!box)return;e.preventDefault();zoom(Math.exp(-Math.max(-180,Math.min(180,e.deltaY))*.0025),e.clientX,e.clientY);},{passive:false});
canvas.addEventListener('pointerdown',e=>{if(!box||e.button>0)return;canvas.focus({preventScroll:true});canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});canvas.classList.add('dragging');resetGesture();});
canvas.addEventListener('pointermove',e=>{
 if(!pointers.has(e.pointerId)||!box)return;pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});const r=canvas.getBoundingClientRect();
 if(pointers.size===1&&lastGesture){box=[lastGesture.box[0]-(e.clientX-lastGesture.x)*lastGesture.box[2]/r.width,lastGesture.box[1]-(e.clientY-lastGesture.y)*lastGesture.box[3]/r.height,lastGesture.box[2],lastGesture.box[3]];reflect();}
 else if(pointers.size===2&&lastGesture){const [a,b]=[...pointers.values()],x=(a.x+b.x)/2,y=(a.y+b.y)/2,d=Math.hypot(a.x-b.x,a.y-b.y);if(d>0&&lastGesture.distance>0)zoom(d/lastGesture.distance,lastGesture.x,lastGesture.y);box[0]-=(x-lastGesture.x)*box[2]/r.width;box[1]-=(y-lastGesture.y)*box[3]/r.height;reflect();lastGesture={x,y,distance:d};}
});
function release(e){pointers.delete(e.pointerId);if(!pointers.size)canvas.classList.remove('dragging');if(box)resetGesture();}
for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,release);
canvas.addEventListener('dblclick',()=>fit());
canvas.addEventListener('keydown',e=>{if(!box)return;const k=e.key;if(['+','=','-','Home','0','ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(k)){e.preventDefault();e.stopPropagation();if(k==='+'||k==='=')zoom(1.3);else if(k==='-')zoom(1/1.3);else if(k==='Home'||k==='0')fit();else {box[k==='ArrowLeft'||k==='ArrowRight'?0:1]+=(k==='ArrowLeft'||k==='ArrowUp'?-1:1)*box[k==='ArrowLeft'||k==='ArrowRight'?2:3]*.08;reflect();}}});
$('drawing-plus').onclick=()=>zoom(1.35);$('drawing-minus').onclick=()=>zoom(1/1.35);$('drawing-fit').onclick=fit;
function applyLayers(){const off=hiddenLayers.get(sheet.id)||new Set();for(const e of content.querySelectorAll('[data-layer]'))e.style.display=off.has(e.dataset.layer)?'none':'';state.hiddenLayers=[...off];for(const input of $('layer-list').querySelectorAll('input'))input.checked=!off.has(input.value);$('layer-count').textContent=`${sheet.layers.length-off.size}/${sheet.layers.length}`;}
function layers(){const list=$('layer-list');list.replaceChildren();for(const name of sheet.layers){const label=document.createElement('label');label.className='layer-item';const input=document.createElement('input');input.type='checkbox';input.value=name;input.checked=true;input.onchange=()=>{const off=hiddenLayers.get(sheet.id)||new Set();input.checked?off.delete(name):off.add(name);hiddenLayers.set(sheet.id,off);applyLayers();};label.append(input,document.createTextNode(name));list.append(label);}applyLayers();}
$('layers-all').onclick=()=>{hiddenLayers.set(sheet.id,new Set());applyLayers();};$('layers-none').onclick=()=>{hiddenLayers.set(sheet.id,new Set(sheet.layers));applyLayers();};
function sanitize(xml){const doc=new DOMParser().parseFromString(xml,'image/svg+xml');if(doc.querySelector('parsererror')||doc.documentElement.localName!=='svg')throw Error('Format SVG tidak valid');const svg=doc.documentElement;for(const e of svg.querySelectorAll('script,foreignObject,iframe,image,a,animate,set'))e.remove();for(const e of [svg,...svg.querySelectorAll('*')])for(const a of [...e.attributes])if(/^on/i.test(a.name)||/^(href|xlink:href)$/i.test(a.name))e.removeAttribute(a.name);svg.removeAttribute('width');svg.removeAttribute('height');return document.importNode(svg,true);}
async function showSheet(id){
 const ticket=++request;const selected=manifest.sheets.find(s=>s.id===id);if(!selected)return;
 state.ready=false;message('Memuat '+selected.title+'…');
 try{let xml=cache.get(id);if(!xml){const r=await fetch(selected.url);if(!r.ok)throw Error('Gambar gagal dimuat ('+r.status+')');xml=await r.text();cache.set(id,xml);}if(ticket!==request)return;
  sheet=selected;content=sanitize(xml);const v=content.viewBox.baseVal;content.setAttribute('x',v.x);content.setAttribute('y',v.y);content.setAttribute('width',v.width);content.setAttribute('height',v.height);canvas.replaceChildren(content);$('drawing-description').textContent=sheet.description;$('drawing-title').textContent=sheet.title;$('drawing-badge').textContent=sheet.kind==='source'?'DWG SUMBER · VEKTOR ASLI':'TURUNAN MODEL · REVISI 04';$('drawing-download').href=sheet.url;$('drawing-download').download=sheet.id+'.svg';canvas.setAttribute('aria-label',sheet.title+'. Seret untuk geser, gulir atau cubit untuk zoom.');state.sheet=id;state.layers=[...sheet.layers];selections[mode]={kind:sheet.kind,id};layers();fit();message('');state.ready=true;
 }catch(e){if(ticket!==request)return;state.errors.push(e.message);message(e.message+'. Pilih gambar lain atau muat ulang.');}
}
function options(preferred){const kind=$('drawing-kind').value;const items=manifest.sheets.filter(s=>s.kind===kind);$('drawing-sheet').replaceChildren();for(const s of items){const o=document.createElement('option');o.value=s.id;o.textContent=s.title;$('drawing-sheet').append(o);}const id=items.some(s=>s.id===preferred)?preferred:items[0].id;$('drawing-sheet').value=id;return showSheet(id);}
async function data(){if(manifest)return manifest;if(!loading)loading=fetch('assets/drawings/manifest.json').then(r=>{if(!r.ok)throw Error('Daftar gambar tidak tersedia');return r.json();}).then(d=>manifest=d).catch(e=>{loading=null;throw e;});return loading;}
async function setMode(next){
 if(next===mode)return;mode=next;state.mode=mode;state.ready=false;document.body.classList.toggle('drawing-mode',mode!=='3d');workspace.hidden=mode==='3d';document.querySelectorAll('[data-workspace]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.workspace===mode)));
 if(window.NGORO){window.NGORO.experience?.setMode('orbit');window.NGORO.drawingMode=mode!=='3d';}pointers.clear();lastGesture=null;
 if(mode==='3d'){++request;return;}const expectedMode=mode;message('Menyiapkan daftar gambar…');
 try{await data();if(mode!==expectedMode)return;$('drawing-kind').value=selections[mode].kind;await options(selections[mode].id);}catch(e){state.errors.push(e.message);message(e.message);}
}
document.querySelectorAll('[data-workspace]').forEach(b=>b.onclick=()=>setMode(b.dataset.workspace));$('drawing-kind').onchange=()=>options();$('drawing-sheet').onchange=e=>showSheet(e.target.value);
const sidebar=document.querySelector('.drawing-sidebar');function panel(collapsed){sidebar.classList.toggle('collapsed',collapsed);$('drawing-panel').setAttribute('aria-expanded',String(!collapsed));$('drawing-panel').textContent=collapsed?'+':'−';document.body.classList.toggle('drawing-options-open',!collapsed&&matchMedia('(max-width:700px)').matches);}
$('drawing-panel').onclick=()=>panel(!sidebar.classList.contains('collapsed'));panel(matchMedia('(max-width:700px)').matches);
let resizing;new ResizeObserver(()=>{clearTimeout(resizing);resizing=setTimeout(()=>{if(content&&mode!=='3d')fit();},80);}).observe(canvas);
$('drawing-print').onclick=()=>{if(!content)return;document.querySelector('.drawing-print-only')?.remove();const page=document.createElement('section');page.className='drawing-print-only';const h=document.createElement('h2');h.textContent=sheet.title;const p=document.createElement('p');p.textContent=(sheet.kind==='source'?'DWG sumber. ':'Turunan model revisi 04. ')+sheet.description+' Skala cetak mengikuti halaman, bukan skala asli DWG.';page.append(h,content.cloneNode(true),p);document.body.append(page);window.print();};window.addEventListener('afterprint',()=>document.querySelector('.drawing-print-only')?.remove());
state.inspect=()=>({ready:state.ready,mode,sheet:state.sheet,zoom:state.zoom,viewBox:box?[...box]:null,layers:state.layers,hiddenLayers:state.hiddenLayers,errors:[...state.errors],svgPaths:content?.querySelectorAll('path').length??0});
