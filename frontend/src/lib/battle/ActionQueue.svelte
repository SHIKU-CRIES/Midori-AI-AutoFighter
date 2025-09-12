<script>
  import { getCharacterImage } from '../systems/assetLoader.js';
  import { flip } from 'svelte/animate';

  export let queue = [];
  export let combatants = [];
  export let reducedMotion = false;
  export let showActionValues = false;

    function findCombatant(id) {
      return combatants.find((c) => c.id === id) || { id };
    }

    $: activeIndex = queue.findIndex((e) => !e.bonus);
  </script>

<div class="action-queue" data-testid="action-queue">
  {#each queue as entry, i (i)}
    {@const fighter = findCombatant(entry.id)}
    <div
      class="entry"
      class:active={i === activeIndex}
      class:bonus={entry.bonus}
      animate:flip={{ duration: reducedMotion ? 0 : 200 }}
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
    gap: 0.25rem;
    justify-content: center;
    align-items: center;
    z-index: 2;
  }
  .entry {
    position: relative;
    width: 40px;
    height: 40px;
  }
    .entry.active {
      outline: 2px solid #fff;
    }
    .entry.bonus {
      opacity: 0.6;
    }
  .portrait {
    width: 100%;
    height: 100%;
    display: block;
  }
  .av {
    position: absolute;
    bottom: -0.6rem;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.6rem;
  }
</style>
