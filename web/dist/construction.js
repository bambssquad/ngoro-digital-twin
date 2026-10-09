import * as T from './vendor/three.module.js';

export const STAGES=[
 {title:'Persiapan tapak',detail:'Tanah dan konteks dasar tapak. Mulai dari model kosong.'},
 {title:'Pondasi & sloof',detail:'Pondasi, pedestal dan sloof. Tanah disembunyikan sementara agar bagian bawah terbaca.'},
 {title:'Kolom & angkur',detail:'Baseplate, baut angkur dan kolom utama berdiri di atas pondasi.'},
 {title:'Rangka & pengaku',detail:'Rafter, haunch, gording dan ikatan angin melengkapi rangka baja.'},
 {title:'Dinding & atap',detail:'Selubung gudang, kantor, pos dan penutup atap mulai terbaca.'},
 {title:'Lantai & akses',detail:'Lantai, tangga, pintu, gerbang dan perkerasan kawasan.'},
 {title:'Interior & utilitas',detail:'Isi ruang, perlengkapan dan utilitas visual dari model.'},
 {title:'Lansekap & selesai',detail:'Lansekap dan konteks akhir. Semua elemen model ditampilkan.'}
];

export function stageForElement(e){
 const name=e.name||'',group=e.group||'';
 if(group==='Pondasi')return 1;
 if(group==='Struktur')return /^(Kolom|Baseplate|Baut angkur)/.test(name)?2:3;
 if(group==='Atap')return 4;
 if(group==='Lansekap'||group==='Kendaraan')return 7;
 if(group.startsWith('Interior'))return 6;
 if(group==='Tangga'||group==='Sosoran'||group==='Pagar depan'||group==='Gerbang utama'||group.startsWith('Pintu Gudang'))return 5;
 if(group==='Tapak')return name.startsWith('Tanah tapak')?0:/lampu/i.test(name)?6:5;
 if(/^(Lantai|Pelat|Sambungan lantai|Marka|Pintu|Daun pintu|Gagang|Bollard)/.test(name))return 5;
 if(/^(Alat pemadam|Pipa air|Grill|Saluran)/.test(name))return 6;
 if(group==='Parkir')return /^(Tiang|Rangka)/.test(name)?3:5;
 return 4;
}

export function isElementVisible(e,stage){
 if(e.group==='Tapak'&&(e.name||'').startsWith('Tanah tapak')&&stage>0&&stage<5)return false;
 return stageForElement(e)<=stage;
}

// Visibility is reversible. No source element, exported geometry or schedule is changed.
export function createConstruction(records,{elements,parents=[],onChange=()=>{}}){
 let active=false,stage=0,playing=false,elapsed=0,saved=[];
 const stageCounts=STAGES.map((_,i)=>elements.filter(e=>stageForElement(e)===i).length);
 const white=new T.Color(1,1,1),highlight=new T.Color('#a6d6ff'),hidden=new T.Matrix4().makeScale(0,0,0);
 const notify=()=>onChange(inspect());
 function inspect(){return {active,stage,playing,title:STAGES[stage].title,detail:STAGES[stage].detail,visible:elements.filter(e=>isElementVisible(e,stage)).length,stageCount:stageCounts[stage],total:elements.length,stageCounts:[...stageCounts]};}
 function apply(){
  if(!active)return;
  for(const record of saved){
   const {mesh,phases,matrices,technical}=record;
   if(mesh.isInstancedMesh){
    let any=false;
    for(let i=0;i<phases.length;i++){
     const visible=isElementVisible(record.parts[i],stage);any||=visible;
     mesh.setMatrixAt(i,visible?matrices[i]:hidden);mesh.setColorAt(i,phases[i]===stage?highlight:white);
    }
    mesh.visible=any;mesh.instanceMatrix.needsUpdate=true;mesh.instanceColor.needsUpdate=true;
   }else{
    mesh.visible=phases[0]<=stage;
    if(technical)technical.color.copy(record.technicalColor).lerp(new T.Color('#5aa9df'),phases[0]===stage?.28:0);
   }
  }
  notify();
 }
 function setActive(value){
  if(value===active)return;
  active=value;playing=false;elapsed=0;
  if(value){
   const parentStates=parents.map(parent=>({parent,visible:parent.visible}));
   for(const {parent} of parentStates)parent.visible=true;
   saved=records.map(({mesh,elements:parts=[],stage:fixedStage})=>{
    const record={mesh,parts,visible:mesh.visible,material:mesh.material,colors:mesh.isInstancedMesh?mesh.instanceColor?.clone()??null:null,phases:parts.length?parts.map(stageForElement):[fixedStage??7],matrices:[],parentStates};
    if(mesh.isInstancedMesh)for(let i=0;i<mesh.count;i++){const matrix=new T.Matrix4();mesh.getMatrixAt(i,matrix);record.matrices.push(matrix);}
    if(parts.length){
     const m=mesh.material.clone();m.map=null;m.normalMap=null;m.roughnessMap=null;m.roughness=.76;m.metalness=Math.min(m.metalness,.25);m.emissiveIntensity=0;
     m.color.lerp(new T.Color('#9babb8'),.25);record.technical=m;record.technicalColor=m.color.clone();mesh.material=m;
    }
    return record;
   });
   apply();
  }else{
   for(const record of saved){
    const {mesh,matrices,material,colors}=record;mesh.visible=record.visible;
    if(mesh.isInstancedMesh){matrices.forEach((m,i)=>mesh.setMatrixAt(i,m));mesh.instanceMatrix.needsUpdate=true;mesh.instanceColor=colors;}
    mesh.material=material;material.needsUpdate=true;record.technical?.dispose();
   }
   for(const {parent,visible} of saved[0]?.parentStates||[])parent.visible=visible;
   saved=[];notify();
  }
 }
 function setStage(next){stage=Math.max(0,Math.min(7,Number.isFinite(Number(next))?Math.round(Number(next)):0));elapsed=0;playing=false;apply();}
 function setPlaying(value){
  playing=!!value&&active;
  if(playing&&stage===7){stage=0;elapsed=0;apply();}
  notify();
 }
 function update(dt){
  if(!active||!playing||!Number.isFinite(dt)||dt<=0)return;
  elapsed+=dt;
  if(elapsed<5)return;
  const steps=Math.floor(elapsed/5);elapsed%=5;stage=Math.min(7,stage+steps);
  if(stage===7)playing=false;
  apply();
 }
 return {setActive,setStage,setPlaying,update,inspect};
}
