"""Main menu rebuilt with Panda3D DirectGUI elements."""

from __future__ import annotations

import random
from pathlib import Path

from panda3d.core import NodePath
from panda3d.core import TextNode
from direct.gui.DirectFrame import DirectFrame
from panda3d.core import TransparencyAttrib
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton

from game.ui.run_map import RunMap
from autofighter.stats import Stats
from autofighter.save import DB_PATH
from autofighter.save import load_player
from autofighter.save import load_roster
from autofighter.saves import SaveManager
from autofighter.gui import get_widget_scale, set_widget_pos


class TopBar:
    """Top bar with player avatar, name, and pull count."""

    def __init__(self, parent, db_path, avatars_dir):
        self.frame = DirectFrame(
            parent=parent,
            frameSize=(0, 2, -0.25, 0.25),
            frameColor=(1, 1, 1, 0),
        )
        self.name_label = DirectLabel(
            parent=self.frame,
            text="Player",
            scale=get_widget_scale(),
        )
        self.pull_label = DirectLabel(
            parent=self.frame,
            text="0",
            scale=get_widget_scale(),
        )
        self.banner = DirectFrame(parent=self.frame)

        # Group all set_widget_pos calls together for clarity
        # Each set_widget_pos takes a tuple: (x, y, z) where x is horizontal position, y is depth (usually 0), z is vertical position
        set_widget_pos(self.frame, (-0.4, 0, 0.93)) ## Player / number
        set_widget_pos(self.name_label, (0.35, 0, 0))
        set_widget_pos(self.pull_label, (0.8, 0, 0))
        set_widget_pos(self.banner, (1.5, 0, 0))

    def _ensure_avatar(self, db_path: Path, avatars_dir: Path) -> Path | None:
        """Return an existing or randomly selected avatar, persisting it."""
        try:
            with SaveManager(db_path, "") as sm:
                data = sm.fetch_player("player") or {}
                avatar_str = data.get("avatar")
                if avatar_str:
                    avatar_path = Path(avatar_str)
                    if avatar_path.exists():
                        return avatar_path
                candidates = [
                    p
                    for p in avatars_dir.glob("*")
                    if p.suffix.lower() in {".png", ".jpg", ".jpeg"}
                ]
                if not candidates:
                    return None
                avatar_path = random.choice(candidates)
                data["avatar"] = str(avatar_path)
                sm.queue_player("player", data)
                sm.commit()
                return avatar_path
        except Exception:
            return None


class TopLeftPanel:
    """Panel with avatar, pulls, and crafting buttons."""
    def __init__(self, parent, edit_avatar_cmd, pull_characters_cmd, craft_items_cmd):
        self.frame = DirectFrame(
            parent=parent,
            relief="flat",
            frameSize=(0, 0.75, -0.3+0.1, 0.15),
            frameColor=(1, 1, 1, 0.3),
        )
        self.avatar_button = DirectButton(
            parent=self.frame,
            image="assets/textures/icon_diamond.png",
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, 0),
            relief="flat",
            image_color=(1, 1, 1, 1),
            text_pos=(0, -0.12),
            command=edit_avatar_cmd,
        )
        self.avatar_button.setTransparency(TransparencyAttrib.MAlpha)
        self.pulls_button = DirectButton(
            parent=self.frame,
            image="assets/textures/icon_refresh_cw.png",
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, 0),
            relief="flat",
            image_color=(1, 1, 1, 1),
            text_pos=(0, -0.12),
            command=pull_characters_cmd,
        )
        self.pulls_button.setTransparency(TransparencyAttrib.MAlpha)
        self.crafting_button = DirectButton(
            parent=self.frame,
            image="assets/textures/icon_settings.png",
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, 0),
            relief="flat",
            image_color=(1, 1, 1, 1),
            text_pos=(0, -0.12),
            command=craft_items_cmd,
        )
        self.crafting_button.setTransparency(TransparencyAttrib.MAlpha)

        # Group all set_widget_pos calls together for clarity
        # Do not put the set_widget_pos for buttons / icons here, 
        # there is a def lower down that does that
        set_widget_pos(self.frame, (-2.0 + (0.65), 0, 0.95))
        self.buttons = [self.avatar_button, self.pulls_button, self.crafting_button]


class MainMenu:
    """Main menu with a frosted icon stack and vertical command list."""

    def __init__(
        self,
        parent: NodePath,
        app: object,
        *,
        has_run: bool = False,
        db_path: Path | str = DB_PATH,
        avatars_dir: Path | str = Path("assets/textures/players"),
    ) -> None:
        if app is None or not hasattr(app, "scene_manager"):
            raise ValueError("MainMenu requires app with scene_manager")

        self.app = app
        bg_dir = Path("assets/textures/backgrounds")
        bg_choices = list(bg_dir.glob("background_*.png"))
        bg_path = random.choice(bg_choices) if bg_choices else None
        self.root = DirectFrame(
            parent=parent,
            frameSize=(-1, 1, -1, 1),
            image=str(bg_path) if bg_path else None,
            image_scale=1.7,
        )

        self.top_bar = TopBar(self.root, db_path, avatars_dir)

        run_icon = (
            "assets/textures/icon_folder_open.png"
            if has_run
            else "assets/textures/icon_play.png"
        )
        self.top_left_panel = TopLeftPanel(
            self.root,
            self.edit_avatar,
            self.pull_characters,
            self.craft_items,
        )
        self.left_buttons = self.top_left_panel.buttons
        buttons_bg_a: float = 0.3
        text_kwargs = {
            "text_pos": (0.15, -0.02),
            "text_align": TextNode.ALeft,
            "image_pos": (-0.1, 0, 0),
        }
        self.run_button = DirectButton(
            parent=self.root,
            image=run_icon,
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, buttons_bg_a),
            relief="flat",
            image_color=(1, 1, 1, 1),
            command=self.load_run if has_run else self.edit_party,
            **text_kwargs,
        )
        self.edit_player_button = DirectButton(
            parent=self.root,
            image="assets/textures/icon_user_cog.png",
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, buttons_bg_a),
            relief="flat",
            image_color=(1, 1, 1, 1),
            command=self.edit_player,
            **text_kwargs,
        )
        self.edit_team_button = DirectButton(
            parent=self.root,
            image="assets/textures/icon_users.png",
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, buttons_bg_a),
            relief="flat",
            image_color=(1, 1, 1, 1),
            command=self.edit_party,
            **text_kwargs,
        )
        self.settings_button = DirectButton(
            parent=self.root,
            image="assets/textures/icon_volume_2.png",
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, buttons_bg_a),
            relief="flat",
            image_color=(1, 1, 1, 1),
            command=self.options,
            **text_kwargs,
        )
        self.quit_button = DirectButton(
            parent=self.root,
            image="assets/textures/icon_power.png",
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, buttons_bg_a),
            relief="flat",
            image_color=(1, 1, 1, 1),
            command=self.quit,
            **text_kwargs,
        )
        self.right_buttons = [
            self.run_button,
            self.edit_player_button,
            self.edit_team_button,
            self.settings_button,
            self.quit_button,
        ]

        self._layout_buttons()

    def _layout_buttons(self) -> None:
        """Position left panel row and right-side command list."""
        start_x = 0.01 * 12
        spacing = 0.25
        z = -0.085
        for i, button in enumerate(self.left_buttons):
            set_widget_pos(button, (start_x + i * spacing, 0, z))
        right_x = 0.95 + (0.05 * 5)
        start_z = 0.4
        spacing = 0.2
        for i, button in enumerate(self.right_buttons):
            set_widget_pos(button, (right_x, 0, start_z - i * spacing))

        for button in self.left_buttons + self.right_buttons:
            for state in ("image0", "image1", "image2", "image3"):
                try:
                    node = button.component(state)
                except Exception:
                    node = None
                if node:
                    node.setTransparency(TransparencyAttrib.MAlpha)

    # Stub actions
    def start_run(self) -> None:
        """Launch a placeholder run map."""
        if self.app is None:  # pragma: no cover - safeguard
            return

        loaded = load_player()
        stats = loaded[4] if loaded else Stats(hp=1, max_hp=1)
        run_map = RunMap(self.app, stats, [], DB_PATH)
        self.app.scene_manager.switch_to(run_map)  # type: ignore

    def load_run(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for loading a saved run."""

    def edit_player(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for editing the player."""

    def edit_party(self) -> None:  # pragma: no cover - placeholders
        """Open the party picker scene."""
        if self.app is None:  # pragma: no cover - safeguard
            return
        from game.ui.party_picker import PartyPicker

        loaded = load_player()
        stats = loaded[4] if loaded else Stats(hp=1, max_hp=1)
        roster = load_roster()
        # Hide the main menu so its buttons do not overlap the picker
        try:
            self.hide()
        except Exception:
            pass
        picker = PartyPicker(self.app, stats, roster=roster)
        self.app.scene_manager.switch_to(picker)  # type: ignore[attr-defined]

    def pull_characters(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for character pulls."""

    def options(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for an options menu."""

    # Visibility helpers -------------------------------------------------
    def hide(self) -> None:
        """Hide the main menu root frame."""
        if self.root:
            try:
                self.root.hide()
            except Exception:
                pass

    def show(self) -> None:
        """Show the main menu root frame."""
        if self.root:
            try:
                self.root.show()
            except Exception:
                pass

    def craft_items(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for a crafting menu."""

    def edit_avatar(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for changing the player's avatar."""

    def quit(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for application quit logic."""
