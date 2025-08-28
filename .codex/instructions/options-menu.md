# Options Menu

The Options submenu lets players adjust audio levels, system behaviour, and gameplay automation. Controls appear under **Audio**, **System**, and **Gameplay** headings.

## Controls

- **Sound Effects Volume**
  - Slider adjusting sound effect levels.
  - Lucide icon: `volume-2`
  - Label: `SFX Volume`
  - Tooltip: `Adjust sound effect volume.`

- **Music Volume**
  - Slider adjusting background music levels.
  - Lucide icon: `music`
  - Label: `Music Volume`
  - Tooltip: `Adjust background music volume.`

- **Voice Volume**
  - Slider adjusting voice levels.
  - Lucide icon: `mic`
  - Label: `Voice Volume`
  - Tooltip: `Adjust voice volume.`

- **Framerate**
  - Select box limiting server polling frequency.
  - Label: `Framerate`
  - Tooltip: `Limit server polling frequency.`
- **Reduced Motion**
  - Toggle that slows animation effects for accessibility.
  - Label: `Reduced Motion`
  - Tooltip: `Slow down battle animations.`

- **Wipe Save Data**
  - Button that clears all save records after confirmation.
  - Lucide icon: `trash-2`
  - Label: `Wipe Save Data`
  - Tooltip: `Clear all save data.`
  - Behavior: also clears all frontend client storage (localStorage, sessionStorage, IndexedDB), deletes CacheStorage entries, unregisters service workers, and then forces a full page reload so stale roster or party data cannot persist.

- **Backup Save Data**
  - Button that downloads an encrypted snapshot of save tables.
  - Lucide icon: `download`
  - Label: `Backup Save Data`
  - Tooltip: `Download encrypted save backup.`

- **Import Save Data**
  - File picker that uploads an encrypted backup and restores it if valid.
  - Lucide icon: `upload`
  - Label: `Import Save Data`
  - Tooltip: `Import encrypted save backup.`

- **Autocraft**
  - Toggle that automatically crafts materials when possible.
  - Label: `Autocraft`
  - Tooltip: `Automatically craft materials when possible.`
  - Behavior: updates the backend via `/gacha/auto-craft` and stays in sync with the Crafting menu toggle.

- **End Run**
  - Button that terminates the active run.
  - Lucide icon: `power`
  - Label: `End Run`
  - Tooltip: `End the current run.`

## Guidelines

- Each control must include its Lucide icon, visible label, and hover tooltip.
- Changes take effect immediately and should persist between sessions.
