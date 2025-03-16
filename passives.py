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


PassiveProto = Optional[Union[Callable[[Any, Any], None], PassiveEffect]]

class PassiveType:
    """
    A class to represent a passive type with source and target type checks.
    """

    def __init__(self, name: str, source_type, target_type):
        """
        Initializes the PassiveType object.

        Args:
            name: The name of the passive.
            source_type: The expected type of the source.
            target_type: The expected type of the target.
        """
        self.name = name
        self.source_type = source_type
        self.target_type = target_type

    def check_source_type(self, source):
        """
        Checks if the given source is of the expected type.

        Args:
            source: The source object to check.

        Returns:
            True if the source is of the expected type, False otherwise.
        """
        return isinstance(source, self.source_type)

    def check_target_type(self, target):
        """
        Checks if the given target is of the expected type.

        Args:
            target: The target object to check.

        Returns:
            True if the target is of the expected type, False otherwise.
        """
        return isinstance(target, self.target_type)

    def activate(self, target, user) -> None:
        """Applies the passive effect."""

        if not self.check_target_type(target):
            return
        
        if not self.check_source_type(user):
            return
        
        pass