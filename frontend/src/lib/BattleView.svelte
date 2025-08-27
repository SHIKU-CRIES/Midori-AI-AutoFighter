<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import { roomAction } from '$lib';
  import { getRandomBackground } from './assetLoader.js';
  import FighterPortrait from './battle/FighterPortrait.svelte';
  import EnrageIndicator from './battle/EnrageIndicator.svelte';
  import BattleLog from './battle/BattleLog.svelte';
  import BattleEffects from './effects/BattleEffects.svelte';
  export let runId = '';
  export let framerate = 60;
  export let party = [];
  export let enrage = { active: false, stacks: 0 };
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
    if (evt && logAnimations[evt]) effectCue = logAnimations[evt];
  }
  $: flashDuration = reducedMotion ? 20 : 10;
  $: if (!active) clearTimeout(timer);

  // Dynamic sizing per side based on fighter counts
  $: partyCount = Array.isArray(party) ? party.length : 0;
  $: foeCount = Array.isArray(foes) ? foes.length : 0;
  function sizeForParty(n) {
    if (n <= 1) return 9.5; // bigger when solo
    if (n <= 2) return 8.5;
    if (n <= 3) return 8.0;
    if (n <= 4) return 7.5;
    return 7.0; // 5 max party, a bit bigger than old 6rem
  }
  function sizeForFoes(n) {
    if (n <= 1) return 8.0;
    if (n <= 2) return 7.5;
    if (n <= 4) return 7.25;
    if (n <= 6) return 6.75;
    if (n <= 8) return 6.25;
    return 6.0; // keep current size so 10 foes fit
  }
  $: partyPortraitSize = `${sizeForParty(partyCount)}rem`;
  $: foePortraitSize = `${sizeForFoes(foeCount)}rem`;
  
  function differs(a, b) {
    return JSON.stringify(a) !== JSON.stringify(b);
  }

  function pctRatio(val) {
    if (typeof val !== 'number' || !isFinite(val)) return '0%';
    return `${(val * 100).toFixed(2)}%`;
  }

  function pctOdds(val) {
    if (typeof val !== 'number' || !isFinite(val)) return '0%';
    return `${(val * 100).toFixed(2)}%`;
  }

  function pctFromMultiplier(mult) {
    if (typeof mult !== 'number' || !isFinite(mult)) return '0%';
    return `${((mult - 1) * 100).toFixed(2)}%`;
  }

  function formatMitigation(val) {
    if (typeof val !== 'number' || !isFinite(val)) return '-';
    // Rule: 100 = 1x (no mitigation). <100 means more damage taken, >100 reduces damage.
    if (val >= 10) {
      return `x${(val / 100).toFixed(2)}`;
    }
    // If value is already a small multiplier (e.g., 1.0), show directly.
    return `x${val.toFixed(2)}`;
  }

  function fmt2(val) {
    if (typeof val !== 'number' || !isFinite(val)) return '0.00';
    return Number(val).toFixed(2);
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

  async function fetchSnapshot() {
    if (!active || !runId) return;
    const start = performance.now();
    dispatch('snapshot-start');
    try {
      const snap = await roomAction(runId, 'battle', 'snapshot');
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
          return { ...m, element: resolved };
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
          return { ...f, element: resolved };
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
  <EnrageIndicator active={active} {reducedMotion} />
  <BattleEffects cue={effectCue} />
  <div class="party-column" style={`--portrait-size: ${partyPortraitSize}` }>
    {#each party as member (member.id)}
      <div class="combatant">
        <FighterPortrait fighter={member} />
        {#if showHud}
          <div class="stats right stained-glass-panel">
            <div class="name">{(member.name ?? member.id)} ({member.level ?? 1})</div>
            <div class="row"><span class="k">HP</span> <span class="v">{member.hp}/{member.max_hp}</span></div>
            <div class="row"><span class="k">VIT</span> <span class="v">{fmt2(member.vitality ?? 0)}</span></div>
            <div class="row"><span class="k">ATK</span> <span class="v">{member.atk}</span></div>
            <div class="row"><span class="k">DEF</span> <span class="v">{member.defense}</span></div>
            <div class="row"><span class="k">MIT</span> <span class="v">{formatMitigation(member.mitigation)}</span></div>
            <div class="row"><span class="k">CRate</span> <span class="v">{pctOdds(member.crit_rate)}</span></div>
            <div class="row"><span class="k">CDmg</span> <span class="v">{pctFromMultiplier(member.crit_damage)}</span></div>
            <div class="row"><span class="k">E.Hit</span> <span class="v">{pctRatio(member.effect_hit_rate)}</span></div>
            <div class="row"><span class="k">E.Res</span> <span class="v">{pctOdds(member.effect_resistance)}</span></div>
            <div class="row small"><span class="k">AP</span> <span class="v">{member.action_points ?? 0}</span> <span class="k">/ APT</span> <span class="v">{member.actions_per_turn ?? 1}</span></div>
            <details class="advanced">
              <summary>Combat stats</summary>
              <div class="row small"><span class="k">Dmg Dealt</span> <span class="v">{member.damage_dealt ?? 0}</span></div>
              <div class="row small"><span class="k">Dmg Taken</span> <span class="v">{member.damage_taken ?? 0}</span></div>
              <div class="row small"><span class="k">Kills</span> <span class="v">{member.kills ?? 0}</span></div>
            </details>
          </div>
        {/if}
      </div>
    {/each}
  </div>
  {#if showFoes}
    <div class="foe-column" style={`--portrait-size: ${foePortraitSize}` }>
      {#each foes as foe (foe.id)}
        <div class="combatant">
          {#if showHud}
            <div class="stats left stained-glass-panel">
              <div class="name">{(foe.name ?? foe.id)} ({foe.level ?? 1})</div>
              <div class="row"><span class="k">HP</span> <span class="v">{foe.hp}/{foe.max_hp}</span></div>
              <div class="row"><span class="k">VIT</span> <span class="v">{fmt2(foe.vitality ?? 0)}</span></div>
              <div class="row"><span class="k">ATK</span> <span class="v">{foe.atk}</span></div>
              <div class="row"><span class="k">DEF</span> <span class="v">{foe.defense}</span></div>
              <div class="row"><span class="k">MIT</span> <span class="v">{formatMitigation(foe.mitigation)}</span></div>
              <div class="row"><span class="k">CRate</span> <span class="v">{pctOdds(foe.crit_rate)}</span></div>
              <div class="row"><span class="k">CDmg</span> <span class="v">{pctFromMultiplier(foe.crit_damage)}</span></div>
              <div class="row"><span class="k">E.Hit</span> <span class="v">{pctRatio(foe.effect_hit_rate)}</span></div>
              <div class="row"><span class="k">E.Res</span> <span class="v">{pctOdds(foe.effect_resistance)}</span></div>
              <div class="row small"><span class="k">AP</span> <span class="v">{foe.action_points ?? 0}</span> <span class="k">/ APT</span> <span class="v">{foe.actions_per_turn ?? 1}</span></div>
              <details class="advanced">
                <summary>Combat stats</summary>
                <div class="row small"><span class="k">Dmg Dealt</span> <span class="v">{foe.damage_dealt ?? 0}</span></div>
                <div class="row small"><span class="k">Dmg Taken</span> <span class="v">{foe.damage_taken ?? 0}</span></div>
                <div class="row small"><span class="k">Kills</span> <span class="v">{foe.kills ?? 0}</span></div>
              </details>
            </div>
          {/if}
          <FighterPortrait fighter={foe} />
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
  }
  /* Ensure clear spacing on the foe side where layout is reversed */
  .foe-column .combatant { gap: 8px; }
  .foe-column .combatant {
    flex-direction: row-reverse;
  }
  .stats {
    font-size: 0.7rem;
    width: var(--portrait-size);
    flex: 0 0 var(--portrait-size); /* prevent overlap/shrink under portrait */
  }
  .stats .name {
    font-weight: 600;
    margin-bottom: 0.2rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .row { display: flex; justify-content: space-between; gap: 0.25rem; }
  .row.small { font-size: 0.65rem; }
  .k { opacity: 0.85; }
  .v { font-variant-numeric: tabular-nums; }
  .badge { display: none; }
  details.advanced { margin-top: 0.15rem; }
  .stats.right { margin-left: 4px; text-align: left; }
  .stats.left { margin-right: 8px; text-align: right; }
  @media (max-width: 600px) {
    .stats {
      width: 4rem;
      font-size: 0.6rem;
    }
  }
</style>
