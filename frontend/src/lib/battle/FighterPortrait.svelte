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
    <StatusIcons hots={fighter.hots} dots={fighter.dots} />
  </div>
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
</style>
