<script>
  import { onMount, onDestroy } from 'svelte';
  import effekseer from '@zaniar/effekseer-webgl-wasm/effekseer.min.js';

  export let cue = '';

  let canvas;
  let context;
  let loaded = new Map();
  let frame;

  async function init() {
    await new Promise((resolve, reject) => {
      effekseer.initRuntime('/effekseer.wasm', resolve, reject);
    });
    context = effekseer.createContext();
    context.init(canvas);
    loop();
  }

  function loop() {
    if (context) context.update();
    frame = requestAnimationFrame(loop);
  }

  async function playEffect(name) {
    if (!context || !name) return;
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
