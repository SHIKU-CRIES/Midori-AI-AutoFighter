 # Feedback Log

- Date: 2025-08-15
- Author(s): Lead Dev, GitHub Copilot

Summary:

- Initial feedback entries consolidated into a single log.

Details:

2) Crafting menu icons missing (In testing)
- Symptom: Crafting list displays item names and counts but icons and star-rank outlines are missing (no visual sprites displayed).
- Impact: Harder to scan materials and identify rarities quickly; reduces UI polish and can confuse players.
- Suggested follow-up: Verify asset paths and rendering logic for crafting items; check CSS rules that may hide background images or SVG icons. Add a fallback placeholder icon when assets fail to load.

3) Crafted items do not stack and names are janky (In testing)
- Symptom: Crafted items in the crafting menu do not stack (e.g., 8x 4-star ice items show as 8 separate entries) and names are displayed poorly.
- Impact: Inventory is cluttered and hard to read; user cannot easily see total counts of each item.
- Suggested follow-up: Update UI and logic to stack items by type and rarity, and improve name formatting for clarity.


