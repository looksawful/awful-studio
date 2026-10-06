import { chromium } from 'playwright';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';

const [glbPath, out] = process.argv.slice(2);
assert(glbPath && out, 'usage: node ticket143-bottom-audit.mjs exact.glb output-dir');
const bytes = readFileSync(glbPath);
const sha = createHash('sha256').update(bytes).digest('hex');
const doc = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString().trim());
const root = doc.nodes.find(node => node.name === 'CTRL_IPHONE_17');
const frozen = JSON.parse(readFileSync('generated/iphone-review/frozen-current-2026-10-05/asset.json', 'utf8'));
const asset = { ...frozen, label: 'Ticket142 exact audit ' + sha.slice(0,8),
  previewGlb: 'assets/iphone-review/ticket143-audit.glb', sha256: sha, frozenReview: true,
  sourceRevision: root.extras.delivery_source_revision, sourceCommit: root.extras.delivery_source_commit,
  reviewStatus: 'DIAGNOSTIC - NOT HUMAN PASS',
  triangleCount: doc.meshes.reduce((n,m) => n+m.primitives.reduce((a,p)=>a+doc.accessors[p.indices].count/3,0),0) };
mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.route('**/assets/iphone-review/ticket143-audit.glb', route => route.fulfill({ body: bytes, contentType: 'model/gltf-binary' }));
  await page.goto('http://127.0.0.1:6006/iframe.html?id=models-devices--i-phone-17&viewMode=story', { waitUntil: 'networkidle' });
  const viewer = page.locator('awful-model-viewer');
  await page.waitForFunction(() => document.querySelector('awful-model-viewer')?.dataset.modelLoaded === 'iphone-17-v30');
  await viewer.evaluate((element, candidate) => {
    delete element.dataset.modelLoaded; delete element.dataset.snapshotVerified; delete element.dataset.modelError;
    element.asset = candidate;
  }, asset);
  await page.waitForFunction(expected => {
    const element=document.querySelector('awful-model-viewer');
    return element?.dataset.snapshotVerified===expected && element.dataset.modelLoaded==='iphone-17-v30' && !element.dataset.modelError;
  }, sha, {timeout:30000});
  assert.equal(await viewer.evaluate(e=>e._model.getObjectByName('CTRL_IPHONE_17').userData.delivery_source_revision),asset.sourceRevision);
  const part=viewer.locator('select[data-control="part"]');
  const mode=viewer.locator('select[data-control="mode"]');
  const states=viewer.locator('select[data-control="screen-state"]');
  await states.selectOption('screen_on');
  await viewer.locator('select[data-control="colorway"]').selectOption('white');
  const cameras=[['front',[0,0,1],[0,0],0.23,'all'],['front-angle',[0.35,0.1,1],[0,0],0.23,'all'],['island',[0,0,1],[0,0.448],0.037,'all'],['island-angle',[0.35,0.1,1],[0,0.448],0.045,'all'],['receiver',[0,0,1],[0,0.496],0.023,'all'],['receiver-angle',[0.3,0.1,1],[0,0.496],0.023,'all'],['sensor-isolated',[0,0,1],[-0.058,0.448],0.02,'mesh:FRONT_SENSOR_MASK'],['receiver-isolated',[0,0,1],[0,0.496],0.023,'mesh:FRONT_RECEIVER_MIC']];
  const evidence=[];
  for(const [name,direction,fraction,distance,selection] of cameras) {
    await part.selectOption(selection);
    // Never click fit after a preset: fit resets both cameras to front.
    await viewer.evaluate((element,{direction,fraction,distance})=>{
      const body=element._model.getObjectByName('BODY_ALUMINUM');element._model.updateMatrixWorld(true);
      const Vector=element._camera.position.constructor;
      const lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];
      body.traverse(o=>{if(o.isMesh){const p=o.geometry.attributes.position;for(let i=0;i<p.count;i++){
        const v=new Vector().fromBufferAttribute(p,i).applyMatrix4(o.matrixWorld);
        [v.x,v.y,v.z].forEach((n,a)=>{lo[a]=Math.min(lo[a],n);hi[a]=Math.max(hi[a],n)});
      }}});
      const center=new Vector((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(lo[2]+hi[2])/2);
      center.x+=(hi[0]-lo[0])*fraction[0];center.y+=(hi[1]-lo[1])*fraction[1];
      element._controls.target.copy(center);
      element._camera.position.copy(center).add(new Vector(...direction).normalize().multiplyScalar(distance));
      element._camera.lookAt(center);element._controls.update();
    },{direction,fraction,distance});
    let geometry;
    for(const [reviewMode,finish,state] of [...['black','white','mist_blue','sage','lavender'].map(f=>['texture',f,'screen_on']),...['screen_off','screen_lock','screen_website','screen_resume'].map(state=>['texture','white',state]),['clay','white','screen_on'],['wireframe','white','screen_on']]){
      await states.selectOption(state);
      await page.waitForFunction(state => document.querySelector('awful-model-viewer')?.dataset.screenState === state, state);
      await viewer.locator('select[data-control="colorway"]').selectOption(finish);
      await mode.selectOption(reviewMode);
      await page.waitForTimeout(160);
      const buffers=await viewer.evaluate(e=>{
        const rows=[];
        e._model.traverse(o=>{if(o.isMesh){rows.push({
          name:o.name,uuid:o.geometry.uuid,
          positions:Array.from(o.geometry.attributes.position.array),
          indices:o.geometry.index?Array.from(o.geometry.index.array):null,
        })}});
        return rows;
      });
      if(geometry)assert.deepEqual(buffers,geometry);else geometry=buffers;
      await viewer.locator('canvas').screenshot({path:out+'/'+name+'-'+reviewMode+'-'+finish+'-'+state+'.png'});
    }
    evidence.push({name,selection,direction,fraction,distance});
  }
  assert.deepEqual(errors,[]);
  writeFileSync(out+'/audit.json',JSON.stringify({sha,sourceRevision:asset.sourceRevision,sourceCommit:asset.sourceCommit,triangles:asset.triangleCount,evidence,errors},null,2));
  console.log('FRONT_AUDIT',JSON.stringify({sha,sourceRevision:asset.sourceRevision,views:evidence.length,errors}));
} finally { await browser.close(); }
