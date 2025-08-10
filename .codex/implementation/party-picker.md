# Party Picker

Builds a party selection scene with Panda3D DirectGUI that mirrors the main
menu's top bar but swaps the avatar icon for a slightly smaller home button.
The left side hosts a vertically scrollable roster of circular character icons
that fade at the top and bottom using dedicated gradient textures so the list
doesn't hard‑cut. Missing portraits are filled with a random
image from `assets/textures/players/fallbacks`. Selecting an icon overlays a
green diamond image and adds the character to the party, capped at four
members.

A placeholder 3D body model (`body_a`, `body_b`, or `body_c`) sits in the center
and can be rotated left or right with the arrow keys. Models live in
`assets/models` as `.egg` files that are converted to `.bam` when Panda3D tools
are present; otherwise the `.egg` files load directly. The picker roots itself to
`aspect2d` so the interface is always visible. The right side displays a
tabbed stats panel with textured bullet icons. When confirmed, the picker launches a `RunMap`
scene using the encrypted `save.db` to track consumed seeds.

Pressing the top‑left home button tears down the picker and re‑shows the
hidden `MainMenu`, ensuring the menu's right‑side command list does not overlap
the picker.

## Testing
- `uv run pytest tests/test_party_picker.py`
