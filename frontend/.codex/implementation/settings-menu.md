# Settings Menu

The settings overlay exposes audio, system, and gameplay options.

- `SettingsMenu.svelte` receives `backendFlavor` from the page and
  checks it for `"llm"` to decide whether language reasoning model
  controls should appear.
- When the flavor string omits `"llm"`, the component skips
  `getLrmConfig()` and hides the LRM model selector and test button.
