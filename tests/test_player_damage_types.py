from pathlib import Path

from autofighter.stats import Stats
from plugins.damage_types import ALL_DAMAGE_TYPES
from plugins.plugin_loader import PluginLoader


def test_players_define_damage_types() -> None:
    loader = PluginLoader()
    root = Path(__file__).resolve().parents[1] / "plugins"
    loader.discover(str(root))
    player_plugins = loader.get_plugins("player")
    for cls in player_plugins.values():
        player = cls()
        if player.id == "luna":
            assert player.base_damage_type == "Generic"
        else:
            assert player.base_damage_type in ALL_DAMAGE_TYPES
        assert player.damage_types == [player.base_damage_type]


def test_damage_types_register() -> None:
    loader = PluginLoader()
    root = Path(__file__).resolve().parents[1] / "plugins"
    loader.discover(str(root))
    damage_types = loader.get_plugins("damage_type")
    assert {
        "Generic",
        "Light",
        "Dark",
        "Wind",
        "Lightning",
        "Fire",
        "Ice",
    }.issubset(damage_types.keys())


def test_damage_type_event_hooks() -> None:
    loader = PluginLoader()
    root = Path(__file__).resolve().parents[1] / "plugins"
    loader.discover(str(root))
    damage_types = loader.get_plugins("damage_type")
    attacker = Stats(hp=1, max_hp=1)
    target = Stats(hp=1, max_hp=1)
    for cls in damage_types.values():
        plugin = cls()
        plugin.on_hit(attacker, target)
        assert plugin.on_damage(10, attacker, target) == 10
        assert plugin.on_damage_taken(10, attacker, target) == 10
        assert plugin.on_dot_damage_taken(5, attacker, target) == 5
        assert plugin.on_party_damage_taken(10, attacker, target) == 10
        assert plugin.on_party_dot_damage_taken(5, attacker, target) == 5
        assert plugin.on_heal(10, attacker, target) == 10
        assert plugin.on_heal_received(10, attacker, target) == 10
        assert plugin.on_hot_heal_received(5, attacker, target) == 5
        assert plugin.on_party_heal_received(10, attacker, target) == 10
        assert plugin.on_party_hot_heal_received(5, attacker, target) == 5
        assert plugin.on_death(attacker, target) is None
        assert plugin.on_party_member_death(attacker, target) is None
