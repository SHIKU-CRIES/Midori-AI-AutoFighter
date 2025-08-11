"""Minimal run map scene.

Displays a placeholder map and enters a battle room when the first
room is selected.
"""

from __future__ import annotations

from pathlib import Path

try:  # pragma: no cover - fallbacks for headless tests
    from direct.gui.DirectButton import DirectButton
    from panda3d.core import TransparencyAttrib
except Exception:  # pragma: no cover
    class DirectButton:  # type: ignore[misc]
        def __init__(self, *args, **kwargs):
            self.image = kwargs.get("image")

        def setTransparency(self, *args, **kwargs):
            pass

        def setPos(self, *args, **kwargs):
            pass

        def setScale(self, *args, **kwargs):
            pass

        def destroy(self):
            pass

    class TransparencyAttrib:  # type: ignore[misc]
        MAlpha = 0

from autofighter.save import DB_PATH
from autofighter.scene import Scene
from autofighter.stats import Stats


ROOM_ICONS = {
    "battle": "assets/textures/icon_flame.png",
    "shop": "assets/textures/icon_folder_open.png",
    "rest": "assets/textures/icon_pause.png",
    "event": "assets/textures/icon_message_square.png",
    "boss": "assets/textures/icon_power.png",
}


class RunMap(Scene):
    """Simple scene showing placeholder map text."""

    def __init__(
        self,
        app: object,
        player: Stats,
        party: list[str],
        seed_store_path: Path | str | None = None,
    ) -> None:
        self.app = app
        self.player = player
        self.party = party
        self.seed_store_path = Path(seed_store_path) if seed_store_path else DB_PATH
        self.buttons: list[DirectButton] = []

    def setup(self) -> None:
        parent = getattr(self.app, "aspect2d", None)
        rooms = ["battle", "shop", "rest", "event", "boss"]
        for idx, name in enumerate(rooms):
            icon = ROOM_ICONS.get(name)
            btn = DirectButton(
                parent=parent,
                image=icon,
                relief="flat",
                command=self.enter_first_room if idx == 0 else None,
            )
            btn.setTransparency(TransparencyAttrib.MAlpha)
            btn.setPos(0, 0, -0.8 + idx * 0.4)
            btn.setScale(0.1)
            self.buttons.append(btn)

    def enter_first_room(self) -> None:
        from autofighter.battle_room import BattleRoom

        foe_cls = self.app.plugin_loader.get_plugins("player")["luna"]
        foe = foe_cls()
        battle = BattleRoom(
            self.app,
            return_scene_factory=lambda: RunMap(
                self.app, self.player, self.party, self.seed_store_path
            ),
            player=self.player,
            party=self.party,
        )
        battle.base_foe = foe
        battle.foe = foe
        battle.foes = [foe]
        self.app.scene_manager.switch_to(battle)

    def teardown(self) -> None:
        for btn in self.buttons:
            btn.destroy()
        self.buttons.clear()
