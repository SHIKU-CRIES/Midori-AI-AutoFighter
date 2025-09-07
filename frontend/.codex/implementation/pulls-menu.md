# Pulls Menu

The `PullsMenu.svelte` component lets players spend gacha tickets. It shows
current pity and ticket counts and provides buttons for one, five, or ten
pulls. Each button disables when the player lacks enough tickets. After a
successful pull it opens `PullResultsOverlay.svelte`, which queues the
returned items and reveals them one at a time.
