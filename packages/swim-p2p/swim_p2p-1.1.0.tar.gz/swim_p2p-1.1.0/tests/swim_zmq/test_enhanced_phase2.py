#!/usr/bin/env python3
"""
SWIM-ZMQ Phase 2 Comprehensive Integration Test

This test validates the complete Phase 2 reliability stack including:
- Core components: Workflow management, congestion detection, load balancing
- Reliability components: Circuit breaker, buffer monitoring, flow control, capacity tracking
- Integration scenarios: Component interaction, failure handling, recovery
- Performance testing: Load testing, stress scenarios, resource management

Follows software engineering best practices:
- Modular design with clear separation of concerns
- Comprehensive error handling and logging
- Realistic test scenarios and data
- Proper resource management and cleanup
- Detailed reporting and metrics
"""

import os
import sys
import time
import asyncio
import logging
import uuid
import json
import random
import traceback
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from collections import defaultdict, deque
from enum import Enum

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import core Phase 2 components
from swim.messaging.workflow import WorkflowManager, WorkflowMessage, ConsistencyModel
from swim.messaging.congestion import CongestionDetector, CongestionLevel, ThrottleAction
from swim.integration.load_balancer import LoadBalancer, RoutingStrategy, NodeHealth, NodeMetrics

# Import reliability components
from swim.messaging.circuit_breaker import CircuitBreaker, CircuitState, CircuitConfig
from swim.messaging.buffer_monitor import BufferMonitor, BufferState, BufferType
from swim.integration.zmq.flow_control import FlowControlManager, CreditType, FlowState
from swim.integration.zmq.capacity_tracker import CapacityTracker, CapacityState, MetricType


# Configure logging
class TestFormatter(logging.Formatter):
    """Custom formatter for test output."""
    
    def format(self, record):
        # Add test context to log messages
        msg = super().format(record)
        return msg.replace('🚀', '[START]').replace('✅', '[OK]').replace('❌', '[FAIL]')


def setup_logging():
    """Setup comprehensive logging for the test."""
    formatter = TestFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler('phase2_comprehensive_test.log', mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[console_handler, file_handler]
    )
    
    # Set component log levels
    for component in [
        "swim.messaging.workflow", "swim.messaging.congestion", "swim.integration.load_balancer",
        "swim.messaging.circuit_breaker", "swim.messaging.buffer_monitor", 
        "swim.integration.zmq.flow_control", "swim.integration.zmq.capacity_tracker"
    ]:
        logging.getLogger(component).setLevel(logging.INFO)


@dataclass
class TestConfiguration:
    """Test configuration parameters."""
    num_nodes: int = 4
    num_workflows: int = 8
    messages_per_workflow: int = 6
    test_duration: float = 60.0  # seconds
    stress_test_enabled: bool = True
    performance_benchmarking: bool = True
    failure_injection_enabled: bool = True
    
    # Component-specific settings
    circuit_breaker_enabled: bool = True
    buffer_monitoring_enabled: bool = True
    flow_control_enabled: bool = True
    capacity_tracking_enabled: bool = True
    
    # Thresholds and limits
    max_message_size: int = 1024
    max_queue_depth: int = 100
    max_cpu_percent: float = 85.0
    max_memory_percent: float = 80.0


@dataclass
class ReliabilityComponents:
    """Container for all reliability components of a node."""
    circuit_breaker: Optional[CircuitBreaker] = None
    buffer_monitor: Optional[BufferMonitor] = None
    flow_controller: Optional[FlowControlManager] = None
    capacity_tracker: Optional[CapacityTracker] = None


@dataclass
class TestNode:
    """Enhanced test node with all Phase 2 components."""
    node_id: str
    
    # Core components
    workflow_manager: WorkflowManager
    congestion_detector: CongestionDetector
    load_balancer: LoadBalancer
    
    # Reliability components
    reliability: ReliabilityComponents
    
    # Node state
    cpu_usage: float = 0.3
    memory_usage: float = 0.4
    queue_depth: int = 0
    avg_latency: float = 50.0
    success_rate: float = 1.0
    active_connections: int = 0
    
    # Metrics and tracking
    processed_messages: List[str] = field(default_factory=list)
    failed_messages: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, deque] = field(default_factory=lambda: defaultdict(lambda: deque(maxlen=100)))
    
    def update_performance_metric(self, metric_name: str, value: float):
        """Update a performance metric."""
        self.performance_metrics[metric_name].append((time.time(), value))
    
    def get_health_score(self) -> float:
        """Calculate overall node health score (0.0 = unhealthy, 1.0 = healthy)."""
        factors = [
            1.0 - self.cpu_usage,  # Lower CPU usage is better
            1.0 - self.memory_usage,  # Lower memory usage is better
            max(0.0, 1.0 - (self.queue_depth / 100.0)),  # Lower queue depth is better
            self.success_rate,  # Higher success rate is better
            max(0.0, 1.0 - (self.avg_latency / 1000.0))  # Lower latency is better
        ]
        return sum(factors) / len(factors)


class ComponentFactory:
    """Factory for creating and configuring components."""
    
    @staticmethod
    def create_circuit_breaker(node_id: str, target_node: str) -> CircuitBreaker:
        """Create a properly configured circuit breaker."""
        config = CircuitConfig(
            failure_threshold=5,
            recovery_timeout=30.0,
            success_threshold=3
        )
        return CircuitBreaker(node_id, target_node, config)
    
    @staticmethod
    def create_buffer_monitor(node_id: str) -> BufferMonitor:
        """Create a properly configured buffer monitor."""
        return BufferMonitor(node_id)
    
    @staticmethod
    def create_flow_controller(node_id: str) -> FlowControlManager:
        """Create a properly configured flow controller."""
        return FlowControlManager(node_id)
    
    @staticmethod
    def create_capacity_tracker(node_id: str) -> CapacityTracker:
        """Create a properly configured capacity tracker."""
        return CapacityTracker(node_id)


class Phase2ComprehensiveTest:
    """
    Comprehensive integration test for Phase 2 components.
    
    Tests the complete reliability stack with realistic scenarios:
    1. Component initialization and integration
    2. Basic functionality validation
    3. Load balancing and capacity management
    4. Failure injection and recovery
    5. Performance and stress testing
    6. Resource cleanup and reporting
    """
    
    def __init__(self, config: Optional[TestConfiguration] = None):
        """Initialize the comprehensive test."""
        self.config = config or TestConfiguration()
        self.logger = logging.getLogger("phase2_test")
        
        # Test state
        self.nodes: Dict[str, TestNode] = {}
        self.test_workflows: List[str] = []
        self.test_messages: List[str] = []
        self.start_time = 0.0
        
        # Statistics
        self.stats = {
            "workflows_created": 0,
            "workflows_completed": 0,
            "messages_processed": 0,
            "messages_failed": 0,
            "circuit_trips": 0,
            "buffer_overflows": 0,
            "flow_throttles": 0,
            "capacity_warnings": 0,
            "test_phases_passed": 0,
            "test_phases_failed": 0
        }
        
        # Test phases
        self.test_phases = [
            "component_initialization",
            "basic_functionality",
            "load_balancing",
            "circuit_breaker_testing",
            "buffer_management",
            "flow_control",
            "capacity_tracking",
            "integration_scenarios",
            "failure_recovery",
            "performance_testing"
        ]
        
        self.phase_results: Dict[str, bool] = {}
        
        self.logger.info(f"Initialized Phase 2 comprehensive test with {self.config.num_nodes} nodes")
    
    async def run_comprehensive_test(self) -> bool:
        """Run the complete comprehensive test suite."""
        self.start_time = time.time()
        self.logger.info("=" * 80)
        self.logger.info("STARTING PHASE 2 COMPREHENSIVE INTEGRATION TEST")
        self.logger.info("=" * 80)
        
        try:
            # Phase 1: Component Initialization
            success = await self._test_component_initialization()
            self.phase_results["component_initialization"] = success
            if not success:
                self.logger.error("Component initialization failed - aborting test")
                return False
            
            # Phase 2: Basic Functionality
            success = await self._test_basic_functionality()
            self.phase_results["basic_functionality"] = success
            
            # Phase 3: Load Balancing
            success = await self._test_load_balancing()
            self.phase_results["load_balancing"] = success
            
            # Phase 4: Circuit Breaker Testing
            if self.config.circuit_breaker_enabled:
                success = await self._test_circuit_breaker()
                self.phase_results["circuit_breaker_testing"] = success
            
            # Phase 5: Buffer Management
            if self.config.buffer_monitoring_enabled:
                success = await self._test_buffer_management()
                self.phase_results["buffer_management"] = success
            
            # Phase 6: Flow Control
            if self.config.flow_control_enabled:
                success = await self._test_flow_control()
                self.phase_results["flow_control"] = success
            
            # Phase 7: Capacity Tracking
            if self.config.capacity_tracking_enabled:
                success = await self._test_capacity_tracking()
                self.phase_results["capacity_tracking"] = success
            
            # Phase 8: Integration Scenarios
            success = await self._test_integration_scenarios()
            self.phase_results["integration_scenarios"] = success
            
            # Phase 9: Failure Recovery
            if self.config.failure_injection_enabled:
                success = await self._test_failure_recovery()
                self.phase_results["failure_recovery"] = success
            
            # Phase 10: Performance Testing
            if self.config.performance_benchmarking:
                success = await self._test_performance()
                self.phase_results["performance_testing"] = success
            
            # Generate final report
            await self._generate_comprehensive_report()
            
            # Calculate overall success
            passed_phases = sum(1 for result in self.phase_results.values() if result)
            total_phases = len(self.phase_results)
            overall_success = passed_phases >= (total_phases * 0.8)  # 80% pass rate
            
            self.logger.info("=" * 80)
            if overall_success:
                self.logger.info(f"TEST COMPLETED SUCCESSFULLY: {passed_phases}/{total_phases} phases passed")
            else:
                self.logger.warning(f"TEST COMPLETED WITH ISSUES: {passed_phases}/{total_phases} phases passed")
            self.logger.info("=" * 80)
            
            return overall_success
            
        except Exception as e:
            self.logger.error(f"Critical test failure: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    async def _test_component_initialization(self) -> bool:
        """Test component initialization and setup."""
        self.logger.info("PHASE 1: Component Initialization")
        
        try:
            # Create test nodes
            for i in range(self.config.num_nodes):
                node_id = f"node_{i+1}"
                await self._create_test_node(node_id)
            
            # Configure component integration
            await self._configure_component_integration()
            
            # Start all components
            await self._start_all_components()
            
            # Verify component health
            healthy_nodes = await self._verify_component_health()
            
            success = healthy_nodes == len(self.nodes)
            if success:
                self.logger.info(f"[OK] All {len(self.nodes)} nodes initialized successfully")
            else:
                self.logger.error(f"[FAIL] Only {healthy_nodes}/{len(self.nodes)} nodes healthy")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Component initialization failed: {e}")
            return False
    
    async def _create_test_node(self, node_id: str):
        """Create a test node with all components."""
        self.logger.info(f"Creating test node {node_id}")
        
        # Create core components
        workflow_manager = WorkflowManager(node_id)
        congestion_detector = CongestionDetector(node_id)
        load_balancer = LoadBalancer(node_id, RoutingStrategy.ADAPTIVE)
        
        # Create reliability components
        reliability = ReliabilityComponents()
        
        if self.config.circuit_breaker_enabled:
            # Create circuit breaker for each other node
            reliability.circuit_breaker = ComponentFactory.create_circuit_breaker(node_id, "default_target")
        
        if self.config.buffer_monitoring_enabled:
            reliability.buffer_monitor = ComponentFactory.create_buffer_monitor(node_id)
        
        if self.config.flow_control_enabled:
            reliability.flow_controller = ComponentFactory.create_flow_controller(node_id)
        
        if self.config.capacity_tracking_enabled:
            reliability.capacity_tracker = ComponentFactory.create_capacity_tracker(node_id)
        
        # Create test node
        node = TestNode(
            node_id=node_id,
            workflow_manager=workflow_manager,
            congestion_detector=congestion_detector,
            load_balancer=load_balancer,
            reliability=reliability
        )
        
        # Configure callbacks
        await self._configure_node_callbacks(node)
        
        self.nodes[node_id] = node
        self.logger.info(f"Created test node {node_id} with all components")
    
    async def _configure_node_callbacks(self, node: TestNode):
        """Configure callbacks for node components."""
        node_id = node.node_id
        
        # Workflow manager callbacks
        node.workflow_manager.set_message_processor(
            lambda msg: self._process_workflow_message(node_id, msg)
        )
        node.workflow_manager.set_completion_callback(
            lambda wf_id: self._on_workflow_completed(node_id, wf_id)
        )
        node.workflow_manager.set_failure_callback(
            lambda wf_id, reason: self._on_workflow_failed(node_id, wf_id, reason)
        )
        
        # Congestion detector callbacks
        node.congestion_detector.set_congestion_callback(
            lambda level, metrics: self._on_congestion_change(node_id, level, metrics)
        )
        
        # Load balancer callbacks
        node.load_balancer.set_capacity_provider(
            lambda target_node: self._get_node_capacity(target_node)
        )
        node.load_balancer.set_health_checker(
            lambda target_node: self._check_node_health(target_node)
        )
        
        # Reliability component callbacks
        if node.reliability.circuit_breaker:
            node.reliability.circuit_breaker.set_state_change_callback(
                lambda target, old_state, new_state: self._on_circuit_state_change(node_id, target, old_state, new_state)
            )
        
        if node.reliability.buffer_monitor:
            node.reliability.buffer_monitor.set_buffer_overflow_callback(
                lambda buffer_id, metrics: self._on_buffer_overflow(node_id, buffer_id, metrics)
            )
        
        if node.reliability.capacity_tracker:
            node.reliability.capacity_tracker.set_capacity_change_callback(
                lambda target, old_state, new_state: self._on_capacity_change(node_id, target, old_state, new_state)
            )
    
    async def _configure_component_integration(self):
        """Configure integration between components."""
        self.logger.info("Configuring component integration")
        
        # Register nodes with each other's load balancers
        for node_id, node in self.nodes.items():
            for other_node_id in self.nodes.keys():
                if other_node_id != node_id:
                    node.load_balancer.register_node(
                        other_node_id,
                        initial_metrics={
                            "cpu_usage": 0.3,
                            "memory_usage": 0.4,
                            "queue_depth": 0,
                            "avg_latency": 50.0,
                            "success_rate": 1.0,
                            "health": "HEALTHY"
                        }
                    )
        
        # Register buffers with buffer monitors
        for node_id, node in self.nodes.items():
            if node.reliability.buffer_monitor:
                # Register standard buffers
                node.reliability.buffer_monitor.register_buffer(
                    f"{node_id}_workflow_queue",
                    BufferType.WORKFLOW_BUFFER,
                    max_size=self.config.max_queue_depth
                )
                node.reliability.buffer_monitor.register_buffer(
                    f"{node_id}_message_queue",
                    BufferType.MESSAGE_QUEUE,
                    max_size=self.config.max_queue_depth * 2
                )
        
        # Register nodes with capacity trackers
        for node_id, node in self.nodes.items():
            if node.reliability.capacity_tracker:
                for other_node_id in self.nodes.keys():
                    node.reliability.capacity_tracker.register_node(other_node_id)
        
        self.logger.info("Component integration configured")
    
    async def _start_all_components(self):
        """Start all components on all nodes."""
        self.logger.info("Starting all components")
        
        for node_id, node in self.nodes.items():
            # Start core components
            await node.workflow_manager.start()
            await node.congestion_detector.start()
            await node.load_balancer.start()
            
            # Start reliability components
            if node.reliability.circuit_breaker:
                await node.reliability.circuit_breaker.start()
            if node.reliability.buffer_monitor:
                await node.reliability.buffer_monitor.start()
            if node.reliability.flow_controller:
                await node.reliability.flow_controller.start()
            if node.reliability.capacity_tracker:
                await node.reliability.capacity_tracker.start()
            
            self.logger.debug(f"Started all components for {node_id}")
        
        # Allow components to initialize
        await asyncio.sleep(3)
        self.logger.info("All components started")
    
    async def _verify_component_health(self) -> int:
        """Verify component health and return number of healthy nodes."""
        healthy_count = 0
        
        for node_id, node in self.nodes.items():
            is_healthy = True
            
            # Check core components
            if not node.workflow_manager._running:
                self.logger.error(f"Node {node_id}: Workflow manager not running")
                is_healthy = False
            
            if not node.congestion_detector._running:
                self.logger.error(f"Node {node_id}: Congestion detector not running")
                is_healthy = False
            
            if not node.load_balancer._running:
                self.logger.error(f"Node {node_id}: Load balancer not running")
                is_healthy = False
            
            # Check reliability components
            # Replace this line:
            #if node.reliability.circuit_breaker and node.reliability.circuit_breaker.get_state() == CircuitState.OPEN:
            # With this:
            if node.reliability.circuit_breaker and hasattr(node.reliability.circuit_breaker, 'state') and node.reliability.circuit_breaker.state == CircuitState.OPEN:
                self.logger.warning(f"Node {node_id}: Circuit breaker is open")
            
            if node.reliability.buffer_monitor and not node.reliability.buffer_monitor._running:
                self.logger.error(f"Node {node_id}: Buffer monitor not running")
                is_healthy = False
            
            if node.reliability.flow_controller and not node.reliability.flow_controller._running:
                self.logger.error(f"Node {node_id}: Flow controller not running")
                is_healthy = False
            
            if node.reliability.capacity_tracker and not node.reliability.capacity_tracker._running:
                self.logger.error(f"Node {node_id}: Capacity tracker not running")
                is_healthy = False
            
            if is_healthy:
                healthy_count += 1
                self.logger.debug(f"Node {node_id}: All components healthy")
            else:
                self.logger.error(f"Node {node_id}: Component health issues detected")
        
        return healthy_count
    
    async def _test_basic_functionality(self) -> bool:
        """Test basic functionality of all components."""
        self.logger.info("PHASE 2: Basic Functionality Testing")
        
        try:
            # Test workflow creation and processing
            node = self.nodes["node_1"]
            workflow_id = node.workflow_manager.create_workflow(
                trace_id="basic_test_001",
                consistency_model=ConsistencyModel.EVENTUAL
            )
            self.test_workflows.append(workflow_id)
            self.stats["workflows_created"] += 1
            
            # Add messages to workflow
            for i in range(5):
                message_id = f"basic_msg_{workflow_id}_{i}"
                success = await node.workflow_manager.add_message_to_workflow(
                    workflow_id=workflow_id,
                    message_id=message_id,
                    sequence_number=i,
                    payload={"data": f"basic_test_{i}", "size": 256}
                )
                if success:
                    self.test_messages.append(message_id)
            
            # Wait for processing
            await asyncio.sleep(5)
            
            # Verify workflow status
            status = node.workflow_manager.get_workflow_status(workflow_id)
            if status and status["progress"]["completed"] >= 3:
                self.logger.info("[OK] Basic workflow functionality working")
                return True
            else:
                self.logger.error("[FAIL] Basic workflow functionality failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Basic functionality test failed: {e}")
            return False
    
    async def _test_load_balancing(self) -> bool:
        """Test load balancing functionality."""
        self.logger.info("PHASE 3: Load Balancing Testing")
        
        try:
            # Create workflows with load balancing
            source_node = self.nodes["node_1"]
            routing_decisions = []
            
            for i in range(10):
                target_node_id = source_node.load_balancer.route_message(
                    message_type="LOAD_BALANCE_TEST",
                    workflow_id=f"lb_workflow_{i}"
                )
                routing_decisions.append(target_node_id)
            
            # Verify load distribution
            unique_targets = set(routing_decisions)
            if len(unique_targets) >= 2:  # At least 2 different targets
                self.logger.info(f"[OK] Load balancing working - {len(unique_targets)} targets used")
                return True
            else:
                self.logger.warning(f"[PARTIAL] Load balancing limited - only {len(unique_targets)} targets used")
                return False
                
        except Exception as e:
            self.logger.error(f"Load balancing test failed: {e}")
            return False
    
    async def _test_circuit_breaker(self) -> bool:
        """Test circuit breaker functionality."""
        self.logger.info("PHASE 4: Circuit Breaker Testing")
        
        try:
            node = self.nodes["node_1"]
            if not node.reliability.circuit_breaker:
                self.logger.warning("Circuit breaker not enabled - skipping test")
                return True
            
            circuit = node.reliability.circuit_breaker
            # Replace:
            #initial_state = circuit.get_state()
            # With:
            initial_state = circuit.state
            
            # Simulate failures to trip circuit breaker
            for i in range(6):  # Exceed failure threshold
                try:
                    await circuit.call(self._simulate_failing_operation)
                except Exception:
                    pass  # Expected failures
            
            # Check if circuit opened
            # Replace:
            #if circuit.get_state() == CircuitState.OPEN:
            # With:
            if circuit.state == CircuitState.OPEN:
                self.logger.info("[OK] Circuit breaker opened after failures")
                self.stats["circuit_trips"] += 1
                return True
            else:
                self.logger.warning("[PARTIAL] Circuit breaker did not open as expected")
                return False
                
        except Exception as e:
            self.logger.error(f"Circuit breaker test failed: {e}")
            return False
    
    async def _test_buffer_management(self) -> bool:
        """Test buffer management functionality."""
        self.logger.info("PHASE 5: Buffer Management Testing")
        
        try:
            node = self.nodes["node_1"]
            if not node.reliability.buffer_monitor:
                self.logger.warning("Buffer monitor not enabled - skipping test")
                return True
            
            buffer_monitor = node.reliability.buffer_monitor
            buffer_id = f"{node.node_id}_test_buffer"
            
            # Register a small buffer for testing
            buffer_monitor.register_buffer(
                buffer_id,
                BufferType.MESSAGE_QUEUE,
                max_size=10
            )
            
            # Fill buffer beyond capacity
            for i in range(15):
                buffer_monitor.record_buffer_add(buffer_id, item_size=128)
            
            # Check buffer status
            status = buffer_monitor.get_buffer_status(buffer_id)
            if status and status["state"] == "OVERFLOW":
                self.logger.info("[OK] Buffer overflow detection working")
                self.stats["buffer_overflows"] += 1
                return True
            else:
                self.logger.warning("[PARTIAL] Buffer overflow not detected")
                return False
                
        except Exception as e:
            self.logger.error(f"Buffer management test failed: {e}")
            return False
    
    async def _test_flow_control(self) -> bool:
        """Test flow control functionality."""
        self.logger.info("PHASE 6: Flow Control Testing")
        
        try:
            node = self.nodes["node_1"]
            if not node.reliability.flow_controller:
                self.logger.warning("Flow controller not enabled - skipping test")
                return True
            
            flow_controller = node.reliability.flow_controller
            
            # Request flow control tickets
            tickets_granted = 0
            for i in range(20):  # Try to exceed credit limit
                ticket = await flow_controller.request_flow_control(
                    target_node="node_2",
                    priority="normal"
                )
                if ticket:
                    tickets_granted += 1
                    await flow_controller.consume_flow_ticket(ticket)
                else:
                    break
            
            if tickets_granted < 20:  # Some requests were throttled
                self.logger.info(f"[OK] Flow control working - {tickets_granted}/20 tickets granted")
                self.stats["flow_throttles"] += (20 - tickets_granted)
                return True
            else:
                self.logger.warning("[PARTIAL] Flow control may not be limiting properly")
                return False
                
        except Exception as e:
            self.logger.error(f"Flow control test failed: {e}")
            return False
    
    async def _test_capacity_tracking(self) -> bool:
        """Test capacity tracking functionality."""
        self.logger.info("PHASE 7: Capacity Tracking Testing")
        
        try:
            node = self.nodes["node_1"]
            if not node.reliability.capacity_tracker:
                self.logger.warning("Capacity tracker not enabled - skipping test")
                return True
            
            tracker = node.reliability.capacity_tracker
            
            # Update capacity metrics to trigger warnings
            tracker.update_node_capacity("node_2", MetricType.CPU_USAGE, 90.0, 100.0)
            tracker.update_node_capacity("node_2", MetricType.MEMORY_USAGE, 85.0, 100.0)
            
            # Check capacity status
            capacity = tracker.get_node_capacity("node_2")
            if capacity and capacity.get_overall_state() in [CapacityState.HIGH, CapacityState.CRITICAL]:
                self.logger.info("[OK] Capacity tracking detecting high utilization")
                self.stats["capacity_warnings"] += 1
                return True
            else:
                self.logger.warning("[PARTIAL] Capacity tracking not detecting high utilization")
                return False
                
        except Exception as e:
            self.logger.error(f"Capacity tracking test failed: {e}")
            return False
    
    async def _test_integration_scenarios(self) -> bool:
        """Test integration scenarios between components."""
        self.logger.info("PHASE 8: Integration Scenarios Testing")
        
        try:
            # Create workflows across multiple nodes with all components active
            workflows_created = 0
            for i in range(6):
                node_id = f"node_{(i % len(self.nodes)) + 1}"
                node = self.nodes[node_id]
                
                workflow_id = node.workflow_manager.create_workflow(
                    trace_id=f"integration_test_{i}",
                    consistency_model=ConsistencyModel.EVENTUAL
                )
                self.test_workflows.append(workflow_id)
                workflows_created += 1
                
                # Add messages with various priorities
                for j in range(3):
                    message_id = f"integration_msg_{workflow_id}_{j}"
                    await node.workflow_manager.add_message_to_workflow(
                        workflow_id=workflow_id,
                        message_id=message_id,
                        sequence_number=j,
                        payload={"data": f"integration_data_{i}_{j}", "priority": "normal"}
                    )
                    self.test_messages.append(message_id)
            
            # Wait for processing
            await asyncio.sleep(8)
            
            # Check overall system health
            healthy_nodes = await self._verify_component_health()
            if healthy_nodes >= len(self.nodes) * 0.8:  # 80% of nodes healthy
                self.logger.info(f"[OK] Integration scenarios completed - {healthy_nodes}/{len(self.nodes)} nodes healthy")
                return True
            else:
                self.logger.warning(f"[PARTIAL] Integration scenarios - only {healthy_nodes}/{len(self.nodes)} nodes healthy")
                return False
                
        except Exception as e:
            self.logger.error(f"Integration scenarios test failed: {e}")
            return False
    
    async def _test_failure_recovery(self) -> bool:
        """Test failure injection and recovery."""
        self.logger.info("PHASE 9: Failure Recovery Testing")
        
        try:
            # Simulate node failure
            failed_node = self.nodes["node_2"]
            
            # Stop some components to simulate partial failure
            await failed_node.congestion_detector.stop()
            
            # Update load balancer to mark node as unhealthy
            for node_id, node in self.nodes.items():
                if node_id != "node_2":
                    node.load_balancer.update_node_metrics("node_2", {
                        "health": "UNAVAILABLE",
                        "success_rate": 0.0
                    })
            
            # Test routing avoids failed node
            healthy_node = self.nodes["node_1"]
            avoided_failed_node = 0
            for i in range(10):
                target = healthy_node.load_balancer.route_message(
                    message_type="RECOVERY_TEST",
                    workflow_id=f"recovery_test_{i}"
                )
                if target != "node_2":
                    avoided_failed_node += 1
            
            # Simulate recovery
            await failed_node.congestion_detector.start()
            
            # Update load balancer to mark node as healthy again
            for node_id, node in self.nodes.items():
                if node_id != "node_2":
                    node.load_balancer.update_node_metrics("node_2", {
                        "health": "HEALTHY",
                        "success_rate": 1.0
                    })
            
            if avoided_failed_node >= 7:  # 70% avoided failed node
                self.logger.info(f"[OK] Failure recovery working - {avoided_failed_node}/10 routes avoided failed node")
                return True
            else:
                self.logger.warning(f"[PARTIAL] Failure recovery - only {avoided_failed_node}/10 routes avoided failed node")
                return False
                
        except Exception as e:
            self.logger.error(f"Failure recovery test failed: {e}")
            return False
    
    async def _test_performance(self) -> bool:
        """Test performance under load."""
        self.logger.info("PHASE 10: Performance Testing")
        
        try:
            start_time = time.time()
            
            # Create multiple workflows simultaneously
            performance_workflows = []
            for i in range(15):  # Higher load
                node_id = f"node_{(i % len(self.nodes)) + 1}"
                node = self.nodes[node_id]
                
                workflow_id = node.workflow_manager.create_workflow(
                    trace_id=f"perf_test_{i}",
                    consistency_model=ConsistencyModel.EVENTUAL
                )
                performance_workflows.append(workflow_id)
                
                # Add messages quickly
                for j in range(4):
                    message_id = f"perf_msg_{workflow_id}_{j}"
                    await node.workflow_manager.add_message_to_workflow(
                        workflow_id=workflow_id,
                        message_id=message_id,
                        sequence_number=j,
                        payload={"data": f"perf_data_{i}_{j}", "timestamp": time.time()}
                    )
            
            # Wait for processing
            await asyncio.sleep(10)
            
            # Calculate performance metrics
            end_time = time.time()
            duration = end_time - start_time
            throughput = len(performance_workflows) / duration
            
            # Check system stability
            healthy_nodes = await self._verify_component_health()
            
            if throughput >= 1.0 and healthy_nodes >= len(self.nodes) * 0.8:
                self.logger.info(f"[OK] Performance test passed - {throughput:.1f} workflows/sec, {healthy_nodes}/{len(self.nodes)} nodes healthy")
                return True
            else:
                self.logger.warning(f"[PARTIAL] Performance test - {throughput:.1f} workflows/sec, {healthy_nodes}/{len(self.nodes)} nodes healthy")
                return False
                
        except Exception as e:
            self.logger.error(f"Performance test failed: {e}")
            return False
    
    async def _generate_comprehensive_report(self):
        """Generate comprehensive test report."""
        self.logger.info("Generating comprehensive test report")
        
        total_duration = time.time() - self.start_time
        passed_phases = sum(1 for result in self.phase_results.values() if result)
        total_phases = len(self.phase_results)
        
        report = {
            "test_metadata": {
                "test_name": "Phase 2 Comprehensive Integration Test",
                "timestamp": time.time(),
                "duration": total_duration,
                "configuration": {
                    "num_nodes": self.config.num_nodes,
                    "num_workflows": self.config.num_workflows,
                    "messages_per_workflow": self.config.messages_per_workflow,
                    "components_enabled": {
                        "circuit_breaker": self.config.circuit_breaker_enabled,
                        "buffer_monitoring": self.config.buffer_monitoring_enabled,
                        "flow_control": self.config.flow_control_enabled,
                        "capacity_tracking": self.config.capacity_tracking_enabled
                    }
                }
            },
            "test_results": {
                "overall_success": passed_phases >= total_phases * 0.8,
                "phases_passed": passed_phases,
                "phases_total": total_phases,
                "success_rate": passed_phases / total_phases if total_phases > 0 else 0,
                "phase_results": self.phase_results
            },
            "statistics": self.stats,
            "node_health": {}
        }
        
        # Collect node health information
        for node_id, node in self.nodes.items():
            report["node_health"][node_id] = {
                "health_score": node.get_health_score(),
                "cpu_usage": node.cpu_usage,
                "memory_usage": node.memory_usage,
                "queue_depth": node.queue_depth,
                "success_rate": node.success_rate,
                "processed_messages": len(node.processed_messages),
                "failed_messages": len(node.failed_messages)
            }
        
        # Save report
        with open('phase2_comprehensive_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Log summary
        self.logger.info("=" * 60)
        self.logger.info("TEST REPORT SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Duration: {total_duration:.2f} seconds")
        self.logger.info(f"Phases: {passed_phases}/{total_phases} passed ({passed_phases/total_phases:.1%})")
        self.logger.info(f"Workflows: {self.stats['workflows_created']} created, {self.stats['workflows_completed']} completed")
        self.logger.info(f"Messages: {len(self.test_messages)} total, {self.stats['messages_processed']} processed")
        self.logger.info(f"Reliability Events: {self.stats['circuit_trips']} circuit trips, {self.stats['buffer_overflows']} buffer overflows")
        self.logger.info("=" * 60)
    
    async def cleanup_test_environment(self):
        """Clean up test environment."""
        self.logger.info("Cleaning up test environment")
        
        for node_id, node in self.nodes.items():
            try:
                # Stop core components
                await node.workflow_manager.stop()
                await node.congestion_detector.stop()
                await node.load_balancer.stop()
                
                # Stop reliability components
                if node.reliability.circuit_breaker:
                    await node.reliability.circuit_breaker.stop()
                if node.reliability.buffer_monitor:
                    await node.reliability.buffer_monitor.stop()
                if node.reliability.flow_controller:
                    await node.reliability.flow_controller.stop()
                if node.reliability.capacity_tracker:
                    await node.reliability.capacity_tracker.stop()
                
            except Exception as e:
                self.logger.error(f"Error cleaning up {node_id}: {e}")
        
        self.logger.info("Test environment cleanup completed")
    
    # Callback methods
    
    async def _process_workflow_message(self, node_id: str, message: WorkflowMessage) -> None:
        """Process a workflow message."""
        start_time = time.time()
        
        try:
            # Simulate processing time
            processing_time = random.uniform(0.1, 0.5)
            await asyncio.sleep(processing_time)
            
            # Update node metrics
            node = self.nodes[node_id]
            node.update_performance_metric("message_latency", time.time() - start_time)
            
            # Simulate occasional failures (low rate)
            if random.random() < 0.02:  # 2% failure rate
                self.stats["messages_failed"] += 1
                node.failed_messages.append(message.message_id)
                raise Exception(f"Simulated processing failure for {message.message_id}")
            
            # Record successful processing
            node.processed_messages.append(message.message_id)
            self.stats["messages_processed"] += 1
            
        except Exception as e:
            self.logger.debug(f"Message processing failed: {e}")
            raise
    
    def _on_workflow_completed(self, node_id: str, workflow_id: str):
        """Handle workflow completion."""
        self.stats["workflows_completed"] += 1
        self.logger.debug(f"Workflow {workflow_id} completed on {node_id}")
    
    def _on_workflow_failed(self, node_id: str, workflow_id: str, reason: str):
        """Handle workflow failure."""
        self.logger.warning(f"Workflow {workflow_id} failed on {node_id}: {reason}")
    
    def _on_congestion_change(self, node_id: str, level, metrics):
        """Handle congestion level changes."""
        self.logger.info(f"Congestion change on {node_id}: {level.name}")
    
    def _on_circuit_state_change(self, node_id: str, target: str, old_state, new_state):
        """Handle circuit breaker state changes."""
        self.logger.info(f"Circuit breaker {node_id}->{target}: {old_state.name} -> {new_state.name}")
        if new_state == CircuitState.OPEN:
            self.stats["circuit_trips"] += 1
    
    def _on_buffer_overflow(self, node_id: str, buffer_id: str, metrics):
        """Handle buffer overflow events."""
        self.logger.warning(f"Buffer overflow on {node_id}: {buffer_id}")
        self.stats["buffer_overflows"] += 1
    
    def _on_capacity_change(self, node_id: str, target: str, old_state, new_state):
        """Handle capacity state changes."""
        self.logger.info(f"Capacity change {node_id}->{target}: {old_state.name} -> {new_state.name}")
        if new_state in [CapacityState.HIGH, CapacityState.CRITICAL]:
            self.stats["capacity_warnings"] += 1
    
    def _get_node_capacity(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node capacity metrics."""
        if node_id not in self.nodes:
            return None
        
        node = self.nodes[node_id]
        return {
            "cpu_usage": node.cpu_usage,
            "memory_usage": node.memory_usage,
            "queue_depth": node.queue_depth,
            "avg_latency": node.avg_latency,
            "success_rate": node.success_rate,
            "health_score": node.get_health_score()
        }
    
    def _check_node_health(self, node_id: str) -> bool:
        """Check node health."""
        if node_id not in self.nodes:
            return False
        
        node = self.nodes[node_id]
        return node.get_health_score() > 0.7  # 70% health threshold
    
    async def _simulate_failing_operation(self):
        """Simulate an operation that fails."""
        await asyncio.sleep(0.1)
        raise Exception("Simulated operation failure")


@asynccontextmanager
async def comprehensive_test_context(config: Optional[TestConfiguration] = None):
    """Context manager for comprehensive test."""
    test = Phase2ComprehensiveTest(config)
    try:
        yield test
    finally:
        await test.cleanup_test_environment()


async def main():
    """Main test execution function."""
    setup_logging()
    logger = logging.getLogger("phase2_test")
    
    logger.info("Starting Phase 2 Comprehensive Integration Test")
    
    # Create test configuration
    config = TestConfiguration(
        num_nodes=4,
        num_workflows=8,
        messages_per_workflow=6,
        stress_test_enabled=True,
        performance_benchmarking=True,
        failure_injection_enabled=True
    )
    
    start_time = time.time()
    success = False
    
    try:
        async with comprehensive_test_context(config) as test:
            success = await test.run_comprehensive_test()
        
        elapsed_time = time.time() - start_time
        
        if success:
            logger.info(f"TEST COMPLETED SUCCESSFULLY in {elapsed_time:.2f} seconds")
            logger.info("Check phase2_comprehensive_report.json for detailed results")
        else:
            logger.error(f"TEST FAILED after {elapsed_time:.2f} seconds")
            logger.error("Check logs and report for failure details")
        
    except Exception as e:
        logger.error(f"Critical test failure: {e}")
        logger.error(traceback.format_exc())
        success = False
    
    return success


if __name__ == "__main__":
    """Run the Phase 2 comprehensive integration test."""
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
