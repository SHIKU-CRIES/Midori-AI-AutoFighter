 # Feedback Log

- Date: 2025-08-15
- Author(s): Lead Dev, GitHub Copilot

Summary:

- Initial feedback entries consolidated into a single log.

Details:

1) UI clarity
- Observation: The Settings panel uses three logical columns but lacks visible headings.
- Recommendation: Add clear column titles: "Audio", "System", "Gameplay" to group related controls.
  - Audio: SFX Volume, Music Volume, Voice Volume
  - System: Pause on Stat Screen, Framerate
  - Gameplay: Autocraft

2) Framerate persistence bug
- Symptom: Selecting a framerate (controls backend polling frequency in battles) and clicking "Save" resets the value; the selection does not persist.
- Impact: Backend polling frequency cannot be changed as expected; affects network/load behavior in battles.
- Suggested follow-up: Investigate settings save/load path and persistence logic for framerate; reproduce and create a bug report with reproduction steps.

3) Pause-on-Stat behaviour
- Observation: "Pause on Stat Screen" behaves inconsistently and appears unused or janky in current builds.
- Recommendation: Remove or rework this option; if kept, ensure consistent behavior and document its effect.

Notes:
- These entries were originally recorded on 2025-08-15 by the lead developer and GitHub Copilot; consolidated to improve readability.
- Next actions: create issues for the framerate persistence bug and UI headings, or request a patch to add headings and validate settings persistence.
 
4) Player Editor save issue
- Symptom: Modified stat values in the Player Editor (e.g., setting Attack to 100) are not persisting — values revert to 0 after saving/closing.
- Impact: Player customization is broken and can cause confusion or lost progress when editing the player.
- Suggested follow-up: Track the save flow for Player Editor (UI -> state store -> persistence). Add reproduction steps and capture any console/network errors when saving.
 
5) Gacha pulls without tickets
- Symptom: The Pulls UI allows performing pulls even when Tickets are 0 (e.g., Pull 1 / Pull 10 succeed with Tickets: 0 displayed).
- Impact: Enables unintended free pulls and devalues in-game economy; potential client-side exploit.
- Suggested follow-up: Add server-side validation for pulls to require tickets or currency, and ensure the UI reflects current currency/ticket counts. Capture network requests during a pull to verify server response handling.

6) Crafting menu icons missing
- Symptom: Crafting list displays item names and counts but icons and star-rank outlines are missing (no visual sprites displayed).
- Impact: Harder to scan materials and identify rarities quickly; reduces UI polish and can confuse players.
- Suggested follow-up: Verify asset paths and rendering logic for crafting items; check CSS rules that may hide background images or SVG icons. Add a fallback placeholder icon when assets fail to load.

7) Party & Character picker issues
- Symptom: Multiple UI and data inconsistencies observed:
  - Party picker: player type is incorrect (player showing Fire instead of Light) because Player Editor settings are not persisting.
  - DEF is currently under the Core tab; should be at the top of the Defense tab.
  - EXP is placed at the bottom of the Core tab; should appear under HP.
  - Character picker: type icon uses the wrong color and the character box outline color is incorrect.
  - Character picker layout shows multiple characters per row; should display one character per row for readability.
- Impact: Confusing stat layout, incorrect visuals, and mismatched player types can cause gameplay errors and poor UX.
- Suggested follow-up: Reconcile Player Editor persistence first, then audit the character picker rendering and CSS (icon colors, outline colors, layout grid). Reorder stat placement in the UI and add tests to verify correct stat positions and type assignment.
 
8) Remove SPD stat from UI
- Symptom: UI shows a "SPD" stat, but the game does not implement a Speed stat.
- Impact: Misleading and confusing to players; should be removed to avoid confusion.
- Suggested follow-up: Remove SPD from UI components and templates. Search UI code for "spd"/"speed" usages and remove or disable them.

9) Map & Battle UI issues
- Map room scrolling:
  - Symptom: Map requires manual scrolling to bottom to view content; players should only need to see next 4 room groups instead of full map scroll.
  - Suggested follow-up: Implement viewport clipping or pagination to show only the next 4 room groups; reduce DOM nodes rendered for performance.

- Battle UI issues (start of battle / in-battle):
  - Missing party member icons and unknown damage types for characters — party members render without icons, likely missing asset loading or incorrect type mapping.
  - Rewards menu appears unthemed and outside of the battle viewport; right sidebar remains visible inside battle window.
  - Battle background not visible inside battle UI (background missing/clipped).
  - UI layout/positioning is janky on battle start (overlapping elements, sidebar bleeding into viewport).
  - Suggestion: Reuse party picker asset loading and type mapping; add a small shared utility to normalize character asset loading across modules.

- Suggested follow-up: Capture DOM/network during battle start, compare party picker asset load sequence, and ensure battle viewport isolates/hides non-battle UI (sidebars). Create issues with reproduction steps and sample network logs.



