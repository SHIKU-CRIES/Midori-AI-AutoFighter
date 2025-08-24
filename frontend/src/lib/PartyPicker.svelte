<script>
  import { onMount } from 'svelte';
  import { getPlayers } from './api.js';
  import { getCharacterImage, getHourlyBackground, getRandomFallback } from './assetLoader.js';
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
  <PartyRoster {roster} {selected} bind:previewId {compact} />
{:else}
  <MenuPanel style={`background-image: url(${background}); background-size: cover;`}>
    <div class="full" data-testid="party-picker">
      <PartyRoster {roster} {selected} bind:previewId />
      <PlayerPreview {roster} {previewId} />
      <StatTabs {roster} {previewId} {selected} on:toggle={(e) => toggleMember(e.detail)} />
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
  }
</style>
