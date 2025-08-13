"""
Event dispatcher for the SWIM P2P protocol.

This module provides a lightweight, thread-safe event dispatcher that allows
components to subscribe to events without tight coupling. The dispatcher
supports both synchronous and asynchronous handlers.

Key design principles:
- Non-blocking event emission
- Thread-safe operation
- Minimal performance overhead
- Graceful error handling in handlers
- Optional event history for debugging
"""

import asyncio
import logging
import threading
import weakref
from collections import defaultdict, deque
from typing import Any, Callable, Dict, List, Optional, Set, Union, Awaitable, TYPE_CHECKING
from concurrent.futures import ThreadPoolExecutor

# Import only the base types to avoid circular dependency
from swim.events.types import Event, EventCategory, EventSeverity

logger = logging.getLogger(__name__)

# Type definitions
EventHandler = Callable[[Event], None]
AsyncEventHandler = Callable[[Event], Awaitable[Any]]  # Updated to use Awaitable instead of asyncio.coroutine
AnyEventHandler = Union[EventHandler, AsyncEventHandler]


class EventDispatcher:
    """
    Thread-safe event dispatcher for the SWIM protocol.
    
    The dispatcher allows components to register for specific event types
    or categories and receive notifications when events occur. It supports
    both synchronous and asynchronous handlers.
    
    Features:
    - Type-safe event subscription
    - Category-based subscriptions (e.g., all performance events)
    - Asynchronous handler support
    - Event history for debugging
    - Graceful error handling
    - Weak references to prevent memory leaks
    """
    
    def __init__(self, 
                 max_history_size: int = 1000,
                 enable_history: bool = True,
                 max_workers: int = 4):
        """
        Initialize the event dispatcher.
        
        Args:
            max_history_size: Maximum number of events to keep in history
            enable_history: Whether to maintain event history
            max_workers: Maximum number of threads for async handler execution
        """
        self._handlers: Dict[str, List[weakref.ref]] = defaultdict(list)
        self._category_handlers: Dict[EventCategory, List[weakref.ref]] = defaultdict(list)
        self._wildcard_handlers: List[weakref.ref] = []
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Event history
        self._enable_history = enable_history
        self._max_history_size = max_history_size
        self._event_history: deque = deque(maxlen=max_history_size)
        
        # Async support
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Statistics
        self._stats = {
            "events_emitted": 0,
            "handlers_executed": 0,
            "handler_errors": 0,
            "events_dropped": 0
        }
    
    def subscribe(self, 
                  event_type: Union[str, type, EventCategory], 
                  handler: AnyEventHandler,
                  weak: bool = True) -> None:
        """
        Subscribe to events of a specific type or category.
        
        Args:
            event_type: Event type (class name), event class, or EventCategory
            handler: Function to call when event occurs
            weak: Whether to use weak references (prevents memory leaks)
        
        Examples:
            # Subscribe to specific event type
            dispatcher.subscribe("PingTimeoutEvent", my_handler)
            dispatcher.subscribe(PingTimeoutEvent, my_handler)
            
            # Subscribe to all events in a category
            dispatcher.subscribe(EventCategory.PERFORMANCE, my_handler)
            
            # Subscribe to all events
            dispatcher.subscribe("*", my_handler)
        """
        with self._lock:
            handler_ref = weakref.ref(handler) if weak else lambda: handler
            
            if event_type == "*":
                self._wildcard_handlers.append(handler_ref)
            elif isinstance(event_type, EventCategory):
                self._category_handlers[event_type].append(handler_ref)
            elif isinstance(event_type, type):
                self._handlers[event_type.__name__].append(handler_ref)
            else:
                self._handlers[str(event_type)].append(handler_ref)
    
    def unsubscribe(self, 
                    event_type: Union[str, type, EventCategory], 
                    handler: AnyEventHandler) -> bool:
        """
        Unsubscribe from events.
        
        Args:
            event_type: Event type or category to unsubscribe from
            handler: Handler function to remove
            
        Returns:
            True if handler was found and removed, False otherwise
        """
        with self._lock:
            target_list = None
            
            if event_type == "*":
                target_list = self._wildcard_handlers
            elif isinstance(event_type, EventCategory):
                target_list = self._category_handlers.get(event_type, [])
            elif isinstance(event_type, type):
                target_list = self._handlers.get(event_type.__name__, [])
            else:
                target_list = self._handlers.get(str(event_type), [])
            
            # Find and remove the handler
            for i, handler_ref in enumerate(target_list):
                if handler_ref() == handler:
                    target_list.pop(i)
                    return True
            
            return False
    
    def emit(self, event: Event) -> None:
        """
        Emit an event to all registered handlers.
        
        This method is non-blocking and handles errors gracefully.
        
        Args:
            event: Event to emit
        """
        if not isinstance(event, Event):
            logger.error(f"Invalid event type: {type(event)}. Must be instance of Event.")
            self._stats["events_dropped"] += 1
            return
        
        # Add to history
        if self._enable_history:
            with self._lock:
                self._event_history.append(event)
        
        # Update statistics
        self._stats["events_emitted"] += 1
        
        # Get all relevant handlers
        handlers = self._get_handlers_for_event(event)
        
        # Execute handlers
        for handler_ref in handlers:
            handler = handler_ref()
            if handler is None:
                # Handler was garbage collected, will be cleaned up later
                continue
            
            try:
                if asyncio.iscoroutinefunction(handler):
                    self._execute_async_handler(handler, event)
                else:
                    self._execute_sync_handler(handler, event)
                
                self._stats["handlers_executed"] += 1
                
            except Exception as e:
                handler_name = getattr(handler, "__name__", str(handler))
                logger.error(f"Error in event handler {handler_name}: {e}", exc_info=True)
                self._stats["handler_errors"] += 1
    
    def _get_handlers_for_event(self, event: Event) -> List[weakref.ref]:
        """Get all handlers that should receive this event."""
        handlers = []
        
        with self._lock:
            # Wildcard handlers
            handlers.extend(self._wildcard_handlers)
            
            # Type-specific handlers
            event_type_name = event.__class__.__name__
            handlers.extend(self._handlers.get(event_type_name, []))
            
            # Category handlers
            handlers.extend(self._category_handlers.get(event.category, []))
            
            # Clean up dead references
            self._cleanup_dead_references()
        
        return handlers
    
    def _cleanup_dead_references(self) -> None:
        """Remove dead weak references from handler lists."""
        # Clean wildcard handlers
        self._wildcard_handlers = [ref for ref in self._wildcard_handlers if ref() is not None]
        
        # Clean type handlers
        for event_type in list(self._handlers.keys()):
            self._handlers[event_type] = [ref for ref in self._handlers[event_type] if ref() is not None]
            if not self._handlers[event_type]:
                del self._handlers[event_type]
        
        # Clean category handlers
        for category in list(self._category_handlers.keys()):
            self._category_handlers[category] = [ref for ref in self._category_handlers[category] if ref() is not None]
            if not self._category_handlers[category]:
                del self._category_handlers[category]
    
    def _execute_sync_handler(self, handler: EventHandler, event: Event) -> None:
        """Execute a synchronous event handler."""
        try:
            handler(event)
        except Exception as e:
            handler_name = getattr(handler, "__name__", str(handler))
            logger.error(f"Error in sync handler {handler_name}: {e}", exc_info=True)
            raise
    
    def _execute_async_handler(self, handler: AsyncEventHandler, event: Event) -> None:
        """Execute an asynchronous event handler."""
        try:
            # Try to get the current event loop
            try:
                loop = asyncio.get_running_loop()
                # Schedule the coroutine in the current loop
                asyncio.create_task(handler(event))
            except RuntimeError:
                # No event loop running, use thread pool
                future = self._executor.submit(asyncio.run, handler(event))
                # Don't wait for completion to keep emission non-blocking
                
        except Exception as e:
            handler_name = getattr(handler, "__name__", str(handler))
            logger.error(f"Error scheduling async handler {handler_name}: {e}", exc_info=True)
            raise
    
    def get_event_history(self, 
                         limit: Optional[int] = None,
                         category: Optional[EventCategory] = None,
                         severity: Optional[EventSeverity] = None) -> List[Event]:
        """
        Get event history with optional filtering.
        
        Args:
            limit: Maximum number of events to return
            category: Filter by event category
            severity: Filter by minimum severity level
            
        Returns:
            List of events matching the criteria
        """
        if not self._enable_history:
            return []
        
        with self._lock:
            events = list(self._event_history)
        
        # Apply filters
        if category is not None:
            events = [e for e in events if e.category == category]
        
        if severity is not None:
            severity_levels = {
                EventSeverity.DEBUG: 0,
                EventSeverity.INFO: 1,
                EventSeverity.WARNING: 2,
                EventSeverity.ERROR: 3,
                EventSeverity.CRITICAL: 4
            }
            min_level = severity_levels[severity]
            events = [e for e in events if severity_levels[e.severity] >= min_level]
        
        # Apply limit
        if limit is not None:
            events = events[-limit:]
        
        return events
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dispatcher statistics."""
        with self._lock:
            stats = dict(self._stats)
            stats.update({
                "active_handlers": sum(len(handlers) for handlers in self._handlers.values()),
                "category_handlers": sum(len(handlers) for handlers in self._category_handlers.values()),
                "wildcard_handlers": len(self._wildcard_handlers),
                "history_size": len(self._event_history) if self._enable_history else 0
            })
        return stats
    
    def clear_history(self) -> None:
        """Clear the event history."""
        if self._enable_history:
            with self._lock:
                self._event_history.clear()
    
    def shutdown(self) -> None:
        """Shutdown the dispatcher and cleanup resources."""
        logger.info("Shutting down event dispatcher")
        
        # Shutdown thread pool
        self._executor.shutdown(wait=True)
        
        # Clear handlers and history
        with self._lock:
            self._handlers.clear()
            self._category_handlers.clear()
            self._wildcard_handlers.clear()
            if self._enable_history:
                self._event_history.clear()
        
        logger.info("Event dispatcher shutdown complete")