<!--
  OverlayHost.svelte
  Renders all modal overlays based on the overlayView store
  and forwards user actions to the parent GameViewport.
-->
<script>
  import { overlayView, overlayData } from './OverlayController.js';
  import { createEventDispatcher } from 'svelte';
  import OverlaySurface from './OverlaySurface.svelte';
  import PopupWindow from './PopupWindow.svelte';
  import PartyPicker from './PartyPicker.svelte';
  import PullsMenu from './PullsMenu.svelte';
  import CraftingMenu from './CraftingMenu.svelte';
  import RewardOverlay from './RewardOverlay.svelte';
  import PlayerEditor from './PlayerEditor.svelte';
  import InventoryPanel from './InventoryPanel.svelte';
  import SettingsMenu from './SettingsMenu.svelte';
  import ShopMenu from './ShopMenu.svelte';
  import RestRoom from './RestRoom.svelte';
  import BattleView from './BattleView.svelte';
  import ErrorOverlay from './ErrorOverlay.svelte';
  import BackendNotReady from './BackendNotReady.svelte';
  import { rewardOpen as computeRewardOpen } from './viewportState.js';

  export let selected = [];
  export let runId = '';
  export let roomData = null;
  export let editorState = {};
  export let sfxVolume = 50;
  export let musicVolume = 50;
  export let voiceVolume = 50;
  export let framerate = 60;
  export let autocraft = false;
  export let reducedMotion = false;
  export let selectedParty = [];
  export let battleActive = false;

  const dispatch = createEventDispatcher();
  $: rewardOpen = computeRewardOpen(roomData, battleActive);
</script>

{#if $overlayView === 'party'}
  <OverlaySurface>
    <PartyPicker bind:selected />
    <div class="stained-glass-row">
      <button class="icon-btn" on:click={() => dispatch('saveParty')}>Save Party</button>
      <button class="icon-btn" on:click={() => dispatch('back')}>Cancel</button>
    </div>
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
    <PartyPicker bind:selected />
    <div class="stained-glass-row">
      <button class="icon-btn" on:click={() => dispatch('startRun')}>Start Run</button>
      <button class="icon-btn" on:click={() => dispatch('back')}>Cancel</button>
    </div>
  </OverlaySurface>
{/if}

{#if $overlayView === 'pulls'}
  <OverlaySurface>
    <PullsMenu on:close={() => dispatch('back')} />
  </OverlaySurface>
{/if}

{#if $overlayView === 'craft'}
  <OverlaySurface>
    <CraftingMenu on:close={() => dispatch('back')} />
  </OverlaySurface>
{/if}

{#if $overlayView === 'editor'}
  <OverlaySurface>
    <PlayerEditor
      {...editorState}
      on:close={() => dispatch('back')}
      on:save={(e) => { dispatch('editorSave', e.detail); dispatch('back'); }}
    />
  </OverlaySurface>
{/if}

{#if $overlayView === 'inventory'}
  <PopupWindow title="Inventory" padding="0.75rem" on:close={() => dispatch('back')}>
    <InventoryPanel cards={roomData?.cards ?? []} relics={roomData?.relics ?? []} />
  </PopupWindow>
{/if}

{#if $overlayView === 'settings'}
  <PopupWindow title="Settings" on:close={() => dispatch('back')}>
    <SettingsMenu
      {sfxVolume}
      {musicVolume}
      {voiceVolume}
      {framerate}
      {autocraft}
      {reducedMotion}
      {runId}
      on:save={(e) => dispatch('saveSettings', e.detail)}
      on:endRun={() => dispatch('endRun')}
    />
  </PopupWindow>
{/if}

{#if rewardOpen}
  <OverlaySurface>
    <PopupWindow title="Battle Rewards" maxWidth="880px" maxHeight="95vh" on:close={() => dispatch('nextRoom')}>
      <RewardOverlay
        gold={roomData.loot?.gold || 0}
        cards={roomData.card_choices || []}
        relics={roomData.relic_choices || []}
        items={roomData.loot?.items || []}
        partyStats={roomData.party || []}
        ended={Boolean(roomData?.ended)}
        nextRoom={roomData?.next_room}
        on:select={(e) => dispatch('rewardSelect', e.detail)}
        on:next={() => dispatch('nextRoom')}
      />
    </PopupWindow>
  </OverlaySurface>
{/if}

{#if roomData && roomData.result === 'shop'}
  <OverlaySurface>
    <ShopMenu
      items={roomData.items || []}
      gold={roomData.gold}
      reducedMotion={reducedMotion}
      on:buy={(e) => dispatch('shopBuy', e.detail)}
      on:reroll={() => dispatch('shopReroll')}
      on:close={() => dispatch('shopLeave')}
    />
  </OverlaySurface>
{/if}

{#if roomData && roomData.result === 'rest'}
  <OverlaySurface>
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

{#if roomData && (roomData.result === 'battle' || roomData.result === 'boss') && (battleActive || rewardOpen)}
  <div class="overlay-inset">
    <BattleView
      {runId}
      {framerate}
      {selectedParty}
      enrage={roomData?.enrage}
      reducedMotion={reducedMotion}
      active={battleActive}
      on:snapshot-start={() => dispatch('snapshot-start')}
      on:snapshot-end={() => dispatch('snapshot-end')}
    />
  </div>
{/if}

<style>
  .overlay-inset {
    position: absolute;
    inset: 0;
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

  .icon-btn {
    background: rgba(255,255,255,0.10);
    border: none;
    border-radius: 0;
    width: 2.9rem;
    height: 2.9rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background 0.18s, box-shadow 0.18s;
    box-shadow: 0 1px 4px 0 rgba(0,40,120,0.10);
  }
  .icon-btn:hover {
    background: rgba(120,180,255,0.22);
    box-shadow: 0 2px 8px 0 rgba(0,40,120,0.18);
  }
</style>
