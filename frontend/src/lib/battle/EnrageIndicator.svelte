<script>
  // Ambient orbs during combat; gently despawn after combat ends.
  export let active = false;        // true while combat is running
  export let reducedMotion = false; // respect settings

  let ending = false;
  let orbs = [];

  function rand(min, max) { return Math.random() * (max - min) + min; }
  function randInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
  // Restrict hues to only red and blue for enrage visuals
  function redOrBlueHue() {
    // 50/50 chance: red cluster (~350-359 or 0-10) or blue cluster (~200-240)
    if (Math.random() < 0.5) {
      const branch = Math.random() < 0.5 ? rand(350, 359) : rand(0, 10);
      return branch;
    }
    return rand(200, 240);
  }

  function makeOrb() {
    const hue = redOrBlueHue(); // only red or blue
    return {
      id: Math.random().toString(36).slice(2),
      x: rand(0, 100),
      y: rand(0, 100),
      size: rand(2.4, 4.2),
      dx: rand(8, 16),
      dy: rand(6, 14),
      colorDur: rand(6, 10),
      delay: rand(0, 3),
      hue,
    };
  }

  $: if (active) {
    ending = false;
    if (orbs.length === 0) {
      const count = reducedMotion ? 6 : 14;
      orbs = Array.from({ length: count }, makeOrb);
    }
  }
  $: if (!active && orbs.length && !ending) {
    // Begin fade/despawn; keep DOM around briefly then clear.
    ending = true;
    const t = setTimeout(() => { orbs = []; ending = false; }, 3500);
  }
</script>

<div class="enrage-orbs" class:active={active} class:ending={ending} class:reduced={reducedMotion} aria-hidden="true">
  {#each orbs as orb (orb.id)}
    <div
      class="orb"
      style={`--x:${orb.x};--y:${orb.y};--size:${orb.size}rem;--dx:${orb.dx}s;--dy:${orb.dy}s;--hue:${orb.hue};--colorDur:${orb.colorDur}s;--delay:${orb.delay}s;`}
    >
      <div class="i"></div>
    </div>
  {/each}
  <!-- subtle overall vignette for depth -->
  <div class="vignette"></div>
  <!-- fade cover used during ending state -->
  <div class="fade" />
  
</div>

<style>
  .enrage-orbs {
    position: absolute;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0;
    transition: opacity 300ms ease;
  }
  .enrage-orbs.active { opacity: 1; }
  .enrage-orbs.ending { opacity: 0; transition-duration: 2.4s; }

  .orb {
    position: absolute;
    left: calc(var(--x) * 1%);
    top: calc(var(--y) * 1%);
    width: var(--size);
    height: var(--size);
    filter: blur(0.5px);
    animation: driftX var(--dx) linear infinite;
    animation-delay: var(--delay);
  }
  .orb .i {
    width: 100%; height: 100%; border-radius: 50%;
    background: radial-gradient(circle,
      hsla(var(--hue), 90%, 60%, 0.40) 0%,
      hsla(calc(var(--hue) + 10), 95%, 55%, 0.34) 55%,
      rgba(0,0,0,0) 70%
    );
    animation: driftY var(--dy) ease-in-out infinite alternate, hueShift var(--colorDur) linear infinite;
    mix-blend-mode: screen;
    box-shadow: 0 0 12px hsla(var(--hue), 95%, 60%, 0.28), 0 0 24px hsla(var(--hue), 95%, 55%, 0.20);
  }

  .enrage-orbs.reduced .orb { animation: none; }
  .enrage-orbs.reduced .orb .i { animation: none; opacity: 0.5; }

  .vignette { position:absolute; inset:0; background: radial-gradient(ellipse at center, rgba(0,0,0,0) 60%, rgba(0,0,0,0.22) 100%); }
  .fade { position:absolute; inset:0; background: transparent; }

  @keyframes driftX {
    0% { transform: translateX(-10%); }
    100% { transform: translateX(10%); }
  }
  @keyframes driftY {
    0% { transform: translateY(-8%); }
    100% { transform: translateY(8%); }
  }
  @keyframes hueShift {
    0% { filter: hue-rotate(0deg); }
    100% { filter: hue-rotate(12deg); }
  }
</style>
