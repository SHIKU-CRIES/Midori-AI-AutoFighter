# UI Text Rendering Issue (Aug 4, 2025)

The screenshot shows blurry, overlapping, and duplicated text in the Panda3D window. Possible causes:

1. **Multiple UI Layers/Scenes:** If previous scenes or UI elements (OnscreenText, DirectButton, etc.) are not fully destroyed in their `teardown()` methods, remnants may remain and overlap with new UI. The `SceneManager` calls `teardown()` before switching scenes, but if a scene's teardown is incomplete, this can happen.

2. **Repeated Rendering:** If text is being drawn multiple times per frame, or if multiple scenes are active at once, text can appear duplicated and blurry.

3. **Buffer/Clearing Issues:** If the render buffer is not cleared properly between frames or scene switches, old text may persist and overlap.

**Next Steps:**
- Double-check that all UI elements are destroyed in every scene's `teardown()` method.
- Ensure only one scene is active at a time and that `SceneManager.switch_to()` is always used for scene changes.
- If the issue persists, add debug prints to scene setup/teardown to confirm proper destruction and creation of UI elements.


# Duplicate UI Loading Issue (Aug 4, 2025)

The new screenshot again shows duplicated, overlapping text. This suggests the UI (MainMenu or other scene) is being loaded or rendered twice. Possible causes:

1. **Scene Setup Called Twice:** The MainMenu scene may be switched to or set up multiple times, either by repeated calls to `scene_manager.switch_to(MainMenu(self))` or by returning to the menu without proper teardown.

2. **Incomplete Teardown:** If previous UI elements are not fully destroyed in the scene's `teardown()` method, remnants may remain and overlap with new UI.

3. **Multiple Scene Instances:** If more than one instance of MainMenu (or another scene) is active, their UI elements may stack.

**Debugging Steps:**
- Add debug prints to MainMenu's `setup()` and `teardown()` methods to confirm how many times they are called.
- Ensure that every scene switch uses `SceneManager.switch_to()` and that only one scene is active at a time.
- Double-check that all UI elements are destroyed in every scene's `teardown()` method.

This is likely a scene management or teardown bug, not a font or rendering issue.
