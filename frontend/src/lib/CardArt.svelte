<script>
  export let entry = {};
  export let type = 'card';
  export let roundIcon = false;
  export let size = 'normal';
  export let hideFallback = false;
  // When true, suppress ambient marks and border twinkles for cleaner embedding (e.g., shop)
  export let quiet = false;
  import { getHourlyBackground } from './assetLoader.js';
  import { getGlyphArt } from './rewardLoader.js';
  const starColors = {
    1: '#808080',
    2: '#228B22',
    3: '#1E90FF',
    4: '#800080',
    5: '#FFD700',
    fallback: '#708090'
  };
  $: width = size === 'small' ? 140 : 280;
  // Fixed card height so top box can be exactly 50%
  $: cardHeight = size === 'small' ? 320 : 440;
  $: color = starColors[entry.stars] || starColors.fallback;
  // Background image for the interbox (top section)
  // Use special art for specific relics when available.
  let bg = getHourlyBackground();
  $: {
    const custom = getGlyphArt(type, entry);
    bg = custom || getHourlyBackground();
  }
  // Ambient floating gray marks under the glyph box
  function rand(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
  function makeMarks(count) {
    return Array.from({ length: count }, () => ({
      left: Math.random() * 90 + 5, // percent
      top: Math.random() * 70 + 10, // percent
      size: rand(6, 16),            // px
      duration: rand(30, 60),       // seconds
      delay: rand(0, 20),           // seconds
      dx: rand(-24, 24),            // px
      dy: rand(-12, 12),            // px
    }));
  }
  let marks = [];
  $: marks = quiet ? [] : makeMarks(size === 'small' ? 14 : 24);
  // Border twinkles configuration
  function makeTwinkles(count) {
    const sides = ['top','right','bottom','left'];
    const shapes = ['dot','cross','diamond','dot']; // bias towards dots
    return Array.from({ length: count }, () => ({
      side: sides[Math.floor(Math.random() * sides.length)],
      pos: Math.random() * 100,       // 0-100%
      size: rand(4, 9),               // px
      duration: rand(4, 9),           // seconds
      delay: rand(0, 8),              // seconds
      shape: shapes[Math.floor(Math.random() * shapes.length)]
    }));
  }
  let twinkles = [];
  $: starRank = Math.max(1, Math.min(Number(entry?.stars || 1), 5));
  $: baseTwinkles = size === 'small' ? 16 : 28;
  // Slightly increase baseline twinkle intensity for 1-star
  $: twinkleFactor = 1.2 + (starRank - 1) * 0.6;
  $: twinkleCount = Math.round(baseTwinkles * twinkleFactor);
  // Nudge baseline alpha so 1-star is a bit more visible
  $: twinkleAlpha = Math.min(0.85, 0.60 + (starRank - 1) * 0.08);
  $: twinkles = quiet ? [] : makeTwinkles(twinkleCount);
</script>

<div class="card-art" style={`width:${width}px; height:${cardHeight}px; --accent:${color}; --twA:${twinkleAlpha}` }>
  <div class="topbox" style={`--accent:${color}`}>
    <div class="title">{entry.name}</div>
    <div class={`glyph${roundIcon ? ' round' : ''}`}>
      <div class="glyph-bg" style={`background-image:url(${bg})`}></div>
      <div class="glyph-ambient">
        {#each marks as m}
          <span
            class="mark"
            style={`left:${m.left}%; top:${m.top}%; width:${m.size}px; height:${m.size}px; animation-duration:${m.duration}s; animation-delay:${m.delay}s; --dx:${m.dx}px; --dy:${m.dy}px;`}
          />
        {/each}
      </div>
      <div class="stars-overlay">{'★'.repeat(entry.stars || 0)}</div>
    </div>
  </div>
  {#if entry.about}
    <div class="about-box">{entry.about}</div>
  {/if}
  <div class="twinkles" aria-hidden="true">
    {#each twinkles as t}
      <span
        class={`twinkle s-${t.side} shape-${t.shape}`}
        style={`--p:${t.pos}%; --s:${t.size}px; animation-duration:${t.duration}s; animation-delay:${t.delay}s;`}
      />
    {/each}
  </div>
</div>

<style>
  .card-art {
    background: linear-gradient(180deg, rgba(0,0,0,0.65), rgba(0,0,0,0.45));
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 10px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    color: #fff;
    box-shadow: 0 2px 10px rgba(0,0,0,0.35);
    backdrop-filter: blur(6px);
    position: relative;
    box-sizing: border-box;
  }
  .topbox {
    position: relative;
    height: 50%;
    width: 100%;
    background: var(--accent);
    background-image: linear-gradient(180deg, rgba(0,0,0,0.1), rgba(0,0,0,0.25));
    display: grid;
    grid-template-rows: auto 1fr;
    align-items: stretch;
    justify-items: stretch;
    padding: 6px 8px;
    box-sizing: border-box;
  }
  .glyph-bg {
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center;
    filter: saturate(0.9) contrast(1.05);
    opacity: 0.65; /* make image less faded across cards/relics */
    z-index: 0; /* bottom-most inside glyph */
    border-radius: inherit;
  }
  .glyph-ambient {
    position: absolute;
    inset: 0;
    overflow: hidden;
    z-index: 2; /* above image, below stars */
    border-radius: inherit;
  }
  .mark {
    position: absolute;
    background: rgba(200,200,200,0.16);
    border-radius: 50%;
    filter: blur(0.6px);
    animation-name: drift;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
    animation-direction: alternate;
  }
  @keyframes drift {
    from { transform: translate(0, 0); }
    to { transform: translate(var(--dx), var(--dy)); }
  }
  .title {
    justify-self: start;
    align-self: start;
    font-weight: 700;
    font-size: 0.95rem;
    color: #fff;
    text-shadow: 0 1px 2px rgba(0,0,0,0.45);
    z-index: 1;
  }
  .glyph {
    display: flex;
    align-items: center;
    justify-content: center;
    justify-self: stretch;
    align-self: stretch;
    width: 100%;
    max-width: none;
    color: #fff;
    font-weight: 800;
    font-size: 2rem;
    letter-spacing: 1px;
    background: radial-gradient(ellipse at 50% 40%, rgba(255,255,255,0.08), rgba(0,0,0,0.0) 60%),
                linear-gradient(180deg, rgba(0,0,0,0.20), rgba(0,0,0,0.45));
    border: 2px solid rgba(255,255,255,0.18);
    box-shadow: 0 2px 10px rgba(0,0,0,0.35), inset 0 0 0 2px var(--accent);
    border-radius: 10px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.4);
    position: relative;
    margin-top: 6px;
    z-index: 1; /* glyph content base; specific layers override */
  }
  /* Border twinkles around the card outline */
  .twinkles {
    position: absolute;
    inset: 0;
    z-index: 2; /* above base, below glyph stars overlay applies only within glyph */
    pointer-events: none;
    border-radius: inherit;
  }
  .twinkle {
    position: absolute;
    width: var(--s);
    height: var(--s);
    opacity: 0;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255, var(--twA)) 0%, color-mix(in srgb, var(--accent) 60%, transparent) 55%, transparent 70%);
    box-shadow:
      0 0 4px color-mix(in srgb, var(--accent) 65%, transparent),
      0 0 10px color-mix(in srgb, var(--accent) 45%, transparent);
    animation-name: twinkle-pop;
    animation-timing-function: ease-in-out;
    animation-iteration-count: infinite;
  }
  /* Shape variants */
  .twinkle.shape-dot { border-radius: 50%; }
  .twinkle.shape-cross { border-radius: 0; background: none; }
  .twinkle.shape-diamond { border-radius: 2px; transform: rotate(45deg); }

  .twinkle.shape-diamond {
    background:
      radial-gradient(circle at 50% 50%, rgba(255,255,255,var(--twA)) 0%, transparent 70%);
    box-shadow:
      0 0 4px color-mix(in srgb, var(--accent) 65%, transparent),
      0 0 10px color-mix(in srgb, var(--accent) 45%, transparent);
  }
  .twinkle.shape-cross::before,
  .twinkle.shape-cross::after {
    content: '';
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    background: linear-gradient(
      to right,
      transparent,
      color-mix(in srgb, var(--accent) 55%, rgba(255,255,255,var(--twA))),
      transparent
    );
    filter: drop-shadow(0 0 6px color-mix(in srgb, var(--accent) 55%, transparent));
    border-radius: 2px;
  }
  .twinkle.shape-cross::before { width: calc(var(--s) * 1.6); height: calc(var(--s) * 0.18); }
  .twinkle.shape-cross::after  { width: calc(var(--s) * 0.18); height: calc(var(--s) * 1.6); }
  /* Side placement helpers */
  .twinkle.s-top { top: 2px; left: var(--p); }
  .twinkle.s-bottom { bottom: 2px; left: var(--p); }
  .twinkle.s-left { left: 2px; top: var(--p); }
  .twinkle.s-right { right: 2px; top: var(--p); }

  @keyframes twinkle-pop {
    0%, 75%, 100% { opacity: 0; transform: scale(0.3); }
    12% { opacity: 0.6; transform: scale(1); }
    20% { opacity: 0.9; }
    35% { opacity: 0.25; transform: scale(0.8); }
    50% { opacity: 0.0; transform: scale(0.4); }
  }
  .glyph.round {
    justify-self: center;
    align-self: center;
    width: 70%;
    max-width: 180px;
    aspect-ratio: 1 / 1;
    border-radius: 50%;
  }
  .stars-overlay {
    position: absolute;
    bottom: 6px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.95rem;
    text-shadow: 0 1px 2px rgba(0,0,0,0.35);
    pointer-events: none;
    z-index: 3; /* above glyph image and orbs */
  }
  .about-box {
    flex: 1;
    margin: 0;
    background: rgba(0,0,0,0.45);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 0;
    padding: 10px 12px;
    font-size: 0.9rem;
    line-height: 1.25;
    color: #fff;
    text-shadow: 0 1px 2px rgba(0,0,0,0.25);
    box-sizing: border-box;
  }
</style>
