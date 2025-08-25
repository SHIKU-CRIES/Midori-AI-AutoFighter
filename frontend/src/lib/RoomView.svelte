<script>
  export let result = '';
  export let foes = [];
  export let party = [];
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
</style>

<div class="room">
  <div class="foes">
    {#each foes as foe}
      <div class="foe" title={foe.id}>
        <div class="bar" style={`width:${foe.hp}%`}></div>
      </div>
    {/each}
  </div>
  <div class="party">
    {#each party as member}
      <div class="member" title={member}>
        <div class="ult"></div>
      </div>
    {/each}
  </div>
  <!-- Removed bottom result text to avoid showing raw errors in the view. -->
</div>
