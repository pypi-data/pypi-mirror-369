import pytest
from mediator_lite.registry import HANDLER_REGISTRY, handler_for

class DummyCommand:
    pass

def test_handler_registration_order():
    # Clear registry for test isolation
    HANDLER_REGISTRY.clear()

    called = []

    @handler_for(DummyCommand, order=5)
    class HandlerA:
        def handle(self, command):
            called.append("A")
        def can_handle(self, command):
            return True

    @handler_for(DummyCommand, order=1)
    class HandlerB:
        def handle(self, command):
            called.append("B")
        def can_handle(self, command):
            return True

    # Registry should sort by order
    handlers = HANDLER_REGISTRY[DummyCommand]
    orders = [order for order, cls in handlers]
    assert orders == [1, 5]
    assert [cls.__name__ for order, cls in handlers] == ["HandlerB", "HandlerA"]
