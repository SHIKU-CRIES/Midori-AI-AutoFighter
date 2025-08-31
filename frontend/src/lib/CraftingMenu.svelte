<script>
  import { createEventDispatcher, onMount } from 'svelte';

  import { getGacha, setAutoCraft, craftItems } from './systems/api.js';
  import MenuPanel from './MenuPanel.svelte';
  import { stackItems, formatName } from './systems/craftingUtils.js';

  const rawIconModules = import.meta.glob('./assets/items/*/*.png', {
    eager: true,
    import: 'default',
    query: '?url'
  });
  const iconModules = Object.fromEntries(
    Object.entries(rawIconModules).map(([path, src]) => [path, new URL(src, import.meta.url).href])
  );
  // Use a stable item placeholder instead of card placeholder
  const fallbackIcon = new URL('./assets/items/generic/generic1.png', import.meta.url).href;

  const starColors = {
    1: '#808080',  // gray
    2: '#1E90FF',  // blue
    3: '#228B22',  // green
    4: '#800080',  // purple
    5: '#FF3B30',  // red
    6: '#FFD700',  // gold
    fallback: '#708090'
  };

  function onIconError(event) {
    event.target.src = fallbackIcon;
  }

  function getIcon(key) {
    const [rawElement, rawRank] = String(key).split('_');
    const element = String(rawElement || '').toLowerCase();
    const rank = String(rawRank || '').replace(/[^0-9]/g, '') || '1';

    // 1) Prefer a rank-specific file in the element folder: `${rank}.png`
    const rankPath = `./assets/items/${element}/${rank}.png`;
    if (iconModules[rankPath]) return iconModules[rankPath];

    // 2) Otherwise, use any file from the element folder (prefer `generic{rank}.png`)
    const elementPrefix = `./assets/items/${element}/`;
    const elementKeys = Object.keys(iconModules).filter((p) => p.startsWith(elementPrefix));
    const genericRankPath = `${elementPrefix}generic${rank}.png`;
    if (iconModules[genericRankPath]) return iconModules[genericRankPath];
    if (elementKeys.length > 0) return iconModules[elementKeys[0]];

    // 3) Finally, try the generic rank file, then the static fallback icon
    const genericPath = `./assets/items/generic/generic${rank}.png`;
    return iconModules[genericPath] || fallbackIcon;
  }

  function getStarColor(key) {
    const rank = parseInt(String(key).split('_')[1]);
    return starColors[rank] || starColors.fallback;
  }

  const dispatch = createEventDispatcher();
  let items = {};
  let autoCraft = false;
  let selected = null;
  let craftable = false;
  let selectedRequirement = 0;

  onMount(async () => {
    const state = await getGacha();
    items = stackItems(state.items);
    autoCraft = state.auto_craft || false;
  });

  async function craft() {
    const res = await craftItems();
    items = stackItems(res.items);
  }

  async function toggleAuto() {
    autoCraft = !autoCraft;
    await setAutoCraft(autoCraft);
  }

  function close() {
    dispatch('close');
  }

  function getRequirement(key) {
    const rank = parseInt(String(key).split('_')[1]);
    if (rank >= 1 && rank <= 3) return 125;
    if (rank === 4) return 10;
    return 0;
  }

  $: craftable = Object.entries(items).some(([key, count]) => {
    const req = getRequirement(key);
    return req > 0 && count >= req;
  });

  $: selectedRequirement = selected ? getRequirement(selected) : 0;
</script>

<MenuPanel data-testid="crafting-menu">
  <h3>Crafting</h3>
  <div class="content">
    <div class="items-grid">
      {#each Object.entries(items) as [key, value]}
        <button
          class="grid-item"
          style={`--star-color: ${getStarColor(key)}`}
          on:click={() => (selected = key)}
          title={formatName(key)}
        >
          <img
            class="item-icon"
            src={getIcon(key)}
            alt={key}
            on:error={onIconError}
          />
          <span class="badge">{value}</span>
        </button>
      {/each}
    </div>
    <div class="detail">
      {#if selected}
        <img
          class="detail-icon"
          style={`--star-color: ${getStarColor(selected)}`}
          src={getIcon(selected)}
          alt={selected}
          on:error={onIconError}
        />
        <div class="detail-name">{formatName(selected)}</div>
        <div class="detail-count">
          x{items[selected]}{#if selectedRequirement} / {selectedRequirement}{/if}
        </div>
      {:else}
        <p class="placeholder">Select an item</p>
      {/if}
    </div>
  </div>
  <div class="actions">
    <label>
      <input type="checkbox" bind:checked={autoCraft} on:change={toggleAuto} />
      Auto-craft
    </label>
    <button on:click={craft} disabled={!craftable}>Craft</button>
    <button on:click={close}>Done</button>
  </div>
</MenuPanel>

<style>
  .content {
    display: grid;
    grid-template-columns: 1fr 220px; /* grid fills left; fixed detail width */
    gap: 0.75rem;
    align-items: start;
  }

  .items-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(48px, 1fr));
    gap: 0.5rem;
  }

  .grid-item {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    aspect-ratio: 1 / 1;
    background: transparent;
    border: none;
    padding: 0;
    cursor: pointer;
  }

  .item-icon {
    width: 100%;
    height: 100%;
    object-fit: contain;
    border: 2px solid var(--star-color, #708090);
    box-shadow: 0 0 0 1px var(--star-color, #708090);
    background: #000;
  }

  .badge {
    position: absolute;
    right: 2px;
    bottom: 2px;
    background: rgba(0,0,0,0.75);
    color: #fff;
    border: 1px solid #fff;
    padding: 0 0.25rem;
    font-size: 0.7rem;
    line-height: 1.1rem;
  }

  .detail {
    border: 2px solid #fff;
    padding: 0.5rem;
    text-align: center;
    min-height: 80px;
  }
  .detail-icon {
    width: 64px;
    height: 64px;
    border: 2px solid var(--star-color, #708090);
    box-shadow: 0 0 0 1px var(--star-color, #708090);
    margin-bottom: 0.25rem;
    background: #000;
  }
  .detail-name { font-size: 0.9rem; margin-bottom: 0.15rem; }
  .detail-count { font-size: 0.8rem; color: #ddd; }
  .placeholder {
    font-size: 0.8rem;
    color: #ccc;
  }
  .actions {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    margin-top: 0.5rem;
  }
  button {
    border: 2px solid #fff;
    background: #0a0a0a;
    color: #fff;
    padding: 0.3rem 0.6rem;
  }
</style>
