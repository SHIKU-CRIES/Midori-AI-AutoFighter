import sys
import types

from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if "direct" not in sys.modules:
    class DummyLabel(dict):
        def destroy(self) -> None:
            pass

    class DummyButton(dict):
        def __init__(self, *args, **kwargs):
            self.image = kwargs.get("image")

        def setTransparency(self, *args, **kwargs) -> None:
            pass

        def setPos(self, *args, **kwargs) -> None:
            pass

        def setScale(self, *args, **kwargs) -> None:
            pass

        def destroy(self) -> None:
            pass

    direct_mod = types.ModuleType("direct")
    gui_mod = types.ModuleType("direct.gui")
    directgui_mod = types.ModuleType("direct.gui.DirectGui")
    directbutton_mod = types.ModuleType("direct.gui.DirectButton")
    directgui_mod.DirectLabel = (
        lambda *args, **kwargs: DummyLabel(text=kwargs.get("text", ""))
    )
    directbutton_mod.DirectButton = DummyButton
    sys.modules["direct"] = direct_mod
    sys.modules["direct.gui"] = gui_mod
    sys.modules["direct.gui.DirectGui"] = directgui_mod
    sys.modules["direct.gui.DirectButton"] = directbutton_mod

run_map_module = pytest.importorskip("game.ui.run_map")

from autofighter.stats import Stats
from plugins.players.luna import Luna

RunMap = run_map_module.RunMap


class DummyApp:
    def __init__(self) -> None:
        self.scene_manager = type("SM", (), {"switch_to": lambda self, scene: setattr(self, "scene", scene)})()
        self.events: dict[str, object] = {}

    def accept(self, name: str, func) -> None:
        self.events[name] = func

    def ignore(self, name: str) -> None:
        self.events.pop(name, None)


def test_run_map_enters_battle(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class DummyLoader:
        def get_plugins(self, category: str) -> dict[str, type]:
            return {"luna": Luna}

    app = DummyApp()
    app.plugin_loader = DummyLoader()
    stats = Stats(hp=5, max_hp=5)

    class DummyBattle:
        def __init__(
            self,
            app,
            return_scene_factory,
            *,
            player: Stats,
            party: list[str],
        ) -> None:
            self.app = app
            self.return_scene_factory = return_scene_factory
            self.player = player
            self.party = party

    monkeypatch.setitem(
        sys.modules,
        "autofighter.battle_room",
        types.SimpleNamespace(BattleRoom=DummyBattle),
    )
    run_map = RunMap(app, stats, ["ally"], seed_store_path=tmp_path / "seeds.json")
    run_map.setup()
    assert run_map.buttons
    assert hasattr(run_map.buttons[0], "image")

    run_map.enter_first_room()
    assert isinstance(app.scene_manager.scene, DummyBattle)
    battle = app.scene_manager.scene
    assert battle.app is app
    assert battle.player is stats
    assert battle.party == ["ally"]
    assert isinstance(battle.foe, Luna)
    assert battle.foe.hp == 1000
    returned = battle.return_scene_factory()
    assert isinstance(returned, RunMap)
    run_map.teardown()
