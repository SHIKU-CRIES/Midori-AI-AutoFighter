<script>
  // Ambient enrage rain during combat; gently despawn after combat ends.
  export let active = false;        // true while combat is running
  export let reducedMotion = false; // respect settings
  export let enrageData = { active: false, stacks: 0, turns: 0 }; // enrage state data

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

  function makeOrb(intensity = 0) {
    const hue = redOrBlueHue(); // only red or blue
    // Map intensity to visual parameters: more intense = longer, slightly thicker, faster
    // intensity is [0..1]
    const minLen = 12;   // rem units for CSS conversion below
    const maxLen = 36;
    const minThick = 0.05; // rem
    const maxThick = 0.12; // rem
    const len = rand(minLen, minLen + (maxLen - minLen) * (0.35 + 0.65 * intensity));
    const thick = rand(minThick, minThick + (maxThick - minThick) * (0.25 + 0.75 * intensity));
    const baseFallMin = 2.2; // seconds
    const baseFallMax = 5.5;
    const speedScale = 1 - 0.55 * intensity; // up to ~45% faster at max intensity
    const fallMin = baseFallMin * speedScale;
    const fallMax = baseFallMax * speedScale;
    const slant = rand(4, 12); // % drift across X during fall
    return {
      id: Math.random().toString(36).slice(2),
      x: rand(0, 100),
      y: rand(-20, 0), // Start above the viewport for rain effect
      len,
      thick,
      fallSpeed: rand(fallMin, fallMax),
      delay: rand(0, 2.2),
      slant,
      hue,
    };
  }

  function calculateOrbCount() {
    if (!active) return 0;
    // Base/min count to keep subtle ambience; respects Reduced Motion
    // Increase lower-end density for non-reduced motion
    const minCount = reducedMotion ? 4 : 22;
    if (!enrageData.active) return minCount;

    // Intensity scales to 1.0 at 10,000 stacks/turns, then clamps
    const stacks = Math.max(Number(enrageData?.stacks || enrageData?.turns || 0), 0);
    const intensity = Math.min(stacks / 10000, 1);
    // Heavier ceiling for non-reduced motion (increase upper bound as requested)
    const maxCount = reducedMotion ? 40 : 360;
    return Math.round(minCount + intensity * (maxCount - minCount));
  }

  $: if (active) {
    ending = false;
    const targetCount = calculateOrbCount();
    if (orbs.length !== targetCount) {
      const stacks = Math.max(Number(enrageData?.stacks || enrageData?.turns || 0), 0);
      const intensity = Math.min(stacks / 10000, 1);
      orbs = Array.from({ length: targetCount }, () => makeOrb(intensity));
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
      style={`--x:${orb.x};--y:${orb.y};--thick:${orb.thick}rem;--len:${orb.len}rem;--fallSpeed:${orb.fallSpeed}s;--hue:${orb.hue};--delay:${orb.delay}s;--slant:${orb.slant}%;`}
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
    width: var(--thick);
    height: var(--len);
    filter: blur(0.3px);
    animation: rainFall var(--fallSpeed) linear infinite;
    animation-delay: var(--delay);
  }
  .orb .i {
    width: 100%; height: 100%;
    background: linear-gradient(
      to bottom,
      hsla(var(--hue), 95%, 70%, 0.00) 0%,
      hsla(var(--hue), 95%, 65%, 0.35) 20%,
      hsla(var(--hue), 95%, 60%, 0.50) 55%,
      hsla(var(--hue), 95%, 55%, 0.25) 85%,
      hsla(var(--hue), 95%, 70%, 0.00) 100%
    );
    transform: skewX(-12deg);
    animation: hueShift 12s linear infinite;
    mix-blend-mode: screen;
    box-shadow: 0 0 8px hsla(var(--hue), 95%, 60%, 0.20);
  }

  .enrage-orbs.reduced .orb { animation: none; }
  .enrage-orbs.reduced .orb .i { animation: none; opacity: 0.55; }

  .vignette { position:absolute; inset:0; background: radial-gradient(ellipse at center, rgba(0,0,0,0) 60%, rgba(0,0,0,0.22) 100%); }
  .fade { position:absolute; inset:0; background: transparent; }

  @keyframes rainFall {
    0% { 
      transform: translateY(-20vh) translateX(0);
    }
    100% { 
      transform: translateY(120vh) translateX(var(--slant));
    }
  }
  @keyframes hueShift {
    0% { filter: hue-rotate(0deg); }
    100% { filter: hue-rotate(8deg); }
  }
</style>
