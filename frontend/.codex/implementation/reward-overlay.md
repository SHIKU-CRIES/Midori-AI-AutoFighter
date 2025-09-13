# Reward Overlay

`src/lib/RewardOverlay.svelte` presents battle rewards using `RewardCard.svelte` for cards and `CurioChoice.svelte` for relics.
Both components wrap `CardArt.svelte`, which builds the Star Rail–style frame with a star-colored header, centered icon, star count, and description.
`OverlayHost.svelte` spawns `FloatingLoot.svelte` elements when `roomData.loot` is present, so gold and item drops briefly rise on screen and are omitted from the reward overlay.
Assets are resolved by star folder and id through `rewardLoader.js`.

Ambient effects from `EnrageIndicator.svelte` continue to render while the
rewards overlay is shown and fade out gracefully, so the transition from
combat to rewards remains smooth.

`handleLootAcknowledge()` now stops any active battle polling timers before
calling the backend so lingering snapshot requests cannot mark the run as ended
mid‑acknowledgement.
