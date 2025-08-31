<script>
  import { onMount, onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { getPlayers } from './api.js';
  import { getCharacterImage, getHourlyBackground, getRandomFallback, getElementColor } from './assetLoader.js';
  import MenuPanel from './MenuPanel.svelte';
  import PartyRoster from './PartyRoster.svelte';
  import PlayerPreview from './PlayerPreview.svelte';
  import StatTabs from './StatTabs.svelte';
  import { browser, dev } from '$app/environment';

  let background = '';
  let roster = [];

  export let selected = [];
  export let compact = false;
  let previewId;
  export let reducedMotion = false;
  // Label for the primary action; overlays set this to "Save Party" or "Start Run"
  export let actionLabel = 'Save Party';
  // Pressure level for run difficulty
  let pressure = 0;
  const dispatch = createEventDispatcher();
  let previewElementOverride = '';
  // Clear override when preview is not the player
  $: {
    const cur = roster.find(r => r.id === previewId);
    if (!cur?.is_player) previewElementOverride = '';
  }

  // Starfield background tied to current preview element color
  function rand(min, max) { return Math.random() * (max - min) + min; }
  function spawnStar(color) {
    // Default to current starColor if none provided
    const c = color || starColor || '#88a';
    return {
      left: Math.random() * 100,
      size: rand(3, 6),
      duration: rand(6, 14),
      delay: rand(0, 6),
      drift: rand(-20, 20),
      color: c
    };
  }
  function makeStars(count, color) {
    return Array.from({ length: count }, () => spawnStar(color));
  }
  let density = 140;
  let stars = [];
  $: currentElementName = (() => {
    const cur = roster.find(r => r.id === previewId);
    const el = previewElementOverride || (cur && cur.element) || '';
    return el ? String(el) : '';
  })();
  $: starColor = currentElementName ? (() => { try { return getElementColor(currentElementName); } catch { return ''; } })() : '';

  // Global fade pulse helper
  let fading = false;
  function fadePulse(dur = 260, low = 0.25) {
    // use CSS transition on .stars to dip opacity, then restore
    fading = true;
    clearTimeout(fadeTimer);
    fadeTimer = setTimeout(() => { fading = false; }, dur);
  }
  let fadeTimer;

  // Initialize stars once we have a color (delay spawn until element known)
  $: if (stars.length === 0 && starColor) {
    stars = makeStars(density, starColor);
    fadePulse(260);
  }

  // Gradual color transition: on change, slowly replace existing stars
  let lastStarColor = '';
  let replaceTimer = null;
  let forceTimer = null;
  function startColorTransition() {
    if (!starColor) return;
    if (replaceTimer) clearInterval(replaceTimer);
    if (forceTimer) clearTimeout(forceTimer);
    fadePulse(260);
    // Build a deterministic pool of indices that still have the old color
    let pool = stars
      .map((s, i) => ({ s, i }))
      .filter(({ s }) => s.color !== starColor)
      .map(({ i }) => i);
    if (pool.length === 0) return;
    // Compute batch size to finish around target duration
    const intervalMs = 120;
    const targetMs = 1800;
    const ticks = Math.max(1, Math.round(targetMs / intervalMs));
    const batch = Math.max(1, Math.ceil(pool.length / ticks));
    replaceTimer = setInterval(() => {
      const n = Math.min(batch, pool.length);
      for (let k = 0; k < n; k++) {
        const idx = pool.pop();
        if (idx == null) break;
        // Use the latest starColor at replacement time
        stars[idx] = spawnStar();
      }
      stars = stars.slice();
      if (pool.length === 0) {
        clearInterval(replaceTimer);
        replaceTimer = null;
      }
    }, intervalMs);
    // Safety: force any remaining to new color shortly after target
    forceTimer = setTimeout(() => {
      if (pool.length > 0) {
        stars = stars.map(s => (s.color === starColor ? s : spawnStar()));
      }
      if (replaceTimer) { clearInterval(replaceTimer); replaceTimer = null; }
    }, targetMs + 400);
  }
  $: if (starColor && lastStarColor && starColor !== lastStarColor) {
    startColorTransition();
  }
  $: lastStarColor = starColor;

  onDestroy(() => {
    if (replaceTimer) clearInterval(replaceTimer);
    if (fadeTimer) clearTimeout(fadeTimer);
    if (forceTimer) clearTimeout(forceTimer);
  });

  onMount(async () => {
    background = getHourlyBackground();
    try {
      const data = await getPlayers();
      function resolveElement(p) {
        let e = p?.element;
        if (e && typeof e !== 'string') e = e.id || e.name;
        return e && !/generic/i.test(String(e)) ? e : 'Generic';
      }
      roster = data.players
        .map((p) => ({
          id: p.id,
          name: p.name,
          img: getCharacterImage(p.id, p.is_player) || getRandomFallback(),
          owned: p.owned,
          is_player: p.is_player,
          element: resolveElement(p),
          stats: p.stats ?? { hp: 0, atk: 0, defense: 0, level: 1 }
        }))
        .filter((p) => p.owned || p.is_player)
        .sort((a, b) => (a.is_player ? -1 : b.is_player ? 1 : 0));
      selected = selected.filter((id) => roster.some((c) => c.id === id));
      const player = roster.find((p) => p.is_player);
      if (player) {
        if (selected.length === 0) {
          selected = [player.id];
        }
        previewId = selected[0] ?? player.id;
      }
    } catch (e) {
      if (dev || !browser) {
        const { error } = await import('$lib/logger.js');
        error('Unable to load roster. Is the backend running on 59002?');
      }
    }
  });

  function toggleMember(id) {
    if (!id) return;
    if (selected.includes(id)) {
      selected = selected.filter((c) => c !== id);
    } else if (selected.length < 4) {
      selected = [...selected, id];
    }
  }
</script>

{#if compact}
  <PartyRoster {roster} {selected} bind:previewId {compact} {reducedMotion} on:toggle={(e) => toggleMember(e.detail)} />
{:else}
  <MenuPanel style={`background-image: url(${background}); background-size: cover;`}>
    <div class="full" data-testid="party-picker">
      <!-- Starfield background layer (behind content) -->
      <div class="stars" aria-hidden="true" style={`opacity:${fading ? 0.25 : 0.55}`}> 
        {#each stars as s}
          <span class="star" style={`--x:${s.left}%; --s:${s.size}px; --d:${s.duration}s; --delay:${s.delay}s; --dx:${s.drift}px; --c:${s.color};`}>
            <span class="core"></span>
          </span>
        {/each}
      </div>
      <PartyRoster {roster} {selected} bind:previewId {reducedMotion} on:toggle={(e) => toggleMember(e.detail)} />
      <PlayerPreview {roster} {previewId} overrideElement={previewElementOverride} />
      <div class="right-col">
        <StatTabs {roster} {previewId} {selected}
          on:toggle={(e) => toggleMember(e.detail)}
          on:preview-element={(e) => {
            const el = e.detail.element;
            previewElementOverride = el;
            // Also update the player's element in the roster so the left list reflects it
            roster = roster.map(r => r.is_player ? { ...r, element: el } : r);
            // Bubble an editor change so top-level editorState stays in sync for Start Run
            try { dispatch('editorChange', { damageType: el }); } catch {}
          }}
        />
        <div class="party-actions-inline">
          {#if actionLabel === 'Start Run'}
            <div class="pressure-inline" aria-label="Pressure Level Controls">
              <span class="pressure-inline-label">Pressure</span>
              <button class="pressure-btn" on:click={() => pressure = Math.max(0, pressure - 1)} disabled={pressure <= 0}>
                ◀
              </button>
              <span class="pressure-value" data-testid="pressure-value">{pressure}</span>
              <button class="pressure-btn" on:click={() => pressure = pressure + 1}>
                ▶
              </button>
            </div>
          {/if}
          <button class="wide" on:click={() => dispatch('save', { pressure })}>{actionLabel}</button>
          <button class="wide" on:click={() => dispatch('cancel')}>Cancel</button>
        </div>
      </div>
    </div>
  </MenuPanel>
{/if}

<style>
  .full {
    display: grid;
    grid-template-columns: minmax(8rem, 22%) 1fr minmax(12rem, 26%);
    width: 100%;
    height: 96%;
    max-width: 100%;
    max-height: 98%;
    /* allow internal scrolling instead of clipping when content grows */
    position: relative;
    z-index: 0; /* establish stacking context so stars can sit behind */
  }
  .right-col { display: flex; flex-direction: column; min-height: 0; }
  
  .pressure-controls { margin-top: 0.5rem; }
  .pressure-label { display: block; color: #fff; font-size: 0.9rem; margin-bottom: 0.3rem; text-align: center; }
  .pressure-input { display: flex; align-items: center; justify-content: center; gap: 0.5rem; }
  .pressure-btn { 
    background: rgba(0,0,0,0.5); 
    border: 1px solid rgba(255,255,255,0.35); 
    color: #fff; 
    padding: 0.3rem 0.5rem; 
    cursor: pointer;
    border-radius: 3px;
  }
  .pressure-btn:hover:not(:disabled) { 
    background: rgba(255,255,255,0.1); 
  }
  .pressure-btn:disabled { 
    opacity: 0.5; 
    cursor: not-allowed; 
  }
  .pressure-value { 
    color: #fff; 
    font-weight: bold; 
    min-width: 2rem; 
    text-align: center; 
  }
  /* Inline row containing pressure + primary actions */
  .party-actions-inline { display:flex; align-items:center; gap:0.5rem; margin-top: 0.5rem; }
  .pressure-inline { display:flex; align-items:center; gap:0.4rem; padding: 0.2rem 0.4rem; }
  .pressure-inline-label { color:#fff; opacity:0.85; font-size: 0.9rem; margin-right: 0.1rem; }
  .party-actions-inline .wide { flex: 1; border: 1px solid rgba(255,255,255,0.35); background: rgba(0,0,0,0.5); color:#fff; padding: 0.45rem 0.8rem; }

  /* Falling starfield */
  .stars { position:absolute; inset:0; overflow:hidden; pointer-events:none; z-index:-1; opacity: 0.55; transition: opacity 220ms ease; }
  /* Parent handles vertical fall + opacity */
  .star {
    position: absolute;
    top: -10%;
    left: var(--x);
    width: 0;  /* visuals live in .core */
    height: 0; /* prevents layout shifts */
    animation-name: af-fallTop;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
    animation-duration: var(--d);
    animation-delay: var(--delay);
  }
  /* Child handles horizontal drift and the visual shape */
  .star .core {
    position: absolute;
    top: 0;
    left: 0;
    width: var(--s);
    height: var(--s);
    background: radial-gradient(circle, var(--c) 0%, transparent 70%);
    border-radius: 50%;
    filter: drop-shadow(0 0 8px color-mix(in srgb, var(--c) 70%, transparent));
    animation-name: af-drift;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
    animation-duration: var(--d);
    animation-delay: var(--delay);
  }
  .star .core::after {
    content: '';
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    top: calc(var(--s) * -8);
    width: calc(max(2px, var(--s) * 0.4));
    height: calc(var(--s) * 10);
    background: linear-gradient(180deg, color-mix(in srgb, var(--c) 75%, transparent) 0%, transparent 70%);
    filter: blur(1px);
  }
  @keyframes af-fallTop {
    0% { top: -10%; opacity: 0.0; }
    10% { opacity: 1.0; }
    90% { opacity: 1.0; }
    100% { top: 110%; opacity: 0.0; }
  }
  @keyframes af-drift {
    0% { transform: translateX(0); }
    100% { transform: translateX(var(--dx)); }
  }

  /* Respect reduced motion */
  :global(html.reduced-motion) .stars .star,
  :global(body.reduced-motion) .stars .star { animation: none; opacity: 0.35; top: 15%; }
  :global(html.reduced-motion) .stars .star .core,
  :global(body.reduced-motion) .stars .star .core { animation: none; }
  </style>
