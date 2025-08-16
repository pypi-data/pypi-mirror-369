import pytest
from mediator_lite.dispatcher import CommandDispatcher
from mediator_lite.registry import HANDLER_REGISTRY, handler_for

# Example command class
class TestCommand:
    pass

def test_dispatcher_calls_handlers_in_order():
    HANDLER_REGISTRY.clear()
    called = []

    @handler_for(TestCommand, order=2)
    class HandlerA:
        def handle(self, command):
            called.append("A")
        def can_handle(self, command):
            return True

    @handler_for(TestCommand, order=1)
    class HandlerB:
        def handle(self, command):
            called.append("B")
        def can_handle(self, command):
            return True

    dispatcher = CommandDispatcher()
    dispatcher.dispatch(TestCommand())

    # Handlers should be called in order (1 → 2)
    assert called == ["B", "A"]

def test_dispatcher_with_no_handlers():
    HANDLER_REGISTRY.clear()
    class UnknownCommand:
        pass

    dispatcher = CommandDispatcher()
    with pytest.raises(ValueError) as exc:
        dispatcher.dispatch(UnknownCommand())
    assert "No handlers registered" in str(exc.value)

def test_dispatcher_skips_handler_if_cannot_handle():
    HANDLER_REGISTRY.clear()
    called = []

    @handler_for(TestCommand)
    class Handler:
        def handle(self, command):
            called.append("handled")
        def can_handle(self, command):
            return False  # cannot handle this command

    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch(TestCommand())
    # Should skip the handler
    assert result == []
    assert called == []
