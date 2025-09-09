<script>
  import { onMount } from 'svelte';
  import { Zap, Sparkles, LayoutPanelTop, ShoppingCart, Cog, ScrollText } from 'lucide-svelte';
  import { httpGet } from '$lib/systems/httpClient.js';

  let activeTab = 'damage';

  let damageTypes = [];
  let ultimates = [];
  let passives = [];
  let uiTips = [];
  let shopInfo = null;
  let mechs = [];

  async function loadDamage() {
    const data = await httpGet('/guidebook/damage-types', { cache: 'no-store' }, true);
    damageTypes = data?.damage_types || [];
  }
  async function loadUlts() {
    const data = await httpGet('/guidebook/ultimates', { cache: 'no-store' }, true);
    ultimates = data?.ultimates || [];
  }
  async function loadPassives() {
    const data = await httpGet('/guidebook/passives', { cache: 'no-store' }, true);
    passives = data?.passives || [];
  }
  async function loadUI() {
    const data = await httpGet('/guidebook/ui', { cache: 'no-store' }, true);
    uiTips = data?.tips || [];
  }
  async function loadShops() {
    const data = await httpGet('/guidebook/shops', { cache: 'no-store' }, true);
    shopInfo = data || null;
  }
  async function loadMechs() {
    const data = await httpGet('/guidebook/mechs', { cache: 'no-store' }, true);
    mechs = data?.mechanics || [];
  }

  async function ensureTabLoaded(key) {
    if (key === 'damage' && damageTypes.length === 0) await loadDamage();
    if (key === 'ults' && ultimates.length === 0) await loadUlts();
    if (key === 'ui' && uiTips.length === 0) await loadUI();
    if (key === 'shops' && !shopInfo) await loadShops();
    if (key === 'mechs' && mechs.length === 0) await loadMechs();
    if (key === 'passives' && passives.length === 0) await loadPassives();
  }

  onMount(async () => {
    await ensureTabLoaded(activeTab);
  });

  function colorStyle(rgb) {
    if (!rgb || !Array.isArray(rgb) || rgb.length !== 3) return '';
    const [r,g,b] = rgb;
    return `background: rgba(${r},${g},${b},0.35); border-color: rgba(${r},${g},${b},0.9);`;
  }
</script>

<div class="tabbed" data-testid="guidebook">
  <div class="tabs">
    <button class:active={activeTab === 'damage'} on:click={async () => { activeTab = 'damage'; await ensureTabLoaded('damage'); }} title="Damage Types"><Zap /></button>
    <button class:active={activeTab === 'ults'} on:click={async () => { activeTab = 'ults'; await ensureTabLoaded('ults'); }} title="Ults"><Sparkles /></button>
    <button class:active={activeTab === 'ui'} on:click={async () => { activeTab = 'ui'; await ensureTabLoaded('ui'); }} title="UI"><LayoutPanelTop /></button>
    <button class:active={activeTab === 'shops'} on:click={async () => { activeTab = 'shops'; await ensureTabLoaded('shops'); }} title="Shops"><ShoppingCart /></button>
    <button class:active={activeTab === 'mechs'} on:click={async () => { activeTab = 'mechs'; await ensureTabLoaded('mechs'); }} title="Mechs"><Cog /></button>
    <button class:active={activeTab === 'passives'} on:click={async () => { activeTab = 'passives'; await ensureTabLoaded('passives'); }} title="Passives"><ScrollText /></button>
  </div>

  {#if activeTab === 'damage'}
    <div class="panel list">
      {#each damageTypes as d}
        <div class="entry" style={colorStyle(d.color)}>
          <div class="entry-head">
            <span class="pill">{d.id}</span>
            {#if d.weakness}
              <span class="sub">Weak to {d.weakness}</span>
            {/if}
          </div>
          <p class="desc">{d.description || ''}</p>
        </div>
      {/each}
    </div>
  {:else if activeTab === 'ults'}
    <div class="panel list">
      {#each ultimates as u}
        <div class="entry">
          <div class="entry-head">
            <span class="pill">{u.id}</span>
          </div>
          <p class="desc">{u.description || ''}</p>
        </div>
      {/each}
    </div>
  {:else if activeTab === 'ui'}
    <div class="panel list">
      {#each uiTips as tip}
        <div class="entry">
          <div class="entry-head">
            <span class="pill">{tip.name}</span>
          </div>
          <p class="desc">{tip.description}</p>
        </div>
      {/each}
    </div>
  {:else if activeTab === 'shops'}
    <div class="panel list">
      <div class="entry">
        <div class="entry-head">
          <span class="pill">Shop Basics</span>
        </div>
        {#if shopInfo}
          <ul class="bullets">
            <li>Reroll Cost: {shopInfo.reroll_cost}</li>
            <li>Price by Stars: {#each Object.entries(shopInfo.price_by_stars || {}) as [stars, price]}<span class="kv">{stars}★ → {price}</span>{#if stars != Object.keys(shopInfo.price_by_stars).slice(-1)[0]}<span class="sep">, </span>{/if}{/each}</li>
          </ul>
        {/if}
      </div>
    </div>
  {:else if activeTab === 'mechs'}
    <div class="panel list">
      {#each mechs as m}
        <div class="entry">
          <div class="entry-head">
            <span class="pill">{m.name}</span>
          </div>
          <p class="desc">{m.description}</p>
        </div>
      {/each}
    </div>
  {:else if activeTab === 'passives'}
    <div class="panel list">
      {#each passives as p}
        <div class="entry">
          <div class="entry-head">
            <span class="pill">{p.name || p.id}</span>
            {#if p.trigger}<span class="sub">Trigger: {p.trigger}</span>{/if}
          </div>
          <p class="desc">{p.description || ''}</p>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .tabbed { min-width: 720px; min-height: 420px; }
  .tabs { display: flex; gap: 0.5rem; margin-bottom: 0.5rem; }
  .tabs button { border: 2px solid #fff; background: #0a0a0a; color: #fff; padding: 0.3rem; display: flex; align-items: center; justify-content: center; }
  .tabs button.active { background: #fff; color: #0a0a0a; }
  .panel.list { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 0.6rem; }
  .entry { border: 1px solid rgba(255,255,255,0.35); background: rgba(255,255,255,0.06); padding: 0.6rem; box-shadow: 0 1px 4px rgba(0,0,0,0.2); }
  .entry-head { display: flex; gap: 0.5rem; align-items: center; justify-content: space-between; }
  .pill { font-weight: 600; border: 1px solid rgba(255,255,255,0.6); padding: 0.1rem 0.4rem; }
  .sub { font-size: 0.8rem; opacity: 0.9; }
  .desc { margin: 0.4rem 0 0; font-size: 0.9rem; line-height: 1.2; }
  .bullets { margin: 0.2rem 0 0.1rem; padding-left: 1rem; }
  .kv { display: inline-block; margin-right: 0.2rem; }
  .sep { opacity: 0.6; }
  @media (max-width: 800px) { .tabbed { min-width: 100%; } }
</style>

