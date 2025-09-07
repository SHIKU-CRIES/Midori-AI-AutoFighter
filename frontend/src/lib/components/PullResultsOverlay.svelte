<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import CurioChoice from './CurioChoice.svelte';

  export let results = [];

  const dispatch = createEventDispatcher();
  let queue = [];
  let visible = [];

  onMount(() => {
    queue = Array.isArray(results) ? [...results] : [];
    showNext();
  });

  function showNext() {
    if (queue.length === 0) return;
    visible = [...visible, queue.shift()];
    if (queue.length > 0) {
      setTimeout(showNext, 400);
    }
  }

  function close() {
    dispatch('close');
  }
</script>

<div class="layout">
  <div class="choices">
    {#each visible as r, i (i)}
      <div class="reveal" style={`--delay: ${i * 120}ms`}>
        <CurioChoice entry={r} disabled={true} />
      </div>
    {/each}
  </div>
  {#if queue.length === 0 && visible.length}
    <button class="done" on:click={close}>Done</button>
  {/if}
</div>

<style>
  .layout {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
  }
  .choices {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    justify-content: center;
  }
  .done {
    padding: 0.5rem 1rem;
    background: #0a0a0a;
    color: #fff;
    border: 2px solid #fff;
    cursor: pointer;
  }
  .reveal {
    opacity: 0;
    animation: overlay-reveal 0.4s forwards;
  }
  @keyframes overlay-reveal {
    from { transform: translateY(-20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }
</style>
