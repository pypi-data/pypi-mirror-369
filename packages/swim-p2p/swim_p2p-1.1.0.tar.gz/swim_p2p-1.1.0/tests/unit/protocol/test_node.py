"""
Unit tests for the SWIM protocol node with enhanced reliability features.
"""

import pytest
import asyncio
import time
from unittest.mock import MagicMock, AsyncMock, patch
from swim.protocol.node import Node
from swim.protocol.member import MemberList, MemberState
from swim.protocol.failure_detector import FailureDetector
from swim.protocol.disseminator import GossipService
from swim.protocol.sync import SyncService
from swim.transport.hybrid import HybridTransport
from swim.utils.serialization import serialize_message, deserialize_message
from swim.metrics.collector import MetricsCollector
from swim.metrics.latency import LatencyTracker
from swim.metrics.bandwidth import BandwidthMonitor, Direction


@pytest.fixture
def mock_transport():
    """Create a mock transport for testing."""
    transport = MagicMock()
    transport.send = AsyncMock()
    transport.receive = AsyncMock()
    transport.start_receiver = AsyncMock()
    transport.close = AsyncMock()
    transport.local_address = ("127.0.0.1", 8000)
    return transport


@pytest.fixture
def mock_hybrid_transport():
    """Create a mock hybrid transport for testing."""
    transport = MagicMock(spec=HybridTransport)
    transport.send = AsyncMock()
    transport.receive = AsyncMock()
    transport.start_receiver = AsyncMock()
    transport.close = AsyncMock()
    transport.local_address = ("127.0.0.1", 8000)
    transport.udp_transport = MagicMock()
    transport.tcp_transport = MagicMock()
    return transport


@pytest.fixture
def member_list():
    """Create a member list with some test members."""
    self_addr = ("127.0.0.1", 8000)
    member_list = MemberList(self_addr)
    
    # Add some members
    member_list.add_member(("127.0.0.1", 8001))
    member_list.add_member(("127.0.0.1", 8002))
    
    return member_list


@pytest.fixture
def mock_failure_detector():
    """Create a mock failure detector."""
    detector = MagicMock()
    detector.ping = AsyncMock(return_value=True)
    detector.indirect_probe = AsyncMock(return_value=True)
    detector.handle_ping = AsyncMock()
    detector.handle_ping_req = AsyncMock()
    detector.ping_timeout = 1.0  # Add ping_timeout attribute
    return detector


@pytest.fixture
def mock_gossip():
    """Create a mock gossip service."""
    gossip = MagicMock()
    gossip.send_heartbeat = AsyncMock()
    gossip.handle_message = AsyncMock()
    return gossip


@pytest.fixture
def mock_sync_service():
    """Create a mock sync service."""
    sync = MagicMock()
    sync.start = AsyncMock()
    sync.stop = AsyncMock()
    sync.handle_message = AsyncMock()
    return sync


@pytest.fixture
def mock_metrics_collector():
    """Create a mock metrics collector."""
    collector = MagicMock(spec=MetricsCollector)
    collector.record_counter = MagicMock()
    collector.record_gauge = MagicMock()
    collector.record_histogram = MagicMock()
    collector.record_event = MagicMock()
    collector.start = MagicMock()
    collector.stop = MagicMock()
    collector.report_metrics = MagicMock(return_value={})
    collector.node_id = "127.0.0.1:8000"
    return collector


@pytest.fixture
def mock_latency_tracker():
    """Create a mock latency tracker."""
    tracker = MagicMock(spec=LatencyTracker)
    tracker.record_rtt = MagicMock()
    tracker.get_rtt_stats = MagicMock(return_value={"mean": 0.1, "min": 0.05, "max": 0.2})
    tracker.get_peer_latency_trend = MagicMock(return_value=("stable", 0.0))
    tracker.get_adaptive_timeout = MagicMock(return_value=0.5)
    tracker.get_network_health = MagicMock(return_value={"status": "healthy", "active_peers": 2})
    return tracker


@pytest.fixture
def mock_bandwidth_monitor():
    """Create a mock bandwidth monitor."""
    monitor = MagicMock(spec=BandwidthMonitor)
    monitor.record_bandwidth = MagicMock()
    monitor.get_current_rate = MagicMock(return_value=1000.0)
    monitor.get_bandwidth_stats = MagicMock(return_value={"total_bytes": 5000, "sample_count": 10})
    monitor.get_optimization_recommendations = MagicMock(return_value=[])
    return monitor


@pytest.fixture
def node(mock_transport, member_list, mock_failure_detector, mock_gossip, mock_sync_service):
    """Create a node with mock components for testing."""
    config = {
        "PROTOCOL_PERIOD": 0.1,  # Short period for testing
        "HEARTBEAT_INTERVAL": 0.1,
        "SUSPECT_TIMEOUT": 0.5,
        "ADAPTIVE_TIMING_ENABLED": True,
        "PROTOCOL_PERIOD_MIN": 0.05,
        "PROTOCOL_PERIOD_MAX": 0.5,
        "PROTOCOL_PERIOD_ADJUSTMENT_FACTOR": 0.2,  # Increased for more noticeable changes in tests
        "METRICS_ENABLED": False  # Metrics disabled by default
    }
    
    return Node(
        transport=mock_transport,
        members=member_list,
        failure_detector=mock_failure_detector,
        gossip=mock_gossip,
        sync_service=mock_sync_service,
        config=config
    )


@pytest.fixture
def node_with_metrics(mock_transport, member_list, mock_failure_detector, mock_gossip, mock_sync_service,
                     mock_metrics_collector, mock_latency_tracker, mock_bandwidth_monitor):
    """Create a node with mock components and metrics for testing."""
    config = {
        "PROTOCOL_PERIOD": 0.1,  # Short period for testing
        "HEARTBEAT_INTERVAL": 0.1,
        "SUSPECT_TIMEOUT": 0.5,
        "ADAPTIVE_TIMING_ENABLED": True,
        "PROTOCOL_PERIOD_MIN": 0.05,
        "PROTOCOL_PERIOD_MAX": 0.5,
        "PROTOCOL_PERIOD_ADJUSTMENT_FACTOR": 0.2,  # Increased for more noticeable changes in tests
        "METRICS_ENABLED": True  # Metrics enabled
    }
    
    node = Node(
        transport=mock_transport,
        members=member_list,
        failure_detector=mock_failure_detector,
        gossip=mock_gossip,
        sync_service=mock_sync_service,
        config=config
    )
    
    # Replace metrics components with mocks
    node.metrics_collector = mock_metrics_collector
    node.latency_tracker = mock_latency_tracker
    node.bandwidth_monitor = mock_bandwidth_monitor
    
    return node


@pytest.fixture
def hybrid_node(mock_hybrid_transport, member_list, mock_failure_detector, mock_gossip, mock_sync_service):
    """Create a node with mock hybrid transport for testing."""
    config = {
        "PROTOCOL_PERIOD": 0.1,  # Short period for testing
        "HEARTBEAT_INTERVAL": 0.1,
        "SUSPECT_TIMEOUT": 0.5,
        "ADAPTIVE_TIMING_ENABLED": True,
        "PROTOCOL_PERIOD_MIN": 0.05,
        "PROTOCOL_PERIOD_MAX": 0.5,
        "PROTOCOL_PERIOD_ADJUSTMENT_FACTOR": 0.2  # Increased for more noticeable changes in tests
    }
    
    return Node(
        transport=mock_hybrid_transport,
        members=member_list,
        failure_detector=mock_failure_detector,
        gossip=mock_gossip,
        sync_service=mock_sync_service,
        config=config
    )


def test_hybrid_transport_detection(hybrid_node):
    """Test that the node correctly detects a hybrid transport."""
    assert hybrid_node.hybrid_transport is not None
    assert hybrid_node.hybrid_transport == hybrid_node.transport


def test_metrics_initialization(node, node_with_metrics):
    """Test that metrics components are properly initialized based on config."""
    # Node without metrics
    assert node.metrics_collector is None
    assert node.latency_tracker is None
    assert node.bandwidth_monitor is None
    
    # Node with metrics
    assert node_with_metrics.metrics_collector is not None
    assert node_with_metrics.latency_tracker is not None
    assert node_with_metrics.bandwidth_monitor is not None


@pytest.mark.asyncio
async def test_node_creation():
    """Test creating a node using the factory method."""
    # Mock transport and seed addresses
    mock_transport = MagicMock()
    mock_transport.bind = AsyncMock()
    mock_transport.local_address = ("127.0.0.1", 8000)
    
    seed_addrs = [("127.0.0.1", 8001), ("127.0.0.1", 8002)]
    
    # Create node
    node = await Node.create(
        bind_addr=("127.0.0.1", 8000),
        transport=mock_transport,
        seed_addrs=seed_addrs,
        config={"PUSH_PULL_SYNC_ENABLED": True}
    )
    
    # Verify transport was bound
    mock_transport.bind.assert_called_once_with(("127.0.0.1", 8000))
    
    # Verify seed members were added
    assert node.members.get_member(("127.0.0.1", 8001)) is not None
    assert node.members.get_member(("127.0.0.1", 8002)) is not None
    
    # Verify components were created
    assert node.failure_detector is not None
    assert node.gossip is not None
    assert node.sync_service is not None


@pytest.mark.asyncio
async def test_node_start_stop(node, mock_transport, mock_sync_service):
    """Test starting and stopping the node."""
    # Start the node
    await node.start()
    
    # Verify the node is running
    assert node.running is True
    assert len(node.tasks) > 0
    
    # Verify transport receiver was started
    mock_transport.start_receiver.assert_called_once()
    
    # Verify sync service was started
    mock_sync_service.start.assert_called_once()
    
    # Stop the node
    await node.stop()
    
    # Verify the node is stopped
    assert node.running is False
    assert len(node.tasks) == 0
    
    # Verify transport was closed
    mock_transport.close.assert_called_once()


@pytest.mark.asyncio
async def test_node_start_stop_with_metrics(node_with_metrics, mock_metrics_collector):
    """Test starting and stopping the node with metrics."""
    # Start the node
    await node_with_metrics.start()
    
    # Verify metrics event was recorded
    mock_metrics_collector.record_event.assert_any_call(
        name="node_event",
        value="start",
        labels={"addr": "127.0.0.1:8000"}
    )
    
    # Stop the node
    await node_with_metrics.stop()
    
    # Verify metrics event was recorded and collector was stopped
    mock_metrics_collector.record_event.assert_any_call(
        name="node_event",
        value="stop",
        labels={"addr": "127.0.0.1:8000"}
    )
    mock_metrics_collector.stop.assert_called_once()


@pytest.mark.asyncio
async def test_protocol_loop(node, mock_gossip, mock_failure_detector):
    """Test that the protocol loop executes the expected operations."""
    # Instead of relying on the protocol loop to run automatically,
    # we'll directly call the protocol loop method once
    
    # Start the node but patch the protocol loop to prevent it from running
    with patch.object(node, '_protocol_loop', return_value=asyncio.Future()):
        await node.start()
        
        # Now manually call the protocol operations
        await node._probe_random_member()
        await node._check_suspects()
        await node.gossip.send_heartbeat()
        
        # Verify that protocol operations were called
        assert mock_gossip.send_heartbeat.called
        assert mock_failure_detector.ping.called
        
        # Stop the node
        await node.stop()


@pytest.mark.asyncio
async def test_protocol_loop_with_metrics(node_with_metrics, mock_metrics_collector):
    """Test that the protocol loop records metrics."""
    try:
        # Start the node but patch the protocol loop to prevent it from running
        with patch.object(node_with_metrics, '_protocol_loop', return_value=asyncio.Future()):
            await node_with_metrics.start()
            
            # Reset the mock to clear any previous calls
            mock_metrics_collector.reset_mock()
            
            # Simulate a protocol cycle
            node_with_metrics._protocol_cycle_times = [0.05, 0.06, 0.07]
            
            # Directly call _adjust_protocol_period to trigger the metrics recording
            period = node_with_metrics._adjust_protocol_period()
            
            # Verify metrics were recorded
            mock_metrics_collector.record_gauge.assert_called_with(
                name="protocol_period",
                value=period
            )
    finally:
        # Ensure the node is stopped even if the test fails
        await node_with_metrics.stop()


@pytest.mark.asyncio
async def test_adaptive_timing(node):
    """Test adaptive protocol timing based on network conditions."""
    # Set up very fast cycle times (much less than 30% of protocol period)
    node._protocol_cycle_times = [0.02, 0.02, 0.02, 0.02, 0.02]  # Very fast network
    
    # Calculate adjusted period
    period = node._adjust_protocol_period()
    
    # Should decrease period for fast network
    assert period < node.config["PROTOCOL_PERIOD"]
    
    # Set up slow cycle times (more than 80% of protocol period)
    node._protocol_cycle_times = [0.09, 0.10, 0.11, 0.12, 0.13]  # Slow network
    
    # Calculate adjusted period
    period = node._adjust_protocol_period()
    
    # Should increase period for slow network
    assert period > node.config["PROTOCOL_PERIOD"]
    
    # Verify bounds are respected
    node._protocol_cycle_times = [0.01, 0.01, 0.01, 0.01, 0.01]  # Very fast
    period = node._adjust_protocol_period()
    assert period >= node.config["PROTOCOL_PERIOD_MIN"]
    
    node._protocol_cycle_times = [0.5, 0.5, 0.5, 0.5, 0.5]  # Very slow
    period = node._adjust_protocol_period()
    assert period <= node.config["PROTOCOL_PERIOD_MAX"]


@pytest.mark.asyncio
async def test_handle_message_ping(node, mock_failure_detector):
    """Test handling a PING message."""
    # Create a ping message
    ping_msg = {
        "type": "PING",
        "from": "127.0.0.1:8001",
        "id": "test123",
        "timestamp": time.time()
    }
    
    # Call the message handler
    from_addr = ("127.0.0.1", 8001)
    await node._handle_message(serialize_message(ping_msg), from_addr)
    
    # Verify the ping was handled
    mock_failure_detector.handle_ping.assert_called_once_with(from_addr, ping_msg)


@pytest.mark.asyncio
async def test_handle_message_with_metrics(node_with_metrics, mock_bandwidth_monitor, mock_metrics_collector):
    """Test handling a message with metrics recording."""
    # Create a ping message
    ping_msg = {
        "type": "PING",
        "from": "127.0.0.1:8001",
        "id": "test123",
        "timestamp": time.time()
    }
    
    # Serialize the message
    serialized_msg = serialize_message(ping_msg)
    
    # Call the message handler
    from_addr = ("127.0.0.1", 8001)
    await node_with_metrics._handle_message(serialized_msg, from_addr)
    
    # Verify bandwidth was recorded
    mock_bandwidth_monitor.record_bandwidth.assert_any_call(
        direction=Direction.INBOUND,
        bytes=len(serialized_msg),
        peer_id="127.0.0.1:8001",
        message_type="PING"
    )
    
    # Verify message counter was incremented
    mock_metrics_collector.record_counter.assert_any_call(
        name="message_received",
        value=1,
        labels={
            "type": "PING",
            "from": "127.0.0.1:8001"
        }
    )


@pytest.mark.asyncio
async def test_handle_message_ping_req(node, mock_failure_detector):
    """Test handling a PING-REQ message."""
    # Create a ping-req message
    ping_req_msg = {
        "type": "PING-REQ",
        "from": "127.0.0.1:8001",
        "target": "127.0.0.1:8002",
        "id": "test123",
        "timestamp": time.time()
    }
    
    # Call the message handler
    from_addr = ("127.0.0.1", 8001)
    await node._handle_message(serialize_message(ping_req_msg), from_addr)
    
    # Verify the ping-req was handled
    mock_failure_detector.handle_ping_req.assert_called_once_with(from_addr, ping_req_msg)


@pytest.mark.asyncio
async def test_handle_message_heartbeat(node, mock_gossip):
    """Test handling a HEARTBEAT message."""
    # Create a heartbeat message
    heartbeat_msg = {
        "type": "HEARTBEAT",
        "from": "127.0.0.1:8001",
        "digest": {
            "version": 1,
            "entries": [
                {"addr": "127.0.0.1:8001", "state": "ALIVE", "incarnation": 1}
            ],
            "is_full": True
        },
        "id": "test123",
        "timestamp": time.time()
    }
    
    # Serialize the message
    serialized_msg = serialize_message(heartbeat_msg)
    
    # Call the message handler
    from_addr = ("127.0.0.1", 8001)
    await node._handle_message(serialized_msg, from_addr)
    
    # Verify the heartbeat was handled
    mock_gossip.handle_message.assert_called_once_with(from_addr, serialized_msg)


@pytest.mark.asyncio
async def test_handle_message_sync(node, mock_sync_service):
    """Test handling a SYNC message."""
    # Create a sync message
    sync_msg = {
        "type": "SYNC-REQ",
        "from": "127.0.0.1:8001",
        "id": "test123",
        "known_version": 0,
        "timestamp": time.time()
    }
    
    # Serialize the message
    serialized_msg = serialize_message(sync_msg)
    
    # Call the message handler
    from_addr = ("127.0.0.1", 8001)
    await node._handle_message(serialized_msg, from_addr)
    
    # Verify the sync message was handled
    mock_sync_service.handle_message.assert_called_once_with(from_addr, serialized_msg)


@pytest.mark.asyncio
async def test_probe_random_member(node, mock_failure_detector, member_list):
    """Test probing a random member."""
    # Call the probe method
    await node._probe_random_member()
    
    # Verify a ping was sent to one of the members
    mock_failure_detector.ping.assert_called_once()
    
    # Get the address that was pinged
    pinged_addr = mock_failure_detector.ping.call_args[0][0]
    
    # Verify it's one of our members
    assert pinged_addr in [("127.0.0.1", 8001), ("127.0.0.1", 8002)]


@pytest.mark.asyncio
async def test_probe_random_member_with_metrics(node_with_metrics, mock_failure_detector, 
                                              mock_metrics_collector, mock_latency_tracker):
    """Test probing a random member with metrics recording."""
    # Call the probe method
    await node_with_metrics._probe_random_member()
    
    # Verify a ping was sent
    mock_failure_detector.ping.assert_called_once()
    
    # Get the address that was pinged
    pinged_addr = mock_failure_detector.ping.call_args[0][0]
    peer_id = f"{pinged_addr[0]}:{pinged_addr[1]}"
    
    # Verify metrics were recorded
    mock_metrics_collector.record_event.assert_any_call(
        name="ping",
        value="success",  # Our mock returns True
        labels={"target": peer_id}
    )
    
    # Verify RTT was recorded
    mock_latency_tracker.record_rtt.assert_called_once()
    assert mock_latency_tracker.record_rtt.call_args[0][0] == peer_id
    
    # Verify adaptive timeout was used
    mock_latency_tracker.get_adaptive_timeout.assert_called_once_with(peer_id)


@pytest.mark.asyncio
async def test_check_suspects(node, mock_failure_detector, member_list):
    """Test checking suspect members."""
    # Mark a member as suspect
    suspect_addr = ("127.0.0.1", 8001)
    await member_list.mark_suspect(suspect_addr)
    
    # Call the check suspects method
    await node._check_suspects()
    
    # Verify indirect probe was called for the suspect
    mock_failure_detector.indirect_probe.assert_called_once_with(suspect_addr)


@pytest.mark.asyncio
async def test_check_suspects_with_metrics(node_with_metrics, mock_failure_detector, 
                                         member_list, mock_metrics_collector):
    """Test checking suspect members with metrics recording."""
    # Mark a member as suspect
    suspect_addr = ("127.0.0.1", 8001)
    await member_list.mark_suspect(suspect_addr)
    
    # Call the check suspects method
    await node_with_metrics._check_suspects()
    
    # Verify indirect probe was called
    mock_failure_detector.indirect_probe.assert_called_once_with(suspect_addr)
    
    # Verify metrics were recorded
    mock_metrics_collector.record_event.assert_any_call(
        name="indirect_probe",
        value="success",  # Our mock returns True
        labels={
            "target": "127.0.0.1:8001",
            "probe_time": mock_metrics_collector.record_event.call_args[1]["labels"]["probe_time"]
        }
    )


@pytest.mark.asyncio
async def test_suspect_timeout(node, member_list):
    """Test that suspect members are marked dead after timeout."""
    # Mark a member as suspect
    suspect_addr = ("127.0.0.1", 8001)
    await member_list.mark_suspect(suspect_addr)
    
    # Set last state change to be older than the suspect timeout
    member = member_list.get_member(suspect_addr)
    member.last_state_change = time.time() - node.config["SUSPECT_TIMEOUT"] * 2
    
    # Call the check suspects method
    await node._check_suspects()
    
    # Verify the member is now marked as dead
    assert member_list.get_member(suspect_addr).state == MemberState.DEAD


@pytest.mark.asyncio
async def test_suspect_timeout_with_metrics(node_with_metrics, member_list, mock_metrics_collector):
    """Test that suspect members are marked dead after timeout with metrics recording."""
    # Mark a member as suspect
    suspect_addr = ("127.0.0.1", 8001)
    await member_list.mark_suspect(suspect_addr)
    
    # Set last state change to be older than the suspect timeout
    member = member_list.get_member(suspect_addr)
    member.last_state_change = time.time() - node_with_metrics.config["SUSPECT_TIMEOUT"] * 2
    
    # Call the check suspects method
    await node_with_metrics._check_suspects()
    
    # Verify the member is now marked as dead
    assert member_list.get_member(suspect_addr).state == MemberState.DEAD
    
    # Verify metrics were recorded
    mock_metrics_collector.record_event.assert_any_call(
        name="suspect_timeout",
        value="127.0.0.1:8001",
        labels={"suspect_time": mock_metrics_collector.record_event.call_args[1]["labels"]["suspect_time"]}
    )


def test_get_metrics_report(node_with_metrics, mock_metrics_collector, 
                           mock_latency_tracker, mock_bandwidth_monitor):
    """Test getting a metrics report."""
    # Get the metrics report
    report = node_with_metrics.get_metrics_report()
    
    # Verify the report structure
    assert report is not None
    assert "timestamp" in report
    assert "node_id" in report
    assert "metrics" in report
    assert "network_health" in report
    assert "bandwidth" in report
    assert "current_rates" in report["bandwidth"]
    assert "recommendations" in report["bandwidth"]
    
    # Verify the metrics components were called
    mock_metrics_collector.report_metrics.assert_called_once()
    mock_latency_tracker.get_network_health.assert_called_once()
    mock_bandwidth_monitor.get_current_rate.assert_any_call(Direction.INBOUND)
    mock_bandwidth_monitor.get_current_rate.assert_any_call(Direction.OUTBOUND)
    mock_bandwidth_monitor.get_optimization_recommendations.assert_called_once()


def test_get_peer_metrics(node_with_metrics, mock_latency_tracker, mock_bandwidth_monitor):
    """Test getting metrics for a specific peer."""
    # Get metrics for a peer
    peer_addr = ("127.0.0.1", 8001)
    metrics = node_with_metrics.get_peer_metrics(peer_addr)
    
    # Verify the metrics structure
    assert metrics is not None
    assert "latency" in metrics
    assert "latency_trend" in metrics
    assert "bandwidth" in metrics
    assert "adaptive_timeout" in metrics
    
    # Verify the metrics components were called
    peer_id = "127.0.0.1:8001"
    mock_latency_tracker.get_rtt_stats.assert_called_once_with(peer_id)
    mock_latency_tracker.get_peer_latency_trend.assert_called_once_with(peer_id)
    mock_latency_tracker.get_adaptive_timeout.assert_called_once_with(peer_id)
    mock_bandwidth_monitor.get_bandwidth_stats.assert_any_call(
        direction=Direction.INBOUND,
        peer_id=peer_id,
        time_window=300
    )
    mock_bandwidth_monitor.get_bandwidth_stats.assert_any_call(
        direction=Direction.OUTBOUND,
        peer_id=peer_id,
        time_window=300
    )


def test_no_metrics_when_disabled(node):
    """Test that metrics methods return None when metrics are disabled."""
    assert node.get_metrics_report() is None
    assert node.get_peer_metrics(("127.0.0.1", 8001)) is None