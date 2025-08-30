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
    updateParty,
    getActiveRuns
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
  // Preserve the last live battle snapshot (with statuses) for review UI
  let lastBattleSnapshot = null;

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
    // Normalize party/foes shapes: arrays are preferred; accept object maps or alternate keys
    if (snapshot && !Array.isArray(snapshot.party) && snapshot.party && typeof snapshot.party === 'object') {
      snapshot.party = Object.values(snapshot.party);
    }
    if (snapshot && !Array.isArray(snapshot.foes)) {
      if (snapshot.foes && typeof snapshot.foes === 'object') {
        snapshot.foes = Object.values(snapshot.foes);
      } else if (Array.isArray(snapshot.enemies)) {
        snapshot.foes = snapshot.enemies;
      } else if (snapshot.enemies && typeof snapshot.enemies === 'object') {
        snapshot.foes = Object.values(snapshot.enemies);
      }
    }
    if (Array.isArray(snapshot.party)) snapshot.party = map(snapshot.party);
    if (Array.isArray(snapshot.foes)) snapshot.foes = map(snapshot.foes);
    return snapshot;
  }

  onMount(async () => {
    // Always ensure sync is not halted on load
    if (typeof window !== 'undefined') {
      window.afHaltSync = false;
      window.afBattleActive = false; // Initialize battle state for ping indicator
    }

    // Always attempt to restore run state from localStorage, regardless of backend status
    const saved = loadRunState();
    
    async function tryRestoreRun() {
      if (!saved) return;
      
      try {
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
      } catch (e) {
        // If run restoration fails due to backend unavailability, keep the runId for later retry
        if (saved?.runId) {
          runId = saved.runId;
        }
      }
    }
    
    // Try to get backend flavor and restore run
    try {
      backendFlavor = await getBackendFlavor();
      window.backendFlavor = backendFlavor;
      
      // Backend is ready, attempt run restoration
      await tryRestoreRun();
    } catch (e) {
      // Backend not ready, but still attempt to restore run state for later
      if (saved?.runId) {
        runId = saved.runId;
      }
      // Dedicated overlay opened in getBackendFlavor; user can retry when backend is ready
    }
  });

  async function openRun() {
    if (runId) {
      // If we have a runId but don't have map data (e.g., backend was unavailable during load),
      // try to restore the run data now
      if (!mapRooms.length || currentIndex === 0) {
        const saved = loadRunState();
        if (saved?.runId === runId) {
          try {
            const data = await getMap(runId);
            if (data) {
              selectedParty = data.party || selectedParty;
              mapRooms = data.map.rooms || [];
              currentIndex = data.map.current || 0;
              currentRoomType = mapRooms[currentIndex]?.room_type || '';
              nextRoom = mapRooms[currentIndex + 1]?.room_type || '';
            }
          } catch (e) {
            // If we still can't get run data, show error but don't clear runId
            console.warn('Failed to restore run data:', e.message);
          }
        }
      }
      
      homeOverlay();
      if (!battleActive) {
        enterRoom();
      }
    } else {
      openOverlay('party-start');
    }
  }

  function handleRunEnd() {
    // Halt any in-flight battle snapshot polling ASAP
    haltSync = true;
    if (typeof window !== 'undefined') {
      window.afHaltSync = true;
      window.afBattleActive = false; // Update battle state for ping indicator
    }
    runId = '';
    roomData = null;
    nextRoom = '';
    battleActive = false;
    stopBattlePoll();
    homeOverlay();
    clearRunState();
  }

  function handleDefeat() {
    // Clear run state, go to main menu, and show a defeat popup
    haltSync = true;
    if (typeof window !== 'undefined') {
      window.afHaltSync = true;
      window.afBattleActive = false; // Update battle state for ping indicator
    }
    handleRunEnd();
    // Open a lightweight popup informing the player
    openOverlay('defeat');
  }

  async function handleStart(event) {
    const pressure = event?.detail?.pressure || 0;
    haltSync = false;
    if (typeof window !== 'undefined') {
      window.afHaltSync = false;
      window.afBattleActive = false; // Initialize battle state
    }

    // Check for active/live runs first
    try {
      const activeRunsData = await getActiveRuns();
      const activeRuns = activeRunsData.runs || [];
      
      if (activeRuns.length > 0) {
        // Resume the first active run found
        const activeRun = activeRuns[0];
        runId = activeRun.run_id;
        mapRooms = activeRun.map.rooms || [];
        currentIndex = activeRun.map.current || 0;
        currentRoomType = mapRooms[currentIndex]?.room_type || '';
        nextRoom = mapRooms[currentIndex + 1]?.room_type || '';
        saveRunState(runId, nextRoom);
        homeOverlay();
        await enterRoom();
        return;
      }
    } catch (error) {
      // If checking for active runs fails, fall back to starting a new run
      console.warn('Failed to check for active runs, starting new run:', error);
    }

    // No active runs found, start a new run
    const data = await startRun(selectedParty, editorState.damageType, pressure);
    runId = data.run_id;
    mapRooms = data.map.rooms || [];
    currentIndex = data.map.current || 0;
    currentRoomType = mapRooms[currentIndex]?.room_type || '';
    nextRoom = mapRooms[currentIndex + 1]?.room_type || '';
    saveRunState(runId, nextRoom);
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
      lastBattleSnapshot = snap || lastBattleSnapshot;
      if (snap?.error) {
        roomData = snap;
        lastBattleSnapshot = snap || lastBattleSnapshot;
        battleActive = false;
        stopBattlePoll();
        stalledTicks = 0;
        // Surface backend-declared errors via popup
        try { openOverlay('error', { message: snap.error, traceback: '' }); } catch {}
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
        lastBattleSnapshot = snap || lastBattleSnapshot;
        const rewardsReady = hasRewards(roomData);
        if (rewardsReady || snapCompleted) {
          battleActive = false;
          stopBattlePoll();
          nextRoom = snap.next_room || nextRoom;
          if (typeof snap.current_index === 'number') currentIndex = snap.current_index;
          if (snap.current_room) currentRoomType = snap.current_room;
          stalledTicks = 0;
          // If run ended in defeat, immediately return home and show defeat popup
          if (snap?.ended && snap?.result === 'defeat') {
            handleDefeat();
          }
          // Do not auto-advance; show Battle Review popup after rewards.
          return;
        }
      }
      if (combatOver) {
        // Update snapshot but keep polling until rewards are available
        roomData = snap;
        stalledTicks += 1;
        if (stalledTicks > STALL_TICKS) {
          battleActive = false;
          stopBattlePoll();
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
    } catch (err) {
      if (err?.message?.includes('run ended') || err?.status === 404) {
        handleRunEnd();
        return;
      }
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
      if (data?.error) {
        // Show error popup for successful-but-error payloads
        try { openOverlay('error', { message: data.error, traceback: '' }); } catch {}
        return;
      }
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
          stopBattlePoll();
          return;
        }
        // Do not auto-advance; allow Battle Review popup to appear.
        const noFoes = !Array.isArray(data?.foes) || data.foes.length === 0;
        if (noFoes) {
          // Try to fetch the saved battle snapshot (e.g., after refresh while awaiting rewards).
          try {
            if (haltSync || !runId) return;
            const snap = mapStatuses(await roomAction(runId, 'battle', 'snapshot'));
            const snapHasRewards = hasRewards(snap);
            if (snapHasRewards) {
              roomData = snap;
              lastBattleSnapshot = snap || lastBattleSnapshot;
              battleActive = false;
              stopBattlePoll();
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
        if (typeof window !== 'undefined') window.afBattleActive = true; // Update global state for ping indicator
        pollBattle();
      } else {
        battleActive = false;
        if (typeof window !== 'undefined') window.afBattleActive = false; // Update global state for ping indicator
        stopBattlePoll();
        // Non-battle rooms that are immediately ready to advance (no choices)
        // should auto-advance to avoid getting stuck.
        try {
          const noChoices = ((data?.card_choices?.length || 0) === 0) && ((data?.relic_choices?.length || 0) === 0);
          if (data?.awaiting_next && noChoices && runId) {
            await handleNextRoom();
            return;
          }
        } catch {}
      }
    } catch (e) {
      if (e?.status === 404) {
        handleRunEnd();
        openOverlay('error', { message: 'Run not found. Please start a new run.', traceback: '' });
        return;
      }
      try {
        if (haltSync || !runId) return;
        const snap = mapStatuses(await roomAction(runId, 'battle', 'snapshot'));
        roomData = snap;
        battleActive = false;
        stopBattlePoll();
        nextRoom = snap.next_room || nextRoom;
        if (typeof snap.current_index === 'number') currentIndex = snap.current_index;
        if (snap.current_room) currentRoomType = snap.current_room;
        saveRunState(runId, nextRoom);
        // Avoid noisy overlays on transient 400s.
        const simpleRecoverable = (e?.status === 400) || /not ready|awaiting next|invalid room/i.test(String(e?.message || ''));
        if (!simpleRecoverable) {
          openOverlay('error', {
            message: 'Failed to enter room. Restored latest battle state.',
            traceback: (e && e.stack) || ''
          });
        }
      } catch {
        // Surface error via overlay for consistency
        openOverlay('error', { message: 'Failed to enter room.', traceback: '' });
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
    // Do not auto-advance; show Battle Review popup next.
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
      // Refresh map data when advancing floors
      if (res.next_room) {
        currentRoomType = res.next_room;
      }
      const mapData = await getMap(runId);
      if (mapData?.map?.rooms) {
        mapRooms = mapData.map.rooms;
        currentRoomType = mapRooms?.[currentIndex]?.room_type || currentRoomType;
      }
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
      // Refresh map data when advancing floors
      if (res.next_room) {
        currentRoomType = res.next_room;
      }
      const mapData = await getMap(runId);
      if (mapData?.map?.rooms) {
        mapRooms = mapData.map.rooms;
        currentRoomType = mapRooms?.[currentIndex]?.room_type || currentRoomType;
      }
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
    // If the run has ended (defeat), clear state and show defeat popup immediately
    if (roomData?.ended) {
      handleDefeat();
      return;
    }
    // Close reward overlay and unmount previous BattleView immediately
    roomData = null;
    battleActive = false;
    stopBattlePoll();
    try {
      const res = await advanceRoom(runId);
      if (res && typeof res.current_index === 'number') {
        currentIndex = res.current_index;
        // When advancing floors, the mapRooms data becomes stale
        // Use the next_room from the response instead of looking up in old mapRooms
        if (res.next_room) {
          currentRoomType = res.next_room;
        }
        // Refresh map data to get the updated floor information
        const mapData = await getMap(runId);
        if (mapData?.map?.rooms) {
          mapRooms = mapData.map.rooms;
          // Now we can safely use the updated mapRooms
          currentRoomType = mapRooms?.[currentIndex]?.room_type || currentRoomType;
        }
      }
      if (res && res.next_room) {
        nextRoom = res.next_room;
      }
      // Try entering the next room with a few short retries to avoid timing issues
      for (let i = 0; i < 5; i++) {
        await new Promise((r) => setTimeout(r, 150 + i * 150));
        await enterRoom();
        const isBattleSnapshot = roomData && (roomData.result === 'battle' || roomData.result === 'boss');
        const progressed = (roomData && (!isBattleSnapshot || battleActive));
        if (progressed) break;
      }
    } catch (e) {
      // If not ready (e.g., server 400), refresh snapshot so rewards remain visible.
      try {
        if (haltSync || !runId) return;
        const snap = mapStatuses(await roomAction(runId, 'battle', 'snapshot'));
        roomData = snap;
        // If the backend still indicates we're awaiting the next room and
        // there are no choices to make, attempt the advance again.
        const noChoices = ((snap?.card_choices?.length || 0) === 0) && ((snap?.relic_choices?.length || 0) === 0);
        if (snap?.awaiting_next && noChoices) {
          try {
            const res2 = await advanceRoom(runId);
            if (res2 && typeof res2.current_index === 'number') {
              currentIndex = res2.current_index;
              // Refresh map data for retry attempts too
              if (res2.next_room) {
                currentRoomType = res2.next_room;
              }
              const mapData = await getMap(runId);
              if (mapData?.map?.rooms) {
                mapRooms = mapData.map.rooms;
                currentRoomType = mapRooms?.[currentIndex]?.room_type || currentRoomType;
              }
            }
            if (res2 && res2.next_room) {
              nextRoom = res2.next_room;
            }
            for (let i = 0; i < 5; i++) {
              await new Promise((r) => setTimeout(r, 150 + i * 150));
              await enterRoom();
              const isBattleSnapshot = roomData && (roomData.result === 'battle' || roomData.result === 'boss');
              const progressed = (roomData && (!isBattleSnapshot || battleActive));
              if (progressed) break;
            }
            return;
          } catch {}
        }
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
    battleSnapshot={lastBattleSnapshot}
    background={viewportBg}
    mapRooms={mapRooms}
    currentIndex={currentIndex}
    currentRoomType={currentRoomType}
    bind:selected={selectedParty}
    items={items}
    editorState={editorState}
    battleActive={battleActive}
    backendFlavor={backendFlavor}
    on:startRun={handleStart}
    on:editorSave={(e) => handleEditorSave(e)}
    on:openInventory={openInventory}
    on:openParty={handleParty}
    on:back={backOverlay}
    on:home={homeOverlay}
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
