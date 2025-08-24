<script>
  import GameViewport from '$lib/GameViewport.svelte';
  import { onMount } from 'svelte';
  import { getPlayerConfig, savePlayerConfig, getBackendFlavor } from '$lib/api.js';
  import {
    startRun,
    roomAction,
    chooseCard,
    chooseRelic,
    advanceRoom,
    getMap,
    updateParty
  } from '$lib/runApi.js';
  import { loadRunState, saveRunState, clearRunState } from '$lib/runState.js';
  import { buildRunMenu } from '$lib/RunButtons.svelte';
  import { FEEDBACK_URL } from '$lib/constants.js';
  import { openOverlay, backOverlay, homeOverlay } from '$lib/OverlayController.js';
  import { browser, dev } from '$app/environment';

  let runId = '';
  let backendFlavor = '';
  let selectedParty = ['sample_player'];
  let roomData = null;
  // Track map state to render room/floor context in battle header
  let mapRooms = [];
  let currentIndex = 0;
  let currentRoomType = '';
  let viewportBg = '';
  let nextRoom = '';

  let editorState = { pronouns: '', damageType: 'Light', hp: 0, attack: 0, defense: 0 };
  let battleActive = false;
  // When true, suppress backend syncing/polling (e.g., during defeat popup)
  let haltSync = false;

  // Normalize status fields so downstream components can rely on
  // `passives`, `dots`, and `hots` arrays of objects on each fighter.
  function mapStatuses(snapshot) {
    if (!snapshot) return snapshot;
    function map(list = []) {
      return list.map((f) => {
        const status = f.status || {};
        return {
          ...f,
          passives: status.passives || f.passives || [],
          dots: status.dots || f.dots || [],
          hots: status.hots || f.hots || []
        };
      });
    }
    if (Array.isArray(snapshot.party)) snapshot.party = map(snapshot.party);
    if (Array.isArray(snapshot.foes)) snapshot.foes = map(snapshot.foes);
    return snapshot;
  }

  onMount(async () => {
    backendFlavor = await getBackendFlavor();
    window.backendFlavor = backendFlavor;
    // Ensure sync is not halted on load
    if (typeof window !== 'undefined') window.afHaltSync = false;
    const saved = loadRunState();
    if (saved) {
      const data = await getMap(saved.runId);
      if (!data) {
        clearRunState();
      } else {
        runId = saved.runId;
        selectedParty = data.party || selectedParty;
        mapRooms = data.map.rooms || [];
        currentIndex = data.map.current || 0;
        currentRoomType = mapRooms[currentIndex]?.room_type || '';
        nextRoom = mapRooms[currentIndex + 1]?.room_type || '';
        await enterRoom();
      }
    }
  });

  function openRun() {
    if (runId) {
      homeOverlay();
      if (!battleActive) {
        enterRoom();
      }
    } else {
      openOverlay('party-start');
    }
  }

  function handleRunEnd() {
    stopBattlePoll();
    runId = '';
    roomData = null;
    nextRoom = '';
    battleActive = false;
    homeOverlay();
    clearRunState();
  }

  function handleDefeat() {
    // Clear run state, go to main menu, and show a defeat popup
    haltSync = true;
    if (typeof window !== 'undefined') window.afHaltSync = true;
    handleRunEnd();
    // Open a lightweight popup informing the player
    openOverlay('defeat');
  }

  async function handleStart() {
    haltSync = false;
    if (typeof window !== 'undefined') window.afHaltSync = false;
    const data = await startRun(selectedParty);
    runId = data.run_id;
    mapRooms = data.map.rooms || [];
    currentIndex = data.map.current || 0;
    currentRoomType = mapRooms[currentIndex]?.room_type || '';
    nextRoom = mapRooms[currentIndex + 1]?.room_type || '';
    homeOverlay();
    await enterRoom();
  }

  async function handleParty() {
    if (battleActive) return;
    openOverlay('party');
  }

  async function handlePartySave() {
    if (runId) {
      await updateParty(runId, selectedParty);
    }
    backOverlay();
  }

  async function openEditor() {
    if (battleActive) return;
    const data = await getPlayerConfig();
    editorState = {
      pronouns: data.pronouns,
      damageType: data.damage_type,
      hp: data.hp,
      attack: data.attack,
      defense: data.defense,
    };
    openOverlay('editor');
  }

  async function handleEditorSave(e) {
    editorState = {
      ...e.detail,
      hp: +e.detail.hp,
      attack: +e.detail.attack,
      defense: +e.detail.defense,
    };
    await savePlayerConfig({
      pronouns: editorState.pronouns,
      damage_type: editorState.damageType,
      hp: editorState.hp,
      attack: editorState.attack,
      defense: editorState.defense,
    });
  }

  async function openPulls() {
    if (battleActive) return;
    openOverlay('pulls');
  }

  async function openCraft() {
    if (battleActive) return;
    openOverlay('craft');
  }

  function openFeedback() {
    window.open(FEEDBACK_URL, '_blank', 'noopener');
  }

  async function openInventory() {
    if (battleActive) return;
    openOverlay('inventory');
  }

  let battleTimer;
  const STALL_TICKS = 60 * 3;
  let stalledTicks = 0;

  function hasRewards(snap) {
    if (!snap) return false;
    const cards = (snap?.card_choices?.length || 0) > 0;
    const relics = (snap?.relic_choices?.length || 0) > 0;
    const lootItems = (snap?.loot?.items?.length || 0) > 0;
    const lootGold = (snap?.loot?.gold || 0) > 0;
    return cards || relics || lootItems || lootGold;
  }

  function stopBattlePoll() {
    if (battleTimer) {
      clearTimeout(battleTimer);
      battleTimer = null;
    }
  }

  async function pollBattle() {
    if (!battleActive || haltSync || !runId) return;
    try {
      const snap = mapStatuses(await roomAction(runId, 'battle', 'snapshot'));
      if (snap?.error) {
        roomData = snap;
        battleActive = false;
        stalledTicks = 0;
        return;
      }
      const snapHasRewards = hasRewards(snap);
      const snapCompleted = Boolean(snap?.awaiting_next) || Boolean(snap?.next_room) || (snap?.ended && snap?.result === 'defeat');
      const partyDead = Array.isArray(snap?.party) && snap.party.length > 0 && snap.party.every(m => (m?.hp ?? 1) <= 0);
      const foesDead = Array.isArray(snap?.foes) && snap.foes.length > 0 && snap.foes.every(f => (f?.hp ?? 1) <= 0);
      const combatOver = partyDead || foesDead;
      if (snapHasRewards || snapCompleted) {
        // Stop only when rewards or completion flags arrive
        roomData = snap;
        const rewardsReady = hasRewards(roomData);
        if (rewardsReady || snapCompleted) {
          battleActive = false;
          nextRoom = snap.next_room || nextRoom;
          if (typeof snap.current_index === 'number') currentIndex = snap.current_index;
          if (snap.current_room) currentRoomType = snap.current_room;
          stalledTicks = 0;
          // If run ended in defeat, immediately return home and show defeat popup
          if (snap?.ended && snap?.result === 'defeat') {
            handleDefeat();
          }
          return;
        }
      }
      if (combatOver) {
        // Update snapshot but keep polling until rewards are available
        roomData = snap;
        stalledTicks += 1;
        if (stalledTicks > STALL_TICKS) {
          battleActive = false;
          roomData = { ...snap, error: 'Battle results could not be fetched.' };
          if (dev || !browser) {
            const { warn } = await import('$lib/logger.js');
            warn('Battle results could not be fetched.');
          }
          return;
        }
      } else {
        stalledTicks = 0;
      }
    } catch {
      /* ignore */
    }
    if (battleActive && !haltSync && runId) {
      battleTimer = setTimeout(pollBattle, 1000 / 60);
    }
  }

  async function enterRoom() {
    stopBattlePoll();
    if (haltSync) return;
    if (!runId) return;
    // Ensure header reflects the room we are entering now
    currentRoomType = mapRooms?.[currentIndex]?.room_type || currentRoomType || nextRoom;
    if (!currentRoomType) return;
    let endpoint = currentRoomType;
    if (endpoint.includes('battle')) {
      endpoint = currentRoomType.includes('boss') ? 'boss' : 'battle';
    }
    try {
      // Fetch first, then decide whether to show rewards or start battle polling.
      const data = mapStatuses(await roomAction(runId, endpoint));
      roomData = data;
      // If this response indicates a defeated run, stop syncing and show popup.
      if (data?.ended && data?.result === 'defeat') {
        handleDefeat();
        return;
      }
      if (data.party) {
        selectedParty = data.party.map((p) => p.id);
      }
      // Keep map-derived indices and current room type in sync when available
      if (typeof data.current_index === 'number') currentIndex = data.current_index;
      if (data.current_room) currentRoomType = data.current_room;
      nextRoom = data.next_room || (mapRooms?.[currentIndex + 1]?.room_type || nextRoom || '');
      saveRunState(runId, nextRoom);
      if (endpoint === 'battle' || endpoint === 'boss') {
        const gotRewards = hasRewards(data);
        if (gotRewards) {
          battleActive = false;
          return;
        }
        const noFoes = !Array.isArray(data?.foes) || data.foes.length === 0;
        if (noFoes) {
          // Try to fetch the saved battle snapshot (e.g., after refresh while awaiting rewards).
          try {
            if (haltSync || !runId) return;
            const snap = mapStatuses(await roomAction(runId, 'battle', 'snapshot'));
            const snapHasRewards = hasRewards(snap);
            if (snapHasRewards) {
              roomData = snap;
              battleActive = false;
              nextRoom = snap.next_room || nextRoom;
              if (typeof snap.current_index === 'number') currentIndex = snap.current_index;
              if (snap.current_room) currentRoomType = snap.current_room;
              return;
            }
          } catch {}
        }
        // If the snapshot didn't include current room type yet, fall back to pre-room value
        // Actively set a sensible type for header during combat
        if (!currentRoomType) currentRoomType = mapRooms?.[currentIndex]?.room_type || (endpoint.includes('boss') ? 'battle-boss-floor' : 'battle-normal');
        battleActive = true;
        pollBattle();
      } else {
        battleActive = false;
      }
    } catch (e) {
      try {
        if (haltSync || !runId) return;
        const snap = mapStatuses(await roomAction(runId, 'battle', 'snapshot'));
        roomData = snap;
        battleActive = false;
        nextRoom = snap.next_room || nextRoom;
        if (typeof snap.current_index === 'number') currentIndex = snap.current_index;
        if (snap.current_room) currentRoomType = snap.current_room;
        saveRunState(runId, nextRoom);
        if (browser) alert('Failed to enter room. Restored latest battle state.');
      } catch {
        if (browser) alert('Failed to enter room.');
        if (dev || !browser) {
          const { error } = await import('$lib/logger.js');
          error('Failed to enter room.', e);
        }
      }
    }
  }

  async function handleRewardSelect(detail) {
    if (!runId) return;
    let res;
    if (detail.type === 'card') {
      res = await chooseCard(runId, detail.id);
      if (roomData) roomData.card_choices = [];
    } else if (detail.type === 'relic') {
      res = await chooseRelic(runId, detail.id);
      if (roomData) roomData.relic_choices = [];
    }
    if (res && res.next_room) {
      nextRoom = res.next_room;
    }
  }
  async function handleShopBuy(item) {
    if (!runId) return;
    roomData = await roomAction(runId, 'shop', item);
  }
  async function handleShopReroll() {
    if (!runId) return;
    roomData = await roomAction(runId, 'shop', 'reroll');
  }
  async function handleShopLeave() {
    if (!runId) return;
    await roomAction(runId, 'shop', 'leave');
    const res = await advanceRoom(runId);
    if (res && typeof res.current_index === 'number') {
      currentIndex = res.current_index;
      currentRoomType = mapRooms?.[currentIndex]?.room_type || currentRoomType;
    }
    if (res && res.next_room) {
      nextRoom = res.next_room;
    }
    await enterRoom();
  }
  async function handleRestPull() {
    if (!runId) return;
    roomData = await roomAction(runId, 'rest', 'pull');
  }
  async function handleRestSwap() {
    if (!runId) return;
    roomData = await roomAction(runId, 'rest', 'swap');
  }
  async function handleRestCraft() {
    if (!runId) return;
    roomData = await roomAction(runId, 'rest', 'craft');
  }
  async function handleRestLeave() {
    if (!runId) return;
    await roomAction(runId, 'rest', 'leave');
    const res = await advanceRoom(runId);
    if (res && typeof res.current_index === 'number') {
      currentIndex = res.current_index;
      currentRoomType = mapRooms?.[currentIndex]?.room_type || currentRoomType;
    }
    if (res && res.next_room) {
      nextRoom = res.next_room;
    }
    await enterRoom();
  }

  async function handleNextRoom() {
    if (!runId) return;
    // Ensure syncing is enabled when advancing to the next room
    haltSync = false;
    if (typeof window !== 'undefined') window.afHaltSync = false;
    // If rewards are still present, don't attempt to advance.
    // Only block if there are still selectable choices (cards/relics).
    if ((roomData?.card_choices?.length || 0) > 0 || (roomData?.relic_choices?.length || 0) > 0) {
      return;
    }
    // Close reward overlay and unmount previous BattleView immediately
    roomData = null;
    battleActive = false;
    if (roomData?.ended) {
      // Run has ended (defeat). Clear state, return to main, and show popup.
      handleDefeat();
      return;
    }
    try {
      const res = await advanceRoom(runId);
      if (res && typeof res.current_index === 'number') {
        currentIndex = res.current_index;
        currentRoomType = mapRooms?.[currentIndex]?.room_type || currentRoomType;
      }
      if (res && res.next_room) {
        nextRoom = res.next_room;
      }
      await enterRoom();
    } catch (e) {
      // If not ready (e.g., server 400), refresh snapshot so rewards remain visible.
      try {
        if (haltSync || !runId) return;
        const snap = mapStatuses(await roomAction(runId, 'battle', 'snapshot'));
        roomData = snap;
      } catch {
        /* no-op */
      }
    }
  }
  let items = [];
  $: items = buildRunMenu(
    {
      openRun,
      handleParty,
      openEditor,
      openPulls,
      openCraft,
      openFeedback,
      openInventory,
      openSettings: () => openOverlay('settings')
    },
    battleActive
  );

</script>

<style>
  :global(:root) {
    --glass-bg: linear-gradient(135deg, rgba(10,10,10,0.96) 0%, rgba(30,30,30,0.92) 100%),
      repeating-linear-gradient(120deg, rgba(255,255,255,0.04) 0 2px, transparent 2px 8px),
      linear-gradient(60deg, rgba(255,255,255,0.06) 10%, rgba(0,0,0,0.38) 80%);
    --glass-border: 1.5px solid rgba(40,40,40,0.44);
    --glass-shadow: 0 2px 18px 0 rgba(0,0,0,0.32), 0 1.5px 0 0 rgba(255,255,255,0.04) inset;
    --glass-filter: blur(3.5px) saturate(1.05);
  }
  :global(html, body) {
    margin: 0;
    padding: 0;
    height: 100vh;
    /* allow scrolling when content is larger than the viewport
       (prevent content from being clipped at the right/bottom) */
    overflow: auto;
    background: #000;
    color: #fff;
    box-sizing: border-box;
  }

  /* Make the viewport container responsive and avoid forcing a second
     full-height which can overflow when inner elements have borders/padding. */
  .viewport-wrap {
    width: 100%;
    max-width: 98vw;
    max-height: 98vh;
    height: 100%;
    margin: 0 auto;
    box-sizing: border-box;
    /* avoid horizontal scrollbar; allow vertical scrolling */
    overflow-x: hidden;
    overflow-y: auto;
    padding: 0 0.5rem; /* small horizontal padding so elements don't touch the edge */
  }
</style>

<div class="viewport-wrap">
  <GameViewport
    runId={runId}
    roomData={roomData}
    background={viewportBg}
    mapRooms={mapRooms}
    currentIndex={currentIndex}
    currentRoomType={currentRoomType}
    bind:selected={selectedParty}
    items={items}
    editorState={editorState}
    battleActive={battleActive}
    on:startRun={handleStart}
    on:editorSave={(e) => handleEditorSave(e)}
    on:target={openInventory}
    on:back={backOverlay}
    on:home={homeOverlay}
    on:openEditor={openEditor}
    on:settings={() => openOverlay('settings')}
    on:rewardSelect={(e) => handleRewardSelect(e.detail)}
    on:shopBuy={(e) => handleShopBuy(e.detail)}
    on:shopReroll={handleShopReroll}
    on:shopLeave={handleShopLeave}
    on:restPull={handleRestPull}
    on:restSwap={handleRestSwap}
    on:restCraft={handleRestCraft}
    on:restLeave={handleRestLeave}
    on:nextRoom={handleNextRoom}
    on:endRun={handleRunEnd}
    on:saveParty={handlePartySave}
    on:error={(e) => openOverlay('error', e.detail)}
  />
</div>
