# Settings Menu

The settings overlay now uses a tabbed layout with icon-only buttons
for each category:

- **Audio**: `Volume2` icon.
- **System**: `Cog` icon.
- **LLM**: `Brain` icon, shown only when language model controls are
  available.
- **Gameplay**: `Gamepad` icon.

`SettingsMenu.svelte` receives `backendFlavor` from the page and
checks it for `"llm"` to decide whether the LLM tab should appear. When
the flavor string omits `"llm"`, the component skips `getLrmConfig()`
and hides the model selector and test button.

The Gameplay tab's **End Run** button now attempts to end the current run by
ID and falls back to clearing all runs when the ID is missing or the targeted
request fails.
