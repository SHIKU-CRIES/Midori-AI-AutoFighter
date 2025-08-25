# Logging

Battle modules and plugin packages should log through the shared backend logger.

```python
import logging

log = logging.getLogger(__name__)
```

Use `log.debug`, `log.info`, and so on instead of `print`. Records propagate through the queued buffer and are written to `backend/logs/backend.log` roughly every 15 seconds.

## Battle Modules

```python
from logging import getLogger

log = getLogger(__name__)

def attack(player, foe):
    log.info("%s attacks %s", player.name, foe.name)
    ...
```

## Plugins

```python
import logging

log = logging.getLogger(__name__)

class BurnRelic:
    plugin_type = "relic"
    id = "burn"

    def apply(self, target):
        log.debug("Applying burn to %s", target)
```
