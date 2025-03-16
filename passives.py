import typing

from typing import Any
from typing import Union

from typing import Callable
from typing import Optional
from typing import Protocol

class PassiveEffect(Protocol):
    """Protocol defining the interface for passive effects."""

    def activate(self, target, user) -> None:
        """Applies the passive effect.

        Args:
            target: The target Player object.
            user: The user Player object.
        """
        ...


PassiveType = Optional[Union[Callable[[Any, Any], None], PassiveEffect]]