<script>
  import {
    Play,
    Map,
    Users,
    User,
    Settings,
    SquareChartGantt,
    PackageOpen,
    Hammer
  } from 'lucide-svelte';
  import GameViewport from '$lib/GameViewport.svelte';
  import {
    startRun,
    fetchMap,
    getPlayerConfig,
    savePlayerConfig
  } from '$lib/api.js';

  let runId = '';
  let currentMap = [];
  let selectedParty = ['sample_player'];
  let roomData = null;
  let viewportBg = '';
  let viewMode = 'main';
  let editorState = { pronouns: '', damage: 'Light', hp: 0, attack: 0, defense: 0 };

  function openRun() {
    viewMode = 'party-start';
  }

  async function openMap() {
    if (!runId) return;
    viewMode = 'map';
    const data = await fetchMap(runId);
    currentMap = data.rooms.slice(data.current).map((n) => n.room_type);
  }

  async function handleStart() {
    const data = await startRun(selectedParty);
    runId = data.run_id;
    currentMap = data.map.rooms.slice(data.map.current).map((n) => n.room_type);
    viewMode = 'main';
  }

  function handleParty() {
    viewMode = 'party';
  }

  async function openEditor() {
    const data = await getPlayerConfig();
    editorState = data;
    viewMode = 'editor';
  }

  function handleEditorSave(e) {
    editorState = e.detail;
    savePlayerConfig(editorState);
  }

  function openPulls() {
    viewMode = 'pulls';
  }

  function openCraft() {
    viewMode = 'craft';
  }

  function handleTarget() {
    viewMode = 'stats';
  }

  const items = [
    { icon: Play, label: 'Run', action: openRun },
    { icon: Map, label: 'Map', action: openMap },
    { icon: Users, label: 'Party', action: handleParty },
    { icon: User, label: 'Edit', action: openEditor },
    { icon: PackageOpen, label: 'Pulls', action: openPulls },
    { icon: Hammer, label: 'Craft', action: openCraft },
    { icon: Settings, label: 'Settings', action: () => (viewMode = 'settings') },
    { icon: SquareChartGantt, label: 'Stats', action: () => (viewMode = 'stats') }
  ];

</script>

<style>
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
    /* allow inner UI panels to scroll if they grow beyond available space */
    overflow: auto;
    padding: 0 0.5rem; /* small horizontal padding so elements don't touch the edge */
  }
</style>

<div class="viewport-wrap">
  <GameViewport
    runId={runId}
    roomData={roomData}
    background={viewportBg}
    bind:selected={selectedParty}
    bind:viewMode={viewMode}
    items={items}
    editorState={editorState}
    map={currentMap}
    on:startRun={() => { handleStart(); viewMode = 'main'; }}
    on:editorSave={(e) => { handleEditorSave(e); viewMode = 'main'; }}
    on:target={handleTarget}
  />
</div>
