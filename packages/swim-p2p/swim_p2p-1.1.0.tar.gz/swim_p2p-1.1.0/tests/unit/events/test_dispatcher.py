"""
Tests for the event dispatcher.

This module tests the event dispatcher functionality including
subscription, emission, error handling, and thread safety.
"""

import pytest
import asyncio
import threading
import time
from unittest.mock import Mock, patch
from concurrent.futures import Future

from swim.events.dispatcher import EventDispatcher
from swim.events.types import (
    EventCategory, EventSeverity,
    PingTimeoutEvent, LatencyThresholdExceededEvent, ResourceExhaustionEvent
)


class TestEventDispatcherBasics:
    """Test basic dispatcher functionality."""
    
    def test_dispatcher_creation(self):
        """Test that dispatcher can be created with default settings."""
        dispatcher = EventDispatcher()
        
        assert dispatcher._max_history_size == 1000
        assert dispatcher._enable_history is True
        assert len(dispatcher._event_history) == 0
        
        stats = dispatcher.get_statistics()
        assert stats["events_emitted"] == 0
        assert stats["handlers_executed"] == 0
        assert stats["handler_errors"] == 0
    
    def test_dispatcher_custom_settings(self):
        """Test dispatcher creation with custom settings."""
        dispatcher = EventDispatcher(
            max_history_size=500,
            enable_history=False,
            max_workers=8
        )
        
        assert dispatcher._max_history_size == 500
        assert dispatcher._enable_history is False
    
    def test_dispatcher_shutdown(self):
        """Test dispatcher shutdown."""
        dispatcher = EventDispatcher()
        
        # Add some handlers
        handler = Mock()
        dispatcher.subscribe("PingTimeoutEvent", handler)
        
        # Shutdown
        dispatcher.shutdown()
        
        # Verify cleanup
        stats = dispatcher.get_statistics()
        assert stats["active_handlers"] == 0


class TestEventSubscription:
    """Test event subscription functionality."""
    
    def test_subscribe_by_event_name(self):
        """Test subscribing to events by name."""
        dispatcher = EventDispatcher()
        handler = Mock()
        
        dispatcher.subscribe("PingTimeoutEvent", handler)
        
        stats = dispatcher.get_statistics()
        assert stats["active_handlers"] == 1
    
    def test_subscribe_by_event_class(self):
        """Test subscribing to events by class."""
        dispatcher = EventDispatcher()
        handler = Mock()
        
        dispatcher.subscribe(PingTimeoutEvent, handler)
        
        stats = dispatcher.get_statistics()
        assert stats["active_handlers"] == 1
    
    def test_subscribe_by_category(self):
        """Test subscribing to events by category."""
        dispatcher = EventDispatcher()
        handler = Mock()
        
        dispatcher.subscribe(EventCategory.PERFORMANCE, handler)
        
        stats = dispatcher.get_statistics()
        assert stats["category_handlers"] == 1
    
    def test_subscribe_wildcard(self):
        """Test subscribing to all events."""
        dispatcher = EventDispatcher()
        handler = Mock()
        
        dispatcher.subscribe("*", handler)
        
        stats = dispatcher.get_statistics()
        assert stats["wildcard_handlers"] == 1
    
    def test_unsubscribe(self):
        """Test unsubscribing from events."""
        dispatcher = EventDispatcher()
        handler = Mock()
        
        # Subscribe and verify
        dispatcher.subscribe("PingTimeoutEvent", handler)
        stats = dispatcher.get_statistics()
        assert stats["active_handlers"] == 1
        
        # Unsubscribe and verify
        result = dispatcher.unsubscribe("PingTimeoutEvent", handler)
        assert result is True
        
        stats = dispatcher.get_statistics()
        assert stats["active_handlers"] == 0
    
    def test_unsubscribe_nonexistent(self):
        """Test unsubscribing a handler that wasn't subscribed."""
        dispatcher = EventDispatcher()
        handler = Mock()
        
        result = dispatcher.unsubscribe("PingTimeoutEvent", handler)
        assert result is False


class TestEventEmission:
    """Test event emission and handler execution."""
    
    def test_emit_to_specific_handler(self):
        """Test emitting events to specific handlers."""
        dispatcher = EventDispatcher()
        handler = Mock()
        
        dispatcher.subscribe("PingTimeoutEvent", handler)
        
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        
        dispatcher.emit(event)
        
        # Give time for handler execution
        time.sleep(0.1)
        
        handler.assert_called_once_with(event)
        
        stats = dispatcher.get_statistics()
        assert stats["events_emitted"] == 1
        assert stats["handlers_executed"] == 1
    
    def test_emit_to_category_handler(self):
        """Test emitting events to category handlers."""
        dispatcher = EventDispatcher()
        handler = Mock()
        
        dispatcher.subscribe(EventCategory.PERFORMANCE, handler)
        
        event = LatencyThresholdExceededEvent(
            peer_address="127.0.0.1:8000",
            current_latency_ms=250.0,
            threshold_ms=200.0,
            measurement_window="1m"
        )
        
        dispatcher.emit(event)
        
        # Give time for handler execution
        time.sleep(0.1)
        
        handler.assert_called_once_with(event)
    
    def test_emit_to_wildcard_handler(self):
        """Test emitting events to wildcard handlers."""
        dispatcher = EventDispatcher()
        handler = Mock()
        
        dispatcher.subscribe("*", handler)
        
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        
        dispatcher.emit(event)
        
        # Give time for handler execution
        time.sleep(0.1)
        
        handler.assert_called_once_with(event)
    
    def test_emit_to_multiple_handlers(self):
        """Test emitting events to multiple handlers."""
        dispatcher = EventDispatcher()
        handler1 = Mock()
        handler2 = Mock()
        handler3 = Mock()
        
        # Subscribe different ways
        dispatcher.subscribe("PingTimeoutEvent", handler1)
        dispatcher.subscribe(EventCategory.PROTOCOL, handler2)
        dispatcher.subscribe("*", handler3)
        
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        
        dispatcher.emit(event)
        
        # Give time for handler execution
        time.sleep(0.1)
        
        # All handlers should be called
        handler1.assert_called_once_with(event)
        handler2.assert_called_once_with(event)
        handler3.assert_called_once_with(event)
        
        stats = dispatcher.get_statistics()
        assert stats["events_emitted"] == 1
        assert stats["handlers_executed"] == 3
    
    def test_emit_invalid_event(self):
        """Test emitting invalid events."""
        dispatcher = EventDispatcher()
        
        # Try to emit a non-event object
        dispatcher.emit("not an event")
        
        stats = dispatcher.get_statistics()
        assert stats["events_emitted"] == 0
        assert stats["events_dropped"] == 1


class TestAsyncHandlers:
    """Test asynchronous event handlers."""
    
    @pytest.mark.asyncio
    async def test_async_handler_execution(self):
        """Test that async handlers are executed properly."""
        dispatcher = EventDispatcher()
        
        # Create an async handler
        async def async_handler(event):
            await asyncio.sleep(0.01)  # Simulate async work
            async_handler.called = True
            async_handler.event = event
        
        async_handler.called = False
        async_handler.event = None
        
        dispatcher.subscribe("PingTimeoutEvent", async_handler)
        
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        
        dispatcher.emit(event)
        
        # Give time for async execution
        await asyncio.sleep(0.1)
        
        assert async_handler.called is True
        assert async_handler.event == event
    
    def test_mixed_sync_async_handlers(self):
        """Test mixing sync and async handlers."""
        dispatcher = EventDispatcher()
        
        sync_handler = Mock()
        
        async def async_handler(event):
            await asyncio.sleep(0.01)
            async_handler.called = True
        
        async_handler.called = False
        
        dispatcher.subscribe("PingTimeoutEvent", sync_handler)
        dispatcher.subscribe("PingTimeoutEvent", async_handler)
        
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        
        dispatcher.emit(event)
        
        # Give time for execution
        time.sleep(0.1)
        
        # Both handlers should be called
        sync_handler.assert_called_once_with(event)
        assert async_handler.called is True


class TestErrorHandling:
    """Test error handling in event dispatching."""
    
    def test_handler_exception_handling(self):
        """Test that handler exceptions don't break the dispatcher."""
        dispatcher = EventDispatcher()
        
        def failing_handler(event):
            raise ValueError("Handler error")
        
        good_handler = Mock()
        
        dispatcher.subscribe("PingTimeoutEvent", failing_handler)
        dispatcher.subscribe("PingTimeoutEvent", good_handler)
        
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        
        # Should not raise exception
        dispatcher.emit(event)
        
        # Give time for execution
        time.sleep(0.1)
        
        # Good handler should still be called
        good_handler.assert_called_once_with(event)
        
        stats = dispatcher.get_statistics()
        assert stats["handler_errors"] == 1
        assert stats["handlers_executed"] == 1  # Only the good handler


class TestEventHistory:
    """Test event history functionality."""
    
    def test_event_history_enabled(self):
        """Test that event history is maintained when enabled."""
        dispatcher = EventDispatcher(enable_history=True, max_history_size=10)
        
        events = []
        for i in range(5):
            event = PingTimeoutEvent(
                target_address=f"127.0.0.1:800{i}",
                timeout_duration=1.5,
                attempt_number=1
            )
            events.append(event)
            dispatcher.emit(event)
        
        history = dispatcher.get_event_history()
        assert len(history) == 5
        
        # Events should be in chronological order
        for i, event in enumerate(history):
            assert event.target_address == f"127.0.0.1:800{i}"
    
    def test_event_history_disabled(self):
        """Test that event history is not maintained when disabled."""
        dispatcher = EventDispatcher(enable_history=False)
        
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        dispatcher.emit(event)
        
        history = dispatcher.get_event_history()
        assert len(history) == 0
    
    def test_event_history_size_limit(self):
        """Test that event history respects size limits."""
        dispatcher = EventDispatcher(enable_history=True, max_history_size=3)
        
        # Emit more events than the limit
        for i in range(5):
            event = PingTimeoutEvent(
                target_address=f"127.0.0.1:800{i}",
                timeout_duration=1.5,
                attempt_number=1
            )
            dispatcher.emit(event)
        
        history = dispatcher.get_event_history()
        assert len(history) == 3
        
        # Should contain the last 3 events
        for i, event in enumerate(history):
            assert event.target_address == f"127.0.0.1:800{i + 2}"
    
    def test_event_history_filtering(self):
        """Test event history filtering capabilities."""
        dispatcher = EventDispatcher(enable_history=True)
        
        # Emit different types of events
        ping_event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        ping_event.severity = EventSeverity.WARNING
        
        latency_event = LatencyThresholdExceededEvent(
            peer_address="127.0.0.1:8001",
            current_latency_ms=250.0,
            threshold_ms=200.0,
            measurement_window="1m"
        )
        latency_event.severity = EventSeverity.ERROR
        
        dispatcher.emit(ping_event)
        dispatcher.emit(latency_event)
        
        # Test category filtering
        performance_events = dispatcher.get_event_history(category=EventCategory.PERFORMANCE)
        assert len(performance_events) == 1
        assert isinstance(performance_events[0], LatencyThresholdExceededEvent)
        
        # Test severity filtering
        error_events = dispatcher.get_event_history(severity=EventSeverity.ERROR)
        assert len(error_events) == 1
        assert isinstance(error_events[0], LatencyThresholdExceededEvent)
        
        # Test limit
        limited_events = dispatcher.get_event_history(limit=1)
        assert len(limited_events) == 1
    
    def test_clear_history(self):
        """Test clearing event history."""
        dispatcher = EventDispatcher(enable_history=True)
        
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        dispatcher.emit(event)
        
        assert len(dispatcher.get_event_history()) == 1
        
        dispatcher.clear_history()
        assert len(dispatcher.get_event_history()) == 0


class TestThreadSafety:
    """Test thread safety of the dispatcher."""
    
    def test_concurrent_subscription(self):
        """Test that concurrent subscription is thread-safe."""
        dispatcher = EventDispatcher()
        handlers = []
        
        def subscribe_handler(handler_id):
            handler = Mock()
            handler.id = handler_id
            handlers.append(handler)
            dispatcher.subscribe("PingTimeoutEvent", handler)
        
        # Create multiple threads subscribing concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=subscribe_handler, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All handlers should be registered
        stats = dispatcher.get_statistics()
        assert stats["active_handlers"] == 10
    
    def test_concurrent_emission(self):
        """Test that concurrent event emission is thread-safe."""
        dispatcher = EventDispatcher()
        handler = Mock()
        dispatcher.subscribe("PingTimeoutEvent", handler)
        
        def emit_event(event_id):
            event = PingTimeoutEvent(
                target_address=f"127.0.0.1:800{event_id}",
                timeout_duration=1.5,
                attempt_number=1
            )
            dispatcher.emit(event)
        
        # Create multiple threads emitting concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=emit_event, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Give time for handler execution
        time.sleep(0.2)
        
        # Handler should be called for each event
        assert handler.call_count == 10
        
        stats = dispatcher.get_statistics()
        assert stats["events_emitted"] == 10


class TestWeakReferences:
    """Test weak reference handling for handlers."""
    
    def test_weak_reference_cleanup(self):
        """Test that weak references are cleaned up when handlers are deleted."""
        dispatcher = EventDispatcher()
        
        class TestHandler:
            def __init__(self, name):
                self.name = name
                self.called = False
            
            def __call__(self, event):
                self.called = True
        
        # Create handlers
        handler1 = TestHandler("handler1")
        handler2 = TestHandler("handler2")
        
        dispatcher.subscribe("PingTimeoutEvent", handler1)
        dispatcher.subscribe("PingTimeoutEvent", handler2)
        
        stats = dispatcher.get_statistics()
        assert stats["active_handlers"] == 2
        
        # Delete one handler
        del handler1
        
        # Emit an event to trigger cleanup
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        dispatcher.emit(event)
        
        # Give time for execution and cleanup
        time.sleep(0.1)
        
        # Only handler2 should be called
        assert handler2.called is True
        
        # Stats should reflect cleanup (this might require manual cleanup call)
        dispatcher._cleanup_dead_references()
        stats = dispatcher.get_statistics()
        assert stats["active_handlers"] == 1
