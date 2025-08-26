import importlib.util
import inspect
import logging
from pathlib import Path
from types import ModuleType


class PluginLoader:
    """Load plugins from a directory and expose them by category."""

    def __init__(self) -> None:
        self._registry: dict[str, dict[str, type]] = {}

    def discover(self, plugin_dir: str) -> None:
        """Discover plugin modules under ``plugin_dir``.

        Parameters
        ----------
        plugin_dir:
            Root directory containing plugin modules organised in subfolders
            by category.
        """

        base_path = Path(plugin_dir)
        if not base_path.exists():
            logging.info("Plugin directory '%s' does not exist", plugin_dir)
            return

        for file_path in base_path.rglob("*.py"):
            if file_path.name == "__init__.py":
                continue
            if file_path.parent == base_path and base_path.name == "plugins":
                continue
            if base_path.name != "templates" and "templates" in file_path.parts:
                continue

            spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
            if spec is None or spec.loader is None:
                logging.warning("Could not load spec for %s", file_path)
                continue

            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)  # type: ignore[arg-type]
            except Exception as exc:
                logging.exception("Failed loading plugin %s: %s", file_path, exc)
                continue

            self._register_module(module)

    def _register_module(self, module: ModuleType) -> None:
        for _, obj in inspect.getmembers(module, inspect.isclass):
            plugin_type = getattr(obj, "plugin_type", None)
            if plugin_type is None:
                continue
            plugin_id = getattr(obj, "id", obj.__name__)
            self._registry.setdefault(plugin_type, {})[plugin_id] = obj

    def get_plugins(self, plugin_type: str) -> dict[str, type]:
        """Return plugins registered under ``plugin_type``."""

        return self._registry.get(plugin_type, {}).copy()
