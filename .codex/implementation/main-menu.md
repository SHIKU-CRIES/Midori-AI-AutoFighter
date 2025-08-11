# Main Menu

Rebuilt the main menu under `aspect2d` using Panda3D DirectGUI widgets. A
random background image from `assets/textures/backgrounds` fills the window and
is slightly zoomed in for depth. The
top bar hosts a compact 28×28 avatar, player name, pull count, and a banner
placeholder. The avatar is randomly chosen on first launch and persisted to the
encrypted `save.db` database.

The main controls are split into two clusters. A frosted panel anchored at the
upper left rows **Avatar** (diamond icon), **Pulls**, and **Crafting** buttons over
a light backer with labels tucked beneath their icons. On the right side a
vertical command list offers **Start/Load Run**, **Edit Player** (user‑cog icon),
**Edit Team** (users icon), **Settings**, and **Quit** with labels positioned to the
right of each icon. Icons are scaled with `get_widget_scale()` and rendered with
alpha transparency. Selecting **Start Run** or **Edit Team** opens the
`PartyPicker` scene so the player can choose allies before the run begins.

`MainMenu.hide()` and `MainMenu.show()` toggle the root frame so overlay scenes
like `PartyPicker` do not display on top of the menu. `edit_party()` hides the
menu before launching the picker, and returning home shows it again.

`MainMenu` now requires an application object exposing a `scene_manager` so
menu actions like `edit_party` can transition between scenes. The constructor
raises a `ValueError` if such an object is not supplied.

## Testing
- `uv run pytest tests/test_menu.py::test_main_menu_structure`
- `uv run pytest tests/test_menu.py::test_run_button_label_switch`
- `uv run pytest tests/test_menu.py::test_main_menu_requires_app`
