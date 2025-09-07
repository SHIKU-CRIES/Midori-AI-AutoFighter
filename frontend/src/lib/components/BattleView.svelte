<script>
  import { onMount, onDestroy, createEventDispatcher, tick } from 'svelte';
  import { scale } from 'svelte/transition';
  import { roomAction } from '$lib';
  import { getRandomBackground, getElementColor } from '../systems/assetLoader.js';
  import FighterUIItem from '../battle/FighterUIItem.svelte';
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
    if (evt && logAnimations[evt]) {
      queueEffect(logAnimations[evt]);
    }
  }

  function differs(a, b) {
    return JSON.stringify(a) !== JSON.stringify(b);
  }

  function guessElementFromId(id) {
    if (!id) return 'Generic';
    const s = String(id).toLowerCase();
    if (s.includes('fire') || s.includes('flame') || s.includes('burn')) return 'Fire';
    if (s.includes('water') || s.includes('aqua') || s.includes('ice') || s.includes('frost')) return 'Water';
    if (s.includes('earth') || s.includes('stone') || s.includes('rock') || s.includes('ground')) return 'Earth';
    if (s.includes('air') || s.includes('wind') || s.includes('storm') || s.includes('lightning')) return 'Air';
    if (s.includes('light') || s.includes('holy') || s.includes('divine')) return 'Light';
    if (s.includes('dark') || s.includes('shadow') || s.includes('void')) return 'Dark';
    return 'Generic';
  }

  function detectSummons(partySummons, foeSummons) {
    const all = new Set(knownSummons);
    for (const [, summons] of partySummons) {
      for (const s of summons) {
        if (!all.has(s.id)) {
          queueEffect('SummonEffect');
          all.add(s.id);
          break;
        }
      }
    }
    for (const [, summons] of foeSummons) {
      for (const s of summons) {
        if (!all.has(s.id)) {
          queueEffect('SummonEffect');
          all.add(s.id);
          break;
        }
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
          : Object.entries(snap.party_summons).flatMap(([owner, list]) =>
              (Array.isArray(list) ? list : [list]).map(s => ({ owner_id: owner, ...s })),
            );
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
          : Object.entries(snap.foe_summons).flatMap(([owner, list]) =>
              (Array.isArray(list) ? list : [list]).map(s => ({ owner_id: owner, ...s })),
            );
        for (const s of arr) {
          const owner = s?.owner_id;
          if (!owner) continue;
          if (!foeSummons.has(owner)) foeSummons.set(owner, []);
          foeSummons.get(owner).push(s);
        }
      }

      detectSummons(partySummons, foeSummons);

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
          let elem =
            (Array.isArray(f.damage_types) && f.damage_types[0]) ||
            f.damage_type ||
            f.element;
          let resolved = typeof elem === 'string' ? elem : (elem?.id || elem?.name);
          if (!resolved) {
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
      // Silently ignore errors to avoid spam during rapid polling
    } finally {
      dispatch('snapshot-end');
      const elapsed = performance.now() - start;
      const remaining = Math.max(0, pollDelay - elapsed);
      if (active && runId) {
        timer = setTimeout(fetchSnapshot, remaining);
      }
    }
  }

  onMount(() => {
    if (active && runId) {
      fetchSnapshot();
    }
  });

  onDestroy(() => {
    if (timer) {
      clearTimeout(timer);
      timer = null;
    }
  });

  // Watch active state changes
  $: if (active && runId && !timer) {
    fetchSnapshot();
  } else if (!active && timer) {
    clearTimeout(timer);
    timer = null;
  }
</script>

<div
  class="modern-battle-field"
  style={`background-image: url(${bg})`}
  data-testid="modern-battle-view"
>
  <EnrageIndicator active={Boolean(enrage?.active)} {reducedMotion} enrageData={enrage} />
  <BattleEffects cue={effectCue} />
  
  <!-- Foes at the top -->
  {#if showFoes}
    <div class="foe-row">
      {#each foes as foe (foe.id)}
        <div class="foe-container">
          <!-- Buffs at the very top -->
          <div class="foe-buffs">
            {#if foe.passives?.length || foe.dots?.length || foe.hots?.length}
              <div class="status-bar">
                {#each (foe.passives || []).slice(0, 6) as passive}
                  <div class="status-icon passive" title={passive.id}>
                    <span class="status-text">{passive.id}</span>
                    {#if passive.stacks > 1}
                      <span class="status-count">{passive.stacks}</span>
                    {/if}
                  </div>
                {/each}
                {#each (foe.dots || []).slice(0, 6) as dot}
                  <div class="status-icon dot" title="{dot.id} - {dot.damage} dmg for {dot.turns} turns">
                    <span class="status-text">{dot.id}</span>
                    {#if dot.turns > 1}
                      <span class="status-count">{dot.turns}</span>
                    {/if}
                  </div>
                {/each}
                {#each (foe.hots || []).slice(0, 6) as hot}
                  <div class="status-icon hot" title="{hot.id} - {hot.healing} heal for {hot.turns} turns">
                    <span class="status-text">{hot.id}</span>
                    {#if hot.turns > 1}
                      <span class="status-count">{hot.turns}</span>
                    {/if}
                  </div>
                {/each}
              </div>
            {/if}
          </div>
          
          <!-- HP bar on top -->
          <div class="foe-hp-bar">
            <div class="hp-bar-container">
              <div 
                class="hp-bar-fill"
                style="width: {Math.max(0, Math.min(100, (foe.hp / foe.max_hp) * 100))}%; 
                       background: {(foe.hp / foe.max_hp) <= 0.3 ? 'linear-gradient(90deg, #ff4444, #ff6666)' : 'linear-gradient(90deg, #44ffff, #66dddd)'}"
              ></div>
              {#if foe.hp < foe.max_hp}
                <div class="hp-text">{foe.hp}</div>
              {/if}
            </div>
          </div>
          
          <!-- Character photo/portrait -->
          <FighterUIItem fighter={foe} position="top" {reducedMotion} />
          
          <!-- Summons -->
          {#if foe.summons?.length}
            <div class="summon-list">
              {#each foe.summons as summon (summon.id)}
                <div
                  in:scale={{ duration: reducedMotion ? 0 : 200 }}
                  class="summon-entry"
                >
                  <FighterUIItem fighter={summon} position="top" {reducedMotion} size="small" />
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}

  <!-- Party at the bottom -->
  <div class="party-row">
    {#each party as member (member.id)}
      <div class="party-container">
        <div class="party-main">
          <!-- Character photo as base -->
          <FighterUIItem fighter={member} position="bottom" {reducedMotion} />
          
          <!-- Ult gauge as circle to the right -->
          <div class="ult-gauge-container">
            <div 
              class="ult-gauge"
              class:ult-ready={member.ultimate_ready}
              style="--element-color: {getElementColor(member.element)}"
            >
              <svg class="ult-circle" viewBox="0 0 36 36">
                <path
                  class="ult-circle-bg"
                  d="M18 2.0845 a 15.915 15.915 0 0 1 0 31.83 a 15.915 15.915 0 0 1 0 -31.83"
                />
                <path
                  class="ult-circle-fill"
                  stroke-dasharray="{Math.max(0, Math.min(100, (member.ultimate_charge / 15) * 100))}, 100"
                  d="M18 2.0845 a 15.915 15.915 0 0 1 0 31.83 a 15.915 15.915 0 0 1 0 -31.83"
                />
              </svg>
              {#if member.ultimate_ready}
                <div class="ult-ready-glow"></div>
              {/if}
            </div>
          </div>
        </div>
        
        <!-- HP bar under the photo -->
        <div class="party-hp-bar">
          <div class="hp-bar-container">
            <div 
              class="hp-bar-fill"
              style="width: {Math.max(0, Math.min(100, (member.hp / member.max_hp) * 100))}%; 
                     background: {(member.hp / member.max_hp) <= 0.3 ? 'linear-gradient(90deg, #ff4444, #ff6666)' : 'linear-gradient(90deg, #44ffff, #66dddd)'}"
            ></div>
            {#if member.hp < member.max_hp}
              <div class="hp-text">{member.hp}</div>
            {/if}
          </div>
        </div>
        
        <!-- Buffs under HP bar -->
        <div class="party-buffs">
          {#if member.passives?.length || member.dots?.length || member.hots?.length}
            <div class="status-bar">
              {#each (member.passives || []).slice(0, 6) as passive}
                <div class="status-icon passive" title={passive.id}>
                  <span class="status-text">{passive.id}</span>
                  {#if passive.stacks > 1}
                    <span class="status-count">{passive.stacks}</span>
                  {/if}
                </div>
              {/each}
              {#each (member.dots || []).slice(0, 6) as dot}
                <div class="status-icon dot" title="{dot.id} - {dot.damage} dmg for {dot.turns} turns">
                  <span class="status-text">{dot.id}</span>
                  {#if dot.turns > 1}
                    <span class="status-count">{dot.turns}</span>
                  {/if}
                </div>
              {/each}
              {#each (member.hots || []).slice(0, 6) as hot}
                <div class="status-icon hot" title="{hot.id} - {hot.healing} heal for {hot.turns} turns">
                  <span class="status-text">{hot.id}</span>
                  {#if hot.turns > 1}
                    <span class="status-count">{hot.turns}</span>
                  {/if}
                </div>
              {/each}
            </div>
          {/if}
        </div>

        <!-- Summons -->
        {#if member.summons?.length}
          <div class="summon-list">
            {#each member.summons as summon (summon.id)}
              <div
                in:scale={{ duration: reducedMotion ? 0 : 200 }}
                class="summon-entry"
              >
                <FighterUIItem fighter={summon} position="bottom" {reducedMotion} size="small" />
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/each}
  </div>

  {#if showHud}
    <BattleLog entries={logs} />
  {/if}
</div>

<style>
  .modern-battle-field {
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 1rem;
    overflow: hidden;
    gap: 1rem;
  }

  .modern-battle-field > * {
    position: relative;
    z-index: 1;
  }

  /* Foe row at top */
  .foe-row {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
    align-items: flex-start;
  }

  .foe-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
  }

  .foe-buffs {
    min-height: 24px;
    display: flex;
    justify-content: center;
  }

  .foe-hp-bar {
    width: 80px;
    margin-bottom: 0.25rem;
  }

  /* Party row at bottom */
  .party-row {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
    align-items: flex-end;
  }

  .party-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
  }

  .party-main {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  /* Ult gauge styling */
  .ult-gauge-container {
    position: relative;
  }

  .ult-gauge {
    width: 36px;
    height: 36px;
    position: relative;
  }

  .ult-circle {
    width: 100%;
    height: 100%;
    transform: rotate(-90deg);
  }

  .ult-circle-bg {
    fill: none;
    stroke: rgba(255, 255, 255, 0.2);
    stroke-width: 2;
  }

  .ult-circle-fill {
    fill: none;
    stroke: var(--element-color, #4CAF50);
    stroke-width: 2.5;
    stroke-linecap: round;
    transition: stroke-dasharray 0.3s ease;
  }

  .ult-ready .ult-circle-fill {
    filter: drop-shadow(0 0 6px var(--element-color));
  }

  .ult-ready-glow {
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    background: radial-gradient(circle, var(--element-color, #4CAF50) 0%, transparent 70%);
    opacity: 0.3;
    animation: pulse 1.5s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.3; }
    50% { transform: scale(1.1); opacity: 0.6; }
  }

  /* HP bars */
  .hp-bar-container {
    position: relative;
    width: 100%;
    height: 8px;
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.3);
    overflow: hidden;
  }

  .hp-bar-fill {
    height: 100%;
    transition: width 0.3s ease, background 0.3s ease;
  }

  .hp-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 0.7rem;
    font-weight: bold;
    color: #fff;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
    pointer-events: none;
  }

  .party-hp-bar {
    width: 80px;
  }

  /* Status effects */
  .status-bar {
    display: flex;
    gap: 0.2rem;
    flex-wrap: wrap;
    justify-content: center;
    max-width: 120px;
  }

  .status-icon {
    position: relative;
    min-width: 16px;
    height: 16px;
    border-radius: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.6rem;
    font-weight: bold;
    color: #fff;
    text-shadow: 0 1px 1px rgba(0, 0, 0, 0.8);
    cursor: help;
  }

  .status-icon.passive {
    background: linear-gradient(135deg, #3498DB, #2980B9);
  }

  .status-icon.dot {
    background: linear-gradient(135deg, #E74C3C, #C0392B);
  }

  .status-icon.hot {
    background: linear-gradient(135deg, #2ECC71, #27AE60);
  }

  .status-text {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 14px;
  }

  .status-count {
    position: absolute;
    top: -4px;
    right: -4px;
    background: rgba(0, 0, 0, 0.8);
    color: #fff;
    font-size: 0.5rem;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
  }

  /* Summons */
  .summon-list {
    display: flex;
    gap: 0.25rem;
    margin-top: 0.25rem;
  }

  .summon-entry {
    display: flex;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .modern-battle-field {
      padding: 0.5rem;
      gap: 0.5rem;
    }

    .foe-row, .party-row {
      gap: 0.5rem;
    }

    .ult-gauge {
      width: 30px;
      height: 30px;
    }

    .status-bar {
      max-width: 100px;
    }

    .status-icon {
      min-width: 14px;
      height: 14px;
      font-size: 0.55rem;
    }
  }

  @media (max-width: 600px) {
    .party-row, .foe-row {
      flex-direction: column;
      align-items: center;
    }

    .party-main {
      gap: 0.25rem;
    }

    .summon-list {
      gap: 0.2rem;
    }
  }
</style>