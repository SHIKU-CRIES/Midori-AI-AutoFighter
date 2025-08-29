<script>
  // Renders a fighter portrait with HP bar, element chip, and status icons.
  import { getCharacterImage, getElementColor, getElementIcon } from '../assetLoader.js';
  import StatusIcons from './StatusIcons.svelte';

  export let fighter = {};
  $: passiveTip = (fighter.passives || [])
    .map((p) => `${p.id}${p.stacks > 1 ? ` x${p.stacks}` : ''}`)
    .join(', ');

  // Percent helpers for HP and overheal (shields)
  $: _maxHP = Number(fighter?.max_hp || 0);
  $: _hp = Number(fighter?.hp || 0);
  $: _shields = Number(fighter?.shields || 0);
  $: hpPct = _maxHP > 0 ? Math.min(100, (100 * _hp) / _maxHP) : 0;
  $: ohPct = _maxHP > 0 ? Math.max(0, Math.min(100, (100 * _shields) / _maxHP)) : 0;
  // TODO: Make this dynamic per-character (max overheal percent).
  // For now, allow up to +100% overheal to display visually.
  const OH_CAP_UI = 100;
  $: ohDispPct = Math.min(ohPct, OH_CAP_UI);
</script>

<div class="portrait-wrap">
  <div class="hp-bar">
    {#if ohDispPct > 0}
      <div
        class="overheal-fill"
        style={`width: calc(${ohDispPct}% + 5px); left: -5px;`}
      ></div>
    {/if}
    <div class="hp-fill" style={`width: ${hpPct}%`}></div>
  </div>
  <div class="portrait-frame" title={passiveTip}>
    <img
      src={getCharacterImage(fighter.id)}
      alt=""
      class="portrait"
      style={`border-color: ${getElementColor(fighter.element)}`}
    />
    <div class="element-chip">
      <svelte:component
        this={getElementIcon(fighter.element)}
        class="element-icon"
        style={`color: ${getElementColor(fighter.element)}`}
        aria-hidden="true" />
    </div>
  </div>
  {#if ((Array.isArray(fighter.hots) ? fighter.hots.length : 0) + (Array.isArray(fighter.dots) ? fighter.dots.length : 0) + (Array.isArray(fighter.active_effects) ? fighter.active_effects.length : 0)) > 0}
    <!-- Buff Bar: shows current HoT/DoT effects under the portrait. -->
    <!-- This bar is intentionally styled with a stained-glass look, matching
         the stats panels and top bars. Keep this comment to clarify purpose. -->
    <div class="buff-bar">
      <StatusIcons hots={fighter.hots} dots={fighter.dots} active_effects={fighter.active_effects} layout="bar" />
    </div>
  {/if}
</div>

<style>
  .portrait-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .hp-bar {
    width: var(--portrait-size);
    height: 0.5rem;
    border: 1px solid #000;
    background: #333;
    margin-bottom: 0.2rem;
    position: relative;
    overflow: visible; /* allow underlay to extend slightly to the left */
  }
  .hp-fill { height: 100%; background: #0f0; position: absolute; left: 0; top: 0; }
  .overheal-fill {
    height: calc(100% + 4px);
    background: rgba(255, 255, 255, 0.92);
    position: absolute;
    left: 0;
    top: -2px; /* slight upward offset */
  }
  .portrait-frame { position: relative; width: var(--portrait-size); height: var(--portrait-size); }
  .portrait {
    width: 100%;
    height: 100%;
    border: 2px solid #555;
    border-radius: 4px;
    display: block;
  }
  .element-chip {
    position: absolute;
    bottom: 2px;
    right: 2px;
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: center;
    pointer-events: none;
  }
  .element-icon { width: 16px; height: 16px; display: block; }

  /* Buff Bar (stained-glass style) */
  .buff-bar {
    width: calc(var(--portrait-size) - 0.75rem); /* slightly narrower than portrait (left/right smaller) */
    margin: 0.5rem auto 0; /* add a bit more space from portrait and center it */
    padding: 0.25rem;
    background: var(--glass-bg);
    box-shadow: var(--glass-shadow);
    border: var(--glass-border);
    backdrop-filter: var(--glass-filter);
  }
</style>
