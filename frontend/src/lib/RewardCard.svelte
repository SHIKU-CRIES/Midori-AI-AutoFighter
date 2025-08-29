<script>
  import CardArt from './CardArt.svelte';
  import { createEventDispatcher } from 'svelte';
  export let entry = {};
  export let type = 'card';
  export let size = 'normal';
  export let quiet = false;
  const dispatch = createEventDispatcher();
  function handleClick() {
    dispatch('select', { type, id: entry?.id, entry });
  }
  // enable usage as a normal button too
  export let disabled = false;
  export let ariaLabel = '';
  $: label = ariaLabel || `Select ${type} ${entry?.name || entry?.id || ''}`;
  $: btnType = 'button';
  $: tabIndex = disabled ? -1 : 0;
  $: role = 'button';
  $: ariaDisabled = disabled ? 'true' : 'false';
  $: onKey = (e) => {
    if (disabled) return;
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };
  $: noop = null;
  // end
  
</script>

<button class="card tooltip-trigger" type={btnType} aria-label={label} {tabIndex} role={role} aria-disabled={ariaDisabled} on:click={handleClick} on:keydown={onKey}>
  <CardArt {entry} {type} {size} hideFallback={true} {quiet} />
  {#if entry.about}
    <div class="tooltip">
      {entry.about}
    </div>
  {/if}
</button>

<style>
  .card {
    position: relative;
    padding: 0;
    border: none;
    background: none;
    cursor: pointer;
    filter: drop-shadow(0 2px 6px rgba(0,0,0,0.35));
    transition: transform 120ms ease, filter 120ms ease;
  }
  .card:hover,
  .card:focus-visible {
    transform: translateY(-2px);
    filter: drop-shadow(0 6px 14px rgba(0,0,0,0.45));
    outline: none;
  }
  .card:hover .tooltip {
    opacity: 1;
    visibility: visible;
  }
  
  .tooltip {
    position: absolute;
    bottom: 120%;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0,0,0,0.9);
    color: #fff;
    padding: 0.75rem;
    border-radius: 6px;
    font-size: 0.8rem;
    white-space: normal;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.2s ease;
    z-index: 1000;
    border: 1px solid rgba(255,255,255,0.2);
    max-width: 320px;
    text-align: center;
    line-height: 1.3;
  }

  .tooltip::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: rgba(0,0,0,0.9);
  }
</style>
