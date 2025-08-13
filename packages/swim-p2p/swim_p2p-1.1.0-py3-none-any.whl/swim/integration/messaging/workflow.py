"""
Workflow context and ordering management for SWIM-ZMQ integration.

This module provides workflow-aware message processing with ordering guarantees,
dependency tracking, and failure recovery within workflow boundaries.
Supports both strict and eventual consistency models for different use cases.
"""

import asyncio
import time
import uuid
import logging
from typing import Dict, List, Optional, Set, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    """Workflow execution states."""
    PENDING = auto()      # Workflow created, not started
    ACTIVE = auto()       # Workflow executing
    COMPLETED = auto()    # All messages processed successfully
    FAILED = auto()       # Workflow failed, requires intervention
    TIMEOUT = auto()      # Workflow timed out
    CANCELLED = auto()    # Workflow cancelled by user


class ConsistencyModel(Enum):
    """Consistency models for workflow execution."""
    STRICT = auto()       # All messages must be processed in order
    EVENTUAL = auto()     # Messages can be processed out of order
    CAUSAL = auto()       # Only causally related messages must be ordered


@dataclass
class WorkflowMessage:
    """Represents a message within a workflow context."""
    message_id: str
    workflow_id: str
    sequence_number: int
    dependencies: Set[str] = field(default_factory=set)
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    processed_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def is_ready_for_processing(self, completed_messages: Set[str]) -> bool:
        """Check if all dependencies are satisfied."""
        return self.dependencies.issubset(completed_messages)
    
    def can_retry(self) -> bool:
        """Check if message can be retried."""
        return self.retry_count < self.max_retries


@dataclass
class WorkflowContext:
    """Context for managing workflow execution."""
    workflow_id: str
    trace_id: Optional[str] = None
    consistency_model: ConsistencyModel = ConsistencyModel.EVENTUAL
    timeout_seconds: float = 300.0  # 5 minutes default
    created_at: float = field(default_factory=time.time)
    state: WorkflowState = WorkflowState.PENDING
    
    # Message tracking
    messages: Dict[str, WorkflowMessage] = field(default_factory=dict)
    completed_messages: Set[str] = field(default_factory=set)
    failed_messages: Set[str] = field(default_factory=set)
    
    # Execution tracking
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    last_activity: float = field(default_factory=time.time)
    
    def is_expired(self) -> bool:
        """Check if workflow has timed out."""
        if self.state in [WorkflowState.COMPLETED, WorkflowState.FAILED, WorkflowState.CANCELLED]:
            return False
        return time.time() - self.created_at > self.timeout_seconds
    
    def get_ready_messages(self) -> List[WorkflowMessage]:
        """Get messages ready for processing based on dependencies."""
        ready = []
        for msg in self.messages.values():
            if (msg.message_id not in self.completed_messages and 
                msg.message_id not in self.failed_messages and
                msg.is_ready_for_processing(self.completed_messages)):
                ready.append(msg)
        
        # Sort by sequence number for strict consistency
        if self.consistency_model == ConsistencyModel.STRICT:
            ready.sort(key=lambda m: m.sequence_number)
        
        return ready
    
    def get_progress(self) -> Dict[str, Any]:
        """Get workflow progress statistics."""
        total = len(self.messages)
        completed = len(self.completed_messages)
        failed = len(self.failed_messages)
        pending = total - completed - failed
        
        return {
            "total_messages": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "progress_percent": (completed / total * 100) if total > 0 else 0,
            "state": self.state.name,
            "elapsed_time": time.time() - self.created_at,
            "last_activity": self.last_activity
        }


class WorkflowManager:
    """
    Manages workflow contexts and message dependencies.
    
    Provides ordering guarantees within workflow boundaries and supports
    both strict and eventual consistency models for different use cases.
    """
    
    def __init__(self, node_id: str):
        """
        Initialize workflow manager.
        
        Args:
            node_id: Identifier for this node
        """
        self.node_id = node_id
        self.workflows: Dict[str, WorkflowContext] = {}
        self.message_to_workflow: Dict[str, str] = {}
        
        # Configuration
        self.cleanup_interval = 60.0  # Clean up expired workflows every minute
        self.max_workflows = 1000     # Maximum concurrent workflows
        self.default_timeout = 300.0  # Default workflow timeout
        
        # Callbacks
        self.message_processor: Optional[Callable] = None
        self.completion_callback: Optional[Callable] = None
        self.failure_callback: Optional[Callable] = None
        
        # Background tasks
        self._running = False
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Statistics
        self._stats = {
            "workflows_created": 0,
            "workflows_completed": 0,
            "workflows_failed": 0,
            "workflows_timeout": 0,
            "messages_processed": 0,
            "messages_failed": 0
        }
        
        logger.info(f"WORKFLOW_MANAGER: Initialized for node {node_id}")
    
    def set_message_processor(self, processor: Callable[[WorkflowMessage], asyncio.Task]):
        """Set callback for processing workflow messages."""
        self.message_processor = processor
        logger.info("WORKFLOW_MANAGER: Message processor configured")
    
    def set_completion_callback(self, callback: Callable[[str], None]):
        """Set callback for workflow completion events."""
        self.completion_callback = callback
        logger.info("WORKFLOW_MANAGER: Completion callback configured")
    
    def set_failure_callback(self, callback: Callable[[str, str], None]):
        """Set callback for workflow failure events."""
        self.failure_callback = callback
        logger.info("WORKFLOW_MANAGER: Failure callback configured")
    
    async def start(self):
        """Start the workflow manager background tasks."""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("WORKFLOW_MANAGER: Started background cleanup task")
    
    async def stop(self):
        """Stop the workflow manager and clean up resources."""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Cancel any pending workflows
        for workflow_id in list(self.workflows.keys()):
            await self.cancel_workflow(workflow_id)
        
        logger.info("WORKFLOW_MANAGER: Stopped and cleaned up resources")
    
    def create_workflow(
        self,
        workflow_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        consistency_model: ConsistencyModel = ConsistencyModel.EVENTUAL,
        timeout_seconds: Optional[float] = None
    ) -> str:
        """
        Create a new workflow context.
        
        Args:
            workflow_id: Optional workflow identifier (generated if not provided)
            trace_id: Optional trace identifier for correlation
            consistency_model: Consistency model for message processing
            timeout_seconds: Workflow timeout (uses default if not provided)
            
        Returns:
            The workflow identifier
            
        Raises:
            RuntimeError: If maximum workflows exceeded
        """
        if len(self.workflows) >= self.max_workflows:
            raise RuntimeError(f"Maximum workflows ({self.max_workflows}) exceeded")
        
        if workflow_id is None:
            workflow_id = str(uuid.uuid4())
        
        if workflow_id in self.workflows:
            raise ValueError(f"Workflow {workflow_id} already exists")
        
        timeout = timeout_seconds or self.default_timeout
        
        workflow = WorkflowContext(
            workflow_id=workflow_id,
            trace_id=trace_id,
            consistency_model=consistency_model,
            timeout_seconds=timeout
        )
        
        self.workflows[workflow_id] = workflow
        self._stats["workflows_created"] += 1
        
        logger.info(f"WORKFLOW_CREATE: Created workflow {workflow_id} "
                   f"(model: {consistency_model.name}, timeout: {timeout}s)")
        
        return workflow_id
    
    async def add_message_to_workflow(
        self,
        workflow_id: str,
        message_id: str,
        sequence_number: int,
        payload: Dict[str, Any],
        dependencies: Optional[Set[str]] = None,
        max_retries: int = 3
    ) -> bool:
        """
        Add a message to a workflow.
        
        Args:
            workflow_id: Target workflow identifier
            message_id: Unique message identifier
            sequence_number: Message sequence number for ordering
            payload: Message payload data
            dependencies: Set of message IDs this message depends on
            max_retries: Maximum retry attempts for this message
            
        Returns:
            True if message was added successfully
        """
        if workflow_id not in self.workflows:
            logger.error(f"WORKFLOW_ADD: Workflow {workflow_id} not found")
            return False
        
        workflow = self.workflows[workflow_id]
        
        if workflow.state not in [WorkflowState.PENDING, WorkflowState.ACTIVE]:
            logger.warning(f"WORKFLOW_ADD: Cannot add message to workflow {workflow_id} "
                          f"in state {workflow.state.name}")
            return False
        
        if message_id in workflow.messages:
            logger.warning(f"WORKFLOW_ADD: Message {message_id} already exists in workflow {workflow_id}")
            return False
        
        message = WorkflowMessage(
            message_id=message_id,
            workflow_id=workflow_id,
            sequence_number=sequence_number,
            dependencies=dependencies or set(),
            payload=payload,
            max_retries=max_retries
        )
        
        workflow.messages[message_id] = message
        self.message_to_workflow[message_id] = workflow_id
        workflow.last_activity = time.time()
        
        logger.info(f"WORKFLOW_ADD: Added message {message_id} to workflow {workflow_id} "
                   f"(seq: {sequence_number}, deps: {len(message.dependencies)})")
        
        # Start workflow if this is the first message
        if workflow.state == WorkflowState.PENDING:
            await self._start_workflow(workflow_id)
        
        # Process ready messages
        await self._process_ready_messages(workflow_id)
        
        return True
    
    def add_message_to_workflow_sync(
        self,
        workflow_id: str,
        message_id: str,
        sequence_number: int,
        payload: Dict[str, Any],
        dependencies: Optional[Set[str]] = None,
        max_retries: int = 3
    ) -> bool:
        """
        Synchronous version of add_message_to_workflow for non-async contexts.
        
        This method adds the message but defers processing to the next event loop cycle.
        Use this when you need to add messages from synchronous code.
        
        Args:
            workflow_id: Target workflow identifier
            message_id: Unique message identifier
            sequence_number: Message sequence number for ordering
            payload: Message payload data
            dependencies: Set of message IDs this message depends on
            max_retries: Maximum retry attempts for this message
            
        Returns:
            True if message was added successfully
        """
        if workflow_id not in self.workflows:
            logger.error(f"WORKFLOW_ADD_SYNC: Workflow {workflow_id} not found")
            return False
        
        workflow = self.workflows[workflow_id]
        
        if workflow.state not in [WorkflowState.PENDING, WorkflowState.ACTIVE]:
            logger.warning(f"WORKFLOW_ADD_SYNC: Cannot add message to workflow {workflow_id} "
                          f"in state {workflow.state.name}")
            return False
        
        if message_id in workflow.messages:
            logger.warning(f"WORKFLOW_ADD_SYNC: Message {message_id} already exists in workflow {workflow_id}")
            return False
        
        message = WorkflowMessage(
            message_id=message_id,
            workflow_id=workflow_id,
            sequence_number=sequence_number,
            dependencies=dependencies or set(),
            payload=payload,
            max_retries=max_retries
        )
        
        workflow.messages[message_id] = message
        self.message_to_workflow[message_id] = workflow_id
        workflow.last_activity = time.time()
        
        logger.info(f"WORKFLOW_ADD_SYNC: Added message {message_id} to workflow {workflow_id} "
                   f"(seq: {sequence_number}, deps: {len(message.dependencies)})")
        
        # Schedule async processing for next event loop cycle
        asyncio.create_task(self._handle_new_message(workflow_id))
        
        return True
    
    async def _handle_new_message(self, workflow_id: str):
        """Handle new message addition asynchronously."""
        try:
            if workflow_id not in self.workflows:
                return
            
            workflow = self.workflows[workflow_id]
            
            # Start workflow if this is the first message
            if workflow.state == WorkflowState.PENDING:
                await self._start_workflow(workflow_id)
            
            # Process ready messages
            await self._process_ready_messages(workflow_id)
            
        except Exception as e:
            logger.error(f"WORKFLOW_HANDLE: Error handling new message in workflow {workflow_id}: {e}")
    
    async def _start_workflow(self, workflow_id: str):
        """Start workflow execution."""
        if workflow_id not in self.workflows:
            return
        
        workflow = self.workflows[workflow_id]
        workflow.state = WorkflowState.ACTIVE
        workflow.started_at = time.time()
        
        logger.info(f"WORKFLOW_START: Started workflow {workflow_id}")
    
    async def _process_ready_messages(self, workflow_id: str):
        """Process messages that are ready for execution."""
        if workflow_id not in self.workflows:
            return
        
        workflow = self.workflows[workflow_id]
        ready_messages = workflow.get_ready_messages()
        
        if not ready_messages:
            return
        
        logger.debug(f"WORKFLOW_PROCESS: Processing {len(ready_messages)} ready messages "
                    f"in workflow {workflow_id}")
        
        for message in ready_messages:
            if self.message_processor:
                try:
                    # Process message asynchronously
                    result = self.message_processor(message)
                    if asyncio.iscoroutine(result):
                        await result
                    elif asyncio.iscoroutinefunction(self.message_processor):
                        # If processor is async but didn't return coroutine, call it properly
                        await self.message_processor(message)
                    
                    # Mark as completed
                    await self.mark_message_completed(message.message_id)
                    
                except Exception as e:
                    logger.error(f"WORKFLOW_PROCESS: Error processing message {message.message_id}: {e}")
                    await self.mark_message_failed(message.message_id, str(e))
            else:
                logger.warning(f"WORKFLOW_PROCESS: No message processor configured")
                break
    
    async def mark_message_completed(self, message_id: str) -> bool:
        """
        Mark a message as completed.
        
        Args:
            message_id: Message identifier
            
        Returns:
            True if message was marked as completed
        """
        workflow_id = self.message_to_workflow.get(message_id)
        if not workflow_id or workflow_id not in self.workflows:
            logger.error(f"WORKFLOW_COMPLETE: Message {message_id} not found in any workflow")
            return False
        
        workflow = self.workflows[workflow_id]
        
        if message_id not in workflow.messages:
            logger.error(f"WORKFLOW_COMPLETE: Message {message_id} not found in workflow {workflow_id}")
            return False
        
        message = workflow.messages[message_id]
        message.processed_at = time.time()
        workflow.completed_messages.add(message_id)
        workflow.last_activity = time.time()
        
        self._stats["messages_processed"] += 1
        
        logger.info(f"WORKFLOW_COMPLETE: Marked message {message_id} as completed "
                   f"in workflow {workflow_id}")
        
        # Check if workflow is complete
        if self._is_workflow_complete(workflow):
            await self._complete_workflow(workflow_id)
        else:
            # Process any newly ready messages
            await self._process_ready_messages(workflow_id)
        
        return True
    
    async def mark_message_failed(self, message_id: str, error: str) -> bool:
        """
        Mark a message as failed.
        
        Args:
            message_id: Message identifier
            error: Error description
            
        Returns:
            True if message was marked as failed
        """
        workflow_id = self.message_to_workflow.get(message_id)
        if not workflow_id or workflow_id not in self.workflows:
            logger.error(f"WORKFLOW_FAIL: Message {message_id} not found in any workflow")
            return False
        
        workflow = self.workflows[workflow_id]
        
        if message_id not in workflow.messages:
            logger.error(f"WORKFLOW_FAIL: Message {message_id} not found in workflow {workflow_id}")
            return False
        
        message = workflow.messages[message_id]
        message.retry_count += 1
        workflow.last_activity = time.time()
        
        if message.can_retry():
            logger.warning(f"WORKFLOW_RETRY: Message {message_id} failed, retrying "
                          f"({message.retry_count}/{message.max_retries}): {error}")
            
            # Retry the message
            await self._process_ready_messages(workflow_id)
        else:
            logger.error(f"WORKFLOW_FAIL: Message {message_id} failed permanently "
                        f"after {message.retry_count} retries: {error}")
            
            workflow.failed_messages.add(message_id)
            self._stats["messages_failed"] += 1
            
            # Check if workflow should fail
            if self._should_fail_workflow(workflow):
                await self._fail_workflow(workflow_id, f"Message {message_id} failed: {error}")
        
        return True
    
    def _is_workflow_complete(self, workflow: WorkflowContext) -> bool:
        """Check if workflow is complete."""
        total_messages = len(workflow.messages)
        completed_messages = len(workflow.completed_messages)
        return total_messages > 0 and completed_messages == total_messages
    
    def _should_fail_workflow(self, workflow: WorkflowContext) -> bool:
        """Check if workflow should be marked as failed."""
        # For now, fail if any message fails permanently
        # This could be made configurable based on failure tolerance
        return len(workflow.failed_messages) > 0
    
    async def _complete_workflow(self, workflow_id: str):
        """Mark workflow as completed."""
        if workflow_id not in self.workflows:
            return
        
        workflow = self.workflows[workflow_id]
        workflow.state = WorkflowState.COMPLETED
        workflow.completed_at = time.time()
        
        self._stats["workflows_completed"] += 1
        
        progress = workflow.get_progress()
        logger.info(f"WORKFLOW_COMPLETE: Completed workflow {workflow_id} "
                   f"({progress['completed']}/{progress['total_messages']} messages, "
                   f"{progress['elapsed_time']:.2f}s)")
        
        if self.completion_callback:
            try:
                if asyncio.iscoroutinefunction(self.completion_callback):
                    await self.completion_callback(workflow_id)
                else:
                    self.completion_callback(workflow_id)
            except Exception as e:
                logger.error(f"WORKFLOW_COMPLETE: Error in completion callback: {e}")
    
    async def _fail_workflow(self, workflow_id: str, reason: str):
        """Mark workflow as failed."""
        if workflow_id not in self.workflows:
            return
        
        workflow = self.workflows[workflow_id]
        workflow.state = WorkflowState.FAILED
        
        self._stats["workflows_failed"] += 1
        
        progress = workflow.get_progress()
        logger.error(f"WORKFLOW_FAIL: Failed workflow {workflow_id}: {reason} "
                    f"({progress['completed']}/{progress['total_messages']} messages completed)")
        
        if self.failure_callback:
            try:
                if asyncio.iscoroutinefunction(self.failure_callback):
                    await self.failure_callback(workflow_id, reason)
                else:
                    self.failure_callback(workflow_id, reason)
            except Exception as e:
                logger.error(f"WORKFLOW_FAIL: Error in failure callback: {e}")
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            True if workflow was cancelled
        """
        if workflow_id not in self.workflows:
            logger.warning(f"WORKFLOW_CANCEL: Workflow {workflow_id} not found")
            return False
        
        workflow = self.workflows[workflow_id]
        workflow.state = WorkflowState.CANCELLED
        
        logger.info(f"WORKFLOW_CANCEL: Cancelled workflow {workflow_id}")
        return True
    
    async def _cleanup_loop(self):
        """Background task to clean up expired workflows."""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired_workflows()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"WORKFLOW_CLEANUP: Error in cleanup loop: {e}")
    
    async def _cleanup_expired_workflows(self):
        """Clean up expired workflows."""
        expired_workflows = []
        
        for workflow_id, workflow in self.workflows.items():
            if workflow.is_expired():
                expired_workflows.append(workflow_id)
        
        for workflow_id in expired_workflows:
            workflow = self.workflows[workflow_id]
            workflow.state = WorkflowState.TIMEOUT
            
            self._stats["workflows_timeout"] += 1
            
            logger.warning(f"WORKFLOW_TIMEOUT: Workflow {workflow_id} timed out "
                          f"after {workflow.timeout_seconds}s")
            
            # Clean up message mappings
            for message_id in workflow.messages:
                self.message_to_workflow.pop(message_id, None)
            
            # Remove workflow
            del self.workflows[workflow_id]
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status and progress."""
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        return {
            "workflow_id": workflow_id,
            "trace_id": workflow.trace_id,
            "consistency_model": workflow.consistency_model.name,
            "progress": workflow.get_progress(),
            "ready_messages": len(workflow.get_ready_messages())
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get workflow manager statistics."""
        active_workflows = sum(1 for w in self.workflows.values() 
                              if w.state == WorkflowState.ACTIVE)
        
        return {
            "node_id": self.node_id,
            "active_workflows": active_workflows,
            "total_workflows": len(self.workflows),
            "statistics": self._stats.copy(),
            "configuration": {
                "max_workflows": self.max_workflows,
                "default_timeout": self.default_timeout,
                "cleanup_interval": self.cleanup_interval
            }
        }
