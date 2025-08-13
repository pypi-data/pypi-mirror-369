"""
Tests for event type definitions.

This module tests the event type hierarchy, ensuring that events
are properly structured, serializable, and maintain their contracts.
"""

import pytest
import time
from datetime import datetime

from swim.events.types import (
    Event, EventCategory, EventSeverity,
    ProtocolEvent, PerformanceEvent, NetworkEvent, ApplicationEvent,
    PingTimeoutEvent, SyncCompletedEvent, TransportErrorEvent,
    LatencyThresholdExceededEvent, BandwidthLimitReachedEvent, ResourceExhaustionEvent,
    ConnectionEstablishedEvent, ConnectionLostEvent, NetworkPartitionDetectedEvent,
    MetricsCollectionEvent, ConfigurationChangedEvent, ShutdownInitiatedEvent
)


class TestEventBase:
    """Test the base Event class functionality."""
    
    def test_event_creation_requires_category(self):
        """Test that events must define a category."""
        # This should fail because Event is abstract
        with pytest.raises(TypeError):
            Event()
    
    def test_event_has_required_fields(self):
        """Test that events have all required fields."""
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        
        assert hasattr(event, 'timestamp')
        assert hasattr(event, 'event_id')
        assert hasattr(event, 'source_node')
        assert hasattr(event, 'severity')
        assert hasattr(event, 'category')
        assert hasattr(event, 'metadata')
    
    def test_event_timestamp_is_current(self):
        """Test that event timestamp is set to current time."""
        before = time.time()
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        after = time.time()
        
        assert before <= event.timestamp <= after
    
    def test_event_id_is_unique(self):
        """Test that event IDs are unique."""
        event1 = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        event2 = PingTimeoutEvent(
            target_address="127.0.0.1:8001",
            timeout_duration=1.5,
            attempt_number=1
        )
        
        assert event1.event_id != event2.event_id
    
    def test_event_age_calculation(self):
        """Test that event age is calculated correctly."""
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        
        # Age should be very small initially
        assert event.age_seconds < 1.0
        
        # Mock an older timestamp
        event.timestamp = time.time() - 10.0
        assert 9.0 < event.age_seconds < 11.0
    
    def test_event_datetime_property(self):
        """Test that datetime property works correctly."""
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        
        dt = event.datetime
        assert isinstance(dt, datetime)
        assert abs((dt.timestamp() - event.timestamp)) < 1.0


class TestProtocolEvents:
    """Test protocol-specific events."""
    
    def test_ping_timeout_event(self):
        """Test PingTimeoutEvent creation and serialization."""
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=2,
            is_indirect=True,
            source_node="127.0.0.1:8001"
        )
        
        assert event.category == EventCategory.PROTOCOL
        assert event.severity == EventSeverity.WARNING
        assert event.target_address == "127.0.0.1:8000"
        assert event.timeout_duration == 1.5
        assert event.attempt_number == 2
        assert event.is_indirect is True
        
        # Test serialization
        data = event.to_dict()
        assert data["event_type"] == "PingTimeoutEvent"
        assert data["target_address"] == "127.0.0.1:8000"
        assert data["timeout_duration"] == 1.5
        assert data["attempt_number"] == 2
        assert data["is_indirect"] is True
    
    def test_sync_completed_event(self):
        """Test SyncCompletedEvent creation and serialization."""
        event = SyncCompletedEvent(
            peer_address="127.0.0.1:8000",
            duration_ms=150.5,
            members_exchanged=5,
            bytes_transferred=1024
        )
        
        assert event.category == EventCategory.PROTOCOL
        assert event.severity == EventSeverity.INFO
        assert event.peer_address == "127.0.0.1:8000"
        assert event.duration_ms == 150.5
        assert event.members_exchanged == 5
        assert event.bytes_transferred == 1024
        
        # Test serialization
        data = event.to_dict()
        assert data["event_type"] == "SyncCompletedEvent"
        assert data["peer_address"] == "127.0.0.1:8000"
        assert data["duration_ms"] == 150.5
    
    def test_transport_error_event(self):
        """Test TransportErrorEvent creation and serialization."""
        event = TransportErrorEvent(
            error_type="ConnectionRefused",
            error_message="Connection refused by peer",
            target_address="127.0.0.1:8000",
            operation="ping"
        )
        
        assert event.category == EventCategory.PROTOCOL
        assert event.severity == EventSeverity.ERROR
        assert event.error_type == "ConnectionRefused"
        assert event.error_message == "Connection refused by peer"
        assert event.target_address == "127.0.0.1:8000"
        assert event.operation == "ping"


class TestPerformanceEvents:
    """Test performance-related events."""
    
    def test_latency_threshold_exceeded_event(self):
        """Test LatencyThresholdExceededEvent creation."""
        event = LatencyThresholdExceededEvent(
            peer_address="127.0.0.1:8000",
            current_latency_ms=250.5,
            threshold_ms=200.0,
            measurement_window="1m"
        )
        
        assert event.category == EventCategory.PERFORMANCE
        assert event.severity == EventSeverity.WARNING
        assert event.peer_address == "127.0.0.1:8000"
        assert event.current_latency_ms == 250.5
        assert event.threshold_ms == 200.0
        assert event.measurement_window == "1m"
    
    def test_bandwidth_limit_reached_event(self):
        """Test BandwidthLimitReachedEvent creation."""
        event = BandwidthLimitReachedEvent(
            current_bandwidth_bps=950000.0,
            limit_bandwidth_bps=1000000.0,
            direction="outbound",
            utilization_percent=95.0
        )
        
        assert event.category == EventCategory.PERFORMANCE
        assert event.severity == EventSeverity.WARNING
        assert event.current_bandwidth_bps == 950000.0
        assert event.limit_bandwidth_bps == 1000000.0
        assert event.direction == "outbound"
        assert event.utilization_percent == 95.0
    
    def test_resource_exhaustion_event(self):
        """Test ResourceExhaustionEvent creation."""
        event = ResourceExhaustionEvent(
            resource_type="memory",
            current_usage=7.5,
            total_available=8.0,
            utilization_percent=93.75
        )
        
        assert event.category == EventCategory.PERFORMANCE
        assert event.severity == EventSeverity.ERROR
        assert event.resource_type == "memory"
        assert event.current_usage == 7.5
        assert event.total_available == 8.0
        assert event.utilization_percent == 93.75


class TestNetworkEvents:
    """Test network-related events."""
    
    def test_connection_established_event(self):
        """Test ConnectionEstablishedEvent creation."""
        event = ConnectionEstablishedEvent(
            peer_address="127.0.0.1:8000",
            connection_type="tcp",
            connection_id="conn_123"
        )
        
        assert event.category == EventCategory.NETWORK
        assert event.severity == EventSeverity.INFO
        assert event.peer_address == "127.0.0.1:8000"
        assert event.connection_type == "tcp"
        assert event.connection_id == "conn_123"
    
    def test_connection_lost_event(self):
        """Test ConnectionLostEvent creation."""
        event = ConnectionLostEvent(
            peer_address="127.0.0.1:8000",
            connection_type="tcp",
            connection_id="conn_123",
            reason="timeout",
            duration_seconds=30.5
        )
        
        assert event.category == EventCategory.NETWORK
        assert event.severity == EventSeverity.WARNING
        assert event.peer_address == "127.0.0.1:8000"
        assert event.connection_type == "tcp"
        assert event.connection_id == "conn_123"
        assert event.reason == "timeout"
        assert event.duration_seconds == 30.5
    
    def test_network_partition_detected_event(self):
        """Test NetworkPartitionDetectedEvent creation."""
        event = NetworkPartitionDetectedEvent(
            affected_nodes=["127.0.0.1:8000", "127.0.0.1:8001"],
            partition_confidence=0.85,
            detection_method="connectivity_matrix"
        )
        
        assert event.category == EventCategory.NETWORK
        assert event.severity == EventSeverity.CRITICAL
        assert event.affected_nodes == ["127.0.0.1:8000", "127.0.0.1:8001"]
        assert event.partition_confidence == 0.85
        assert event.detection_method == "connectivity_matrix"


class TestApplicationEvents:
    """Test application-level events."""
    
    def test_metrics_collection_event(self):
        """Test MetricsCollectionEvent creation."""
        event = MetricsCollectionEvent(
            collection_duration_ms=50.5,
            metrics_count=25,
            collection_type="periodic"
        )
        
        assert event.category == EventCategory.APPLICATION
        assert event.severity == EventSeverity.INFO
        assert event.collection_duration_ms == 50.5
        assert event.metrics_count == 25
        assert event.collection_type == "periodic"
    
    def test_configuration_changed_event(self):
        """Test ConfigurationChangedEvent creation."""
        event = ConfigurationChangedEvent(
            changed_keys=["ping_interval", "sync_interval"],
            change_source="api"
        )
        
        assert event.category == EventCategory.APPLICATION
        assert event.severity == EventSeverity.INFO
        assert event.changed_keys == ["ping_interval", "sync_interval"]
        assert event.change_source == "api"
    
    def test_shutdown_initiated_event(self):
        """Test ShutdownInitiatedEvent creation."""
        event = ShutdownInitiatedEvent(
            shutdown_reason="user_request",
            graceful=True,
            estimated_shutdown_time_seconds=5.0
        )
        
        assert event.category == EventCategory.APPLICATION
        assert event.severity == EventSeverity.INFO
        assert event.shutdown_reason == "user_request"
        assert event.graceful is True
        assert event.estimated_shutdown_time_seconds == 5.0


class TestEventSerialization:
    """Test event serialization and deserialization."""
    
    def test_event_to_dict_contains_required_fields(self):
        """Test that to_dict includes all required fields."""
        event = PingTimeoutEvent(
            target_address="127.0.0.1:8000",
            timeout_duration=1.5,
            attempt_number=1
        )
        
        data = event.to_dict()
        
        required_fields = [
            "event_type", "event_id", "timestamp", "source_node",
            "severity", "category", "metadata"
        ]
        
        for field in required_fields:
            assert field in data
        
        # Check event-specific fields
        assert "target_address" in data
        assert "timeout_duration" in data
        assert "attempt_number" in data
    
    def test_event_serialization_roundtrip(self):
        """Test that events can be serialized and maintain their data."""
        original_event = LatencyThresholdExceededEvent(
            peer_address="127.0.0.1:8000",
            current_latency_ms=250.5,
            threshold_ms=200.0,
            measurement_window="1m",
            source_node="127.0.0.1:8001",
            metadata={"test": "value"}
        )
        
        # Serialize to dict
        data = original_event.to_dict()
        
        # Verify all data is present
        assert data["event_type"] == "LatencyThresholdExceededEvent"
        assert data["peer_address"] == "127.0.0.1:8000"
        assert data["current_latency_ms"] == 250.5
        assert data["threshold_ms"] == 200.0
        assert data["measurement_window"] == "1m"
        assert data["source_node"] == "127.0.0.1:8001"
        assert data["metadata"] == {"test": "value"}
        assert data["severity"] == "warning"
        assert data["category"] == "performance"
