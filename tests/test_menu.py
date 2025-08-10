from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from shutil import copy

import pytest

pytest.importorskip("direct")
sys.modules["sqlcipher3"] = sqlite3
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import loadPrcFileData

from autofighter.saves import SaveManager
from game.ui.menu import MainMenu
import game.ui.party_picker as pp
from plugins.plugin_loader import PluginLoader


class AppStub:
    def __init__(self) -> None:
        self.scene_manager = type("SM", (), {"switch_to": lambda self, scene: setattr(self, "scene", scene)})()


def _setup_temp_assets(tmp_path: Path) -> tuple[Path, Path]:
    db_path = tmp_path / "save.db"
    avatars_dir = tmp_path / "avatars"
    avatars_dir.mkdir()
    copy("assets/textures/players/player1.png", avatars_dir / "a.png")
    copy("assets/textures/players/player2.png", avatars_dir / "b.png")
    return db_path, avatars_dir


def test_main_menu_structure(tmp_path: Path) -> None:
    loadPrcFileData("", "window-type none")
    base = ShowBase()
    try:
        db_path, avatars_dir = _setup_temp_assets(tmp_path)
        menu = MainMenu(
            base.aspect2d,
            AppStub(),
            db_path=db_path,
            avatars_dir=avatars_dir,
        )
        assert len(menu.left_buttons) == 3
        assert len(menu.right_buttons) == 5
        assert menu.run_button["text"] == "Start Run"
        assert menu.run_button["image"].endswith("icon_play.png")
        assert menu.root["image"].endswith("background_01.png")
        assert menu.top_bar.getParent() == menu.root
        assert menu.top_left_panel.getParent() == menu.root
        assert menu.top_left_panel.getPos()[0] < -1.0
        assert menu.root.getParent() == base.aspect2d
        for button in menu.left_buttons + menu.right_buttons:
            assert button["image"]
            assert button["text"]
            assert button["frameColor"][3] < 1
            assert button["image_color"] == (1, 1, 1, 1)
        for button in menu.left_buttons:
            assert button["text_pos"][1] < 0
        for button in menu.right_buttons:
            assert button["text_pos"][0] > 0
        xs = [btn.getPos()[0] for btn in menu.left_buttons]
        zs = [btn.getPos()[2] for btn in menu.left_buttons]
        assert xs[0] < xs[1] < xs[2]
        assert max(zs) - min(zs) < 0.01
        assert menu.root["image_scale"] > 1
        assert menu.avatar["frameSize"][1] <= 0.14
        right_xs = [btn.getPos()[0] for btn in menu.right_buttons]
        assert all(x > 0.9 for x in right_xs)
        assert isinstance(menu.name_label, DirectLabel)
        assert isinstance(menu.pull_label, DirectLabel)
        with SaveManager(db_path, "") as sm:
            data = sm.fetch_player("player") or {}
        assert Path(data["avatar"]).exists()
    finally:
        base.destroy()


def test_run_button_label_switch(tmp_path: Path) -> None:
    loadPrcFileData("", "window-type none")
    base = ShowBase()
    try:
        db_path, avatars_dir = _setup_temp_assets(tmp_path)
        menu = MainMenu(
            base.aspect2d,
            AppStub(),
            has_run=True,
            db_path=db_path,
            avatars_dir=avatars_dir,
        )
        assert menu.run_button["text"] == "Load Run"
        assert menu.run_button["image"].endswith("icon_folder_open.png")
    finally:
        base.destroy()


def test_main_menu_requires_app(tmp_path: Path) -> None:
    loadPrcFileData("", "window-type none")
    base = ShowBase()
    try:
        db_path, avatars_dir = _setup_temp_assets(tmp_path)
        with pytest.raises(ValueError):
            MainMenu(base.aspect2d, object(), db_path=db_path, avatars_dir=avatars_dir)
    finally:
        base.destroy()


def test_edit_party_hides_menu(tmp_path: Path) -> None:
    loadPrcFileData("", "window-type none")
    base = ShowBase()
    try:
        db_path, avatars_dir = _setup_temp_assets(tmp_path)
        app = AppStub()
        app.plugin_loader = PluginLoader()
        app.plugin_loader.discover("plugins/players")
        menu = MainMenu(
            base.aspect2d,
            app,
            db_path=db_path,
            avatars_dir=avatars_dir,
        )
        app.main_menu = menu
        menu.edit_party()
        assert menu.root.isHidden()
        assert isinstance(app.scene_manager.scene, pp.PartyPicker)
    finally:
        base.destroy()
