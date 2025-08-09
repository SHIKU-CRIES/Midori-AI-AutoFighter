"""Main menu rebuilt with Panda3D DirectGUI elements."""

from __future__ import annotations

import random

from pathlib import Path

from panda3d.core import NodePath
from panda3d.core import TextNode
from panda3d.core import TransparencyAttrib
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton

from game.ui.run_map import RunMap
from autofighter.stats import Stats
from autofighter.save import DB_PATH
from autofighter.saves import SaveManager
from autofighter.gui import get_widget_scale, set_widget_pos


class MainMenu:
    """Main menu with a frosted icon stack and vertical command list."""

    def __init__(
        self,
        parent: NodePath,
        app: object | None = None,
        *,
        has_run: bool = False,
        db_path: Path | str = DB_PATH,
        avatars_dir: Path | str = Path("assets/textures/players"),
    ) -> None:
        self.app = app
        self.root = DirectFrame(
            parent=parent,
            frameSize=(-1, 1, -1, 1),
            image="assets/textures/backgrounds/background_01.png",
            image_scale=1.2,
        )

        self.top_bar = DirectFrame(
            parent=self.root,
            frameSize=(0, 2, -0.25, 0.25),
            frameColor=(1, 1, 1, 0),
        )
        set_widget_pos(self.top_bar, (-1, 0, 0.95))
        avatar_path = self._ensure_avatar(Path(db_path), Path(avatars_dir))
        self.avatar = DirectFrame(
            parent=self.top_bar,
            frameSize=(0, 0.14, 0, 0.14),
            image=str(avatar_path) if avatar_path else None,
        )
        set_widget_pos(self.avatar, (0.03, 0, -0.03))
        self.name_label = DirectLabel(
            parent=self.top_bar,
            text="Player",
            scale=get_widget_scale(),
        )
        set_widget_pos(self.name_label, (0.35, 0, -0.05))
        self.pull_label = DirectLabel(
            parent=self.top_bar,
            text="0",
            scale=get_widget_scale(),
        )
        set_widget_pos(self.pull_label, (0.8, 0, -0.05))
        self.banner = DirectFrame(parent=self.top_bar)
        set_widget_pos(self.banner, (1.5, 0, -0.05))

        run_icon = (
            "assets/textures/icon_folder_open.png"
            if has_run
            else "assets/textures/icon_play.png"
        )
        self.top_left_panel = DirectFrame(
            parent=self.root,
            frameSize=(0, 0.9, -0.3, 0.15),
            frameColor=(1, 1, 1, 0.3),
        )
        set_widget_pos(self.top_left_panel, (-1.2, 0, 0.95))
        self.avatar_button = DirectButton(
            parent=self.top_left_panel,
            text="Avatar",
            image="assets/textures/icon_user.png",
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, 0.2),
            relief="flat",
            image_color=(1, 1, 1, 1),
            text_pos=(0, -0.12),
            command=self.edit_avatar,
        )
        self.pulls_button = DirectButton(
            parent=self.top_left_panel,
            text="Pulls",
            image="assets/textures/icon_refresh_cw.png",
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, 0.2),
            relief="flat",
            image_color=(1, 1, 1, 1),
            text_pos=(0, -0.12),
            command=self.pull_characters,
        )
        self.crafting_button = DirectButton(
            parent=self.top_left_panel,
            text="Crafting",
            image="assets/textures/icon_settings.png",
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, 0.2),
            relief="flat",
            image_color=(1, 1, 1, 1),
            text_pos=(0, -0.12),
            command=self.craft_items,
        )
        self.left_buttons = [
            self.avatar_button,
            self.pulls_button,
            self.crafting_button,
        ]
        text_kwargs = {
            "text_pos": (0.15, -0.02),
            "text_align": TextNode.ALeft,
            "image_pos": (-0.1, 0, 0),
        }
        self.run_button = DirectButton(
            parent=self.root,
            text="Load Run" if has_run else "Start Run",
            image=run_icon,
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, 0.2),
            relief="flat",
            image_color=(1, 1, 1, 1),
            command=self.load_run if has_run else self.start_run,
            **text_kwargs,
        )
        self.edit_player_button = DirectButton(
            parent=self.root,
            text="Edit Player",
            image="assets/textures/icon_user.png",
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, 0.2),
            relief="flat",
            image_color=(1, 1, 1, 1),
            command=self.edit_player,
            **text_kwargs,
        )
        self.edit_team_button = DirectButton(
            parent=self.root,
            text="Edit Team",
            image="assets/textures/icon_user.png",
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, 0.2),
            relief="flat",
            image_color=(1, 1, 1, 1),
            command=self.edit_party,
            **text_kwargs,
        )
        self.settings_button = DirectButton(
            parent=self.root,
            text="Settings",
            image="assets/textures/icon_volume_2.png",
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, 0.2),
            relief="flat",
            image_color=(1, 1, 1, 1),
            command=self.options,
            **text_kwargs,
        )
        self.quit_button = DirectButton(
            parent=self.root,
            text="Quit",
            image="assets/textures/icon_power.png",
            scale=get_widget_scale(),
            frameColor=(1, 1, 1, 0.2),
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
        start_x = 0.05
        spacing = 0.22
        z = 0.05
        for i, button in enumerate(self.left_buttons):
            set_widget_pos(button, (start_x + i * spacing, 0, z))
        right_x = 0.95
        start_z = 0.4
        spacing = 0.18
        for i, button in enumerate(self.right_buttons):
            set_widget_pos(button, (right_x, 0, start_z - i * spacing))

        for button in self.left_buttons + self.right_buttons + [self.avatar]:
            for state in ("image0", "image1", "image2", "image3"):
                try:
                    node = button.component(state)
                except Exception:
                    node = None
                if node:
                    node.setTransparency(TransparencyAttrib.MAlpha)

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

    # Stub actions
    def start_run(self) -> None:
        """Launch a placeholder run map."""
        if self.app is None:  # pragma: no cover - safeguard
            return

        run_map = RunMap(self.app, Stats(hp=1, max_hp=1), [], Path("used_seeds.json"))
        self.app.scene_manager.switch_to(run_map)

    def load_run(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for loading a saved run."""

    def edit_player(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for editing the player."""

    def edit_party(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for editing the party."""

    def pull_characters(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for character pulls."""

    def options(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for an options menu."""

    def craft_items(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for a crafting menu."""

    def edit_avatar(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for changing the player's avatar."""

    def quit(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for application quit logic."""
