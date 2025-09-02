<script>
  import { onMount, onDestroy, createEventDispatcher, tick } from 'svelte';
  import { scale } from 'svelte/transition';
  import { roomAction } from '$lib';
  import { getRandomBackground } from '../systems/assetLoader.js';
  import FighterPortrait from '../battle/FighterPortrait.svelte';
  import EnrageIndicator from '../battle/EnrageIndicator.svelte';
  import BattleLog from '../battle/BattleLog.svelte';
  import BattleEffects from '../effects/BattleEffects.svelte';
  export let runId = '';
  export let framerate = 60;
  export let party = [];
  export let enrage = { active: false, stacks: 0, turns: 0 };
  export let reducedMotion = false;
  export let active = true;
  export let showHud = true;
  export let showFoes = true;
  let foes = [];
  let timer;
  let logs = [];
  const logAnimations = {
    damage: 'HitEffect',
    burn: 'Fire1',
    poison: 'Poison',
    heal: 'HealOne1'
  };
  let effectCue = '';
  function queueEffect(name) {
    if (!name || reducedMotion) return;
    effectCue = name;
    tick().then(() => {
      effectCue = '';
    });
  }
  let knownSummons = new Set();
  const dispatch = createEventDispatcher();
  let pollDelay = 1000 / framerate;
  $: pollDelay = 1000 / framerate;
  let bg = getRandomBackground();
  function logToEvent(line) {
    if (typeof line !== 'string') return null;
    const l = line.toLowerCase();
    if (l.includes('burn')) return 'burn';
    if (l.includes('poison')) return 'poison';
    if (l.includes('heal')) return 'heal';
    if (l.includes('damage')) return 'damage';
    return null;
  }
  $: if (logs.length) {
    const evt = logToEvent(logs[logs.length - 1]);
    if (evt && logAnimations[evt]) queueEffect(logAnimations[evt]);
  }
  $: flashDuration = reducedMotion ? 20 : 10;
  $: if (!active) clearTimeout(timer);

  // Dynamic sizing per side based on fighter counts
  $: partyCount = Array.isArray(party) ? party.length : 0;
  $: foeCount = Array.isArray(foes) ? foes.length : 0;
  function sizeForParty(n) {
    if (n <= 1) return 10.0; // slightly bigger when solo
    if (n <= 2) return 9.0;
    if (n <= 3) return 8.5;
    if (n <= 4) return 8.0;
    return 7.5; // 5 max party
  }
  function sizeForFoes(n) {
    if (n <= 1) return 8.5;
    if (n <= 2) return 8.0;
    if (n <= 4) return 7.75;
    if (n <= 6) return 7.25;
    if (n <= 8) return 6.75;
    return 6.5; // still compact to fit many foes
  }
  $: partyPortraitSize = `${sizeForParty(partyCount)}rem`;
  $: foePortraitSize = `${sizeForFoes(foeCount)}rem`;
  
  function differs(a, b) {
    return JSON.stringify(a) !== JSON.stringify(b);
  }

  function guessElementFromId(id) {
    const s = (id || '').toLowerCase();
    if (s.includes('lightning')) return 'Lightning';
    if (s.includes('light')) return 'Light';
    if (s.includes('dark')) return 'Dark';
    if (s.includes('fire')) return 'Fire';
    if (s.includes('ice')) return 'Ice';
    if (s.includes('wind')) return 'Wind';
    return 'Generic';
  }

  function detectSummons(pSummons, fSummons) {
    const all = new Set([
      ...Array.from(pSummons.values()).flat().map((s) => s.id),
      ...Array.from(fSummons.values()).flat().map((s) => s.id)
    ]);
    for (const id of all) {
      if (!knownSummons.has(id)) {
        queueEffect('SummonSpawn');
        break;
      }
    }
    knownSummons = all;
  }

  async function fetchSnapshot() {
    if (!active || !runId) return;
    const start = performance.now();
    dispatch('snapshot-start');
    try {
      const snap = await roomAction(runId, 'battle', 'snapshot');
      // Normalize alternate shapes for compatibility
      if (snap && !Array.isArray(snap.party) && snap.party && typeof snap.party === 'object') {
        snap.party = Object.values(snap.party);
      }
      if (snap && !Array.isArray(snap.foes)) {
        if (snap.foes && typeof snap.foes === 'object') {
          snap.foes = Object.values(snap.foes);
        } else if (Array.isArray(snap.enemies)) {
          snap.foes = snap.enemies;
        } else if (snap.enemies && typeof snap.enemies === 'object') {
          snap.foes = Object.values(snap.enemies);
        }
      }
      // Map summons to their owners
      const partySummons = new Map();
      if (snap && snap.party_summons) {
        const arr = Array.isArray(snap.party_summons)
          ? snap.party_summons
          : Object.values(snap.party_summons);
        for (const s of arr) {
          const owner = s?.owner_id;
          if (!owner) continue;
          if (!partySummons.has(owner)) partySummons.set(owner, []);
          partySummons.get(owner).push(s);
        }
      }
      const foeSummons = new Map();
      if (snap && snap.foe_summons) {
        const arr = Array.isArray(snap.foe_summons)
          ? snap.foe_summons
          : Object.values(snap.foe_summons);
        for (const s of arr) {
          const owner = s?.owner_id;
          if (!owner) continue;
          if (!foeSummons.has(owner)) foeSummons.set(owner, []);
          foeSummons.get(owner).push(s);
        }
      }
      detectSummons(partySummons, foeSummons);
      // removed console logging to avoid snapshot/round-trip spam
      // Do not overwrite party/foes directly; we enrich below to preserve
      // existing per-entity element data and avoid regressions.
      if (snap.enrage && differs(snap.enrage, enrage)) enrage = snap.enrage;
      if (snap.party) {
        const prevById = new Map((party || []).map(p => [p.id, p]));
        const enriched = (snap.party || []).map(m => {
          let elem =
            (Array.isArray(m.damage_types) && m.damage_types[0]) ||
            m.damage_type ||
            m.element ||
            '';
          if (!elem || /generic/i.test(String(elem))) {
            const prev = prevById.get(m.id);
            if (prev && (prev.element || prev.damage_type)) {
              elem = prev.element || prev.damage_type;
            } else {
              elem = guessElementFromId(m.id);
            }
          }
          const resolved = typeof elem === 'string' ? elem : (elem?.id || elem?.name || 'Generic');
          return { ...m, element: resolved, summons: partySummons.get(m.id) || [] };
        });
        if (differs(enriched, party)) party = enriched;
      }
      if (snap.foes) {
        const prevById = new Map((foes || []).map(f => [f.id, f]));
        const enrichedFoes = (snap.foes || []).map(f => {
          // Prefer primary from damage_types; then singular damage_type or element.
          let elem =
            (Array.isArray(f.damage_types) && f.damage_types[0]) ||
            f.damage_type ||
            f.element;
          let resolved = typeof elem === 'string' ? elem : (elem?.id || elem?.name);
          if (!resolved) {
            // Fall back to previously known element if available; otherwise leave empty
            const prev = prevById.get(f.id);
            resolved = prev?.element || prev?.damage_type || '';
          }
          return { ...f, element: resolved, summons: foeSummons.get(f.id) || [] };
        });
        if (differs(enrichedFoes, foes)) foes = enrichedFoes;
      }
      if (Array.isArray(snap.log)) logs = snap.log;
      else if (Array.isArray(snap.logs)) logs = snap.logs;
    } catch (e) {
      /* ignore */
    } finally {
      const duration = performance.now() - start;
      dispatch('snapshot-end', { duration });
      if (active && runId) {
        timer = setTimeout(fetchSnapshot, Math.max(0, pollDelay - duration));
      }
    }
  }

  onMount(() => {
    if (active) fetchSnapshot();
  });

  onDestroy(() => {
    clearTimeout(timer);
  });
</script>

<div
  class="battle-field"
  style={`background-image: url(${bg})`}
  data-testid="battle-view"
>
  <EnrageIndicator active={Boolean(enrage?.active)} {reducedMotion} enrageData={enrage} />
  <BattleEffects cue={effectCue} />
  <div class="party-column" style={`--portrait-size: ${partyPortraitSize}` }>
    {#each party as member (member.id)}
      <div class="combatant">
        <FighterPortrait fighter={member} {reducedMotion} />
        {#if member.summons?.length}
          <div class="summon-list right">
            {#each member.summons as summon (summon.id)}
              <div
                in:scale={{ duration: reducedMotion ? 0 : 200 }}
                class="summon-entry"
              >
                <FighterPortrait
                  fighter={summon}
                  {reducedMotion}
                  style="--portrait-size: calc(var(--portrait-size) * 0.6)"
                />
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/each}
  </div>
  {#if showFoes}
    <div class="foe-column" style={`--portrait-size: ${foePortraitSize}` }>
      {#each foes as foe (foe.id)}
        <div class="combatant">
          {#if foe.summons?.length}
            <div class="summon-list left">
              {#each foe.summons as summon (summon.id)}
                <div
                  in:scale={{ duration: reducedMotion ? 0 : 200 }}
                  class="summon-entry"
                >
                  <FighterPortrait
                    fighter={summon}
                    {reducedMotion}
                    style="--portrait-size: calc(var(--portrait-size) * 0.6)"
                  />
                </div>
              {/each}
            </div>
          {/if}
          <FighterPortrait fighter={foe} {reducedMotion} />
        </div>
      {/each}
    </div>
  {/if}
  {#if showHud}
    <BattleLog entries={logs} />
  {/if}
</div>

<style>
  .battle-field {
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    padding: 0.5rem;
    overflow: hidden;
  }
  .battle-field > * {
    position: relative;
    z-index: 1;
  }
  .party-column,
  .foe-column {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.8rem; /* add a bit more space so effects don't crowd */
  }

  .stained-glass-panel {
    background: var(--glass-bg);
    box-shadow: var(--glass-shadow);
    border: var(--glass-border);
    backdrop-filter: var(--glass-filter);
    padding: 0.25rem;
  }

  .party-column {
    order: 1;
  }

  .foe-column {
    order: 2;
  }
  .combatant {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .summon-list {
    display: flex;
    gap: 0.25rem;
  }
  .summon-entry {
    display: flex;
  }
  .summon-list.right {
    flex-direction: row;
  }
  .summon-list.left {
    flex-direction: row-reverse;
  }
  @media (max-width: 600px) {
    .summon-list {
      gap: 0.2rem;
    }
  }
</style>
