<script>
  import { onMount, onDestroy } from 'svelte';
  // Feature flag to disable effects for now
  const EFFEKSEER_ENABLED = false;
  // Dynamically import Effekseer only when enabled
  let effekseerApi;

  export let cue = '';

  let canvas;
  let context;
  let loaded = new Map();
  let frame;

  async function init() {
    if (!EFFEKSEER_ENABLED) return;
    if (!effekseerApi) {
      const mod = await import('@zaniar/effekseer-webgl-wasm/effekseer.min.js');
      // Try common shapes: default export, named, or global
      effekseerApi = mod?.default || mod?.effekseer || globalThis.effekseer;
    }
    if (!effekseerApi) return; // silently skip when unavailable
    await new Promise((resolve, reject) => {
      effekseerApi.initRuntime('/effekseer.wasm', resolve, reject);
    });
    context = effekseerApi.createContext();
    // Create a WebGL context from the canvas
    const gl =
      canvas.getContext('webgl2', { alpha: true, premultipliedAlpha: true }) ||
      canvas.getContext('webgl', { alpha: true, premultipliedAlpha: true }) ||
      canvas.getContext('experimental-webgl');
    if (!gl) throw new Error('WebGL not supported');
    context.init(gl);
    loop();
  }

  function loop() {
    if (context) {
      context.update();
      context.draw();
    }
    frame = requestAnimationFrame(loop);
  }

  async function playEffect(name) {
    if (!EFFEKSEER_ENABLED || !context || !name) return;
    let effect = loaded.get(name);
    if (!effect) {
      const url = new URL(`../assets/effects/${name}.efkefc`, import.meta.url).href;
      effect = await new Promise((resolve, reject) => {
        const e = context.loadEffect(
          url,
          1.0,
          () => resolve(e),
          () => reject(new Error('load failed'))
        );
      });
      loaded.set(name, effect);
    }
    context.play(effect);
  }

  $: if (cue) playEffect(cue);

  onMount(init);
  onDestroy(() => cancelAnimationFrame(frame));
</script>

<canvas bind:this={canvas} class="effect-layer"></canvas>

<style>
  .effect-layer {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }
</style>
