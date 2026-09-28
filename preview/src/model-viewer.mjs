import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { availableLods, cameraDirection, previewMaterialPolicy, resolveAssetUrl, validateModelProvenance } from './viewer-core.mjs';

const tagName = 'awful-model-viewer';

class AwfulModelViewer extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._asset = null;
    this._raf = 0;
    this._disposed = false;
    this._model = null;
    this._mixer = null;
    this._animationClips = [];
    this._screenGlow = null;
    this._clock = new THREE.Clock();
  }

  set asset(value) {
    this._asset = value;
    if (this.isConnected) this.#setup();
  }

  get asset() { return this._asset; }

  connectedCallback() {
    if (this._asset) this.#setup();
  }

  disconnectedCallback() { this.#dispose(); }

  #setup() {
    this.#dispose();
    this._disposed = false;
    const asset = this._asset;
    this.shadowRoot.innerHTML = `
      <style>${styles}</style>
      <section class="shell">
        <div class="toolbar">
          <label>LOD <select data-control="lod"></select></label>
          <label>mode <select data-control="mode"><option>texture</option><option>wireframe</option><option>clay</option><option>normals</option></select></label>
          <label>projection <select data-control="projection"><option value="perspective">perspective</option><option value="orthographic">orthographic</option></select></label>
          <button data-camera="front">front</button><button data-camera="side">side</button><button data-camera="top">top</button>
          <button data-action="fit">fit</button>
          <label><input data-control="autorotate" type="checkbox"> rotate</label>
          <label>screen <select data-control="screen-state"></select></label>
          <label>clip <select data-control="animation-clip"></select></label>
          <label><input data-control="animation" type="checkbox"> animation</label>
          <label><input data-control="clip" type="checkbox"> section</label>
          <input data-control="clip-position" type="range" min="-1" max="1" step="0.01" value="0">
          <label><input data-control="axes" type="checkbox"> axes</label>
          <input data-control="background" type="color" value="#111111" aria-label="background">
          <button data-action="fullscreen">fullscreen</button>
        </div>
        <div class="stage" data-stage></div>
        <pre class="meta" data-meta></pre>
      </section>`;

    this.#initThree(asset);
    this.#bindControls(asset);
    this.#loadModel(availableLods(asset)[0].path);
  }
  #initThree(asset) {
    const stage = this.shadowRoot.querySelector('[data-stage]');
    const width = Math.max(stage.clientWidth, 640);
    const height = Math.max(stage.clientHeight, 480);

    this._scene = new THREE.Scene();
    this._scene.background = new THREE.Color('#111111');
    this._perspective = new THREE.PerspectiveCamera(35, width / height, 0.001, 1000);
    this._ortho = new THREE.OrthographicCamera(-2, 2, 2, -2, 0.001, 1000);
    this._camera = this._perspective;

    this._renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    this._renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    this._renderer.setSize(width, height, false);
    this._renderer.outputColorSpace = THREE.SRGBColorSpace;
    this._renderer.toneMapping = THREE.NeutralToneMapping;
    this._renderer.toneMappingExposure = 0.7;
    this._renderer.localClippingEnabled = true;
    stage.append(this._renderer.domElement);

    const pmrem = new THREE.PMREMGenerator(this._renderer);
    this._environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    this._scene.environment = this._environment;
    this._scene.environmentIntensity = 1.0;
    pmrem.dispose();

    this._viewLight = new THREE.DirectionalLight(0xffffff, 0.65);
    this._scene.add(this._viewLight);
    this._scene.add(this._viewLight.target);

    this._axes = new THREE.AxesHelper(1);
    this._axes.visible = false;
    this._scene.add(this._axes);
    this._clipPlane = new THREE.Plane(new THREE.Vector3(1, 0, 0), 0);

    this._controls = new OrbitControls(this._camera, this._renderer.domElement);
    this._controls.enableDamping = true;
    this._controls.autoRotate = false;
    this._controls.autoRotateSpeed = 1.2;

    this._resizeObserver = new ResizeObserver(() => this.#resize());
    this._resizeObserver.observe(stage);
    this.shadowRoot.querySelector('[data-meta]').textContent = this.#metadata(asset);
    this.#animate();
  }

  #metadata(asset) {
    const lines = [asset.label, `id: ${asset.id}`, `version: ${asset.version}`, `source: ${asset.sourceBlend}`, `preview: ${asset.previewGlb}`];
    if (asset.triangleCount != null) lines.push(`triangles: ${asset.triangleCount}`);
    if (asset.materialCount != null) lines.push(`materials: ${asset.materialCount}`);
    if (asset.sourceCommit) lines.push(`source commit: ${asset.sourceCommit}`);
    return lines.join('\n');
  }
  #bindControls(asset) {
    const lod = this.shadowRoot.querySelector('[data-control="lod"]');
    for (const option of availableLods(asset)) {
      const el = document.createElement('option');
      el.value = option.path;
      el.textContent = option.name;
      lod.append(el);
    }
    lod.addEventListener('change', () => this.#loadModel(lod.value));

    const screenState = this.shadowRoot.querySelector('[data-control="screen-state"]');
    const states = Object.keys(asset.screenStates ?? {});
    for (const state of states) {
      const option = document.createElement('option');
      option.value = state;
      option.textContent = state.replace('screen_', '');
      screenState.append(option);
    }
    if (!states.length) {
      screenState.disabled = true;
      screenState.append(new Option('n/a', ''));
    } else {
      screenState.value = states.includes('screen_on') ? 'screen_on' : states[0];
      screenState.addEventListener('change', () => this.#applyScreenState(screenState.value));
    }
    const animationClip = this.shadowRoot.querySelector('[data-control="animation-clip"]');
    animationClip.disabled = true;
    animationClip.append(new Option('n/a', ''));
    animationClip.addEventListener('change', () => this.#selectAnimationClip(animationClip.value));

    this.shadowRoot.querySelector('[data-control="autorotate"]').addEventListener('change', (event) => {
      this._controls.autoRotate = event.currentTarget.checked;
    });
    this.shadowRoot.querySelector('[data-control="animation"]').addEventListener('change', (event) => {
      if (!this._animationAction) return;
      if (event.currentTarget.checked) this._animationAction.reset().play();
      this._animationAction.paused = !event.currentTarget.checked;
    });
    this.shadowRoot.querySelector('[data-control="mode"]').addEventListener('change', (event) => {
      this.#applyRenderMode(event.currentTarget.value);
    });
    this.shadowRoot.querySelector('[data-control="projection"]').addEventListener('change', (event) => {
      this.#setProjection(event.currentTarget.value);
    });
    this.shadowRoot.querySelector('[data-control="background"]').addEventListener('input', (event) => {
      this._scene.background.set(event.currentTarget.value);
    });
    this.shadowRoot.querySelector('[data-control="clip"]').addEventListener('change', () => this.#applyClipping());
    this.shadowRoot.querySelector('[data-control="clip-position"]').addEventListener('input', (event) => {
      this._clipPlane.constant = Number(event.currentTarget.value);
      this.#applyClipping();
    });
    this.shadowRoot.querySelector('[data-control="axes"]').addEventListener('change', (event) => {
      this._axes.visible = event.currentTarget.checked;
    });
    for (const button of this.shadowRoot.querySelectorAll('[data-camera]')) {
      button.addEventListener('click', () => this.#cameraPreset(button.dataset.camera));
    }
    this.shadowRoot.querySelector('[data-action="fit"]').addEventListener('click', () => this.#fitModel());
    this.shadowRoot.querySelector('[data-action="fullscreen"]').addEventListener('click', () => this.requestFullscreen());
  }

  async #loadModel(repoPath) {
    if (this._model) {
      this._scene.remove(this._model);
      this.#disposeObject(this._model);
      this._model = null;
    }
    this._mixer = null;
    this._animationAction = null;
    const loader = new GLTFLoader();
    loader.setMeshoptDecoder(MeshoptDecoder);
    const basePath = new URL('.', document.baseURI).pathname;
    const gltf = await loader.loadAsync(resolveAssetUrl(repoPath, basePath));
    if (this._disposed) return;
    if (this._asset.group === 'Devices') {
      const root = gltf.scene.getObjectByName(this._asset.root);
      const provenanceErrors = validateModelProvenance(this._asset, root);
      if (provenanceErrors.length) {
        throw new Error(`Rejected stale/wrong-stage asset ${this._asset.id}: ${provenanceErrors.join('; ')}`);
      }
    }
    this._model = gltf.scene;
    this._scene.add(this._model);
    this.dataset.modelLoaded = this._asset.id;
    const maxAnisotropy = this._renderer.capabilities.getMaxAnisotropy();
    this._model.traverse((object) => {
      if (!object.isMesh) return;
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      for (const material of materials) {
        const policy = previewMaterialPolicy(material.name, { hasTexture: Boolean(material.map || material.emissiveMap) });
        if (policy.alphaTest != null) material.alphaTest = policy.alphaTest;
        if (policy.transparent != null) material.transparent = policy.transparent;
        if (policy.opacity != null) material.opacity = policy.opacity;
        if (policy.depthWrite != null) material.depthWrite = policy.depthWrite;
        if (policy.frontSide) material.side = THREE.FrontSide;
        if (policy.emissiveIntensity != null) material.emissiveIntensity = policy.emissiveIntensity;
        if (policy.envMapIntensity != null) material.envMapIntensity = policy.envMapIntensity;
        if (policy.transmission != null && 'transmission' in material) material.transmission = policy.transmission;
        if (policy.minRoughness != null && 'roughness' in material) material.roughness = Math.max(material.roughness, policy.minRoughness);
        if (policy.maxClearcoat != null && 'clearcoat' in material) material.clearcoat = Math.min(material.clearcoat, policy.maxClearcoat);
        material.needsUpdate = true;
        for (const texture of [material.map, material.emissiveMap, material.normalMap, material.roughnessMap, material.metalnessMap]) {
          if (!texture) continue;
          texture.anisotropy = maxAnisotropy;
          texture.needsUpdate = true;
        }
        if (material.name === 'MAT_SCREEN_CONTENT' && !material.userData.previewScreenOn) {
          material.userData.previewScreenOn = {
            map: material.map,
            emissiveMap: material.emissiveMap,
            color: material.color?.clone(),
            emissive: material.emissive?.clone(),
            emissiveIntensity: material.emissiveIntensity,
          };
        }
      }
      object.userData.previewOriginalMaterial = object.material;
      object.castShadow = false;
      object.receiveShadow = false;
    });
    this._animationClips = gltf.animations;
    const animationClip = this.shadowRoot.querySelector('[data-control="animation-clip"]');
    animationClip.innerHTML = '';
    if (gltf.animations.length) {
      this._mixer = new THREE.AnimationMixer(this._model);
      animationClip.disabled = false;
      for (const clip of gltf.animations) animationClip.append(new Option(clip.name, clip.name));
      this.#selectAnimationClip(gltf.animations[0].name);
    } else {
      animationClip.disabled = true;
      animationClip.append(new Option('n/a', ''));
    }
    this.#setupScreenGlow();
    const screenState = this.shadowRoot.querySelector('[data-control="screen-state"]');
    if (!screenState.disabled) this.#applyScreenState(screenState.value);
    this.#fitModel();
    this.#applyRenderMode(this.shadowRoot.querySelector('[data-control="mode"]').value);
    this.#applyClipping();
  }

  #selectAnimationClip(name) {
    if (!this._mixer) return;
    const clip = this._animationClips.find((item) => item.name === name);
    if (!clip) return;
    this._animationAction?.stop();
    this._animationAction = this._mixer.clipAction(clip);
    this._animationAction.reset();
    this._animationAction.setLoop(THREE.LoopOnce, 1);
    this._animationAction.clampWhenFinished = true;
    this._animationAction.play();
    this._animationAction.paused = !this.shadowRoot.querySelector('[data-control="animation"]').checked;
  }

  #setupScreenGlow() {
    this._screenGlow?.removeFromParent();
    this._screenGlow = null;
    const screen = this._model?.getObjectByName('SCREEN_CONTENT');
    if (!screen || !this._asset.screenStates) return;
    screen.geometry?.computeBoundingBox?.();
    const size = screen.geometry?.boundingBox?.getSize(new THREE.Vector3()) ?? new THREE.Vector3(0.12, 0.2, 0.001);
    const dimensions = [Math.abs(size.x), Math.abs(size.y), Math.abs(size.z)].sort((a, b) => b - a);
    const energy = Number(this._asset.screenGlow?.energy ?? this._asset.screenGlow?.source_energy_w ?? 8);
    this._screenGlow = new THREE.RectAreaLight(0xe6f0ff, energy, dimensions[0], dimensions[1]);
    this._screenGlow.name = 'AWFUL_SCREEN_GLOW';
    this._screenGlow.position.set(0, 0, 0.002);
    this._screenGlow.rotation.y = Math.PI;
    screen.add(this._screenGlow);
  }

  #applyScreenState(state) {
    if (!this._model || !state) return;
    const stateSpec = this._asset.screenStates?.[state] ?? {};
    const on = state !== 'screen_off';
    this._model.traverse((object) => {
      if (!object.isMesh) return;
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      for (const material of materials) {
        if (material.name !== 'MAT_SCREEN_CONTENT') continue;
        const saved = material.userData.previewScreenOn;
        if (!saved) continue;
        material.map = on ? saved.map : null;
        material.emissiveMap = on ? saved.emissiveMap : null;
        if (material.color) on && saved.color ? material.color.copy(saved.color) : material.color.set(0x010101);
        if (material.emissive) on && saved.emissive ? material.emissive.copy(saved.emissive) : material.emissive.set(0x000000);
        material.emissiveIntensity = on ? Number(stateSpec.emission_strength ?? saved.emissiveIntensity ?? 0.8) : 0;
        material.needsUpdate = true;
      }
    });
    if (this._screenGlow) {
      const base = Number(this._asset.screenGlow?.energy ?? this._asset.screenGlow?.source_energy_w ?? 8);
      this._screenGlow.intensity = on
        ? Number(stateSpec.glow_energy ?? base * Number(stateSpec.glow_intensity ?? 1))
        : 0;
    }
  }

  #bounds() {
    if (!this._model) return null;
    const box = new THREE.Box3().setFromObject(this._model);
    if (box.isEmpty()) return null;
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    return { box, center, size, max: Math.max(size.x, size.y, size.z, 0.001) };
  }

  #fitModel() {
    const bounds = this.#bounds();
    if (!bounds) return;
    const { center, max } = bounds;
    const distance = max / (2 * Math.tan(THREE.MathUtils.degToRad(this._perspective.fov / 2))) * 1.45;
    const direction = new THREE.Vector3(...cameraDirection('front'));
    this._perspective.position.copy(center).add(direction.multiplyScalar(distance));
    this._perspective.near = Math.max(distance / 1000, 0.001);
    this._perspective.far = distance * 100;
    this._perspective.updateProjectionMatrix();

    const half = max * 0.72;
    const aspect = Math.max(this._renderer.domElement.clientWidth / Math.max(this._renderer.domElement.clientHeight, 1), 0.1);
    this._ortho.left = -half * aspect;
    this._ortho.right = half * aspect;
    this._ortho.top = half;
    this._ortho.bottom = -half;
    this._ortho.position.copy(center).add(new THREE.Vector3(...cameraDirection('front')).multiplyScalar(max * 3));
    this._ortho.near = 0.001;
    this._ortho.far = max * 100;
    this._ortho.updateProjectionMatrix();

    this._controls.target.copy(center);
    this._controls.update();
  }

  #cameraPreset(name) {
    const bounds = this.#bounds();
    if (!bounds) return;
    const direction = new THREE.Vector3(...cameraDirection(name));
    const distance = Math.max(bounds.max * 3, 0.5);
    this._camera.position.copy(bounds.center).add(direction.multiplyScalar(distance));
    this._camera.lookAt(bounds.center);
    this._controls.target.copy(bounds.center);
    this._controls.update();
  }

  #setProjection(kind) {
    const old = this._camera;
    const next = kind === 'orthographic' ? this._ortho : this._perspective;
    next.position.copy(old.position);
    next.quaternion.copy(old.quaternion);
    this._camera = next;
    this._controls.object = next;
    this._controls.update();
    this.#resize();
  }
  #applyRenderMode(mode) {
    if (!this._model) return;
    this._model.traverse((object) => {
      if (!object.isMesh) return;
      const original = object.userData.previewOriginalMaterial;
      if (object.userData.previewTempMaterial) {
        object.userData.previewTempMaterial.dispose();
        object.userData.previewTempMaterial = null;
      }
      if (mode === 'texture' || mode === 'wireframe') {
        object.material = original;
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        for (const material of materials) material.wireframe = mode === 'wireframe';
      } else {
        const temp = mode === 'normals'
          ? new THREE.MeshNormalMaterial()
          : new THREE.MeshStandardMaterial({ color: 0xb9b7b2, roughness: 0.58, metalness: 0.05 });
        object.userData.previewTempMaterial = temp;
        object.material = temp;
      }
    });
    this.#applyClipping();
  }

  #applyClipping() {
    if (!this._model) return;
    const enabled = this.shadowRoot.querySelector('[data-control="clip"]').checked;
    this._model.traverse((object) => {
      if (!object.isMesh) return;
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      for (const material of materials) {
        material.clippingPlanes = enabled ? [this._clipPlane] : [];
        material.needsUpdate = true;
      }
    });
  }

  #resize() {
    if (!this._renderer) return;
    const stage = this.shadowRoot.querySelector('[data-stage]');
    const width = Math.max(stage.clientWidth, 1);
    const height = Math.max(stage.clientHeight, 1);
    this._renderer.setSize(width, height, false);
    this._perspective.aspect = width / height;
    this._perspective.updateProjectionMatrix();
    const span = (this._ortho.top - this._ortho.bottom) || 2;
    const half = span / 2;
    const aspect = width / height;
    this._ortho.left = -half * aspect;
    this._ortho.right = half * aspect;
    this._ortho.updateProjectionMatrix();
  }

  #animate() {
    if (this._disposed) return;
    const delta = this._clock.getDelta();
    this._mixer?.update(delta);
    this._controls?.update();
    if (this._viewLight && this._camera && this._controls) {
      this._viewLight.position.copy(this._camera.position);
      this._viewLight.target.position.copy(this._controls.target);
      this._viewLight.target.updateMatrixWorld();
    }
    this._renderer?.render(this._scene, this._camera);
    this._raf = requestAnimationFrame(() => this.#animate());
  }
  #disposeObject(root) {
    root.traverse((object) => {
      if (!object.isMesh) return;
      object.geometry?.dispose?.();
      const temp = object.userData.previewTempMaterial;
      temp?.dispose?.();
    });
  }

  #dispose() {
    this._disposed = true;
    if (this._raf) cancelAnimationFrame(this._raf);
    this._raf = 0;
    this._resizeObserver?.disconnect();
    this._controls?.dispose();
    if (this._model) this.#disposeObject(this._model);
    this._screenGlow?.removeFromParent();
    this._screenGlow = null;
    this._environment?.dispose?.();
    this._renderer?.dispose();
    this._renderer?.domElement?.remove();
    this._model = null;
    this._mixer = null;
  }
}

const styles = `
  :host { display:block; min-height:720px; color:#ececec; font:12px/1.4 ui-monospace,SFMono-Regular,Consolas,monospace; }
  .shell { display:grid; grid-template-rows:auto minmax(560px,1fr) auto; min-height:720px; background:#0b0b0c; border:1px solid #252527; }
  .toolbar { display:flex; flex-wrap:wrap; gap:6px; align-items:center; padding:8px; border-bottom:1px solid #252527; background:#111113; }
  label { display:inline-flex; gap:5px; align-items:center; }
  button, select, input { font:inherit; color:#ececec; background:#19191c; border:1px solid #343438; border-radius:4px; }
  button, select { min-height:28px; padding:3px 7px; }
  input[type='range'] { width:92px; }
  input[type='color'] { width:32px; height:28px; padding:2px; }
  button:hover { background:#232328; }
  .stage { position:relative; min-height:560px; overflow:hidden; background:#111; }
  .stage canvas { display:block; width:100%; height:100%; min-height:560px; }
  .meta { margin:0; padding:10px; border-top:1px solid #252527; white-space:pre-wrap; color:#a9a9ad; background:#0e0e10; }
`;

if (!customElements.get(tagName)) customElements.define(tagName, AwfulModelViewer);

export function createModelViewer(asset) {
  const element = document.createElement(tagName);
  element.asset = asset;
  return element;
}
