<script>
  export let color = 'var(--element-color, currentColor)';
  export let duration = '1.2s';
  export let reducedMotion = false;
</script>

<div
  class="triple-ring-spinner"
  style={`--spinner-color: ${color}; --duration: ${duration};`}
  class:reduced={reducedMotion}
  aria-hidden="true"
>
  <div class="ring r1"></div>
  <div class="ring r2"></div>
  <div class="ring r3"></div>
</div>

<style>
  .triple-ring-spinner {
    position: relative;
    width: var(--spinner-size, clamp(14px, calc(var(--portrait-size) * 0.18), 32px));
    height: var(--spinner-size, clamp(14px, calc(var(--portrait-size) * 0.18), 32px));
  }
  .ring {
    position: absolute;
    top: 50%;
    left: 50%;
    border: 2px solid var(--spinner-color, currentColor);
    border-radius: 50%;
    opacity: 0.6;
    animation: pulse calc(var(--duration) * 2) ease-in-out infinite;
  }
  .r1 { --ring-size: 100%; animation-delay: 0s; }
  .r2 { --ring-size: 66%; animation-delay: calc(var(--duration) / 3); }
  .r3 { --ring-size: 33%; animation-delay: calc(var(--duration) * 2 / 3); }
  .ring {
    width: var(--ring-size);
    height: var(--ring-size);
    margin: calc(var(--ring-size) / -2);
  }
  .ring::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: calc(var(--ring-size) * 0.15);
    height: calc(var(--ring-size) * 0.15);
    border-radius: 50%;
    background: var(--spinner-color, currentColor);
    transform-origin: center;
    animation: spin var(--duration) linear infinite;
  }
  @keyframes spin {
    from { transform: rotate(0deg) translateX(calc(var(--ring-size) / 2)); }
    to { transform: rotate(360deg) translateX(calc(var(--ring-size) / 2)); }
  }
  @keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.6; }
    50% { transform: scale(1.2); opacity: 1; }
  }
  .reduced .ring,
  .reduced .ring::before {
    animation: none;
  }
</style>
