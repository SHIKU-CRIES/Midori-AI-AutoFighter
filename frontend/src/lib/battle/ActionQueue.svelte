<script>
  import { getCharacterImage, getElementColor } from '../systems/assetLoader.js';
  import { flip } from 'svelte/animate';

  export let queue = [];
  export let combatants = [];
  export let reducedMotion = false;
  export let showActionValues = false;

    function findCombatant(id) {
      return combatants.find((c) => c.id === id) || { id };
    }

    $: displayQueue = queue.filter((e) => {
      const fighter = findCombatant(e.id);
      return fighter.hp >= 1;
    });
    $: activeIndex = displayQueue.findIndex((e) => !e.bonus);
  </script>

<div class="action-queue" data-testid="action-queue">
  {#each displayQueue as entry, i (entry.bonus ? `b-${entry.id}-${i}` : entry.id)}
    {@const fighter = findCombatant(entry.id)}
    {@const elColor = getElementColor(fighter.element)}
    <div
      class="entry"
      class:active={i === activeIndex}
      class:bonus={entry.bonus}
      style="--element-color: {elColor}"
      animate:flip={{ duration: reducedMotion ? 0 : 220 }}
    >
      <img src={getCharacterImage(fighter.summon_type || fighter.id)} alt="" class="portrait" />
      {#if showActionValues}
        <div class="av">{Math.round(entry.action_value)}</div>
      {/if}
    </div>
  {/each}
</div>

<style>
  .action-queue {
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    justify-content: center;
    align-items: center;
    z-index: 2;
  }
  .entry {
    position: relative;
    width: 160px;
    height: 90px; /* 16:9 */
    will-change: transform;
    border: 2px solid var(--element-color);
    border-radius: 8px;
    overflow: hidden;
    }
  .entry.bonus {
    opacity: 0.6;
  }
  .portrait {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: cover;
  }
  .av {
    position: absolute;
    bottom: 4px;
    right: 4px;
    font-size: 0.75rem;
    background: rgba(0,0,0,0.35);
    box-shadow: inset 0 0 0 2px color-mix(in oklab, var(--element-color) 60%, black);
    border-radius: 6px;
    padding: 0 6px;
    color: var(--element-color);
  }
</style>
