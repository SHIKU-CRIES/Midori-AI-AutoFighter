# Party Picker

Builds a party selection scene that mirrors the main menu's top bar but swaps the avatar icon for a slightly smaller home button. A background is randomly selected from PNG images under `frontend/src/lib/assets/backgrounds` to match the main menu.

The left side hosts a vertically scrollable roster of circular character icons, each parented to a transparent slot where a damage-type ring overlays the portrait so the ring fully masks any corners, including the player's avatar. The list fades at the top and bottom using CSS gradients so the list doesn't hard‑cut and omits its default frame color or horizontal scrollbar for a clean look. Player data is fetched from the Quart backend's `/players` endpoint, which enumerates every plugin character and marks owned entries. Only owned characters and the player's avatar populate the roster, and missing portraits are filled with a random PNG from `frontend/src/lib/assets/characters`. Each slot shows a Lucide element icon in its corner to denote the character's damage type. Selecting an icon overlays a green diamond image and adds the character to the party, capped at four members.

The player's avatar is always pinned to the top of the roster and clicks route through the same selection handler so their stats panel refreshes like any other character. Their stats populate the panel by default so a damage type can be chosen even on a fresh save where no other characters are owned.

Selecting any portrait swaps the body preview and stat readout to match that character. A placeholder 3D body model will sit in the center and can be rotated left or right with the arrow keys. Models will live in `assets/models` as `.glb` files. The picker roots itself to `aspect2d` so the interface is always visible. The right side displays a tabbed stats panel grouped automatically by the `Stats` dataclass field types. Each line includes a bullet icon that swaps to the matching element icon and colors the text whenever a damage type name appears. A row of Lucide damage type icons lets the player change their base element. When confirmed, the picker launches a `RunMap` scene using the encrypted `save.db` to track consumed seeds. A "Start Run" button in the lower-right corner triggers this transition.

Pressing the top‑left home button tears down the picker and re‑shows the hidden `MainMenu`, ensuring the menu's right‑side command list does not overlap the picker.

## Testing
- `bun test frontend/tests/partypicker.test.js`
