<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import FighterPortrait from './battle/FighterPortrait.svelte';
  import RewardCard from './RewardCard.svelte';
  import CurioChoice from './CurioChoice.svelte';
  import { getElementColor, getDotImage, getDotElement } from './assetLoader.js';
  import { getBattleSummary, getBattleEvents } from './runApi.js';
  import { Sparkles, Shield, CreditCard, Zap, Flame, Heart, Coins, TrendingUp, Users, User } from 'lucide-svelte';

  export let runId = '';
  export let battleIndex = 0;
  export let cards = [];
  export let relics = [];
  export let party = [];
  export let foes = [];
  export let partyData = [];
  export let foeData = [];

  const dispatch = createEventDispatcher();
  let summary = { damage_by_type: {} };
  let events = [];
  let showEvents = false;
  let loadingEvents = false;
  
  // Tab system for entity-specific breakdowns
  let activeTab = 'overview';
  let availableTabs = [];

  const elements = ['Generic', 'Light', 'Dark', 'Wind', 'Lightning', 'Fire', 'Ice'];

  // Prefer room-provided ids; if no bar data is available for them, fall back
  // to the ids present in the fetched summary to ensure graphs are shown.
  let partyDisplay = [];
  let foesDisplay = [];
  // Prefer full objects from room snapshot so DoTs/HoTs/buffs render in FighterPortrait
  $: partyDisplay = (partyData && partyData.length
    ? partyData
    : (party && party.length
        ? party.map(id => ({ id }))
        : (summary.party_members || []).map(id => ({ id }))
      )
  );
  $: foesDisplay = (foeData && foeData.length
    ? foeData
    : (foes && foes.length
        ? foes.map(id => ({ id }))
        : (summary.foes || []).map(id => ({ id }))
      )
  );

  onMount(async () => {
    if (!runId || !battleIndex) return;
    let cancelled = false;
    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
    async function loadWithRetry() {
      for (let attempt = 0; attempt < 10 && !cancelled; attempt++) {
        try {
          const res = await getBattleSummary(runId, battleIndex);
          summary = res || { damage_by_type: {} };
          return;
        } catch (err) {
          // 404 is expected briefly while the backend writes logs
          if (err?.status !== 404) {
            console.warn('Battle summary fetch failed', err?.message || err);
            return;
          }
        }
        await sleep(attempt < 5 ? 400 : 800);
      }
    }
    loadWithRetry();
    return () => { cancelled = true; };
  });

  // Build mapping of outgoing effects by source id so effects are grouped
  // with the character/foe that created them (not just who currently has them).
  function buildOutgoingMap() {
    const map = new Map();
    const push = (sid, bucket, eff) => {
      if (!sid) return;
      const entry = map.get(sid) || { dots: [], hots: [], buffs: [] };
      entry[bucket].push(eff);
      map.set(sid, entry);
    };
    const all = [...(partyDisplay || []), ...(foesDisplay || [])];
    for (const ent of all) {
      const dots = Array.isArray(ent.dots) ? ent.dots : [];
      const hots = Array.isArray(ent.hots) ? ent.hots : [];
      const buffs = Array.isArray(ent.active_effects) ? ent.active_effects : [];
      for (const d of dots) push(d.source, 'dots', d);
      for (const h of hots) push(h.source, 'hots', h);
      for (const b of buffs) push(b.source, 'buffs', b);
    }
    return map;
  }
  $: outgoingBySource = buildOutgoingMap();

  // Build available tabs based on available entities
  $: {
    const tabs = [{ id: 'overview', label: 'Overview', icon: Users, type: 'overview' }];
    
    // Add party member tabs
    for (const member of partyDisplay || []) {
      if (member.id) {
        tabs.push({
          id: member.id,
          label: member.name || member.id,
          type: 'party',
          entity: member
        });
      }
    }
    
    // Add foe tabs
    for (const foe of foesDisplay || []) {
      if (foe.id) {
        tabs.push({
          id: foe.id,
          label: foe.name || foe.id,
          type: 'foe',
          entity: foe
        });
      }
    }
    
    availableTabs = tabs;
  }

  // Get entity-specific data for a tab
  function getEntityData(entityId) {
    if (!summary || entityId === 'overview') return null;
    
    return {
      damage: summary.damage_by_type?.[entityId] || {},
      criticals: summary.critical_hits?.[entityId] || 0,
      criticalDamage: summary.critical_damage?.[entityId] || 0,
      shieldAbsorbed: summary.shield_absorbed?.[entityId] || 0,
      dotDamage: summary.dot_damage?.[entityId] || 0,
      hotHealing: summary.hot_healing?.[entityId] || 0,
      resourcesSpent: summary.resources_spent?.[entityId] || {},
      tempHpGranted: summary.temporary_hp_granted?.[entityId] || 0
    };
  }

  function barData(id) {
    const totals = summary.damage_by_type?.[id] || {};
    const total = Object.values(totals).reduce((a, b) => a + b, 0) || 1;
    return elements
      .map((el) => ({ element: el, pct: ((totals[el] || 0) / total) * 100 }))
      .filter((seg) => seg.pct > 0);
  }

  function primaryElement(id) {
    const totals = summary.damage_by_type?.[id] || {};
    const entries = Object.entries(totals);
    if (entries.length === 0) return 'Generic';
    return entries.sort((a, b) => b[1] - a[1])[0][0];
  }

  function handleSelect(e) {
    dispatch('select', e.detail);
  }

  // Derived helpers for labels and totals
  function fmt(n) {
    try { return Number(n).toLocaleString(); } catch { return String(n ?? 0); }
  }
  function elementBreakdown(id) {
    const totals = summary.damage_by_type?.[id] || {};
    const total = Object.values(totals).reduce((a, b) => a + b, 0) || 1;
    return elements
      .map((el) => ({ element: el, value: totals[el] || 0, pct: ((totals[el] || 0) / total) * 100 }))
      .filter((seg) => seg.value > 0)
      .sort((a, b) => b.value - a.value);
  }
  function totalDealt(id) { return summary.total_damage_dealt?.[id] || 0; }
  function totalTaken(id) { return summary.total_damage_taken?.[id] || 0; }
  function totalHeal(id) { return summary.total_healing_done?.[id] || 0; }
  function totalHits(id) { return summary.total_hits_landed?.[id] || 0; }

  async function toggleEvents() {
    showEvents = !showEvents;
    if (showEvents && events.length === 0 && runId && battleIndex) {
      loadingEvents = true;
      try {
        const data = await getBattleEvents(runId, battleIndex);
        events = Array.isArray(data) ? data : [];
      } catch (e) {
        // swallow; optional view
      } finally {
        loadingEvents = false;
      }
    }
  }

  // If no bars for provided ids but summary has data for others, switch display ids
  $: {
    const hasAnyBars = (list) => Array.isArray(list) && list.some((e) => barData(e.id).length > 0);
    const summaryParty = (summary?.party_members || []).map(id => ({ id, element: 'Generic' }));
    const summaryFoes = (summary?.foes || []).map(id => ({ id, element: 'Generic' }));
    if (!hasAnyBars(partyDisplay) && hasAnyBars(summaryParty)) partyDisplay = summaryParty;
    if (!hasAnyBars(foesDisplay) && hasAnyBars(summaryFoes)) foesDisplay = summaryFoes;
  }
</script>

<style>
  .layout {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 1rem;
    /* Make portraits smaller so bars are clearly visible */
    --portrait-size: 4.5rem;
  }
  .side {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }
  .combatant {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    width: 100%;
  }
  .row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    width: 100%;
    justify-content: center;
  }
  .row.player { flex-direction: row; }
  .row.foe { flex-direction: row-reverse; }
  .portrait-col { display: flex; flex-direction: column; align-items: center; }
  .bars {
    display: flex;
    width: 8rem;
    height: 0.55rem;
    position: relative;
    z-index: 1;
  }
  .bar {
    height: 100%;
  }
  .name-chip {
    width: var(--portrait-size);
    margin: 0 0 0.25rem 0;
    font-size: 0.78rem;
    color: #eee;
    text-align: center;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    background: rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.12);
    padding: 2px 4px;
  }
  .bar-wrap { display: flex; flex-direction: column; align-items: stretch; min-width: 8rem; }
  .bar-label { font-size: 0.7rem; color: #bbb; margin-bottom: 0.25rem; text-align: left; }
  .bar-stats { margin-top: 0.25rem; font-size: 0.72rem; color: #ddd; }
  .bar-stats { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .rewards {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }
  .effects-out { margin-top: 0.35rem; max-width: 320px; }
  .effects-section { margin-top: 0.25rem; }
  .effects-title { font-size: 0.72rem; color: #aaa; margin-bottom: 0.1rem; text-align: center; }
  .effect-cap { display: grid; grid-template-columns: 30px 1fr; gap: 0.4rem; align-items: center; margin: 0.15rem 0; padding: 0.25rem 0; }
  .effect-cap .dot-mini { width: 26px; height: 26px; border-radius: 4px; border: 2px solid #555; }
  .cap-lines { font-size: 0.7rem; line-height: 1.2; color: #ddd; }
  .cap-name { font-weight: 600; color: #eee; }
  .cap-stats { opacity: 0.9; }
  /* Hide in-portrait HP and Buff bars only inside the review UI */
  .review :global(.portrait-wrap .hp-bar) { display: none; }
  .review :global(.portrait-wrap .buff-bar) { display: none; }
  .subtle { opacity: 0.85; }
  .events {
    margin-top: 0.75rem;
    max-height: 240px;
    overflow: auto;
    border: var(--glass-border);
    background: rgba(0,0,0,0.4);
    padding: 0.5rem;
  }
  .event-row { font-size: 0.72rem; color: #ddd; margin: 0.15rem 0; white-space: nowrap; }
  .header { font-size: 0.85rem; color: #fff; margin-bottom: 0.25rem; display: flex; align-items: center; gap: 0.75rem; }
  .spacer { flex: 1; }
  .mini-btn { border: 1px solid #888; background: #111; color: #fff; font-size: 0.7rem; padding: 0.2rem 0.4rem; cursor: pointer; }
  .reward-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(200px, 1fr));
    gap: 0.75rem;
    max-width: 960px;
  }
  .effects-summary {
    margin-top: 0.75rem;
    border: var(--glass-border);
    background: rgba(0,0,0,0.4);
    padding: 0.75rem;
    border-radius: 4px;
  }
  .effects-header {
    font-size: 0.85rem;
    color: #fff;
    margin-bottom: 0.5rem;
    text-align: center;
    font-weight: 600;
  }
  .effects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }
  .effects-column {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  .effects-column-title {
    font-size: 0.75rem;
    color: #aaa;
    margin-bottom: 0.25rem;
    text-align: center;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .effect-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.25rem 0.5rem;
    background: rgba(255,255,255,0.05);
    border-radius: 3px;
    border: 1px solid rgba(255,255,255,0.1);
  }
  .effect-name {
    font-size: 0.72rem;
    color: #ddd;
    font-weight: 500;
  }
  .effect-count {
    font-size: 0.7rem;
    color: #bbb;
    font-weight: 600;
    background: rgba(255,255,255,0.1);
    padding: 0.1rem 0.3rem;
    border-radius: 2px;
  }
  .new-badge {
    font-size: 0.6rem;
    color: #4ade80;
    background: rgba(74, 222, 128, 0.2);
    padding: 0.1rem 0.25rem;
    border-radius: 2px;
    margin-left: 0.25rem;
    border: 1px solid rgba(74, 222, 128, 0.3);
  }
  .new-feature-badge {
    font-size: 0.65rem;
    color: #fbbf24;
    background: rgba(251, 191, 36, 0.2);
    padding: 0.15rem 0.35rem;
    border-radius: 3px;
    margin-left: 0.5rem;
    border: 1px solid rgba(251, 191, 36, 0.4);
    font-weight: 600;
    text-shadow: 0 0 4px rgba(251, 191, 36, 0.3);
  }
  .detail-section {
    margin-top: 0.75rem;
    border-top: 1px solid rgba(255,255,255,0.1);
    padding-top: 0.5rem;
  }
  .detail-title {
    font-size: 0.75rem;
    color: #aaa;
    margin-bottom: 0.35rem;
    text-align: center;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .detail-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 0.25rem;
  }
  .detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.2rem 0.4rem;
    background: rgba(255,255,255,0.03);
    border-radius: 2px;
    border: 1px solid rgba(255,255,255,0.05);
  }
  .detail-name {
    font-size: 0.7rem;
    color: #ccc;
    font-weight: 500;
  }
  .detail-stats {
    font-size: 0.65rem;
    color: #999;
    font-weight: 600;
  }
  
  /* Tab system styles */
  .battle-review-tabs {
    background: rgba(0,0,0,0.4);
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
  }
  
  .tabs-nav {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    padding-bottom: 1rem;
  }
  
  .tab-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    background: rgba(255,255,255,0.1);
    color: #ccc;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.75rem;
    min-width: 0;
  }
  
  .tab-btn:hover {
    background: rgba(255,255,255,0.2);
    color: #fff;
  }
  
  .tab-btn.active {
    background: rgba(120,180,255,0.3);
    color: #fff;
    border: 1px solid rgba(120,180,255,0.5);
  }
  
  .tab-label {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100px;
  }
  
  .tab-content {
    min-height: 300px;
  }
  
  /* Entity breakdown styles */
  .entity-breakdown {
    padding: 1rem;
    background: rgba(0,0,0,0.2);
    border-radius: 6px;
  }
  
  .entity-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
  }
  
  .entity-header h3 {
    margin: 0;
    color: #fff;
    font-size: 1.2rem;
  }
  
  .entity-section {
    margin-bottom: 1.5rem;
  }
  
  .entity-section h4 {
    margin: 0 0 0.75rem 0;
    color: #fff;
    font-size: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .damage-breakdown {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.5rem;
  }
  
  .damage-item {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem;
    background: rgba(255,255,255,0.05);
    border-radius: 4px;
  }
  
  .damage-element {
    color: #ccc;
    font-size: 0.8rem;
  }
  
  .damage-amount {
    color: #fff;
    font-weight: 600;
    font-size: 0.8rem;
  }
  
  .entity-stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.75rem;
  }
  
  .stat-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    background: rgba(255,255,255,0.05);
    border-radius: 4px;
    font-size: 0.8rem;
  }
  
  .stat-value {
    color: #fff;
    font-weight: 600;
    margin-left: auto;
  }
  
  .stat-detail {
    color: #ccc;
    font-size: 0.7rem;
  }
  
  .resource-breakdown {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
    margin-left: auto;
  }
  
  .resource-item {
    background: rgba(255,255,255,0.1);
    padding: 0.2rem 0.4rem;
    border-radius: 2px;
    font-size: 0.7rem;
    color: #fff;
  }
  
  /* Enhanced icons in titles */
  .effects-header,
  .effects-column-title,
  .detail-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
</style>

<div class="layout review">
  <div class="side">
    {#each partyDisplay as member}
      <div class="combatant">
        <div class="row player">
          <div class="portrait-col">
            <div class="name-chip">{member.id || member}</div>
            <FighterPortrait
            fighter={{
              ...member,
              id: (member.id || member),
              element: (member.element || primaryElement(member.id || member)),
              hp: (Number.isFinite(member.hp) ? member.hp : 1),
              max_hp: (Number.isFinite(member.max_hp) && member.max_hp > 0 ? member.max_hp : 1),
              dots: member.dots || [],
              hots: member.hots || [],
              active_effects: member.active_effects || [],
              shields: member.shields || 0,
            }}
          />
          </div>
          <div class="bar-wrap">
            <div class="bar-label">Element Damage</div>
            <div class="bars">
              {#each barData(member.id || member) as seg}
                <div
                  class="bar"
                  style={`width: ${seg.pct}%; background: ${getElementColor(seg.element)}`}
                />
              {/each}
            </div>
            <div class="bar-stats">Dealt: {fmt(totalDealt(member.id || member))} • Taken: {fmt(totalTaken(member.id || member))} • Heals: {fmt(totalHeal(member.id || member))} • Hits: {fmt(totalHits(member.id || member))}</div>
            {#if outgoingBySource.get(member.id || member)}
              <div class="effects-title" style="margin-top: 0.35rem;">DoTs / HoTs</div>
              {#if (outgoingBySource.get(member.id || member).dots || []).length}
                <div class="effects-section">
                  {#each outgoingBySource.get(member.id || member).dots as d}
                    <div class="effect-cap" title={`${d.name || d.id} • Dmg: ${d.damage ?? 0} • Turns: ${d.turns}${d.stacks > 1 ? ` • x${d.stacks}` : ''}`}>
                      <img class="dot-mini" src={getDotImage(d)} alt={d.name || d.id} style={`border-color: ${getElementColor(getDotElement(d))}`}/>
                      <div class="cap-lines">
                        <div class="cap-name">{d.name || d.id}</div>
                        <div class="cap-stats">Dmg {fmt(d.damage ?? 0)} • Turns {d.turns}{d.stacks > 1 ? ` • x${d.stacks}` : ''}</div>
                      </div>
                    </div>
                  {/each}
                </div>
              {/if}
              {#if (outgoingBySource.get(member.id || member).hots || []).length}
                <div class="effects-section">
                  {#each outgoingBySource.get(member.id || member).hots as h}
                    <div class="effect-cap" title={`${h.name || h.id} • Heal: ${h.healing ?? 0} • Turns: ${h.turns}${h.stacks > 1 ? ` • x${h.stacks}` : ''}`}>
                      <img class="dot-mini" src={getDotImage({ ...h, type: 'hot' })} alt={h.name || h.id} style={`border-color: ${getElementColor(getDotElement(h))}`}/>
                      <div class="cap-lines">
                        <div class="cap-name">{h.name || h.id}</div>
                        <div class="cap-stats">Heal {fmt(h.healing ?? 0)} • Turns {h.turns}{h.stacks > 1 ? ` • x${h.stacks}` : ''}</div>
                      </div>
                    </div>
                  {/each}
                </div>
              {/if}
              {#if (outgoingBySource.get(member.id || member).buffs || []).length}
                <div class="effects-section">
                  {#each outgoingBySource.get(member.id || member).buffs as b}
                    <div class="effect-cap" title={`${b.name || 'Effect'}${b.duration ? ` • ${b.duration} turns` : ''}`}>
                      <img class="dot-mini" src={getDotImage({ id: b.name || 'effect', type: 'generic' })} alt={b.name || 'Effect'} style={`border-color: ${getElementColor('generic')}`}/>
                      <div class="cap-lines">
                        <div class="cap-name">{b.name || 'Effect'}</div>
                        <div class="cap-stats">{b.duration ? `${b.duration} turns` : 'Active'}</div>
                      </div>
                    </div>
                  {/each}
                </div>
              {/if}
            {/if}
          </div>
        </div>
        
      </div>
    {/each}
  </div>
  <div class="side rewards">
    {#if cards.length}
      <div class="reward-grid">
        {#each cards.slice(0,3) as card, i (card.id)}
          <RewardCard entry={card} type="card" on:select={handleSelect} />
        {/each}
      </div>
    {/if}
    {#if relics.length}
      <div class="reward-grid">
        {#each relics.slice(0,3) as relic, i (relic.id)}
          <CurioChoice entry={relic} on:select={handleSelect} />
        {/each}
      </div>
    {/if}
  </div>
  <div class="side">
    {#each foesDisplay as foe}
      <div class="combatant">
        <div class="row foe">
          <div class="portrait-col">
            <div class="name-chip">{foe.id || foe}</div>
            <FighterPortrait
            fighter={{
              ...foe,
              id: (foe.id || foe),
              element: (foe.element || primaryElement(foe.id || foe)),
              hp: (Number.isFinite(foe.hp) ? foe.hp : 1),
              max_hp: (Number.isFinite(foe.max_hp) && foe.max_hp > 0 ? foe.max_hp : 1),
              dots: foe.dots || [],
              hots: foe.hots || [],
              active_effects: foe.active_effects || [],
              shields: foe.shields || 0,
            }}
          />
          </div>
          <div class="bar-wrap">
            <div class="bar-label">Element Damage</div>
            <div class="bars">
              {#each barData(foe.id || foe) as seg}
                <div
                  class="bar"
                  style={`width: ${seg.pct}%; background: ${getElementColor(seg.element)}`}
                />
              {/each}
            </div>
            <div class="bar-stats">Dealt: {fmt(totalDealt(foe.id || foe))} • Taken: {fmt(totalTaken(foe.id || foe))} • Heals: {fmt(totalHeal(foe.id || foe))} • Hits: {fmt(totalHits(foe.id || foe))}</div>
          </div>
        </div>
        
        {#if outgoingBySource.get(foe.id || foe)}
          <div class="effects-out">
            {#if (outgoingBySource.get(foe.id || foe).dots || []).length}
              <div class="effects-section">
                <div class="effects-title">DoTs Applied</div>
                {#each outgoingBySource.get(foe.id || foe).dots as d}
                  <div class="effect-cap" title={`${d.name || d.id} • Dmg: ${d.damage ?? 0} • Turns: ${d.turns}${d.stacks > 1 ? ` • x${d.stacks}` : ''}`}>
                    <img class="dot-mini" src={getDotImage(d)} alt={d.name || d.id} style={`border-color: ${getElementColor(getDotElement(d))}`}/>
                    <div class="cap-lines">
                      <div class="cap-name">{d.name || d.id}</div>
                      <div class="cap-stats">Dmg {fmt(d.damage ?? 0)} • Turns {d.turns}{d.stacks > 1 ? ` • x${d.stacks}` : ''}</div>
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
            {#if (outgoingBySource.get(foe.id || foe).hots || []).length}
              <div class="effects-section">
                <div class="effects-title">HoTs Applied</div>
                {#each outgoingBySource.get(foe.id || foe).hots as h}
                  <div class="effect-cap" title={`${h.name || h.id} • Heal: ${h.healing ?? 0} • Turns: ${h.turns}${h.stacks > 1 ? ` • x${h.stacks}` : ''}`}>
                    <img class="dot-mini" src={getDotImage({ ...h, type: 'hot' })} alt={h.name || h.id} style={`border-color: ${getElementColor(getDotElement(h))}`}/>
                    <div class="cap-lines">
                      <div class="cap-name">{h.name || h.id}</div>
                      <div class="cap-stats">Heal {fmt(h.healing ?? 0)} • Turns {h.turns}{h.stacks > 1 ? ` • x${h.stacks}` : ''}</div>
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
            {#if (outgoingBySource.get(foe.id || foe).buffs || []).length}
              <div class="effects-section">
                <div class="effects-title">Buffs/Debuffs Applied</div>
                {#each outgoingBySource.get(foe.id || foe).buffs as b}
                  <div class="effect-cap" title={`${b.name || 'Effect'}${b.duration ? ` • ${b.duration} turns` : ''}`}>
                    <img class="dot-mini" src={getDotImage({ id: b.name || 'effect', type: 'generic' })} alt={b.name || 'Effect'} style={`border-color: ${getElementColor('generic')}`}/>
                    <div class="cap-lines">
                      <div class="cap-name">{b.name || 'Effect'}</div>
                      <div class="cap-stats">{b.duration ? `${b.duration} turns` : 'Active'}</div>
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/if}
      </div>
    {/each}
  </div>

  <!-- Top-level summary and raw events toggle -->
  <div class="side" style="grid-column: 1 / -1;">
    <div class="header">
      <div>Result: {summary?.result || '—'}</div>
      <div>Duration: {summary?.duration_seconds ? Math.round(summary.duration_seconds) + 's' : '—'}</div>
      <div>Events: {fmt(summary?.event_count || (events?.length || 0))}</div>
      {#if summary?.relic_effects && Object.keys(summary.relic_effects).length > 0}
        <div>Relic Effects: {Object.values(summary.relic_effects).reduce((a, b) => a + b, 0)} <span class="new-badge">NEW</span></div>
      {/if}
      {#if summary?.card_effects && Object.keys(summary.card_effects).length > 0}
        <div>Card Effects: {Object.values(summary.card_effects).reduce((a, b) => a + b, 0)} <span class="new-badge">NEW</span></div>
      {/if}
      {#if summary?.critical_hits && Object.keys(summary.critical_hits).length > 0}
        <div>Criticals: {Object.values(summary.critical_hits).reduce((a, b) => a + b, 0)}</div>
      {/if}
      {#if summary?.shield_absorbed && Object.keys(summary.shield_absorbed).length > 0}
        <div>Shields: {Object.values(summary.shield_absorbed).reduce((a, b) => a + b, 0)} absorbed</div>
      {/if}
      <span class="spacer"></span>
      <button class="mini-btn" on:click={toggleEvents}>{showEvents ? 'Hide' : 'Show'} Event Log</button>
    </div>
    {#if showEvents}
      <div class="events">
        {#if loadingEvents}
          <div class="event-row subtle">Loading events…</div>
        {:else if events.length === 0}
          <div class="event-row subtle">No events available.</div>
        {:else}
          {#each events.slice(-200) as ev}
            <div class="event-row">[{ev.event_type}] {ev.attacker_id || '—'} → {ev.target_id || '—'}{ev.amount != null ? ` (${ev.amount})` : ''}{ev.damage_type ? ` [${ev.damage_type}]` : ''}{ev.source_type ? ` {${ev.source_type}}` : ''}</div>
          {/each}
        {/if}
      </div>
    {/if}
    
    <!-- Tab-based Battle Review Interface -->
    {#if (summary?.relic_effects && Object.keys(summary.relic_effects).length > 0) || (summary?.card_effects && Object.keys(summary.card_effects).length > 0)}
      <div class="battle-review-tabs">
        <!-- Tab Navigation -->
        <div class="tabs-nav">
          {#each availableTabs as tab}
            <button 
              class="tab-btn" 
              class:active={activeTab === tab.id} 
              on:click={() => activeTab = tab.id}
            >
              {#if tab.icon}
                <svelte:component this={tab.icon} size={16} />
              {:else if tab.entity}
                <FighterPortrait 
                  id={tab.entity.id} 
                  size="24px" 
                  showBuffs={false}
                  showHp={false}
                />
              {/if}
              <span class="tab-label">{tab.label}</span>
            </button>
          {/each}
        </div>

        <!-- Tab Content -->
        <div class="tab-content">
          {#if activeTab === 'overview'}
            <div class="effects-summary">
              <div class="effects-header">
                <Sparkles size={20} />
                Effects Summary <span class="new-feature-badge">NEW FEATURE</span>
              </div>
              <div class="effects-grid">
                {#if summary?.relic_effects && Object.keys(summary.relic_effects).length > 0}
                  <div class="effects-column">
                    <div class="effects-column-title">
                      <Shield size={16} />
                      Relic Effects
                    </div>
                    {#each Object.entries(summary.relic_effects).sort((a, b) => b[1] - a[1]) as [relicName, count]}
                      <div class="effect-item">
                        <span class="effect-name">{relicName}</span>
                        <span class="effect-count">×{count}</span>
                      </div>
                    {/each}
                  </div>
                {/if}
                {#if summary?.card_effects && Object.keys(summary.card_effects).length > 0}
                  <div class="effects-column">
                    <div class="effects-column-title">
                      <CreditCard size={16} />
                      Card Effects
                    </div>
              {#each Object.entries(summary.card_effects).sort((a, b) => b[1] - a[1]) as [cardName, count]}
                <div class="effect-item">
                  <span class="effect-name">{cardName}</span>
                  <span class="effect-count">×{count}</span>
                </div>
              {/each}
            </div>
          {/if}
        </div>
        
        <!-- Additional detailed tracking information -->
        {#if summary?.critical_hits && Object.keys(summary.critical_hits).length > 0}
          <div class="detail-section">
            <div class="detail-title">
              <Zap size={16} />
              Critical Hits Analysis
            </div>
            <div class="detail-grid">
              {#each Object.entries(summary.critical_hits).sort((a, b) => b[1] - a[1]) as [entity, crits]}
                <div class="detail-item">
                  <span class="detail-name">{entity}</span>
                  <span class="detail-stats">
                    {crits} crits
                    {#if summary?.critical_damage?.[entity]}
                      ({fmt(summary.critical_damage[entity])} dmg)
                    {/if}
                  </span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
        
        {#if summary?.shield_absorbed && Object.keys(summary.shield_absorbed).length > 0}
          <div class="detail-section">
            <div class="detail-title">
              <Shield size={16} />
              Shield Protection
            </div>
            <div class="detail-grid">
              {#each Object.entries(summary.shield_absorbed).sort((a, b) => b[1] - a[1]) as [entity, absorbed]}
                <div class="detail-item">
                  <span class="detail-name">{entity}</span>
                  <span class="detail-stats">{fmt(absorbed)} absorbed</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
        
        {#if summary?.dot_damage && Object.keys(summary.dot_damage).length > 0}
          <div class="detail-section">
            <div class="detail-title">
              <Flame size={16} />
              DoT Damage
            </div>
            <div class="detail-grid">
              {#each Object.entries(summary.dot_damage).sort((a, b) => b[1] - a[1]) as [entity, damage]}
                <div class="detail-item">
                  <span class="detail-name">{entity}</span>
                  <span class="detail-stats">{fmt(damage)} DoT dmg</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
        
        {#if summary?.hot_healing && Object.keys(summary.hot_healing).length > 0}
          <div class="detail-section">
            <div class="detail-title">
              <Heart size={16} />
              HoT Healing
            </div>
            <div class="detail-grid">
              {#each Object.entries(summary.hot_healing).sort((a, b) => b[1] - a[1]) as [entity, healing]}
                <div class="detail-item">
                  <span class="detail-name">{entity}</span>
                  <span class="detail-stats">{fmt(healing)} HoT heal</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
        
        {#if summary?.resources_spent && Object.keys(summary.resources_spent).length > 0}
          <div class="detail-section">
            <div class="detail-title">
              <Coins size={16} />
              Resource Usage
            </div>
            <div class="detail-grid">
              {#each Object.entries(summary.resources_spent) as [entity, resources]}
                <div class="detail-item">
                  <span class="detail-name">{entity}</span>
                  <span class="detail-stats">
                    {#each Object.entries(resources) as [type, amount]}
                      {type}: {fmt(amount)}
                    {/each}
                  </span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
        
        {#if summary?.temporary_hp_granted && Object.keys(summary.temporary_hp_granted).length > 0}
          <div class="detail-section">
            <div class="detail-title">
              <TrendingUp size={16} />
              Temporary HP
            </div>
            <div class="detail-grid">
              {#each Object.entries(summary.temporary_hp_granted).sort((a, b) => b[1] - a[1]) as [entity, tempHp]}
                <div class="detail-item">
                  <span class="detail-name">{entity}</span>
                  <span class="detail-stats">{fmt(tempHp)} temp HP</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
        
        {#if summary?.effect_applications && Object.keys(summary.effect_applications).length > 0}
          <div class="detail-section">
            <div class="detail-title">
              <Sparkles size={16} />
              Effect Applications
            </div>
            <div class="detail-grid">
              {#each Object.entries(summary.effect_applications).sort((a, b) => b[1] - a[1]).slice(0, 8) as [effect, count]}
                <div class="detail-item">
                  <span class="detail-name">{effect}</span>
                  <span class="detail-stats">×{count}</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
              </div>
            {:else}
              <!-- Entity-specific tab content -->
              {@const entityData = getEntityData(activeTab)}
              {@const currentTab = availableTabs.find(t => t.id === activeTab)}
              {#if entityData && currentTab}
                <div class="entity-breakdown">
                  <div class="entity-header">
                    <h3>{currentTab.label} Breakdown</h3>
                    {#if currentTab.entity}
                      <FighterPortrait 
                        id={currentTab.entity.id} 
                        size="48px" 
                        showBuffs={true}
                        showHp={true}
                      />
                    {/if}
                  </div>
                  
                  <!-- Damage Output -->
                  {#if Object.keys(entityData.damage).length > 0}
                    <div class="entity-section">
                      <h4>Damage Output</h4>
                      <div class="damage-breakdown">
                        {#each Object.entries(entityData.damage) as [element, damage]}
                          <div class="damage-item">
                            <span class="damage-element">{element}</span>
                            <span class="damage-amount">{fmt(damage)}</span>
                          </div>
                        {/each}
                      </div>
                    </div>
                  {/if}
                  
                  <!-- Stats Grid -->
                  <div class="entity-stats-grid">
                    {#if entityData.criticals > 0}
                      <div class="stat-item">
                        <Zap size={16} />
                        <span>Critical Hits</span>
                        <span class="stat-value">{entityData.criticals}</span>
                        {#if entityData.criticalDamage > 0}
                          <span class="stat-detail">({fmt(entityData.criticalDamage)} dmg)</span>
                        {/if}
                      </div>
                    {/if}
                    
                    {#if entityData.shieldAbsorbed > 0}
                      <div class="stat-item">
                        <Shield size={16} />
                        <span>Shield Absorbed</span>
                        <span class="stat-value">{fmt(entityData.shieldAbsorbed)}</span>
                      </div>
                    {/if}
                    
                    {#if entityData.dotDamage > 0}
                      <div class="stat-item">
                        <Flame size={16} />
                        <span>DoT Damage</span>
                        <span class="stat-value">{fmt(entityData.dotDamage)}</span>
                      </div>
                    {/if}
                    
                    {#if entityData.hotHealing > 0}
                      <div class="stat-item">
                        <Heart size={16} />
                        <span>HoT Healing</span>
                        <span class="stat-value">{fmt(entityData.hotHealing)}</span>
                      </div>
                    {/if}
                    
                    {#if entityData.tempHpGranted > 0}
                      <div class="stat-item">
                        <TrendingUp size={16} />
                        <span>Temp HP Granted</span>
                        <span class="stat-value">{fmt(entityData.tempHpGranted)}</span>
                      </div>
                    {/if}
                    
                    {#if Object.keys(entityData.resourcesSpent).length > 0}
                      <div class="stat-item">
                        <Coins size={16} />
                        <span>Resources Spent</span>
                        <div class="resource-breakdown">
                          {#each Object.entries(entityData.resourcesSpent) as [type, amount]}
                            <span class="resource-item">{type}: {fmt(amount)}</span>
                          {/each}
                        </div>
                      </div>
                    {/if}
                  </div>
                </div>
              {/if}
            {/if}
          </div>
        </div>
    {/if}
  </div>
</div>
