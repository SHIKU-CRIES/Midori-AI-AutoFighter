<script>
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';

  let pingStatus = 'unknown'; // 'healthy', 'degraded', 'error', 'unknown'
  let pingTime = null;
  let isInCombat = false;
  let interval;
  let lastUpdateTime = 0;

  // Check if we're in combat by looking for battle-related elements or state
  function checkCombatState() {
    if (typeof window !== 'undefined') {
      // Check if battle is active from global state
      isInCombat = window.afBattleActive || false;
      
      // Also check for battle-related DOM elements as fallback
      const battleElements = document.querySelectorAll('[data-battle-active], .battle-view, .battle-snapshot');
      if (battleElements.length > 0) {
        isInCombat = true;
      }
    }
  }

  async function checkBackendHealth() {
    if (!browser) return;
    
    try {
      const startTime = performance.now();
      const response = await fetch('/api/performance/health', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        signal: AbortSignal.timeout(5000) // 5 second timeout
      });
      
      const endTime = performance.now();
      const networkPingTime = endTime - startTime;
      
      if (response.ok) {
        const data = await response.json();
        pingStatus = data.status === 'ok' ? 'healthy' : 
                    data.status === 'degraded' ? 'degraded' : 'error';
        
        // Use backend-reported ping if available, otherwise use network round-trip
        pingTime = data.ping_ms || networkPingTime;
        lastUpdateTime = Date.now();
      } else {
        pingStatus = 'error';
        pingTime = networkPingTime;
      }
    } catch (error) {
      pingStatus = 'error';
      pingTime = null;
      console.warn('Health check failed:', error.message);
    }
  }

  function getIndicatorSymbol() {
    checkCombatState();
    
    if (isInCombat) {
      // In combat: show ping time if available
      if (pingTime !== null) {
        return `${Math.round(pingTime)}ms`;
      }
      return '●'; // Solid dot when in combat but no ping data
    } else {
      // Out of combat: show +/- based on health
      return pingStatus === 'healthy' ? '+' : '-';
    }
  }

  function getIndicatorColor() {
    if (pingStatus === 'healthy') {
      return isInCombat ? '#00ff88' : '#00ff88'; // Green for healthy
    } else if (pingStatus === 'degraded') {
      return '#ffaa00'; // Orange for degraded
    } else if (pingStatus === 'error') {
      return '#ff4444'; // Red for error
    } else {
      return '#888888'; // Gray for unknown
    }
  }

  function getTooltipText() {
    checkCombatState();
    
    const baseStatus = pingStatus === 'healthy' ? 'Backend Healthy' :
                      pingStatus === 'degraded' ? 'Backend Degraded' :
                      pingStatus === 'error' ? 'Backend Error' : 'Backend Status Unknown';
    
    if (isInCombat && pingTime !== null) {
      return `${baseStatus}\nCombat Sync: ${Math.round(pingTime)}ms`;
    } else if (isInCombat) {
      return `${baseStatus}\nIn Combat`;
    } else {
      return baseStatus;
    }
  }

  onMount(() => {
    if (browser) {
      // Initial check
      checkBackendHealth();
      
      // Set up periodic health checks every 2 seconds
      interval = setInterval(() => {
        checkBackendHealth();
      }, 2000);

      // Listen for battle state changes
      const handleBattleStateChange = () => {
        checkCombatState();
      };

      // Set up mutation observer to detect battle state changes
      const observer = new MutationObserver(handleBattleStateChange);
      observer.observe(document.body, {
        attributes: true,
        attributeFilter: ['data-battle-active'],
        subtree: true
      });

      return () => {
        observer.disconnect();
      };
    }
  });

  onDestroy(() => {
    if (interval) {
      clearInterval(interval);
    }
  });

  // Check if the indicator is stale (no updates for >10 seconds)
  $: isStale = lastUpdateTime > 0 && (Date.now() - lastUpdateTime) > 10000;
</script>

<style>
  .ping-indicator {
    position: fixed;
    top: 12px;
    right: 12px;
    z-index: 10000;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    font-weight: bold;
    padding: 6px 10px;
    background: rgba(0, 0, 0, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    backdrop-filter: blur(4px);
    user-select: none;
    cursor: help;
    transition: all 0.2s ease;
    min-width: 24px;
    text-align: center;
  }

  .ping-indicator:hover {
    background: rgba(0, 0, 0, 0.95);
    border-color: rgba(255, 255, 255, 0.4);
    transform: scale(1.05);
  }

  .ping-indicator.stale {
    opacity: 0.5;
    animation: pulse 2s infinite;
  }

  .ping-indicator.combat {
    border-color: rgba(255, 255, 255, 0.6);
    box-shadow: 0 0 8px rgba(0, 255, 136, 0.3);
  }

  @keyframes pulse {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 0.8; }
  }
</style>

<div 
  class="ping-indicator" 
  class:stale={isStale}
  class:combat={isInCombat}
  style="color: {getIndicatorColor()}"
  title={getTooltipText()}
>
  {getIndicatorSymbol()}
</div>