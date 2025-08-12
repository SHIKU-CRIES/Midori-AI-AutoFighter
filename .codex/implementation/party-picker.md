# Party Picker

The Svelte `PartyPicker` component lets players choose up to four allies before a run. A random background image is selected from `frontend/src/lib/assets/backgrounds`, and portraits load from `assets/characters` with a fallback to a random portrait when an image is missing.

The roster only shows owned characters plus the player's avatar, which is pinned to the top and preselected. The list scrolls vertically with a gradient fade at the top and bottom. Clicking a portrait toggles selection unless the character is the player or the party already has four members.

`PartyPicker` dispatches a `confirm` event containing the selected ids. The main menu opens the picker in two modes:

- **Party:** from the Party button, allowing pre-run lineup adjustments.
- **Run:** from the Run button, which after confirmation starts a run, updates the party via `/update_party`, and hides the picker.

## Testing
- `bun test frontend/tests/partypicker.test.js`
