# Main Menu

Rebuilt the main menu under `aspect2d` using Panda3D DirectGUI widgets. A
themed background fills the window and is slightly zoomed in for depth. The
top bar hosts a compact 28×28 avatar, player name, pull count, and a banner
placeholder. The avatar is randomly chosen on first launch and persisted to the
encrypted `save.db` database.

The main controls are split into two clusters. A frosted panel anchored at the
upper left rows **Avatar**, **Pulls**, and **Crafting** buttons over a light
backer with labels tucked beneath their icons. On the right side a vertical
command list offers **Start/Load Run**, **Edit Player**, **Edit Team**,
**Settings**, and **Quit** with labels positioned to the right of each icon.
Icons are scaled with `get_widget_scale()` and rendered with alpha
transparency. Selecting **Start Run** currently launches a placeholder `RunMap`
scene that displays basic routing text.

## Testing
- `uv run pytest tests/test_menu.py::test_main_menu_structure`
- `uv run pytest tests/test_menu.py::test_run_button_label_switch`
