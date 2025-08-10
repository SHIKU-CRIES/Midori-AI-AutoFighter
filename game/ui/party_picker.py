"""Party picker screen for selecting allies before a run.

This implementation mirrors the layout guidance from the main menu and
introduces a scrollable roster, placeholder 3D preview, and tabbed stats
panel. Each icon sits in a circular slot whose outline color represents the
character's element. Selecting an icon toggles a check mark in its lower-right
corner and adds the character to the party list (up to four members).

The center of the screen displays a simple 3D model that the player can rotate
left or right. The right side hosts a tabbed panel with stat icons so the user
can review details for the highlighted character.
"""

from __future__ import annotations

import random
import subprocess

from pathlib import Path

try:  # pragma: no cover - fallbacks for headless tests
    from direct.gui.DirectButton import DirectButton
    from direct.gui.DirectFrame import DirectFrame
    from direct.gui.DirectLabel import DirectLabel
    from direct.gui.DirectScrolledFrame import DirectScrolledFrame
    from panda3d.core import NodePath, TextNode, TransparencyAttrib
except Exception:  # pragma: no cover
    DirectButton = DirectFrame = DirectLabel = DirectScrolledFrame = object  # type: ignore
    NodePath = TextNode = TransparencyAttrib = object  # type: ignore

from autofighter.gui import set_widget_pos
from autofighter.gui import get_widget_scale
from autofighter.save import DB_PATH
from autofighter.scene import Scene
from autofighter.stats import Stats

from game.ui.menu import TopBar, TopLeftPanel
from game.ui.run_map import RunMap


def rebuild_models(model_dir: Path) -> None:
    """Rebuild ``.egg`` models into ``.bam`` every boot.

    Panda3D converts EGG files to BAM for fast loading.  During development we
    regenerate these each time the picker is opened so artists can tweak the
    source meshes without manual steps.  Missing tools or models are ignored so
    tests can run without Panda3D utilities installed.
    """

    for egg in model_dir.glob("*.egg"):
        bam = egg.with_suffix(".bam")
        try:
            if bam.exists():
                bam.unlink()
            subprocess.run(
                ["egg2bam", "-o", str(bam), str(egg)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:  # pragma: no cover - tool may be missing
            continue


class PickerTopLeftPanel(TopLeftPanel):
    """Top-left panel with home, pulls, and crafting buttons."""

    def __init__(self, parent, home_cmd, pull_characters_cmd, craft_items_cmd):
        super().__init__(parent, home_cmd, pull_characters_cmd, craft_items_cmd)
        # Swap the avatar icon for a home button that returns to the menu.
        scale = get_widget_scale() * 0.95
        if hasattr(self.avatar_button, "setScale"):
            self.avatar_button["image"] = "assets/textures/icon_home.png"
            self.avatar_button["command"] = home_cmd
            self.avatar_button.setScale(scale)
        else:  # fallback for dict-like stubs
            self.avatar_button["image"] = "assets/textures/icon_home.png"
            self.avatar_button["command"] = home_cmd
            self.avatar_button["scale"] = scale


class PartyPicker(Scene):
    """Scene for selecting allies before starting a run."""

    def __init__(self, app: object, player: Stats, *, roster: list[str] | None = None) -> None:
        self.app = app
        self.player = player
        self.char_ids = list(roster or [])
        self.selected: list[str] = []
        self.root: DirectFrame | None = None
        self.top_left_panel: PickerTopLeftPanel | None = None
        self.top_bar: TopBar | None = None
        self.scroll: DirectScrolledFrame | None = None
        self.buttons: dict[str, DirectButton] = {}
        self.checkmarks: dict[str, DirectLabel] = {}
        self.model = None
        self.rotation = 0.0

    # ------------------------------------------------------------------
    # UI setup
    def setup(self) -> None:
        parent = getattr(self.app, "aspect2d", NodePath("party-picker-root"))
        self.root = DirectFrame(parent=parent)
        self.top_bar = TopBar(self.root, DB_PATH, Path("assets/textures/players"))
        self.top_left_panel = PickerTopLeftPanel(
            self.root,
            self.home,
            self.pull_characters,
            self.craft_items,
        )
        self._layout_buttons()

        # Build roster list inside a vertical scroll frame on the left
        self.scroll = DirectScrolledFrame(
            parent=self.root,
            frameSize=(-0.25, 0.25, -0.7, 0.7),
            canvasSize=(-0.25, 0.25, -0.7 - 0.25 * len(self.char_ids), 0.7),
            pos=(-1.05, 0, 0),
            scrollBarWidth=0.05,
        )

        icons_dir = Path("assets/textures/players")
        fallback_icons = list((icons_dir / "fallbacks").glob("*.png"))
        for idx, cid in enumerate(self.char_ids):
            icon = icons_dir / f"{cid}.png"
            if not icon.exists() and fallback_icons:
                icon = random.choice(fallback_icons)
            btn = DirectButton(
                parent=self.scroll.getCanvas(),
                image=str(icon),
                relief="flat",
                command=self.toggle,
                extraArgs=[cid],
            )
            btn.setScale(0.1)
            set_widget_pos(btn, (0, 0, 0.55 - idx * 0.25))
            for state in ("image0", "image1", "image2", "image3"):
                try:
                    node = btn.component(state)
                except Exception:
                    node = None
                if node:
                    node.setTransparency(TransparencyAttrib.MAlpha)
            mark = DirectLabel(
                parent=btn,
                image="assets/textures/icon_diamond.png",
                image_color=(0, 1, 0, 1),
                relief="flat",
                pos=(0.07, 0, -0.07),
                scale=0.05,
            )
            mark.hide()
            self.buttons[cid] = btn
            self.checkmarks[cid] = mark

        # Fade textures at top and bottom to soften the roster edges
        top_fade = DirectFrame(
            parent=self.root,
            image="assets/textures/roster_fade_top.png",
            frameColor=(1, 1, 1, 0),
            pos=(-1.05, 0, 0.7),
            scale=(0.25, 1, 0.05),
        )
        top_fade.setTransparency(TransparencyAttrib.MAlpha)
        bottom_fade = DirectFrame(
            parent=self.root,
            image="assets/textures/roster_fade_bottom.png",
            frameColor=(1, 1, 1, 0),
            pos=(-1.05, 0, -0.7),
            scale=(0.25, 1, 0.05),
        )
        bottom_fade.setTransparency(TransparencyAttrib.MAlpha)

        # Placeholder model preview; attaches to render if available
        model_dir = Path("assets/models")
        rebuild_models(model_dir)
        loader = getattr(self.app, "loader", None)
        render = getattr(self.app, "render", None)
        if loader and render:
            try:
                # Preferred fast-loading BAM model
                self.model = loader.loadModel(str(model_dir / "body_a.bam"))
            except Exception:  # pragma: no cover - may not exist during dev
                try:
                    # Fallback to the source EGG if BAM is unavailable
                    self.model = loader.loadModel(str(model_dir / "body_a.egg"))
                except Exception:  # pragma: no cover - last resort primitive
                    try:
                        # Final fallback: Panda3D's built-in cube
                        self.model = loader.loadModel("models/box")
                    except Exception:
                        self.model = None
            if self.model:
                self.model.reparentTo(render)
                self.model.setPos(0, 5, 0)

        # Rotate model with arrow keys
        if hasattr(self.app, "accept"):
            self.app.accept("arrow_left", self.rotate_model, [-10])
            self.app.accept("arrow_right", self.rotate_model, [10])

        # Tabbed stats panel on the right
        self._build_stat_panel()

    # ------------------------------------------------------------------
    def _layout_buttons(self) -> None:
        if not self.top_left_panel:
            return
        start_x = 0.01 * 12
        spacing = 0.25
        z = -0.085
        for i, button in enumerate(self.top_left_panel.buttons):
            set_widget_pos(button, (start_x + i * spacing, 0, z))

    # ------------------------------------------------------------------
    def _build_stat_panel(self) -> None:
        """Create a simple tabbed stats viewer."""

        panel = DirectFrame(
            parent=self.root,
            frameSize=(0, 0.6, -0.6, 0.6),
            frameColor=(0, 0, 0, 0.2),
            pos=(0.7, 0, 0),
        )
        self.stat_tabs: dict[str, DirectFrame] = {}

        tabs = {
            "Vitals": ["hp", "max_hp"],
            "Combat": ["atk", "defense"],
        }
        for idx, (name, stats) in enumerate(tabs.items()):
            btn = DirectButton(
                parent=panel,
                text=name,
                pos=(0.3, 0, 0.5 - idx * 0.1),
                command=self.show_tab,
                extraArgs=[name],
            )
            btn.setScale(0.05)
            tab_frame = DirectFrame(parent=panel, frameColor=(0, 0, 0, 0))
            for s_idx, stat in enumerate(stats):
                DirectLabel(
                    parent=tab_frame,
                    image="assets/textures/icon_diamond.png",
                    relief="flat",
                    pos=(0, 0, 0.3 - s_idx * 0.1),
                    scale=0.05,
                )
                value = getattr(self.player, stat, 0)
                DirectLabel(
                    parent=tab_frame,
                    text=f"{stat}: {value}",
                    text_align=TextNode.ALeft,
                    pos=(0.1, 0, 0.3 - s_idx * 0.1),
                    scale=0.05,
                )
            tab_frame.hide()
            self.stat_tabs[name] = tab_frame

        self.stat_panel = panel
        self.show_tab("Vitals")

    # ------------------------------------------------------------------
    def show_tab(self, name: str) -> None:
        for frame in self.stat_tabs.values():
            frame.hide()
        if name in self.stat_tabs:
            self.stat_tabs[name].show()

    # ------------------------------------------------------------------
    def rotate_model(self, delta: float) -> None:
        if self.model:
            self.rotation += delta
            try:
                self.model.setH(self.rotation)
            except Exception:  # pragma: no cover - model may be stub
                pass

    # ------------------------------------------------------------------
    # Selection logic
    def toggle(self, char_id: str) -> None:
        mark = self.checkmarks.get(char_id)
        if char_id in self.selected:
            self.selected.remove(char_id)
            if mark:
                mark.hide()
        elif len(self.selected) < 4:
            self.selected.append(char_id)
            if mark:
                mark.show()

    def start_run(self) -> None:
        if self.app is None:  # pragma: no cover - safeguard
            return
        run_map = RunMap(self.app, self.player, self.selected, DB_PATH)
        self.app.scene_manager.switch_to(run_map)  # type: ignore[attr-defined]

    def home(self) -> None:
        if self.app is None:  # pragma: no cover
            return
        # Tear down the picker scene and reveal the main menu again
        try:
            self.app.scene_manager.switch_to(None)  # type: ignore[attr-defined]
        except Exception:
            pass
        main_menu = getattr(self.app, "main_menu", None)
        if main_menu:
            try:
                main_menu.show()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Stub commands
    def pull_characters(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for character pulls."""

    def craft_items(self) -> None:  # pragma: no cover - placeholders
        """Placeholder for crafting."""

    # ------------------------------------------------------------------
    def teardown(self) -> None:
        for btn in self.buttons.values():
            try:
                btn.destroy()
            except Exception:
                pass
        for mark in self.checkmarks.values():
            try:
                mark.destroy()
            except Exception:
                pass
        self.buttons.clear()
        self.checkmarks.clear()
        if self.scroll:
            try:
                self.scroll.destroy()
            except Exception:
                pass
            self.scroll = None
        if self.top_left_panel:
            for btn in self.top_left_panel.buttons:
                try:
                    btn.destroy()
                except Exception:
                    pass
            self.top_left_panel = None
        if self.top_bar:
            try:
                self.top_bar.frame.destroy()
            except Exception:
                pass
            self.top_bar = None
        if hasattr(self.app, "ignore"):
            self.app.ignore("arrow_left")
            self.app.ignore("arrow_right")
        if self.model:
            try:
                self.model.removeNode()
            except Exception:
                pass
            self.model = None
        if self.root:
            try:
                self.root.destroy()
            except Exception:
                pass
            self.root = None

