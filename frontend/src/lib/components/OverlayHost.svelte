<!--
  OverlayHost.svelte
  Renders all modal overlays based on the overlayView store
  and forwards user actions to the parent GameViewport.
-->
<script>
  import { overlayView, overlayData } from '../systems/OverlayController.js';
  import { createEventDispatcher } from 'svelte';
  import OverlaySurface from './OverlaySurface.svelte';
  import PopupWindow from './PopupWindow.svelte';
  import PartyPicker from './PartyPicker.svelte';
  import PullsMenu from './PullsMenu.svelte';
  import CraftingMenu from './CraftingMenu.svelte';
  import BattleReview from './BattleReview.svelte';
  import RewardOverlay from './RewardOverlay.svelte';
  import PlayerEditor from './PlayerEditor.svelte';
  import InventoryPanel from './InventoryPanel.svelte';
  import SettingsMenu from './SettingsMenu.svelte';
  import ShopMenu from './ShopMenu.svelte';
  import RestRoom from './RestRoom.svelte';
  import BattleView from './BattleView.svelte';
  import ErrorOverlay from './ErrorOverlay.svelte';
  import BackendNotReady from './BackendNotReady.svelte';
  import FloatingLoot from './FloatingLoot.svelte';
  import CombatViewer from './CombatViewer.svelte';
  import { rewardOpen as computeRewardOpen } from '../systems/viewportState.js';

  export let selected = [];
  export let runId = '';
  export let roomData = null;
  export let battleSnapshot = null;
  export let editorState = {};
  export let sfxVolume = 50;
  export let musicVolume = 50;
  export let voiceVolume = 50;
  export let framerate = 60;
  export let autocraft = false;
  export let reducedMotion = false;
  export let selectedParty = [];
  export let battleActive = false;
  export let backendFlavor = '';

  const dispatch = createEventDispatcher();
  // Determine whether to show rewards overlay based on raw room data.
  // Floating loot messages are suppressed after first display via `lootConsumed`,
  // but the overlay should remain visible until the player advances.
  $: rewardOpen = computeRewardOpen(roomData, battleActive);
  // Review should display after a battle finishes, once reward choices (if any) are done.
  $: reviewOpen = Boolean(
    roomData && (roomData.result === 'battle' || roomData.result === 'boss') && !battleActive
  );

  // Hint to pause battle snapshot polling globally while rewards are open
  $: {
    try {
      if (typeof window !== 'undefined') window.afRewardOpen = Boolean(rewardOpen);
    } catch {}
  }

  function titleForItem(item) {
    if (!item) return '';
    if (item.name) return item.name;
    if (item.id === 'ticket') return 'Gacha Ticket';
    const id = String(item.id || '').toLowerCase();
    const cap = id.charAt(0).toUpperCase() + id.slice(1);
    const stars = Number.isFinite(item.stars) ? String(item.stars) : '';
    return stars ? `${cap} Upgrade (${stars})` : `${cap} Upgrade`;
  }

  let lootMessages = [];
  let lootConsumed = false;
  let lastRoom = null;
  let msgId = 0;
  function pushLoot(text) {
    lootMessages = [...lootMessages, { id: msgId++, text }];
  }
  function removeLoot(id) {
    lootMessages = lootMessages.filter((m) => m.id !== id);
  }
  $: if (roomData !== lastRoom) {
    lootConsumed = false;
    lastRoom = roomData;
  }
  $: if (!lootConsumed && roomData?.loot) {
    if (roomData.loot.gold) pushLoot(`Gold +${roomData.loot.gold}`);
    if (roomData.loot.items) {
      for (const item of roomData.loot.items) {
        pushLoot(titleForItem(item));
      }
    }
    lootConsumed = true;
  }
</script>

{#if $overlayView === 'party'}
  <OverlaySurface zIndex={1300}>
    <PartyPicker bind:selected {reducedMotion}
      on:save={() => dispatch('saveParty')}
      on:editorChange={(e) => dispatch('editorChange', e.detail)}
      on:cancel={() => dispatch('back')}
    />
  </OverlaySurface>
{/if}

{#if $overlayView === 'defeat'}
  <PopupWindow title="Defeat" on:close={() => dispatch('back')}>
    <div style="padding: 0.5rem 0.25rem; line-height: 1.4;">
      <p>Your party was defeated.</p>
      <p>You have been returned to the main menu.</p>
      <div class="stained-glass-row" style="justify-content: flex-end; margin-top: 0.75rem;">
        <button class="icon-btn" on:click={() => dispatch('back')}>OK</button>
      </div>
    </div>
  </PopupWindow>
{/if}

{#if $overlayView === 'error'}
  <ErrorOverlay
    message={$overlayData.message || 'An unexpected error occurred.'}
    traceback={$overlayData.traceback || ''}
    on:close={() => dispatch('back')}
  />
{/if}

{#if $overlayView === 'backend-not-ready'}
  <BackendNotReady
    apiBase={$overlayData.apiBase || ''}
    message={$overlayData.message || 'Backend is not ready yet.'}
    on:close={() => dispatch('back')}
  />
{/if}

{#if $overlayView === 'party-start'}
  <OverlaySurface>
    <PartyPicker bind:selected {reducedMotion}
      actionLabel="Start Run"
      on:save={(e) => dispatch('startRun', e.detail)}
      on:editorChange={(e) => dispatch('editorChange', e.detail)}
      on:cancel={() => dispatch('back')}
    />
  </OverlaySurface>
{/if}

{#if $overlayView === 'pulls'}
  <OverlaySurface zIndex={1300}>
    <PullsMenu on:close={() => dispatch('back')} />
  </OverlaySurface>
{/if}

{#if $overlayView === 'craft'}
  <OverlaySurface zIndex={1300}>
    <CraftingMenu on:close={() => dispatch('back')} />
  </OverlaySurface>
{/if}

{#if $overlayView === 'editor'}
  <OverlaySurface zIndex={1300}>
    <PlayerEditor
      {...editorState}
      on:close={() => dispatch('back')}
      on:save={(e) => { dispatch('editorSave', e.detail); dispatch('back'); }}
    />
  </OverlaySurface>
{/if}

{#if $overlayView === 'inventory'}
  <PopupWindow title="Inventory" padding="0.75rem" maxWidth="1040px" zIndex={1300} on:close={() => dispatch('back')}>
    <InventoryPanel cards={roomData?.cards ?? []} relics={roomData?.relics ?? []} />
  </PopupWindow>
{/if}

{#if $overlayView === 'combat-viewer'}
  <OverlaySurface zIndex={1300}>
    <CombatViewer 
      party={battleSnapshot?.party ?? []}
      foes={battleSnapshot?.foes ?? []}
      {runId}
      {battleSnapshot}
      on:close={() => dispatch('back')}
      on:pauseCombat={() => dispatch('pauseCombat')}
      on:resumeCombat={() => dispatch('resumeCombat')}
    />
  </OverlaySurface>
{/if}

{#if $overlayView === 'settings'}
  <PopupWindow title="Settings" maxWidth="960px" maxHeight="90vh" zIndex={1300} on:close={() => dispatch('back')}>
    <SettingsMenu
      {sfxVolume}
      {musicVolume}
      {voiceVolume}
      {framerate}
      {autocraft}
      {reducedMotion}
      {runId}
      {backendFlavor}
      on:save={(e) => dispatch('saveSettings', e.detail)}
      on:endRun={() => dispatch('endRun')}
    />
  </PopupWindow>
{/if}

{#if rewardOpen}
  <OverlaySurface zIndex={1100}>
    <PopupWindow
      title={(roomData?.card_choices?.length || 0) > 0 ? 'Choose a Card' : 'Choose a Relic'}
      maxWidth="880px"
      maxHeight="95vh"
      zIndex={1100}
      on:close={() => { /* block closing while choices remain */ }}
    >
      <RewardOverlay
        cards={roomData.card_choices || []}
        relics={roomData.relic_choices || []}
        items={[]}
        gold={0}
        on:select={(e) => dispatch('rewardSelect', e.detail)}
        on:next={() => dispatch('nextRoom')}
      />
    </PopupWindow>
  </OverlaySurface>
{/if}

{#if reviewOpen && !rewardOpen}
  <OverlaySurface zIndex={1100}>
    <PopupWindow
      title="Battle Review"
      maxWidth="1200px"
      maxHeight="95vh"
      zIndex={1100}
      on:close={() => dispatch('nextRoom')}
    >
      <BattleReview
        runId={runId}
        battleIndex={roomData?.battle_index || 0}
        partyData={(battleSnapshot?.party && battleSnapshot?.party.length) ? battleSnapshot.party : (roomData?.party || [])}
        foeData={(battleSnapshot?.foes && battleSnapshot?.foes.length) ? battleSnapshot.foes : (roomData?.foes || [])}
        cards={[]}
        relics={[]}
      />
      <div class="stained-glass-row" style="justify-content: flex-end; margin-top: 0.75rem;">
        <button class="icon-btn" on:click={() => dispatch('nextRoom')}>Next Room</button>
      </div>
    </PopupWindow>
  </OverlaySurface>
{/if}

{#if roomData && roomData.result === 'shop'}
  <OverlaySurface zIndex={1100}>
    <ShopMenu
      items={roomData.stock || roomData.items || []}
      gold={roomData.gold}
      reducedMotion={reducedMotion}
      on:buy={(e) => dispatch('shopBuy', e.detail)}
      on:reroll={() => dispatch('shopReroll')}
      on:close={() => dispatch('shopLeave')}
    />
  </OverlaySurface>
{/if}

{#if roomData && roomData.result === 'rest'}
  <OverlaySurface zIndex={1100}>
    <RestRoom
      gold={roomData.gold}
      reducedMotion={reducedMotion}
      on:pull={() => dispatch('restPull')}
      on:swap={() => dispatch('restSwap')}
      on:craft={() => dispatch('restCraft')}
      on:close={() => dispatch('restLeave')}
    />
  </OverlaySurface>
{/if}

{#if roomData && (roomData.result === 'battle' || roomData.result === 'boss') && (battleActive || rewardOpen || reviewOpen)}
  <div class="overlay-inset">
    <BattleView
      {runId}
      {framerate}
      {selectedParty}
      enrage={roomData?.enrage}
      reducedMotion={reducedMotion}
      active={battleActive}
      showHud={true}
      showFoes={true}
      on:snapshot-start={() => dispatch('snapshot-start')}
      on:snapshot-end={() => dispatch('snapshot-end')}
    />
  </div>
{/if}

{#each lootMessages as m, i (m.id)}
  <FloatingLoot message={m.text} offset={i * 20} on:done={() => removeLoot(m.id)} />
{/each}

<style>
  .overlay-inset {
    position: absolute;
    inset: 0;
    z-index: 1; /* always sit below popup overlays */
    background: rgba(0,0,0,0.85);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
  }
  .stained-glass-row {
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
    margin-top: 0.5rem;
    padding: 0.5rem 0.7rem;
    background: var(--glass-bg);
    box-shadow: var(--glass-shadow);
    border: var(--glass-border);
    backdrop-filter: var(--glass-filter);
  }

  /* Party actions: stack full-width buttons vertically */
  .party-actions {
    flex-direction: column;
    align-items: stretch;
  }
  .party-actions .icon-btn {
    width: 100%;
    height: auto;
    padding: 0.6rem 0.75rem;
    font-size: 1rem;
    justify-content: center;
  }

  .icon-btn {
    background: rgba(255,255,255,0.10);
    border: none;
    border-radius: 0;
    width: 2.9rem;
    height: 2.9rem;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    border: 1px solid rgba(255,255,255,0.35);
    cursor: pointer;
    transition: background 0.18s, box-shadow 0.18s;
    box-shadow: 0 1px 4px 0 rgba(0,40,120,0.10);
  }
  .icon-btn:hover {
    background: rgba(120,180,255,0.22);
    box-shadow: 0 2px 8px 0 rgba(0,40,120,0.18);
  }
</style>
