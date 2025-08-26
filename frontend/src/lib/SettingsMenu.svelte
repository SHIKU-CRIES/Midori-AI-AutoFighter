<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { Volume2, Music, Mic, Power, Trash2, Download, Upload } from 'lucide-svelte';
  import { endRun, wipeData, exportSave, importSave, setAutoCraft, getGacha, getLrmConfig, setLrmModel, testLrmModel } from './api.js';
  import { saveSettings, clearSettings, clearAllClientData } from './settingsStorage.js';

  const dispatch = createEventDispatcher();
  export let sfxVolume = 50;
  export let musicVolume = 50;
  export let voiceVolume = 50;
  export let framerate = 60;
  export let autocraft = false;
  export let reducedMotion = false;
  export let lrmModel = '';
  export let runId = '';

  let saveStatus = '';
  let saveTimeout;
  let resetTimeout;
  let lrmOptions = [];
  let testReply = '';

  // Keep autocraft in sync with backend flag so this toggle
  // mirrors the Crafting menu's auto-craft behavior.
  onMount(async () => {
    try {
      const state = await getGacha();
      if (typeof state?.auto_craft === 'boolean') {
        autocraft = state.auto_craft;
        // Persist locally and notify parent so UI reflects server state
        save();
      }
    } catch {
      /* ignore network/backend issues; leave local state */
    }
    try {
      const cfg = await getLrmConfig();
      lrmOptions = cfg?.available_models || [];
      lrmModel = cfg?.current_model || lrmModel;
      saveSettings({ lrmModel });
    } catch {
      /* ignore */
    }
  });

  function save() {
    saveSettings({
      sfxVolume,
      musicVolume,
      voiceVolume,
      framerate: Number(framerate),
      autocraft,
      reducedMotion
    });
    dispatch('save', {
      sfxVolume,
      musicVolume,
      voiceVolume,
      framerate: Number(framerate),
      autocraft,
      reducedMotion
    });
    saveStatus = 'Saved';
    clearTimeout(resetTimeout);
    resetTimeout = setTimeout(() => {
      saveStatus = '';
    }, 1000);
  }

  function scheduleSave() {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(save, 300);
  }

  async function handleAutocraftToggle() {
    // Save locally and notify parent
    scheduleSave();
    // Update backend to match
    try { await setAutoCraft(autocraft); } catch { /* ignore */ }
  }

  function handleModelChange() {
    saveSettings({ lrmModel });
    dispatch('save', { lrmModel });
    setLrmModel(lrmModel).catch(() => {});
  }

  async function handleTestModel() {
    testReply = '';
    try {
      const res = await testLrmModel('Say hello');
      testReply = res?.response || '';
    } catch {
      testReply = 'Error';
    }
  }


  async function handleEndRun() {
    if (runId) {
      try {
        await endRun(runId);
      } catch (e) {
        console.error('Failed to end run', e);
      } finally {
        dispatch('endRun');
      }
    }
  }

  let wipeStatus = '';

  async function handleWipe() {
    wipeStatus = '';
    if (!confirm('This will erase all save data. Continue?')) return;
    let ok = true;
    try {
      await wipeData();
    } catch (e) {
      ok = false;
    } finally {
      // Always clear client state and reload, even if backend wipe fails
      clearSettings();
      await clearAllClientData();
      sfxVolume = 50;
      musicVolume = 50;
      voiceVolume = 50;
      framerate = 60;
      autocraft = false;
      reducedMotion = false;
      runId = '';
      wipeStatus = ok ? 'Save data wiped. Reloading…' : 'Backend wipe failed; cleared local data. Reloading…';
      setTimeout(() => {
        try { window.location.reload(); } catch {}
      }, 50);
    }
  }

  async function handleBackup() {
    const blob = await exportSave();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'backup.afsave';
    a.click();
    URL.revokeObjectURL(url);
  }

  async function handleImport(event) {
    const [file] = event.target.files;
    if (file) {
      await importSave(file);
    }
  }
</script>

<div data-testid="settings-menu">
  <div class="cols">
    <div class="col">
      <h4>Audio</h4>
      <div class="control" title="Adjust sound effect volume.">
        <Volume2 />
        <label>SFX Volume</label>
        <input type="range" min="0" max="100" bind:value={sfxVolume} on:input={scheduleSave} />
      </div>
      <div class="control" title="Adjust background music volume.">
        <Music />
        <label>Music Volume</label>
        <input type="range" min="0" max="100" bind:value={musicVolume} on:input={scheduleSave} />
      </div>
      <div class="control" title="Adjust voice volume.">
        <Mic />
        <label>Voice Volume</label>
        <input type="range" min="0" max="100" bind:value={voiceVolume} on:input={scheduleSave} />
      </div>
    </div>
    <div class="col">
      <h4>System</h4>
      <div class="control" title="Limit server polling frequency.">
        <label>Framerate</label>
        <select bind:value={framerate} on:change={scheduleSave}>
          <option value={30}>30</option>
          <option value={60}>60</option>
          <option value={120}>120</option>
        </select>
      </div>
      <div class="control" title="Slow down battle animations.">
        <label>Reduced Motion</label>
        <input type="checkbox" bind:checked={reducedMotion} on:change={scheduleSave} />
      </div>
      <div class="control" title="Select language reasoning model.">
        <label>LRM Model</label>
        <select bind:value={lrmModel} on:change={handleModelChange}>
          {#each lrmOptions as opt}
            <option value={opt}>{opt}</option>
          {/each}
        </select>
      </div>
      <div class="control" title="Send a sample prompt to the selected model.">
        <label>Test Model</label>
        <button on:click={handleTestModel}>Test</button>
      </div>
      {#if testReply}
        <p class="status" data-testid="lrm-test-reply">{testReply}</p>
      {/if}
      <div class="control" title="Clear all save data.">
        <Trash2 />
        <label>Wipe Save Data</label>
        <button on:click={handleWipe}>Wipe</button>
      </div>
      {#if wipeStatus}
        <p class="status" data-testid="wipe-status">{wipeStatus}</p>
      {/if}
      <div class="control" title="Download encrypted backup of save data.">
        <Download />
        <label>Backup Save Data</label>
        <button on:click={handleBackup}>Backup</button>
      </div>
      <div class="control" title="Import an encrypted save backup.">
        <Upload />
        <label>Import Save Data</label>
        <input type="file" accept=".afsave" on:change={handleImport} />
      </div>
    </div>
    <div class="col">
      <h4>Gameplay</h4>
      <div class="control" title="Automatically craft materials when possible.">
        <label>Autocraft</label>
        <input type="checkbox" bind:checked={autocraft} on:change={handleAutocraftToggle} />
      </div>
      <div class="control" title="End the current run.">
        <Power />
        <label>End Run</label>
        <button on:click={handleEndRun} disabled={!runId}>End</button>
      </div>
    </div>
  </div>
  <div class="actions">
    {#if saveStatus}
      <p class="status" data-testid="save-status">{saveStatus}</p>
    {/if}
  </div>
</div>

<style>
  .cols {
    display: flex;
    gap: 1rem;
  }

  .col {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  h4 {
    margin: 0 0 0.25rem 0;
    font-size: 1rem;
  }

  .control {
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }

  label {
    flex: 1;
    font-size: 0.85rem;
  }

  input[type='range'] {
    flex: 2;
  }

  select {
    flex: 2;
    background: #0a0a0a;
    color: #fff;
    border: 1px solid #fff;
  }

  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }

  button {
    border: 2px solid #fff;
    background: #0a0a0a;
    color: #fff;
    padding: 0.3rem 0.6rem;
  }

  .status {
    margin: 0;
    font-size: 0.8rem;
  }
</style>
