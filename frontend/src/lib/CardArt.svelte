<script>
  import { getRewardArt } from './rewardLoader.js';
  export let entry = {};
  export let type = 'card';
  export let roundIcon = false;
  export let size = 'normal';
  const starColors = {
    1: '#808080',
    2: '#228B22',
    3: '#1E90FF',
    4: '#800080',
    5: '#FFD700',
    fallback: '#708090'
  };
  $: width = size === 'small' ? 110 : 220;
  $: iconHeight = size === 'small' ? 60 : 120;
</script>

<div class="card-art" style={`width:${width}px`}>
  <div class="header" style={`background:${starColors[entry.stars] || starColors.fallback}`}>{entry.name}</div>
  <div class={`icon${roundIcon ? ' round' : ''}`} style={`height:${iconHeight}px`}>
    <img src={getRewardArt(type, `${entry.stars}star/${entry.id}`)} alt={entry.name} />
  </div>
  <div class="stars">{'★'.repeat(entry.stars || 0)}</div>
  {#if entry.about}
    <div class="about">{entry.about}</div>
  {/if}
</div>

<style>
  .card-art {
    background: rgba(0,0,0,0.6);
    border: 1px solid rgba(255,255,255,0.2);
    padding-bottom: 0.5rem;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    color: #fff;
  }
  .header {
    padding: 0.25rem 0.4rem;
    font-weight: bold;
    text-align: left;
    font-size: 0.9rem;
  }
  .icon {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .icon img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }
  .icon.round img {
    border-radius: 50%;
  }
  .stars {
    text-align: center;
    margin-top: 0.25rem;
    font-size: 0.85rem;
  }
  .about {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
    text-align: left;
  }
</style>
