from collections import defaultdict

# Registry: maps Command type -> list of (order, handler_class or factory)
HANDLER_REGISTRY = defaultdict(list)


def handler_for(command_type, order: int = 0):
    """
    Decorator to register a handler class for a given Command type.
    The dispatcher decides how to instantiate the handler
    (directly or via a DI container).
    """
    def decorator(cls):
        HANDLER_REGISTRY[command_type].append((order, cls))
        HANDLER_REGISTRY[command_type].sort(key=lambda x: x[0])  # keep sorted
        return cls
    return decorator
