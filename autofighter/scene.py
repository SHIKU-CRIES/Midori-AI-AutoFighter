from __future__ import annotations

from direct.showbase.ShowBase import ShowBase


class Scene:
    def setup(self) -> None:
        """Initialize scene objects."""
        pass

    def teardown(self) -> None:
        """Clean up scene objects."""
        pass


class SceneManager:
    def __init__(self, base: ShowBase) -> None:
        self.base = base
        self.current: Scene | None = None

    def switch_to(self, scene: Scene | None) -> None:
        if self.current:
            self.current.teardown()
        self.current = scene
        if self.current:
            self.current.setup()
