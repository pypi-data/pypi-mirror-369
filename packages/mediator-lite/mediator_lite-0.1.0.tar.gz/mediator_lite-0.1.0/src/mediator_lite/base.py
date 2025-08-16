from abc import ABC, abstractmethod


class Command:
    """Base class for all commands (pure data carrier)."""
    pass


class CommandHandler(ABC):
    """Base class for all handlers."""

    @abstractmethod
    def handle(self, command: Command):
        """Execute the command logic."""
        pass

    def can_handle(self, command: Command) -> bool:
        """Optional secondary filter for handling commands."""
        return True
