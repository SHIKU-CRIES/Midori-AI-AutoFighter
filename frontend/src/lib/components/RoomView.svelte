<script>
  export let result = '';
  export let foes = [];
  export let party = [];
  export let activeId = null;
</script>

<style>
  .room {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    aspect-ratio: 16 / 9;
    width: 100%;
    border: 2px solid #fff;
    padding: 0.5rem;
    box-sizing: border-box;
  }

  .foes,
  .party {
    display: flex;
    justify-content: center;
    gap: 0.25rem;
    width: 100%;
  }

  .foe {
    width: 40px;
    height: 40px;
    border: 2px solid #f00;
    position: relative;
  }

  .foe .bar {
    position: absolute;
    bottom: -6px;
    left: 0;
    height: 4px;
    background: red;
    width: 100%;
  }

  .member {
    width: 40px;
    height: 40px;
    border: 2px solid #0f0;
    position: relative;
  }

  .member .ult {
    position: absolute;
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
    width: 12px;
    height: 12px;
    border: 2px solid #fff;
    border-radius: 50%;
  }

  @media (min-width: 600px) {
    .foe:nth-child(n+11) {
      display: none;
    }
  }

  @media (max-width: 599px) {
    .foe:nth-child(n+4) {
      display: none;
    }
    .room {
      aspect-ratio: auto;
    }
  }

  .arrow {
    position: absolute;
    left: 50%;
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
  }

  .arrow-party {
    bottom: 100%;
    border-bottom: 6px solid #fff;
    animation: bounce-up 0.5s ease-in-out infinite;
  }

  .arrow-foe {
    top: 100%;
    border-top: 6px solid #fff;
    animation: bounce-down 0.5s ease-in-out infinite;
  }

  @keyframes bounce-up {
    0%, 100% {
      transform: translateX(-50%) translateY(0);
    }
    50% {
      transform: translateX(-50%) translateY(-4px);
    }
  }

  @keyframes bounce-down {
    0%, 100% {
      transform: translateX(-50%) translateY(0);
    }
    50% {
      transform: translateX(-50%) translateY(4px);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .arrow-party,
    .arrow-foe {
      animation: none;
    }
  }
</style>

<div class="room">
  <div class="foes">
    {#each foes as foe}
      <div class="foe" title={foe.id}>
        {#if activeId === foe.id}
          <div class="arrow arrow-foe"></div>
        {/if}
        <div class="bar" style={`width:${foe.hp}%`}></div>
      </div>
    {/each}
  </div>
  <div class="party">
    {#each party as member}
      <div class="member" title={member}>
        {#if activeId === member.id}
          <div class="arrow arrow-party"></div>
        {/if}
        <div class="ult"></div>
      </div>
    {/each}
  </div>
  <!-- Removed bottom result text to avoid showing raw errors in the view. -->
</div>
