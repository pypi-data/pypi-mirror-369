from .registry import HANDLER_REGISTRY
from .base import Command


class CommandDispatcher:
    """Dispatches commands to their registered handlers."""

    def __init__(self, handler_factory=None):
        """
        handler_factory: optional callable that receives a handler class
        and returns an instance. Default is naive instantiation.
        """
        self.handler_factory = handler_factory or (lambda cls: cls())

    def dispatch(self, command: Command):
        handlers = HANDLER_REGISTRY.get(type(command), [])
        if not handlers:
            raise ValueError(f"No handlers registered for {type(command).__name__}")

        results = []
        for order, handler_cls in handlers:
            handler = self.handler_factory(handler_cls)
            if handler.can_handle(command):
                results.append(handler.handle(command))
        return results
