<script>
  export let entry = {};
  export let type = 'card';
  export let roundIcon = false;
  export let size = 'normal';
  export let hideFallback = false;
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
  // Ambient floating gray marks under the glyph box
  function rand(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
  const markCount = 8;
  const marks = Array.from({ length: markCount }, () => ({
    left: Math.random() * 90 + 5, // percent
    top: Math.random() * 70 + 10, // percent
    size: rand(8, 18),            // px
    duration: rand(30, 60),       // seconds
    delay: rand(0, 20),           // seconds
    dx: rand(-24, 24),            // px
    dy: rand(-12, 12),            // px
  }));
</script>

<div class="card-art" style={`width:${width}px; height:${cardHeight}px`}>
  <div class="topbox" style={`--accent:${color}`}>
    <div class="ambient">
      {#each marks as m}
        <span
          class="mark"
          style={`left:${m.left}%; top:${m.top}%; width:${m.size}px; height:${m.size}px; animation-duration:${m.duration}s; animation-delay:${m.delay}s; --dx:${m.dx}px; --dy:${m.dy}px;`}
        />
      {/each}
    </div>
    <div class="title">{entry.name}</div>
    <div class={`glyph${roundIcon ? ' round' : ''}`}>
      <div class="stars-overlay">{'★'.repeat(entry.stars || 0)}</div>
    </div>
  </div>
  {#if entry.about}
    <div class="about-box">{entry.about}</div>
  {/if}
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
  .ambient {
    position: absolute;
    inset: 0;
    overflow: hidden;
    z-index: 0;
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
    z-index: 1;
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
    z-index: 2;
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
