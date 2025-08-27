<script context="module">
  import { Play, Users, User, PackageOpen, Hammer, Settings, MessageSquare, Package } from 'lucide-svelte';

  // Build the run menu items array. Handlers are functions for each action.
  export function buildRunMenu(handlers, battleActive) {
    return [
      { icon: Play, label: 'Run', action: handlers.openRun, disabled: false },
      { icon: Users, label: 'Party', action: handlers.handleParty, disabled: battleActive },
      { icon: User, label: 'Edit', action: handlers.openEditor, disabled: battleActive },
      { icon: PackageOpen, label: 'Pulls', action: handlers.openPulls, disabled: battleActive },
      { icon: Hammer, label: 'Craft', action: handlers.openCraft, disabled: battleActive },
      { icon: Settings, label: 'Settings', action: handlers.openSettings, disabled: false },
      { icon: MessageSquare, label: 'Feedback', action: handlers.openFeedback, disabled: false },
      // Inventory moved to in-run NavBar; remove from main menu
    ];
  }
</script>
