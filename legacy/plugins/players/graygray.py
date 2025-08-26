"""Player plugin for Graygray."""

from passives import get_passive
from player import Player

from plugins.players.base import PlayerPlugin


class Graygray(PlayerPlugin):
    """Graygray player implementation."""

    plugin_type = "player"
    id = "graygray"
    name = "Graygray"

    def build(self, name: str | None = None, **kwargs) -> Player:
        """Construct and return the player instance."""
        player = Player(name or self.name)
        player.load()
        player.set_photo(self.id)
        player.isplayer = True
        passive = get_passive("graygray_passive")
        if passive:
            passive.on_apply(player)
        return player
