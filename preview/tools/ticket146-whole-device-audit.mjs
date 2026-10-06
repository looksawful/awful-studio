import { chromium } from 'playwright';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';

const [glbPath, out] = process.argv.slice(2);
assert(glbPath && out, 'usage: node whole-device-audit.mjs exact.glb output-dir');
const bytes = readFileSync(glbPath);
const sha = createHash('sha256').update(bytes).digest('hex');
const doc = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString().trim());
const root = doc.nodes.find(node => node.name === 'CTRL_IPHONE_17');
const manifest = JSON.parse(readFileSync('../assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30.asset.json','utf8'));
assert.equal(sha, manifest.artifacts.compat_glb.sha256);
assert.equal(root.extras.delivery_source_revision, manifest.source_revision);
const frozen = JSON.parse(readFileSync('generated/iphone-review/frozen-current-2026-10-05/asset.json','utf8'));
const reviewMeshes = frozen.reviewParts.flatMap(group => group.meshes).slice().sort();
const glbMeshes = doc.nodes.filter(node => Number.isInteger(node.mesh)).map(node => node.name).slice().sort();
assert.equal(glbMeshes.length, 51);
assert.deepEqual(glbMeshes, reviewMeshes);
const triangles = doc.meshes.reduce((n,m)=>n+m.primitives.reduce((a,p)=>a+doc.accessors[p.indices].count/3,0),0);
const asset = { ...frozen,
  label: 'Ticket146 exact whole-device candidate ' + sha.slice(0,8),
  previewGlb: 'assets/iphone-review/ticket146-candidate.glb',
  sha256: sha,
  frozenReview: true,
  sourceRevision: root.extras.delivery_source_revision,
  sourceCommit: root.extras.delivery_source_commit,
  reviewStatus: 'CANDIDATE - HUMAN PASS REQUIRED',
  triangleCount: triangles
};
mkdirSync(out,{recursive:true});
const browser=await chromium.launch({headless:true});
try {
  const page=await browser.newPage({viewport:{width:1400,height:1000}});
  const errors=[]; page.on('pageerror',e=>errors.push(String(e)));
  await page.route('**/assets/iphone-review/ticket146-candidate.glb',route=>route.fulfill({body:bytes,contentType:'model/gltf-binary'}));
  await page.goto('http://127.0.0.1:6006/iframe.html?id=models-devices--i-phone-17&viewMode=story',{waitUntil:'networkidle'});
  const viewer=page.locator('awful-model-viewer');
  await page.waitForFunction(()=>document.querySelector('awful-model-viewer')?.dataset.modelLoaded==='iphone-17-v30');
  await viewer.evaluate((element,candidate)=>{
    delete element.dataset.modelLoaded; delete element.dataset.snapshotVerified; delete element.dataset.modelError;
    element.asset=candidate;
  },asset);
  await page.waitForFunction(expected=>{
    const e=document.querySelector('awful-model-viewer');
    return e?.dataset.snapshotVerified===expected && e.dataset.modelLoaded==='iphone-17-v30' && !e.dataset.modelError;
  },sha,{timeout:30000});
  const identity=await viewer.evaluate((e,names)=>{
    const root=e._model.getObjectByName('CTRL_IPHONE_17');
    const present=names.map(name=>[name,Boolean(e._model.getObjectByName(name))]);
    return {revision:root.userData.delivery_source_revision,commit:root.userData.delivery_source_commit,present};
  },reviewMeshes);
  assert.equal(identity.revision,manifest.source_revision);
  assert.deepEqual(identity.present.filter(([,present])=>!present),[]);
  const part=viewer.locator('select[data-control="part"]');
  const mode=viewer.locator('select[data-control="mode"]');
  const states=viewer.locator('select[data-control="screen-state"]');
  const finish=viewer.locator('select[data-control="colorway"]');
  const cameras=[
    ['front',[0,0,1],[0,0],0.29,'all'],
    ['front-three-quarter',[0.45,0.10,1],[0,0],0.29,'all'],
    ['left-side',[1,0,0],[0,0],0.20,'all'],
    ['right-side',[-1,0,0],[0,0],0.20,'all'],
    ['bottom',[0,-1,0],[0,-0.42],0.16,'all'],
    ['back',[0,0,-1],[0,0],0.29,'all'],
    ['rear-three-quarter',[-0.4,0.1,-1],[0,0],0.29,'all'],
    ['camera-system',[0,0,-1],[0.317,0.35],0.095,'all'],
    ['rear-mic',[0,0,-1],[0.218,0.35],0.019,'all'],
    ['housing-wire',[0,0,-1],[0.317,0.35],0.095,'mesh:CAMERA_HOUSING']
  ];
  const evidence=[];
  for(const [name,direction,fraction,distance,selection] of cameras){
    await part.selectOption(selection);
    await viewer.evaluate((element,{direction,fraction,distance})=>{
      const body=element._model.getObjectByName('BODY_ALUMINUM'); element._model.updateMatrixWorld(true);
      const V=element._camera.position.constructor,lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];
      body.traverse(o=>{if(o.isMesh){const p=o.geometry.attributes.position;for(let i=0;i<p.count;i++){
        const v=new V().fromBufferAttribute(p,i).applyMatrix4(o.matrixWorld);
        [v.x,v.y,v.z].forEach((n,a)=>{lo[a]=Math.min(lo[a],n);hi[a]=Math.max(hi[a],n)});
      }}});
      const c=new V((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(lo[2]+hi[2])/2);
      c.x+=(hi[0]-lo[0])*fraction[0]; c.y+=(hi[1]-lo[1])*fraction[1];
      element._controls.target.copy(c); element._camera.position.copy(c).add(new V(...direction).normalize().multiplyScalar(distance));
      element._camera.lookAt(c); element._controls.update();
    },{direction,fraction,distance});
    let geometry=null;
    const cases=[['texture','white','screen_on'],['clay','white','screen_on'],['wireframe','white','screen_on']];
    for(const [reviewMode,color,state] of cases){
      await states.selectOption(state); await finish.selectOption(color); await mode.selectOption(reviewMode); await page.waitForTimeout(120);
      const buffers=await viewer.evaluate(e=>{
        const rows=[]; e._model.traverse(o=>{if(o.isMesh)rows.push([o.name,Array.from(o.geometry.attributes.position.array),o.geometry.index?Array.from(o.geometry.index.array):null])});
        return rows;
      });
      if(geometry) assert.deepEqual(buffers,geometry); else geometry=buffers;
      await viewer.locator('canvas').screenshot({path:out+'/'+name+'-'+reviewMode+'-'+color+'-'+state+'.png'});
    }
    evidence.push({name,selection,direction,fraction,distance});
  }
  await part.selectOption('all');
  await mode.selectOption('texture');
  await finish.selectOption('black');
  const expectedFinishes=[['black','292a2c'],['white','b8b8b6'],['mist_blue','687c95'],['sage','737e5e'],['lavender','998fa8']];
  for(const [color,expected] of expectedFinishes){
    await finish.selectOption(color);
    const actual=await viewer.evaluate(e=>{let x; e._model.traverse(o=>{if(o.isMesh)for(const m of(Array.isArray(o.material)?o.material:[o.material]))if(m?.name==='MAT_ANODIZED_ALUMINUM')x=m.color.getHexString()});return x});
    assert.equal(actual,expected);
  }
  await finish.selectOption('black');
  await states.selectOption('screen_off');
  const off=await viewer.evaluate(e=>{let x; e._model.traverse(o=>{if(o.isMesh)for(const m of(Array.isArray(o.material)?o.material:[o.material]))if(m?.name==='MAT_SCREEN_CONTENT')x={map:Boolean(m.map),emission:m.emissiveIntensity}});return x});
  assert.equal(off.map,false); assert.equal(off.emission,0);
  await states.selectOption('screen_on');
  const on=await viewer.evaluate(e=>{let x; e._model.traverse(o=>{if(o.isMesh)for(const m of(Array.isArray(o.material)?o.material:[o.material]))if(m?.name==='MAT_SCREEN_CONTENT')x={map:Boolean(m.map),emission:m.emissiveIntensity}});return x});
  assert.equal(on.map,true); assert.equal(on.emission,1);
  assert.deepEqual(errors,[]);
  const result={sha,meshoptSha:manifest.artifacts.meshopt_glb.sha256,pluginSha:manifest.artifacts.plugin_bundle.sha256,sourceRevision:manifest.source_revision,sourceCommit:manifest.source_commit,writerHead:'45cc11b',meshNodes:glbMeshes.length,nodeCount:doc.nodes.length,triangles,evidence,errors};
  writeFileSync(out+'/audit.json',JSON.stringify(result,null,2));
  console.log('TICKET146_WHOLE_DEVICE_GREEN',JSON.stringify({sha,sourceRevision:manifest.source_revision,meshNodes:glbMeshes.length,nodeCount:doc.nodes.length,triangles,views:evidence.length,errors}));
} finally { await browser.close(); }
