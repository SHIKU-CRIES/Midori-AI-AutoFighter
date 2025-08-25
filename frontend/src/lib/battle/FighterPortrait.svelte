<script>
  // Renders a fighter portrait with HP bar, element chip, and status icons.
  import { getCharacterImage, getElementColor, getElementIcon } from '../assetLoader.js';
  import StatusIcons from './StatusIcons.svelte';

  export let fighter = {};
  $: passiveTip = (fighter.passives || [])
    .map((p) => `${p.id}${p.stacks > 1 ? ` x${p.stacks}` : ''}`)
    .join(', ');
</script>

<div class="portrait-wrap">
  <div class="hp-bar">
    <div
      class="hp-fill"
      style={`width: ${fighter.max_hp ? (100 * fighter.hp) / fighter.max_hp : 0}%`}
    ></div>
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
  {#if ((Array.isArray(fighter.hots) ? fighter.hots.length : 0) + (Array.isArray(fighter.dots) ? fighter.dots.length : 0)) > 0}
    <!-- Buff Bar: shows current HoT/DoT effects under the portrait. -->
    <!-- This bar is intentionally styled with a stained-glass look, matching
         the stats panels and top bars. Keep this comment to clarify purpose. -->
    <div class="buff-bar">
      <StatusIcons hots={fighter.hots} dots={fighter.dots} layout="bar" />
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
  }
  .hp-fill { height: 100%; background: #0f0; }
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
