## Feedback Log
Details

### 1) Crafting menu icons missing (In testing)
- Symptom: Crafting list displays item names and counts but icons and star-rank outlines are missing (no visual sprites displayed).
- Impact: Harder to scan materials and identify rarities quickly; reduces UI polish and can confuse players.
- Suggested follow-up: Verify asset paths and rendering logic for crafting items; check CSS rules that may hide background images or SVG icons. Add a fallback placeholder icon when assets fail to load.

### 2) Crafted items do not stack and names are janky (In testing)
- Symptom: Crafted items in the crafting menu do not stack (e.g., 8x 4-star ice items show as 8 separate entries) and names are displayed poorly.
- Impact: Inventory is cluttered and hard to read; user cannot easily see total counts of each item.
- Suggested follow-up: Update UI and logic to stack items by type and rarity, and improve name formatting for clarity.

### 3) Settings do not autosave (New issue)
- Symptom: Changing settings in the UI does not persist after navigating away or refreshing the page.
- Impact: Poor UX; users must re-enter preferences each session which undermines trust.
- Reproduction steps:
	1. Open Settings page
	2. Modify a setting (toggle, dropdown, text input)
	3. Navigate to another page or refresh
	4. Observe that the change is not persisted
- Suggested follow-up:
	- Check the settings save handler and ensure it writes to the appropriate store (localStorage / backend API). Verify debounce/throttle logic, and that save calls are awaited before navigation.
	- Add unit/integration tests for the settings flow.

### 4) Settings UI needs refinement (New issue)
- Symptom: Settings controls are misaligned, labels are inconsistent, and there is no clear save/auto-save affordance.
- Impact: Users are unsure whether changes will be kept; accessibility and layout issues reduce usability.
- Suggested follow-up:
	- Redesign the settings panel for consistent spacing and label placement. Use accessible form controls and visible save state (Saved / Saving / Error).
	- Add autosave with undo and a manual Save button as a fallback. Provide inline validation messages.
	- Run a short UX pass: spacing, font sizes, and keyboard navigation.


