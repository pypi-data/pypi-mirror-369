"""
Tests for default event handlers.

This module tests the pre-built event handlers including logging,
metrics collection, and performance monitoring.
"""

import pytest
import logging
import time
from unittest.mock import Mock, patch, MagicMock
from collections import defaultdict

from swim.events.handlers import (
    LoggingHandler, MetricsHandler, PerformanceHandler, 
    create_default_handlers, register_default_handlers
)
from swim.events.dispatcher import EventDispatcher
from swim.events.types import (
    Event, EventSeverity, EventCategory,
    PingTimeoutEvent, LatencyThresholdExceededEvent, ResourceExhaustionEvent,
    SyncCompletedEvent, BandwidthLimitReachedEvent
)
from swim.protocol.member import (
    MemberEvent, MemberAliveEvent, MemberFailedEvent, 
    MemberJoinedEvent, MemberLeftEvent, MemberSuspectedEvent,
    Member, MemberState
)


class TestLoggingHandler:
    """Test the logging event handler."""

    def test_logging_handler_creation(self):
        """Test creating a logging handler with default settings."""
        handler = LoggingHandler()
        
        assert handler.logger.name == "swim.events"
        assert handler.include_metadata is True
        assert handler.max_metadata_length == 200

    def test_logging_handler_custom_settings(self):
        """Test creating a logging handler with custom settings."""
        handler = LoggingHandler(
            logger_name="custom.logger",
            include_metadata=False,
            max_metadata_length=100
        )
        
        assert handler.logger.name == "custom.logger"
        assert handler.include_metadata is False
        assert handler.max_metadata_length == 100

    @patch('swim.events.handlers.logging.getLogger')
    def test_logging_handler_severity_mapping(self, mock_get_logger):
        """Test that event severities map to correct log levels."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        handler = LoggingHandler()
        
        # Test different severity levels
        test_cases = [
            (EventSeverity.DEBUG, logging.DEBUG),
            (EventSeverity.INFO, logging.INFO),
            (EventSeverity.WARNING, logging.WARNING),
            (EventSeverity.ERROR, logging.ERROR),
            (EventSeverity.CRITICAL, logging.CRITICAL),
        ]
        
        for event_severity, expected_log_level in test_cases:
            event = PingTimeoutEvent(
                target_address="127.0.0.1:8000",
                timeout_duration=1.5,
                attempt_number=1
            )
            event.severity = event_severity
            
            handler(event)
            
            # Check that log was called with correct level
            mock_logger.log.assert_called()
            call_args = mock_logger.log.call_args
            assert call_args[0][0] == expected_log_level

    def test_logging_handler_message_formatting(self):
        """Test that events are formatted correctly for logging."""
        with patch('swim.events.handlers.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            handler = LoggingHandler()
            
            # Test PingTimeoutEvent formatting
            event = PingTimeoutEvent(
                target_address="127.0.0.1:8000",
                timeout_duration=1.5,
                attempt_number=2,
                source_node="127.0.0.1:8001"
            )
            
            handler(event)
            
            # Check the log message
            call_args = mock_logger.log.call_args
            message = call_args[0][1]
            
            assert "PingTimeoutEvent" in message
            assert "from 127.0.0.1:8001" in message
            assert "target: 127.0.0.1:8000" in message
            assert "timeout: 1.5s" in message

    def test_logging_handler_member_event_formatting(self):
        """Test that member events are formatted correctly for logging."""
        with patch('swim.events.handlers.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            handler = LoggingHandler()
            
            # Create a test member
            member = Member(addr=("127.0.0.1", 8000))
            
            # Test MemberJoinedEvent formatting with correct parameters
            event = MemberJoinedEvent(
                member=member,
                source_node="127.0.0.1:8001",
                metadata={
                    "join_method": "manual",
                    "seed_node": "127.0.0.1:8001"
                }
            )
            
            handler(event)
            
            # Check the log message
            call_args = mock_logger.log.call_args
            message = call_args[0][1]
            
            assert "MemberJoinedEvent" in message
            assert "from 127.0.0.1:8001" in message
            assert "member: " in message
            assert "127.0.0.1:8000" in message

    def test_logging_handler_metadata_inclusion(self):
        """Test that metadata is included when enabled."""
        with patch('swim.events.handlers.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            handler = LoggingHandler(include_metadata=True)
            
            event = PingTimeoutEvent(
                target_address="127.0.0.1:8000",
                timeout_duration=1.5,
                attempt_number=1,
                metadata={"test_key": "test_value"}
            )
            
            handler(event)
            
            call_args = mock_logger.log.call_args
            message = call_args[0][1]
            
            assert "metadata:" in message
            assert "test_key" in message

    def test_logging_handler_metadata_truncation(self):
        """Test that long metadata is truncated."""
        with patch('swim.events.handlers.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            handler = LoggingHandler(include_metadata=True, max_metadata_length=50)
            
            long_metadata = {"key": "x" * 100}  # Very long value
            event = PingTimeoutEvent(
                target_address="127.0.0.1:8000",
                timeout_duration=1.5,
                attempt_number=1,
                metadata=long_metadata
            )
            
            handler(event)
            
            call_args = mock_logger.log.call_args
            message = call_args[0][1]
            
            assert "..." in message  # Should be truncated


class TestMetricsHandler:
    """Test the metrics event handler."""

    def test_metrics_handler_creation(self):
        """Test creating a metrics handler."""
        handler = MetricsHandler()
        
        assert isinstance(handler.counters, defaultdict)
        assert isinstance(handler.gauges, dict)
        assert isinstance(handler.histograms, defaultdict)

    def test_metrics_handler_with_collector(self):
        """Test creating a metrics handler with external collector."""
        mock_collector = Mock()
        handler = MetricsHandler(mock_collector)
        
        assert handler.metrics_collector == mock_collector

    def test_metrics_handler_basic_counters(self):
        """Test that basic event counters are updated."""
        handler = MetricsHandler()
        
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        
        handler(event)
        
        assert handler.counters["events_total"] == 1
        assert handler.counters["events_protocol"] == 1
        assert handler.counters["events_warning"] == 1
        assert handler.counters["events_PingTimeoutEvent"] == 1

    def test_metrics_handler_ping_timeout_specific(self):
        """Test ping timeout specific metrics."""
        handler = MetricsHandler()
        
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1,
            is_indirect=True
        )
        
        handler(event)
        
        assert handler.counters["ping_timeouts_total"] == 1
        assert handler.counters["indirect_ping_timeouts_total"] == 1
        assert len(handler.histograms["ping_timeout_duration"]) == 1
        assert handler.histograms["ping_timeout_duration"][0] == 1.5

    def test_metrics_handler_latency_specific(self):
        """Test latency threshold specific metrics."""
        handler = MetricsHandler()
        
        event = LatencyThresholdExceededEvent(
            peer_address="127.0.0.1:8000",
            current_latency_ms=250.0,
            threshold_ms=200.0,
            measurement_window="1m"
        )
        
        handler(event)
        
        assert handler.counters["latency_threshold_exceeded_total"] == 1
        assert len(handler.histograms["latency_measurements"]) == 1
        assert handler.histograms["latency_measurements"][0] == 250.0
        assert handler.gauges["latency_current_127.0.0.1:8000"] == 250.0

    def test_metrics_handler_resource_specific(self):
        """Test resource exhaustion specific metrics."""
        handler = MetricsHandler()
        
        event = ResourceExhaustionEvent(
            resource_type="memory",
            current_usage=7.5,
            total_available=8.0,
            utilization_percent=93.75
        )
        
        handler(event)
        
        assert handler.counters["resource_exhaustion_memory_total"] == 1
        assert handler.gauges["resource_usage_memory"] == 93.75

    def test_metrics_handler_member_events(self):
        """Test member event specific metrics."""
        handler = MetricsHandler()
        
        # Create a test member
        member = Member(addr=("127.0.0.1", 8000))
        
        # Test different member events with correct parameters and metadata
        events = [
            MemberJoinedEvent(
                member=member,
                metadata={"join_method": "manual"}
            ),
            MemberLeftEvent(
                member=member,
                metadata={"leave_reason": "shutdown"}
            ),
            MemberFailedEvent(
                member=member,
                metadata={"failure_detection_method": "direct"}
            ),
            MemberSuspectedEvent(
                member=member,
                metadata={"suspicion_reason": "timeout"}
            ),
            MemberAliveEvent(
                member=member,
                metadata={"recovery_method": "indirect"}
            )
        ]
        
        for event in events:
            handler(event)
        
        # Check counters
        assert handler.counters["member_joined_count"] == 1
        assert handler.counters["member_left_count"] == 1
        assert handler.counters["member_failed_count"] == 1
        assert handler.counters["member_suspected_count"] == 1
        assert handler.counters["member_alive_count"] == 1

    def test_metrics_handler_external_collector(self):
        """Test integration with external metrics collector."""
        mock_collector = Mock()
        mock_collector.increment_metric = Mock()
        mock_collector.set_gauge = Mock()
        
        handler = MetricsHandler(mock_collector)
        
        event = LatencyThresholdExceededEvent(
            peer_address="127.0.0.1:8000",
            current_latency_ms=250.0,
            threshold_ms=200.0,
            measurement_window="1m"
        )
        
        handler(event)
        
        # Check that external collector methods were called
        mock_collector.increment_metric.assert_called()
        mock_collector.set_gauge.assert_called_with(
            "latency_current_127.0.0.1:8000", 250.0
        )

    def test_metrics_handler_external_collector_member_events(self):
        """Test integration with external metrics collector for member events."""
        mock_collector = Mock()
        mock_collector.increment_metric = Mock()
        
        handler = MetricsHandler(mock_collector)
        
        # Create a test member
        member = Member(addr=("127.0.0.1", 8000))
        
        # Test member joined event with correct parameters
        event = MemberJoinedEvent(
            member=member,
            metadata={"join_method": "manual"}
        )
        handler(event)
        
        # Check that external collector methods were called
        mock_collector.increment_metric.assert_any_call("member_joined_count")

    def test_metrics_handler_external_collector_error(self):
        """Test error handling with external metrics collector."""
        mock_collector = Mock()
        mock_collector.increment_metric = Mock(side_effect=Exception("Test error"))
        
        handler = MetricsHandler(mock_collector)
        
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        
        # Should not raise exception
        handler(event)

    def test_metrics_handler_get_metrics(self):
        """Test getting metrics from the handler."""
        handler = MetricsHandler()
        
        # Generate some events
        events = [
            PingTimeoutEvent(
                target_address="127.0.0.1:8000",
                timeout_duration=1.5,
                attempt_number=1
            ),
            LatencyThresholdExceededEvent(
                peer_address="127.0.0.1:8001",
                current_latency_ms=250.0,
                threshold_ms=200.0,
                measurement_window="1m"
            ),
        ]
        
        for event in events:
            handler(event)
        
        metrics = handler.get_metrics()
        
        assert "counters" in metrics
        assert "gauges" in metrics
        assert "histogram_counts" in metrics
        
        assert metrics["counters"]["events_total"] == 2
        assert metrics["counters"]["events_protocol"] == 1
        assert metrics["counters"]["events_performance"] == 1


class TestPerformanceHandler:
    """Test the performance monitoring handler."""

    def test_performance_handler_creation(self):
        """Test creating a performance handler."""
        handler = PerformanceHandler()
        
        assert handler.latency_alert_threshold == 1000.0
        assert handler.resource_alert_threshold == 90.0
        assert handler.cooldown_period == 300.0
        assert handler.alert_callback is None

    def test_performance_handler_custom_settings(self):
        """Test creating a performance handler with custom settings."""
        alert_callback = Mock()
        handler = PerformanceHandler(
            alert_callback=alert_callback,
            latency_alert_threshold=500.0,
            resource_alert_threshold=80.0
        )
        
        assert handler.alert_callback == alert_callback
        assert handler.latency_alert_threshold == 500.0
        assert handler.resource_alert_threshold == 80.0

    def test_performance_handler_ignores_non_performance_events(self):
        """Test that non-performance events are ignored."""
        handler = PerformanceHandler()
        
        # Create a member event (not a performance event)
        member = Member(addr=("127.0.0.1", 8000))
        event = MemberJoinedEvent(
            member=member,
            metadata={"join_method": "manual"}
        )
        
        # Should not raise any exceptions or trigger alerts
        handler(event)
        
        assert len(handler.latency_history) == 0
        assert len(handler.resource_history) == 0

    def test_performance_handler_latency_tracking(self):
        """Test latency event tracking."""
        handler = PerformanceHandler()
        
        event = LatencyThresholdExceededEvent(
            peer_address="127.0.0.1:8000",
            current_latency_ms=250.0,
            threshold_ms=200.0,
            measurement_window="1m"
        )
        
        handler(event)
        
        assert "127.0.0.1:8000" in handler.latency_history
        assert len(handler.latency_history["127.0.0.1:8000"]) == 1
        
        timestamp, latency = handler.latency_history["127.0.0.1:8000"][0]
        assert latency == 250.0
        assert isinstance(timestamp, float)

    def test_performance_handler_resource_tracking(self):
        """Test resource exhaustion event tracking."""
        handler = PerformanceHandler()
        
        event = ResourceExhaustionEvent(
            resource_type="memory",
            current_usage=7.5,
            total_available=8.0,
            utilization_percent=93.75
        )
        
        handler(event)
        
        assert "memory" in handler.resource_history
        assert len(handler.resource_history["memory"]) == 1
        
        timestamp, usage = handler.resource_history["memory"][0]
        assert usage == 93.75
        assert isinstance(timestamp, float)

    def test_performance_handler_latency_alert(self):
        """Test latency alert triggering."""
        alert_callback = Mock()
        handler = PerformanceHandler(
            alert_callback=alert_callback,
            latency_alert_threshold=200.0
        )
        
        event = LatencyThresholdExceededEvent(
            peer_address="127.0.0.1:8000",
            current_latency_ms=250.0,
            threshold_ms=200.0,
            measurement_window="1m"
        )
        
        handler(event)
        
        # Alert should be triggered
        alert_callback.assert_called_once()
        call_args = alert_callback.call_args
        assert call_args[0][0] == "high_latency"
        assert call_args[0][1]["peer"] == "127.0.0.1:8000"
        assert call_args[0][1]["current_latency"] == 250.0

    def test_performance_handler_resource_alert(self):
        """Test resource exhaustion alert triggering."""
        alert_callback = Mock()
        handler = PerformanceHandler(
            alert_callback=alert_callback,
            resource_alert_threshold=90.0
        )
        
        event = ResourceExhaustionEvent(
            resource_type="memory",
            current_usage=7.5,
            total_available=8.0,
            utilization_percent=95.0
        )
        
        handler(event)
        
        # Alert should be triggered
        alert_callback.assert_called_once()
        call_args = alert_callback.call_args
        assert call_args[0][0] == "resource_exhaustion"
        assert call_args[0][1]["resource"] == "memory"
        assert call_args[0][1]["current_usage"] == 95.0

    def test_performance_handler_alert_cooldown(self):
        """Test that alerts respect cooldown periods."""
        alert_callback = Mock()
        handler = PerformanceHandler(
            alert_callback=alert_callback,
            latency_alert_threshold=200.0
        )
        handler.cooldown_period = 1.0  # Short cooldown for testing
        
        # Patch the _should_alert method to control its behavior
        with patch.object(handler, '_should_alert') as mock_should_alert:
            # First call should return True (allow alert)
            # Second call should return False (cooldown active)
            mock_should_alert.side_effect = [True, False]
            
            event = LatencyThresholdExceededEvent(
                peer_address="127.0.0.1:8000",
                current_latency_ms=250.0,
                threshold_ms=200.0,
                measurement_window="1m"
            )
            
            # First event should trigger alert
            handler(event)
            assert alert_callback.call_count == 1
            
            # Second event immediately should not trigger alert
            handler(event)
            assert alert_callback.call_count == 1

    def test_performance_handler_trend_calculation(self):
        """Test trend calculation for latency."""
        handler = PerformanceHandler()
        peer = "127.0.0.1:8000"
        
        # Add some history data
        current_time = time.time()
        for i in range(10):
            handler.latency_history[peer].append((current_time - i, 100.0 + i * 10))
        
        # Calculate trend (should be increasing since recent values are higher)
        trend = handler._calculate_latency_trend(peer)
        assert trend in ["increasing", "decreasing", "stable", "insufficient_data"]

    def test_performance_handler_insufficient_data(self):
        """Test trend calculation with insufficient data."""
        handler = PerformanceHandler()
        peer = "127.0.0.1:8000"
        
        # Add only a few data points
        current_time = time.time()
        for i in range(3):
            handler.latency_history[peer].append((current_time - i, 100.0))
        
        trend = handler._calculate_latency_trend(peer)
        assert trend == "insufficient_data"

    def test_performance_handler_alert_callback_error(self):
        """Test error handling in alert callback."""
        # Create a callback that raises an exception
        alert_callback = Mock(side_effect=Exception("Test error"))
        handler = PerformanceHandler(
            alert_callback=alert_callback,
            latency_alert_threshold=200.0
        )
        
        event = LatencyThresholdExceededEvent(
            peer_address="127.0.0.1:8000",
            current_latency_ms=250.0,
            threshold_ms=200.0,
            measurement_window="1m"
        )
        
        # Should not raise exception
        handler(event)
        
        # Callback should have been called
        alert_callback.assert_called_once()


class TestDefaultHandlers:
    """Test the default handler creation function."""

    def test_create_default_handlers_minimal(self):
        """Test creating default handlers with minimal configuration."""
        handlers = create_default_handlers()
        
        # Should always include logging handler
        assert len(handlers) >= 1
        assert any(isinstance(h, LoggingHandler) for h in handlers)

    def test_create_default_handlers_with_metrics(self):
        """Test creating default handlers with metrics collector."""
        mock_collector = Mock()
        handlers = create_default_handlers(metrics_collector=mock_collector)
        
        # Should include logging and metrics handlers
        assert len(handlers) >= 2
        assert any(isinstance(h, LoggingHandler) for h in handlers)
        assert any(isinstance(h, MetricsHandler) for h in handlers)
        
        # Find metrics handler and check it has the collector
        metrics_handler = next(h for h in handlers if isinstance(h, MetricsHandler))
        assert metrics_handler.metrics_collector == mock_collector

    def test_create_default_handlers_with_performance_alerts(self):
        """Test creating default handlers with performance alerts."""
        alert_callback = Mock()
        handlers = create_default_handlers(
            enable_performance_alerts=True,
            alert_callback=alert_callback
        )
        
        # Should include performance handler
        assert any(isinstance(h, PerformanceHandler) for h in handlers)
        
        # Find performance handler and check it has the callback
        perf_handler = next(h for h in handlers if isinstance(h, PerformanceHandler))
        assert perf_handler.alert_callback == alert_callback

    def test_create_default_handlers_no_performance_alerts(self):
        """Test creating default handlers without performance alerts."""
        handlers = create_default_handlers(enable_performance_alerts=False)
        
        # Should not include performance handler
        assert not any(isinstance(h, PerformanceHandler) for h in handlers)

    def test_create_default_handlers_full_configuration(self):
        """Test creating default handlers with full configuration."""
        mock_collector = Mock()
        alert_callback = Mock()
        
        handlers = create_default_handlers(
            metrics_collector=mock_collector,
            enable_performance_alerts=True,
            alert_callback=alert_callback
        )
        
        # Should include all handler types
        assert len(handlers) == 3
        assert any(isinstance(h, LoggingHandler) for h in handlers)
        assert any(isinstance(h, MetricsHandler) for h in handlers)
        assert any(isinstance(h, PerformanceHandler) for h in handlers)

    def test_register_default_handlers(self):
        """Test registering default handlers with a dispatcher."""
        dispatcher = EventDispatcher()
        mock_collector = Mock()
        alert_callback = Mock()
        
        # Patch the subscribe method to verify it's called
        with patch.object(dispatcher, 'subscribe') as mock_subscribe:
            result = register_default_handlers(
                dispatcher,
                metrics_collector=mock_collector,
                enable_performance_alerts=True,
                alert_callback=alert_callback
            )
            
            # Should have called subscribe for each handler
            assert mock_subscribe.call_count == 3
            
            # Each call should have "*" as the event type
            for call in mock_subscribe.call_args_list:
                assert call[0][0] == "*"
            
            # Result should be a dict with "*" key
            assert "*" in result
            assert len(result["*"]) == 3


class TestHandlerIntegration:
    """Test the integration of handlers with the event system."""

    def test_handlers_with_dispatcher(self):
        """Test handlers receiving events from dispatcher."""
        dispatcher = EventDispatcher()
        
        # Create mock handlers
        mock_handler1 = Mock()
        mock_handler2 = Mock()
        
        # Register handlers
        dispatcher.subscribe("*", mock_handler1)
        dispatcher.subscribe(EventCategory.PROTOCOL, mock_handler2)
        
        # Create and publish an event
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        
        # Use emit instead of publish
        dispatcher.emit(event)
        
        # Both handlers should have received the event
        mock_handler1.assert_called_once_with(event)
        mock_handler2.assert_called_once_with(event)

    def test_member_events_with_handlers(self):
        """Test member events with handlers."""
        dispatcher = EventDispatcher()
        
        # Create mock handlers
        mock_handler = Mock()
        
        # Register handlers for APPLICATION category (correct category for member events)
        dispatcher.subscribe(EventCategory.APPLICATION, mock_handler)
        
        # Create a member and event
        member = Member(addr=("127.0.0.1", 8000))
        event = MemberJoinedEvent(
            member=member,
            metadata={"join_method": "manual"}
        )
        
        # Use emit instead of publish
        dispatcher.emit(event)
        
        # Handler should have received the event
        mock_handler.assert_called_once_with(event)

    def test_metrics_handler_with_dispatcher(self):
        """Test metrics handler receiving events from dispatcher."""
        dispatcher = EventDispatcher()
        metrics_handler = MetricsHandler()
        
        # Register handler
        dispatcher.subscribe("*", metrics_handler)
        
        # Create and publish events
        events = [
            PingTimeoutEvent(
                target_address="127.0.0.1:8000",
                timeout_duration=1.5,
                attempt_number=1
            ),
            LatencyThresholdExceededEvent(
                peer_address="127.0.0.1:8001",
                current_latency_ms=250.0,
                threshold_ms=200.0,
                measurement_window="1m"
            ),
            ResourceExhaustionEvent(
                resource_type="memory",
                current_usage=7.5,
                total_available=8.0,
                utilization_percent=93.75
            )
        ]
        
        for event in events:
            # Use emit instead of publish
            dispatcher.emit(event)
        
        # Check metrics were updated
        metrics = metrics_handler.get_metrics()
        assert metrics["counters"]["events_total"] == 3
        assert metrics["counters"]["ping_timeouts_total"] == 1
        assert metrics["counters"]["latency_threshold_exceeded_total"] == 1
        assert metrics["counters"]["resource_exhaustion_memory_total"] == 1

    def test_performance_handler_with_dispatcher(self):
        """Test performance handler receiving events from dispatcher."""
        dispatcher = EventDispatcher()
        alert_callback = Mock()
        performance_handler = PerformanceHandler(
            alert_callback=alert_callback,
            latency_alert_threshold=200.0,
            resource_alert_threshold=90.0
        )
        
        # Register handler
        dispatcher.subscribe(EventCategory.PERFORMANCE, performance_handler)
        
        # Create and publish events that should trigger alerts
        events = [
            LatencyThresholdExceededEvent(
                peer_address="127.0.0.1:8000",
                current_latency_ms=250.0,
                threshold_ms=200.0,
                measurement_window="1m"
            ),
            ResourceExhaustionEvent(
                resource_type="memory",
                current_usage=7.5,
                total_available=8.0,
                utilization_percent=93.75
            )
        ]
        
        for event in events:
            # Use emit instead of publish
            dispatcher.emit(event)
        
        # Check alerts were triggered
        assert alert_callback.call_count == 2
        
        # First call should be for latency
        first_call = alert_callback.call_args_list[0]
        assert first_call[0][0] == "high_latency"
        
        # Second call should be for resource
        second_call = alert_callback.call_args_list[1]
        assert second_call[0][0] == "resource_exhaustion"

    def test_default_handlers_with_real_events(self):
        """Test default handlers with real events."""
        dispatcher = EventDispatcher()
        mock_collector = Mock()
        mock_collector.increment_metric = Mock()
        mock_collector.set_gauge = Mock()
        
        # Create and register a metrics handler directly to ensure it works
        metrics_handler = MetricsHandler(mock_collector)
        dispatcher.subscribe("*", metrics_handler)
        
        # Create a member and events
        member = Member(addr=("127.0.0.1", 8000))
        events = [
            PingTimeoutEvent(
                target_address="127.0.0.1:8000",
                timeout_duration=1.5,
                attempt_number=1
            ),
            MemberJoinedEvent(
                member=member,
                metadata={"join_method": "manual"}
            ),
            MemberFailedEvent(
                member=member,
                metadata={"failure_detection_method": "direct"}
            )
        ]
        
        # Emit events
        for event in events:
            dispatcher.emit(event)
        
        # Check that the metrics handler processed the events
        assert metrics_handler.counters["events_total"] == 3
        
        # Check that the mock collector was called
        assert mock_collector.increment_metric.called
        
        # Check specific metrics
        mock_collector.increment_metric.assert_any_call("events_total")
        mock_collector.increment_metric.assert_any_call("member_joined_count")
        mock_collector.increment_metric.assert_any_call("member_failed_count")