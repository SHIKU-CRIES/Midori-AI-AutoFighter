import logging

from logging_config import configure_logging
from plugins.damage_effects import create_dot


def test_plugin_logging_capture():
    listener = configure_logging()
    try:
        logging.getLogger().setLevel(logging.DEBUG)
        create_dot("Fire", 10, object())
        buffer = listener.handlers[0].buffer
        assert any("Creating DoT" in record.getMessage() for record in buffer)
    finally:
        listener.stop()
