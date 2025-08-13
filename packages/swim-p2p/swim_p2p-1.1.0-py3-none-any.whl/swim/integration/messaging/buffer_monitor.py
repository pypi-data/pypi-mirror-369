"""
Buffer monitoring and management system for SWIM-ZMQ integration.

Provides comprehensive buffer monitoring, memory management, and overflow
protection to ensure system stability and prevent memory exhaustion.
"""

import asyncio
import time
import logging
import psutil
import gc
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque, defaultdict
import threading
import weakref

logger = logging.getLogger(__name__)


class BufferState(Enum):
    """Buffer states for monitoring."""
    NORMAL = auto()         # Normal operation
    WARNING = auto()        # Approaching limits
    CRITICAL = auto()       # Critical levels
    OVERFLOW = auto()       # Buffer overflow condition
    EMERGENCY = auto()      # Emergency cleanup needed


class BufferType(Enum):
    """Types of buffers being monitored."""
    MESSAGE_QUEUE = auto()      # Message queues
    SEND_BUFFER = auto()        # Send buffers
    RECEIVE_BUFFER = auto()     # Receive buffers
    WORKFLOW_BUFFER = auto()    # Workflow message buffers
    CIRCUIT_BUFFER = auto()     # Circuit breaker buffers
    GENERAL_MEMORY = auto()     # General memory usage


@dataclass
class BufferMetrics:
    """Metrics for a specific buffer."""
    buffer_type: BufferType
    buffer_id: str
    max_size: int = 1000
    current_size: int = 0
    peak_size: int = 0
    total_items_added: int = 0
    total_items_removed: int = 0
    total_overflows: int = 0
    last_updated: float = field(default_factory=time.time)
    
    # Memory metrics
    memory_usage_bytes: int = 0
    estimated_item_size: int = 0
    
    # Performance metrics
    avg_processing_time: float = 0.0
    processing_times: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def update_size(self, new_size: int):
        """Update buffer size and related metrics."""
        self.current_size = new_size
        self.peak_size = max(self.peak_size, new_size)
        self.last_updated = time.time()
    
    def add_item(self, item_size: int = 0):
        """Record item addition."""
        self.current_size += 1
        self.total_items_added += 1
        self.peak_size = max(self.peak_size, self.current_size)
        
        if item_size > 0:
            self.memory_usage_bytes += item_size
            # Update estimated item size (running average)
            if self.total_items_added > 0:
                self.estimated_item_size = int(
                    (self.estimated_item_size * 0.9) + (item_size * 0.1)
                )
        
        # Check for overflow
        if self.current_size > self.max_size:
            self.total_overflows += 1
        
        self.last_updated = time.time()
    
    def remove_item(self, item_size: int = 0, processing_time: float = 0.0):
        """Record item removal."""
        if self.current_size > 0:
            self.current_size -= 1
            self.total_items_removed += 1
            
            if item_size > 0:
                self.memory_usage_bytes = max(0, self.memory_usage_bytes - item_size)
            
            if processing_time > 0:
                self.processing_times.append(processing_time)
                if self.processing_times:
                    self.avg_processing_time = sum(self.processing_times) / len(self.processing_times)
        
        self.last_updated = time.time()
    
    def get_utilization(self) -> float:
        """Get buffer utilization (0.0 to 1.0)."""
        if self.max_size <= 0:
            return 0.0
        return min(1.0, self.current_size / self.max_size)
    
    def get_state(self) -> BufferState:
        """Get buffer state based on utilization."""
        utilization = self.get_utilization()
        
        if utilization >= 1.0:
            return BufferState.OVERFLOW
        elif utilization >= 0.9:
            return BufferState.CRITICAL
        elif utilization >= 0.75:
            return BufferState.WARNING
        else:
            return BufferState.NORMAL
    
    def get_throughput(self, window_seconds: float = 60.0) -> float:
        """Get items per second throughput."""
        if window_seconds <= 0:
            return 0.0
        
        # Simple approximation based on recent activity
        recent_items = min(self.total_items_removed, 100)  # Last 100 items
        return recent_items / window_seconds
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive buffer status."""
        return {
            "buffer_type": self.buffer_type.name,
            "buffer_id": self.buffer_id,
            "state": self.get_state().name,
            "current_size": self.current_size,
            "max_size": self.max_size,
            "utilization": self.get_utilization(),
            "peak_size": self.peak_size,
            "memory_usage_mb": self.memory_usage_bytes / (1024 * 1024),
            "estimated_item_size": self.estimated_item_size,
            "avg_processing_time": self.avg_processing_time,
            "throughput": self.get_throughput(),
            "statistics": {
                "total_added": self.total_items_added,
                "total_removed": self.total_items_removed,
                "total_overflows": self.total_overflows,
                "last_updated": self.last_updated
            }
        }


class SystemMemoryMonitor:
    """System-wide memory monitoring."""
    
    def __init__(self):
        """Initialize system memory monitor."""
        self.process = psutil.Process()
        self.memory_history: deque = deque(maxlen=100)
        self.gc_stats = {"collections": 0, "freed_objects": 0}
        
    def get_memory_info(self) -> Dict[str, Any]:
        """Get current memory information."""
        try:
            # Process memory info
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            # System memory info
            system_memory = psutil.virtual_memory()
            
            # Python GC info
            gc_stats = gc.get_stats()
            
            info = {
                "process_memory_mb": memory_info.rss / (1024 * 1024),
                "process_memory_percent": memory_percent,
                "system_memory_percent": system_memory.percent,
                "system_available_mb": system_memory.available / (1024 * 1024),
                "gc_collections": sum(stat.get("collections", 0) for stat in gc_stats),
                "gc_collected": sum(stat.get("collected", 0) for stat in gc_stats),
                "timestamp": time.time()
            }
            
            self.memory_history.append(info)
            return info
            
        except Exception as e:
            logger.error(f"BUFFER_MONITOR: Error getting memory info: {e}")
            return {}
    
    def get_memory_trend(self, window_seconds: float = 300.0) -> str:
        """Get memory usage trend."""
        if len(self.memory_history) < 2:
            return "STABLE"
        
        cutoff_time = time.time() - window_seconds
        recent_data = [
            data for data in self.memory_history 
            if data.get("timestamp", 0) >= cutoff_time
        ]
        
        if len(recent_data) < 2:
            return "STABLE"
        
        first_half = recent_data[:len(recent_data)//2]
        second_half = recent_data[len(recent_data)//2:]
        
        avg_first = sum(d["process_memory_mb"] for d in first_half) / len(first_half)
        avg_second = sum(d["process_memory_mb"] for d in second_half) / len(second_half)
        
        change_percent = (avg_second - avg_first) / max(avg_first, 1.0)
        
        if change_percent > 0.1:  # 10% increase
            return "INCREASING"
        elif change_percent < -0.1:  # 10% decrease
            return "DECREASING"
        else:
            return "STABLE"
    
    def force_garbage_collection(self) -> Dict[str, int]:
        """Force garbage collection and return statistics."""
        before_objects = len(gc.get_objects())
        
        # Force collection of all generations
        collected = 0
        for generation in range(3):
            collected += gc.collect(generation)
        
        after_objects = len(gc.get_objects())
        freed_objects = before_objects - after_objects
        
        self.gc_stats["collections"] += 1
        self.gc_stats["freed_objects"] += freed_objects
        
        return {
            "collected": collected,
            "freed_objects": freed_objects,
            "remaining_objects": after_objects
        }


class BufferMonitor:
    """
    Comprehensive buffer monitoring and management system.
    
    Monitors various types of buffers, provides overflow protection, and
    implements automatic cleanup strategies to maintain system stability.
    """
    
    def __init__(self, node_id: str):
        """
        Initialize buffer monitor.
        
        Args:
            node_id: Identifier for this node
        """
        self.node_id = node_id
        self.buffers: Dict[str, BufferMetrics] = {}
        self.system_monitor = SystemMemoryMonitor()
        
        # Configuration
        self.monitoring_interval = 5.0  # seconds
        self.cleanup_interval = 30.0    # seconds
        self.emergency_threshold = 0.95  # 95% memory usage
        self.warning_threshold = 0.8     # 80% memory usage
        
        # Emergency settings
        self.emergency_mode = False
        self.auto_cleanup_enabled = True
        self.max_buffer_age = 300.0  # 5 minutes
        
        # Callbacks
        self.buffer_overflow_callback: Optional[Callable] = None
        self.memory_warning_callback: Optional[Callable] = None
        self.emergency_callback: Optional[Callable] = None
        self.cleanup_callback: Optional[Callable] = None
        
        # Background tasks
        self._running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            "buffers_monitored": 0,
            "total_overflows": 0,
            "emergency_cleanups": 0,
            "memory_warnings": 0,
            "gc_collections": 0
        }
        
        # Buffer registry for weak references
        self._buffer_registry: Dict[str, weakref.ref] = {}
        self._lock = threading.RLock()
        
        logger.info(f"BUFFER_MONITOR: Initialized for node {node_id}")
    
    def set_buffer_overflow_callback(self, callback: Callable[[str, BufferMetrics], None]):
        """Set callback for buffer overflow events."""
        self.buffer_overflow_callback = callback
    
    def set_memory_warning_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set callback for memory warning events."""
        self.memory_warning_callback = callback
    
    def set_emergency_callback(self, callback: Callable[[str], None]):
        """Set callback for emergency situations."""
        self.emergency_callback = callback
    
    def set_cleanup_callback(self, callback: Callable[[List[str]], None]):
        """Set callback for cleanup operations."""
        self.cleanup_callback = callback
    
    async def start(self):
        """Start buffer monitoring."""
        if self._running:
            return
        
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("BUFFER_MONITOR: Started monitoring")
    
    async def stop(self):
        """Stop buffer monitoring."""
        self._running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("BUFFER_MONITOR: Stopped monitoring")
    
    def register_buffer(self, buffer_id: str, buffer_type: BufferType, 
                       max_size: int = 1000, buffer_ref: Any = None) -> BufferMetrics:
        """
        Register a buffer for monitoring.
        
        Args:
            buffer_id: Unique buffer identifier
            buffer_type: Type of buffer
            max_size: Maximum buffer size
            buffer_ref: Optional weak reference to actual buffer
            
        Returns:
            BufferMetrics object for tracking
        """
        with self._lock:
            if buffer_id in self.buffers:
                logger.warning(f"BUFFER_MONITOR: Buffer {buffer_id} already registered")
                return self.buffers[buffer_id]
            
            metrics = BufferMetrics(
                buffer_type=buffer_type,
                buffer_id=buffer_id,
                max_size=max_size
            )
            
            self.buffers[buffer_id] = metrics
            
            # Store weak reference if provided
            if buffer_ref is not None:
                self._buffer_registry[buffer_id] = weakref.ref(buffer_ref)
            
            self.stats["buffers_monitored"] += 1
            logger.info(f"BUFFER_MONITOR: Registered buffer {buffer_id} "
                       f"({buffer_type.name}, max_size={max_size})")
            
            return metrics
    
    def unregister_buffer(self, buffer_id: str):
        """
        Unregister a buffer from monitoring.
        
        Args:
            buffer_id: Buffer identifier
        """
        with self._lock:
            if buffer_id in self.buffers:
                del self.buffers[buffer_id]
                self.stats["buffers_monitored"] -= 1
                
                if buffer_id in self._buffer_registry:
                    del self._buffer_registry[buffer_id]
                
                logger.info(f"BUFFER_MONITOR: Unregistered buffer {buffer_id}")
    
    def update_buffer_size(self, buffer_id: str, new_size: int, item_size: int = 0):
        """
        Update buffer size.
        
        Args:
            buffer_id: Buffer identifier
            new_size: New buffer size
            item_size: Size of items in bytes (optional)
        """
        with self._lock:
            if buffer_id not in self.buffers:
                logger.warning(f"BUFFER_MONITOR: Unknown buffer {buffer_id}")
                return
            
            metrics = self.buffers[buffer_id]
            old_state = metrics.get_state()
            
            metrics.update_size(new_size)
            
            if item_size > 0:
                metrics.memory_usage_bytes = new_size * item_size
                metrics.estimated_item_size = item_size
            
            new_state = metrics.get_state()
            
            # Check for state changes
            if old_state != new_state:
                self._handle_buffer_state_change(buffer_id, metrics, old_state, new_state)
    
    def record_buffer_add(self, buffer_id: str, item_size: int = 0):
        """
        Record item addition to buffer.
        
        Args:
            buffer_id: Buffer identifier
            item_size: Size of added item in bytes
        """
        with self._lock:
            if buffer_id not in self.buffers:
                return
            
            metrics = self.buffers[buffer_id]
            old_state = metrics.get_state()
            
            metrics.add_item(item_size)
            
            new_state = metrics.get_state()
            if old_state != new_state:
                self._handle_buffer_state_change(buffer_id, metrics, old_state, new_state)
    
    def record_buffer_remove(self, buffer_id: str, item_size: int = 0, processing_time: float = 0.0):
        """
        Record item removal from buffer.
        
        Args:
            buffer_id: Buffer identifier
            item_size: Size of removed item in bytes
            processing_time: Time taken to process item
        """
        with self._lock:
            if buffer_id not in self.buffers:
                return
            
            metrics = self.buffers[buffer_id]
            old_state = metrics.get_state()
            
            metrics.remove_item(item_size, processing_time)
            
            new_state = metrics.get_state()
            if old_state != new_state:
                self._handle_buffer_state_change(buffer_id, metrics, old_state, new_state)
    
    def _handle_buffer_state_change(self, buffer_id: str, metrics: BufferMetrics,
                                   old_state: BufferState, new_state: BufferState):
        """Handle buffer state changes."""
        logger.info(f"BUFFER_STATE_CHANGE: {buffer_id} {old_state.name} -> {new_state.name}")
        
        # Handle overflow
        if new_state == BufferState.OVERFLOW:
            self.stats["total_overflows"] += 1
            
            if self.buffer_overflow_callback:
                try:
                    self.buffer_overflow_callback(buffer_id, metrics)
                except Exception as e:
                    logger.error(f"BUFFER_MONITOR: Error in overflow callback: {e}")
            
            # Trigger emergency cleanup if enabled
            if self.auto_cleanup_enabled:
                asyncio.create_task(self._emergency_buffer_cleanup(buffer_id))
        
        # Handle critical state
        elif new_state == BufferState.CRITICAL:
            logger.warning(f"BUFFER_MONITOR: Buffer {buffer_id} in critical state")
    
    async def _emergency_buffer_cleanup(self, buffer_id: str):
        """Perform emergency cleanup on a specific buffer."""
        try:
            logger.warning(f"BUFFER_MONITOR: Emergency cleanup for buffer {buffer_id}")
            
            # Get buffer reference if available
            if buffer_id in self._buffer_registry:
                buffer_ref = self._buffer_registry[buffer_id]()
                if buffer_ref and hasattr(buffer_ref, 'clear'):
                    # Clear the buffer if possible
                    buffer_ref.clear()
                    logger.info(f"BUFFER_MONITOR: Cleared buffer {buffer_id}")
            
            # Update metrics
            if buffer_id in self.buffers:
                self.buffers[buffer_id].current_size = 0
                self.buffers[buffer_id].memory_usage_bytes = 0
            
            self.stats["emergency_cleanups"] += 1
            
            if self.emergency_callback:
                try:
                    self.emergency_callback(f"Emergency cleanup performed on buffer {buffer_id}")
                except Exception as e:
                    logger.error(f"BUFFER_MONITOR: Error in emergency callback: {e}")
                    
        except Exception as e:
            logger.error(f"BUFFER_MONITOR: Error in emergency cleanup: {e}")
    
    def get_buffer_status(self, buffer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific buffer.
        
        Args:
            buffer_id: Buffer identifier
            
        Returns:
            Buffer status dictionary or None if not found
        """
        with self._lock:
            if buffer_id in self.buffers:
                return self.buffers[buffer_id].get_status()
            return None
    
    def get_all_buffer_status(self) -> Dict[str, Any]:
        """Get status of all monitored buffers."""
        with self._lock:
            buffer_status = {}
            state_distribution = defaultdict(int)
            total_memory_mb = 0.0
            
            for buffer_id, metrics in self.buffers.items():
                status = metrics.get_status()
                buffer_status[buffer_id] = status
                
                state_distribution[status["state"]] += 1
                total_memory_mb += status["memory_usage_mb"]
            
            # Get system memory info
            system_memory = self.system_monitor.get_memory_info()
            memory_trend = self.system_monitor.get_memory_trend()
            
            return {
                "monitor_node_id": self.node_id,
                "emergency_mode": self.emergency_mode,
                "total_buffers": len(self.buffers),
                "total_memory_mb": total_memory_mb,
                "state_distribution": dict(state_distribution),
                "system_memory": system_memory,
                "memory_trend": memory_trend,
                "statistics": self.stats.copy(),
                "buffers": buffer_status
            }
    
    def get_memory_pressure(self) -> float:
        """Get current memory pressure (0.0 = low, 1.0 = high)."""
        system_info = self.system_monitor.get_memory_info()
        
        if not system_info:
            return 0.0
        
        # Combine system and process memory usage
        system_pressure = system_info.get("system_memory_percent", 0) / 100.0
        process_pressure = min(1.0, system_info.get("process_memory_percent", 0) / 50.0)  # 50% is high
        
        return max(system_pressure, process_pressure)
    
    def force_cleanup(self, buffer_types: Optional[List[BufferType]] = None) -> Dict[str, int]:
        """
        Force cleanup of buffers.
        
        Args:
            buffer_types: Optional list of buffer types to clean up
            
        Returns:
            Dictionary with cleanup statistics
        """
        cleanup_stats = {"buffers_cleaned": 0, "items_removed": 0, "memory_freed_mb": 0}
        
        with self._lock:
            buffers_to_clean = []
            
            for buffer_id, metrics in self.buffers.items():
                if buffer_types is None or metrics.buffer_type in buffer_types:
                    if metrics.get_state() in [BufferState.WARNING, BufferState.CRITICAL, BufferState.OVERFLOW]:
                        buffers_to_clean.append(buffer_id)
            
            # Perform cleanup
            for buffer_id in buffers_to_clean:
                try:
                    # Get buffer reference
                    if buffer_id in self._buffer_registry:
                        buffer_ref = self._buffer_registry[buffer_id]()
                        if buffer_ref and hasattr(buffer_ref, 'clear'):
                            old_size = self.buffers[buffer_id].current_size
                            old_memory = self.buffers[buffer_id].memory_usage_bytes
                            
                            # Clear buffer
                            buffer_ref.clear()
                            
                            # Update metrics
                            self.buffers[buffer_id].current_size = 0
                            self.buffers[buffer_id].memory_usage_bytes = 0
                            
                            cleanup_stats["buffers_cleaned"] += 1
                            cleanup_stats["items_removed"] += old_size
                            cleanup_stats["memory_freed_mb"] += old_memory / (1024 * 1024)
                            
                            logger.info(f"BUFFER_MONITOR: Cleaned buffer {buffer_id} "
                                       f"(removed {old_size} items, freed {old_memory/1024/1024:.1f}MB)")
                
                except Exception as e:
                    logger.error(f"BUFFER_MONITOR: Error cleaning buffer {buffer_id}: {e}")
            
            # Force garbage collection
            gc_stats = self.system_monitor.force_garbage_collection()
            self.stats["gc_collections"] += 1
            
            if self.cleanup_callback:
                try:
                    self.cleanup_callback(buffers_to_clean)
                except Exception as e:
                    logger.error(f"BUFFER_MONITOR: Error in cleanup callback: {e}")
        
        logger.info(f"BUFFER_MONITOR: Force cleanup completed - {cleanup_stats}")
        return cleanup_stats
    
    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while self._running:
            try:
                await asyncio.sleep(self.monitoring_interval)
                await self._perform_monitoring_cycle()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"BUFFER_MONITOR: Error in monitoring loop: {e}")
    
    async def _perform_monitoring_cycle(self):
        """Perform one monitoring cycle."""
        # Check memory pressure
        memory_pressure = self.get_memory_pressure()
        
        # Handle emergency conditions
        if memory_pressure >= self.emergency_threshold:
            if not self.emergency_mode:
                self.emergency_mode = True
                logger.warning(f"BUFFER_MONITOR: Entering emergency mode (pressure: {memory_pressure:.1%})")
                
                # Force cleanup
                await asyncio.get_event_loop().run_in_executor(
                    None, self.force_cleanup
                )
        
        # Handle warning conditions
        elif memory_pressure >= self.warning_threshold:
            if self.emergency_mode:
                self.emergency_mode = False
                logger.info("BUFFER_MONITOR: Exiting emergency mode")
            
            self.stats["memory_warnings"] += 1
            
            if self.memory_warning_callback:
                try:
                    memory_info = self.system_monitor.get_memory_info()
                    self.memory_warning_callback(memory_info)
                except Exception as e:
                    logger.error(f"BUFFER_MONITOR: Error in memory warning callback: {e}")
        
        else:
            if self.emergency_mode:
                self.emergency_mode = False
                logger.info("BUFFER_MONITOR: Exiting emergency mode")
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._perform_routine_cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"BUFFER_MONITOR: Error in cleanup loop: {e}")
    
    async def _perform_routine_cleanup(self):
        """Perform routine cleanup operations."""
        current_time = time.time()
        
        # Clean up stale buffer references
        stale_buffers = []
        
        with self._lock:
            for buffer_id, weak_ref in list(self._buffer_registry.items()):
                if weak_ref() is None:  # Reference has been garbage collected
                    stale_buffers.append(buffer_id)
        
        for buffer_id in stale_buffers:
            self.unregister_buffer(buffer_id)
        
        if stale_buffers:
            logger.debug(f"BUFFER_MONITOR: Cleaned up {len(stale_buffers)} stale buffer references")
        
        # Periodic garbage collection in low memory situations
        memory_pressure = self.get_memory_pressure()
        if memory_pressure > 0.7:  # 70% memory pressure
            await asyncio.get_event_loop().run_in_executor(
                None, self.system_monitor.force_garbage_collection
            )
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get recommendations for buffer optimization."""
        recommendations = []
        
        if not self.buffers:
            return ["No buffers registered for monitoring"]
        
        # Check for overflowing buffers
        overflow_buffers = [
            bid for bid, metrics in self.buffers.items()
            if metrics.get_state() == BufferState.OVERFLOW
        ]
        
        if overflow_buffers:
            recommendations.append(f"{len(overflow_buffers)} buffers are overflowing - "
                                 f"increase buffer sizes or improve processing speed")
        
        # Check memory usage
        total_memory = sum(m.memory_usage_bytes for m in self.buffers.values())
        if total_memory > 100 * 1024 * 1024:  # 100MB
            recommendations.append(f"High buffer memory usage ({total_memory/1024/1024:.1f}MB) - "
                                 f"consider implementing buffer size limits")
        
        # Check processing times
        slow_buffers = [
            bid for bid, metrics in self.buffers.items()
            if metrics.avg_processing_time > 1.0  # 1 second
        ]
        
        if slow_buffers:
            recommendations.append(f"{len(slow_buffers)} buffers have slow processing times - "
                                 f"optimize message processing logic")
        
        # Check memory pressure
        memory_pressure = self.get_memory_pressure()
        if memory_pressure > 0.8:
            recommendations.append(f"High memory pressure ({memory_pressure:.1%}) - "
                                 f"enable more aggressive cleanup or increase system memory")
        
        # Check emergency mode usage
        if self.stats["emergency_cleanups"] > 0:
            recommendations.append("Emergency cleanups have occurred - "
                                 "review buffer sizing and processing capacity")
        
        if not recommendations:
            recommendations.append("Buffer monitoring operating optimally - no issues detected")
        
        return recommendations


# Additional utility functions for integration
def create_buffer_monitor_for_node(node_id: str) -> BufferMonitor:
    """
    Factory function to create a properly configured buffer monitor.
    
    Args:
        node_id: Node identifier
        
    Returns:
        Configured BufferMonitor instance
    """
    monitor = BufferMonitor(node_id)
    
    # Set up default callbacks
    def default_overflow_callback(buffer_id: str, metrics: BufferMetrics):
        logger.error(f"BUFFER_OVERFLOW: {buffer_id} - {metrics.current_size}/{metrics.max_size}")
    
    def default_memory_warning_callback(memory_info: Dict[str, Any]):
        logger.warning(f"MEMORY_WARNING: {memory_info.get('process_memory_percent', 0):.1f}% usage")
    
    def default_emergency_callback(message: str):
        logger.critical(f"BUFFER_EMERGENCY: {message}")
    
    monitor.set_buffer_overflow_callback(default_overflow_callback)
    monitor.set_memory_warning_callback(default_memory_warning_callback)
    monitor.set_emergency_callback(default_emergency_callback)
    
    return monitor


def get_buffer_health_score(monitor: BufferMonitor) -> float:
    """
    Calculate overall buffer health score (0.0 = poor, 1.0 = excellent).
    
    Args:
        monitor: BufferMonitor instance
        
    Returns:
        Health score between 0.0 and 1.0
    """
    status = monitor.get_all_buffer_status()
    
    if not status.get("buffers"):
        return 1.0  # No buffers = perfect health
    
    # Calculate component scores
    memory_score = 1.0 - monitor.get_memory_pressure()
    
    # Buffer state score
    state_dist = status.get("state_distribution", {})
    total_buffers = status.get("total_buffers", 1)
    
    state_weights = {
        "NORMAL": 1.0,
        "WARNING": 0.7,
        "CRITICAL": 0.3,
        "OVERFLOW": 0.0,
        "EMERGENCY": 0.0
    }
    
    buffer_score = sum(
        state_weights.get(state, 0.5) * count 
        for state, count in state_dist.items()
    ) / total_buffers
    
    # Emergency mode penalty
    emergency_penalty = 0.5 if status.get("emergency_mode", False) else 0.0
    
    # Combine scores
    health_score = (memory_score * 0.4 + buffer_score * 0.6) - emergency_penalty
    
    return max(0.0, min(1.0, health_score))
