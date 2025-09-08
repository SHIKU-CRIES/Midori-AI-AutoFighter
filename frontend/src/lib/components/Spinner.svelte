<script>
  export let size = '1rem';
  export let thickness = '2px';
</script>

<div class="spinner" style={`width: ${size}; height: ${size}; border-width: ${thickness};`}></div>

<style>
  .spinner {
    border-style: solid;
    border-color: currentColor;
    border-right-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
