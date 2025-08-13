"""
Membership model for SWIM P2P.

This module defines the data structures for tracking cluster members
and their states in the SWIM protocol implementation, with enhanced
delta tracking for efficient state synchronization and member events.
"""

import time
import random
import asyncio
import logging
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any, DefaultDict, TYPE_CHECKING
from collections import defaultdict

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from swim.events.dispatcher import EventDispatcher

# Import member event classes from events.types
from swim.events.types import (
    MemberEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
    MemberFailedEvent,
    MemberSuspectedEvent,
    MemberAliveEvent
)

logger = logging.getLogger(__name__)


class MemberState(Enum):
    """Possible states for a cluster member."""
    ALIVE = auto()
    SUSPECT = auto()
    DEAD = auto()


@dataclass(kw_only=True)
class Member:
    """
    Represents a member in the SWIM cluster.
    
    Attributes:
        addr: The network address of the member as (host, port).
        state: The current state of the member (ALIVE, SUSPECT, DEAD).
        incarnation: A monotonically increasing counter for conflict resolution.
        last_heartbeat: Timestamp of the last heartbeat received from this member.
        last_state_change: Timestamp of the last state change.
        rtt_history: List of recent round-trip times for adaptive timeouts.
        metadata: Additional metadata for the member.
    """
    addr: Tuple[str, int]
    state: MemberState = MemberState.ALIVE
    incarnation: int = 1
    last_heartbeat: float = field(default_factory=time.time)
    last_state_change: float = field(default_factory=time.time)
    rtt_history: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def address(self) -> str:
        """Get the address as a string in host:port format."""
        return f"{self.addr[0]}:{self.addr[1]}"
    
    @property
    def is_alive(self) -> bool:
        """Check if the member is in ALIVE state."""
        return self.state == MemberState.ALIVE
    
    @property
    def is_suspect(self) -> bool:
        """Check if the member is in SUSPECT state."""
        return self.state == MemberState.SUSPECT
    
    @property
    def is_dead(self) -> bool:
        """Check if the member is in DEAD state."""
        return self.state == MemberState.DEAD
    
    @property
    def time_since_heartbeat(self) -> float:
        """Get time since last heartbeat in seconds."""
        return time.time() - self.last_heartbeat
    
    @property
    def time_since_state_change(self) -> float:
        """Get time since last state change in seconds."""
        return time.time() - self.last_state_change
    
    def __str__(self) -> str:
        """String representation of a member."""
        return f"Member({self.addr[0]}:{self.addr[1]}, {self.state.name}, inc={self.incarnation})"
    
    def __hash__(self) -> int:
        """Hash based on address for use in sets and dicts."""
        return hash(self.addr)
    
    def __eq__(self, other) -> bool:
        """Equality based on address."""
        if not isinstance(other, Member):
            return False
        return self.addr == other.addr
    
    def add_rtt_sample(self, rtt: float, max_samples: int = 10) -> None:
        """
        Add a round-trip time sample to the history.
        
        Args:
            rtt: The round-trip time in seconds.
            max_samples: Maximum number of samples to keep.
        """
        if rtt < 0:
            logger.warning(f"Negative RTT sample ignored: {rtt}")
            return
            
        self.rtt_history.append(rtt)
        if len(self.rtt_history) > max_samples:
            self.rtt_history.pop(0)
    
    def get_average_rtt(self, default: float = 0.1) -> float:
        """
        Get the average round-trip time from the history.
        
        Args:
            default: Default value if no samples are available.
            
        Returns:
            The average RTT in seconds.
        """
        if not self.rtt_history:
            return default
        return sum(self.rtt_history) / len(self.rtt_history)
    
    def get_percentile_rtt(self, percentile: float = 0.95, default: float = 0.2) -> float:
        """
        Get a percentile of the round-trip time from the history.
        
        Args:
            percentile: The percentile to calculate (0.0 to 1.0).
            default: Default value if no samples are available.
            
        Returns:
            The percentile RTT in seconds.
        """
        if not self.rtt_history:
            return default
        
        if not 0.0 <= percentile <= 1.0:
            raise ValueError("Percentile must be between 0.0 and 1.0")
        
        sorted_rtts = sorted(self.rtt_history)
        index = int(len(sorted_rtts) * percentile)
        return sorted_rtts[min(index, len(sorted_rtts) - 1)]
    
    def get_adaptive_timeout(self, base_timeout: float = 1.0, multiplier: float = 3.0) -> float:
        """
        Calculate an adaptive timeout based on RTT history.
        
        Args:
            base_timeout: Base timeout value.
            multiplier: Multiplier for the percentile RTT.
            
        Returns:
            Adaptive timeout in seconds.
        """
        if not self.rtt_history:
            return base_timeout
        
        # Use 95th percentile RTT with a multiplier
        p95_rtt = self.get_percentile_rtt(0.95)
        adaptive = p95_rtt * multiplier
        
        # Ensure it's at least the base timeout
        return max(adaptive, base_timeout)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert member to dictionary for serialization."""
        return {
            "address": self.address,
            "state": self.state.name.lower(),
            "incarnation": self.incarnation,
            "last_heartbeat": self.last_heartbeat,
            "last_state_change": self.last_state_change,
            "average_rtt": self.get_average_rtt(),
            "rtt_samples": len(self.rtt_history),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Member":
        """Create member from dictionary."""
        try:
            host, port_str = data["address"].split(":")
            addr = (host, int(port_str))
        except (ValueError, KeyError) as e:
            raise ValueError(f"Invalid address format in member data: {e}")
        
        state_map = {
            "alive": MemberState.ALIVE,
            "suspect": MemberState.SUSPECT,
            "dead": MemberState.DEAD
        }
        
        state_str = data.get("state", "alive").lower()
        if state_str not in state_map:
            raise ValueError(f"Invalid member state: {state_str}")
        
        return cls(
            addr=addr,
            state=state_map[state_str],
            incarnation=data.get("incarnation", 1),
            last_heartbeat=data.get("last_heartbeat", time.time()),
            last_state_change=data.get("last_state_change", time.time()),
            metadata=data.get("metadata", {})
        )


class MemberList:
    """
    Maintains the list of members in the SWIM cluster with delta tracking.
    
    This class tracks all known members and their states, and provides
    methods for adding, removing, and updating members. It also supports
    delta tracking for efficient state synchronization and event emission.
    """
    
    def __init__(self, self_addr: Tuple[str, int], event_dispatcher: Optional["EventDispatcher"] = None):
        """
        Initialize a new member list.
        
        Args:
            self_addr: The address of the local node.
            event_dispatcher: Optional event dispatcher for emitting member events.
        """
        self.self_addr = self_addr
        self.event_dispatcher = event_dispatcher
        self._members: Dict[Tuple[str, int], Member] = {}
        self._lock = asyncio.Lock()
        
        # Delta tracking for efficient state synchronization
        self._version = 0
        self._deltas: DefaultDict[int, Set[Tuple[str, int]]] = defaultdict(set)
        self._last_full_sync = time.time()
        self._max_delta_history = 1000  # Maximum number of delta versions to keep
        
        # Statistics
        self._stats = {
            "members_added": 0,
            "members_removed": 0,
            "state_changes": 0,
            "heartbeats_updated": 0,
            "events_emitted": 0
        }
        
        # Add self as a member
        self.add_member(self_addr, join_method="self")
        logger.info(f"Created member list with self at {self_addr[0]}:{self_addr[1]}")
    
    @property
    def size(self) -> int:
        """Get the total number of members."""
        return len(self._members)
    
    @property
    def alive_count(self) -> int:
        """Get the number of alive members."""
        return sum(1 for m in self._members.values() if m.is_alive)
    
    @property
    def suspect_count(self) -> int:
        """Get the number of suspected members."""
        return sum(1 for m in self._members.values() if m.is_suspect)
    
    @property
    def dead_count(self) -> int:
        """Get the number of dead members."""
        return sum(1 for m in self._members.values() if m.is_dead)
    
    def _emit_event(self, event: MemberEvent) -> None:
        """
        Emit a member event if dispatcher is available.
        
        Args:
            event: The event to emit.
        """
        if self.event_dispatcher:
            try:
                self.event_dispatcher.emit(event)
                self._stats["events_emitted"] += 1
            except Exception as e:
                logger.error(f"Error emitting member event: {e}")
    
    def add_member(self, addr: Tuple[str, int], join_method: str = "unknown", 
                   seed_node: Optional[str] = None) -> bool:
        """
        Add a new member to the list.
        
        Args:
            addr: The address of the member to add.
            join_method: How the member joined (e.g., "seed", "gossip", "direct").
            seed_node: The seed node used for joining, if applicable.
            
        Returns:
            True if member was added, False if already exists.
        """
        if addr in self._members:
            logger.debug(f"Member {addr[0]}:{addr[1]} already exists")
            return False
        
        member = Member(addr=addr)
        self._members[addr] = member
        self._record_delta(addr)
        self._stats["members_added"] += 1
        
        # Emit member joined event (except for self)
        if addr != self.self_addr:
            event = MemberJoinedEvent(
                member=member,
                source_node=f"{self.self_addr[0]}:{self.self_addr[1]}",
                metadata={
                    "join_method": join_method,
                    "seed_node": seed_node,
                    "cluster_size": self.size
                }
            )
            self._emit_event(event)
        
        logger.info(f"Added new member: {addr[0]}:{addr[1]} (method: {join_method})")
        return True
    
    def remove_member(self, addr: Tuple[str, int], leave_reason: str = "unknown") -> bool:
        """
        Remove a member from the list.
        
        Args:
            addr: The address of the member to remove.
            leave_reason: Reason for leaving (e.g., "graceful_shutdown", "timeout").
            
        Returns:
            True if member was removed, False if not found.
        """
        if addr not in self._members:
            logger.debug(f"Cannot remove non-existent member: {addr[0]}:{addr[1]}")
            return False
        
        member = self._members[addr]
        was_alive = member.is_alive
        uptime = member.time_since_state_change if member.state == MemberState.ALIVE else None
        
        # Emit member left event (except for self)
        if addr != self.self_addr:
            event = MemberLeftEvent(
                member=member,
                source_node=f"{self.self_addr[0]}:{self.self_addr[1]}",
                metadata={
                    "leave_reason": leave_reason,
                    "was_alive": was_alive,
                    "uptime": uptime
                }
            )
            self._emit_event(event)
        
        del self._members[addr]
        self._record_delta(addr)
        self._stats["members_removed"] += 1
        logger.info(f"Removed member: {addr[0]}:{addr[1]} (reason: {leave_reason})")
        return True
    
    def get_member(self, addr: Tuple[str, int]) -> Optional[Member]:
        """
        Get a member by address.
        
        Args:
            addr: The address of the member to get.
        
        Returns:
            The Member object, or None if not found.
        """
        return self._members.get(addr)
    
    def has_member(self, addr: Tuple[str, int]) -> bool:
        """
        Check if a member exists.
        
        Args:
            addr: The address to check.
            
        Returns:
            True if member exists, False otherwise.
        """
        return addr in self._members
    
    async def update_heartbeat(self, addr: Tuple[str, int], rtt: Optional[float] = None) -> bool:
        """
        Update the last heartbeat time for a member.
        
        Args:
            addr: The address of the member to update.
            rtt: Optional round-trip time to record.
            
        Returns:
            True if heartbeat was updated, False if member not found.
        """
        async with self._lock:
            member = self.get_member(addr)
            if not member:
                logger.debug(f"Cannot update heartbeat for non-existent member: {addr[0]}:{addr[1]}")
                return False
            
            old_time = member.last_heartbeat
            current_time = time.time()
            time_since_last = current_time - old_time
            
            member.last_heartbeat = current_time
            
            # Add RTT sample if provided
            if rtt is not None and rtt > 0:
                member.add_rtt_sample(rtt)
            
            self._stats["heartbeats_updated"] += 1
            
            logger.debug(f"HEARTBEAT for {addr[0]}:{addr[1]} updated "
                        f"(time since last: {time_since_last:.2f}s, "
                        f"state: {member.state.name}, inc: {member.incarnation})")
            return True
    
    async def update_incarnation(self, addr: Tuple[str, int], incarnation: int) -> bool:
        """
        Update the incarnation number for a member.
        
        Args:
            addr: The address of the member to update.
            incarnation: The new incarnation number.
            
        Returns:
            True if incarnation was updated, False otherwise.
        """
        async with self._lock:
            member = self.get_member(addr)
            if not member:
                logger.debug(f"Cannot update incarnation for non-existent member: {addr[0]}:{addr[1]}")
                return False
            
            if incarnation <= member.incarnation:
                logger.debug(f"Incarnation {incarnation} not higher than current {member.incarnation} for {addr[0]}:{addr[1]}")
                return False
            
            old_inc = member.incarnation
            member.incarnation = incarnation
            self._record_delta(addr)
            logger.info(f"INCARNATION for {addr[0]}:{addr[1]} updated from {old_inc} to {incarnation}")
            return True
    
    async def mark_alive(self, addr: Tuple[str, int], incarnation: Optional[int] = None, 
                        recovery_method: str = "ping_response") -> bool:
        """
        Mark a member as ALIVE.
        
        Args:
            addr: The address of the member to mark.
            incarnation: Optional incarnation number for conflict resolution.
            recovery_method: How the member was detected as alive.
            
        Returns:
            True if state was changed, False otherwise.
        """
        async with self._lock:
            member = self.get_member(addr)
            if not member:
                # Auto-add member if it doesn't exist
                self.add_member(addr, join_method="gossip")
                member = self.get_member(addr)
            
            was_suspected = member.is_suspect
            was_suspected_duration = None
            incarnation_changed = False
            state_changed = False
            
            # Update incarnation if provided and higher
            if incarnation is not None and incarnation > member.incarnation:
                member.incarnation = incarnation
                incarnation_changed = True
            
            # Change state if not already alive
            if not member.is_alive:
                old_state = member.state
                old_state_change_time = member.last_state_change
                
                member.state = MemberState.ALIVE
                if not incarnation_changed:
                    member.incarnation += 1
                member.last_state_change = time.time()
                self._record_delta(addr)
                self._stats["state_changes"] += 1
                state_changed = True
                
                if was_suspected:
                    was_suspected_duration = time.time() - old_state_change_time
                
                # Emit member alive event (except for self)
                if addr != self.self_addr:
                    event = MemberAliveEvent(
                        member=member,
                        source_node=f"{self.self_addr[0]}:{self.self_addr[1]}",
                        metadata={
                            "recovery_method": recovery_method,
                            "was_suspected_duration": was_suspected_duration,
                            "incarnation_changed": incarnation_changed,
                            "false_positive": was_suspected and was_suspected_duration and was_suspected_duration < 30.0
                        }
                    )
                    self._emit_event(event)
                
                logger.info(f"STATE CHANGE: Member {addr[0]}:{addr[1]} "
                          f"transitioned from {old_state.name} to ALIVE (inc={member.incarnation})")
            
            # Always update heartbeat
            member.last_heartbeat = time.time()
            return state_changed
    
    async def mark_suspect(self, addr: Tuple[str, int], incarnation: Optional[int] = None,
                          suspicion_reason: str = "ping_timeout", timeout_duration: Optional[float] = None,
                          attempt_number: Optional[int] = None, indirect_ping_attempted: bool = False) -> bool:
        """
        Mark a member as SUSPECT.
        
        Args:
            addr: The address of the member to mark.
            incarnation: Optional incarnation number for conflict resolution.
            suspicion_reason: Reason for suspicion.
            timeout_duration: Duration of the timeout that caused suspicion.
            attempt_number: Number of failed attempts.
            indirect_ping_attempted: Whether indirect ping was attempted.
            
        Returns:
            True if state was changed, False otherwise.
        """
        async with self._lock:
            member = self.get_member(addr)
            if not member:
                logger.warning(f"Cannot mark non-existent member as suspect: {addr[0]}:{addr[1]}")
                return False
            
            state_changed = False
            
            # For our own address (self)
            if addr == self.self_addr:
                # Only accept if incarnation is higher (from another node)
                if incarnation is not None and incarnation > member.incarnation:
                    old_state = member.state
                    member.state = MemberState.SUSPECT
                    member.incarnation = incarnation
                    member.last_state_change = time.time()
                    self._record_delta(addr)
                    self._stats["state_changes"] += 1
                    state_changed = True
                    logger.info(f"STATE CHANGE: Self marked as SUSPECT by remote node (inc={incarnation})")
            else:
                # For remote members
                if not member.is_suspect:  # Only change state if different
                    old_state = member.state
                    member.state = MemberState.SUSPECT
                    
                    # If incarnation is provided and higher, use it; otherwise increment
                    if incarnation is not None and incarnation > member.incarnation:
                        member.incarnation = incarnation
                    else:
                        member.incarnation += 1
                    
                    member.last_state_change = time.time()
                    self._record_delta(addr)
                    self._stats["state_changes"] += 1
                    state_changed = True
                    
                    # Emit member suspected event
                    event = MemberSuspectedEvent(
                        member=member,
                        source_node=f"{self.self_addr[0]}:{self.self_addr[1]}",
                        metadata={
                            "suspicion_reason": suspicion_reason,
                            "timeout_duration": timeout_duration,
                            "attempt_number": attempt_number,
                            "indirect_ping_attempted": indirect_ping_attempted
                        }
                    )
                    self._emit_event(event)
                    
                    logger.info(f"STATE CHANGE: Member {addr[0]}:{addr[1]} transitioned from "
                              f"{old_state.name} to SUSPECT (inc={member.incarnation})")
                elif incarnation is not None and incarnation > member.incarnation:
                    # If already suspect but higher incarnation provided, update incarnation
                    member.incarnation = incarnation
                    self._record_delta(addr)
                    logger.debug(f"Updated incarnation for SUSPECT member {addr[0]}:{addr[1]} (inc={incarnation})")
            
            return state_changed
    
    async def mark_dead(self, addr: Tuple[str, int], incarnation: Optional[int] = None,
                       failure_detection_method: str = "timeout", last_seen: Optional[float] = None,
                       consecutive_failures: Optional[int] = None) -> bool:
        """
        Mark a member as DEAD.
        
        Args:
            addr: The address of the member to mark.
            incarnation: Optional incarnation number for conflict resolution.
            failure_detection_method: How the failure was detected.
            last_seen: When the member was last seen alive.
            consecutive_failures: Number of consecutive failures.
            
        Returns:
            True if state was changed, False otherwise.
        """
        async with self._lock:
            member = self.get_member(addr)
            if not member:
                logger.warning(f"Cannot mark non-existent member as dead: {addr[0]}:{addr[1]}")
                return False
            
            failure_duration = None
            if last_seen is not None:
                failure_duration = time.time() - last_seen
            elif member.last_heartbeat:
                failure_duration = time.time() - member.last_heartbeat
            
            state_changed = False
            
            # For our own address (self)
            if addr == self.self_addr:
                # Only accept if incarnation is higher (from another node)
                if incarnation is not None and incarnation > member.incarnation:
                    old_state = member.state
                    member.state = MemberState.DEAD
                    member.incarnation = incarnation
                    member.last_state_change = time.time()
                    self._record_delta(addr)
                    self._stats["state_changes"] += 1
                    state_changed = True
                    logger.info(f"STATE CHANGE: Self marked as DEAD by remote node (inc={incarnation})")
            else:
                # For remote members
                if not member.is_dead:  # Only change state if different
                    old_state = member.state
                    member.state = MemberState.DEAD
                    
                    # If incarnation is provided and higher, use it; otherwise increment
                    if incarnation is not None and incarnation > member.incarnation:
                        member.incarnation = incarnation
                    else:
                        member.incarnation += 1
                    
                    member.last_state_change = time.time()
                    self._record_delta(addr)
                    self._stats["state_changes"] += 1
                    state_changed = True
                    
                    # Emit member failed event
                    event = MemberFailedEvent(
                        member=member,
                        source_node=f"{self.self_addr[0]}:{self.self_addr[1]}",
                        metadata={
                            "failure_detection_method": failure_detection_method,
                            "last_seen": last_seen,
                            "failure_duration": failure_duration,
                            "consecutive_failures": consecutive_failures
                        }
                    )
                    self._emit_event(event)
                    
                    logger.info(f"STATE CHANGE: Member {addr[0]}:{addr[1]} transitioned from "
                              f"{old_state.name} to DEAD (inc={member.incarnation})")
                elif incarnation is not None and incarnation > member.incarnation:
                    # If already dead but higher incarnation provided, update incarnation
                    member.incarnation = incarnation
                    self._record_delta(addr)
                    logger.debug(f"Updated incarnation for DEAD member {addr[0]}:{addr[1]} (inc={incarnation})")
            
            return state_changed
    
    def get_random_members(self, n: int, exclude: Optional[List[Tuple[str, int]]] = None, 
                          include_dead: bool = False) -> List[Member]:
        """
        Get n random members from the list.
        
        Args:
            n: The number of members to get.
            exclude: Optional list of addresses to exclude.
            include_dead: Whether to include dead members.
        
        Returns:
            A list of up to n random Member objects.
        """
        if n <= 0:
            return []
        
        exclude_set = set(exclude or [])
        exclude_set.add(self.self_addr)  # Always exclude self
        
        # Filter members based on criteria
        eligible = []
        for addr, member in self._members.items():
            if addr in exclude_set:
                continue
            if not include_dead and member.is_dead:
                continue
            eligible.append(member)
        
        if not eligible:
            return []
        
        # Return up to n random members
        return random.sample(eligible, min(n, len(eligible)))
    
    def get_alive_members(self, exclude_self: bool = True) -> List[Member]:
        """
        Get all members that are currently ALIVE.
        
        Args:
            exclude_self: Whether to exclude the local node.
        
        Returns:
            A list of all ALIVE Member objects.
        """
        members = [m for m in self._members.values() if m.is_alive]
        if exclude_self:
            members = [m for m in members if m.addr != self.self_addr]
        return members
    
    def get_suspect_members(self, exclude_self: bool = True) -> List[Member]:
        """
        Get all members that are currently SUSPECT.
        
        Args:
            exclude_self: Whether to exclude the local node.
        
        Returns:
            A list of all SUSPECT Member objects.
        """
        members = [m for m in self._members.values() if m.is_suspect]
        if exclude_self:
            members = [m for m in members if m.addr != self.self_addr]
        return members
    
    def get_dead_members(self, exclude_self: bool = True) -> List[Member]:
        """
        Get all members that are currently DEAD.
        
        Args:
            exclude_self: Whether to exclude the local node.
        
        Returns:
            A list of all DEAD Member objects.
        """
        members = [m for m in self._members.values() if m.is_dead]
        if exclude_self:
            members = [m for m in members if m.addr != self.self_addr]
        return members
    
    def get_all_members(self, exclude_self: bool = False) -> List[Member]:
        """
        Get all members regardless of state.
        
        Args:
            exclude_self: Whether to exclude the local node.
        
        Returns:
            A list of all Member objects.
        """
        members = list(self._members.values())
        if exclude_self:
            members = [m for m in members if m.addr != self.self_addr]
        return members
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get membership statistics."""
        return {
            **self._stats,
            "total_members": self.size,
            "alive_members": self.alive_count,
            "suspect_members": self.suspect_count,
            "dead_members": self.dead_count,
            "version": self._version,
            "delta_history_size": len(self._deltas)
        }
    
    def _record_delta(self, addr: Tuple[str, int]) -> None:
        """
        Record a delta for a member.
        
        This is used for efficient state synchronization.
        
        Args:
            addr: The address of the member that changed.
        """
        self._version += 1
        self._deltas[self._version].add(addr)
        
        # Clean up old deltas to prevent memory growth
        if len(self._deltas) > self._max_delta_history:
            oldest_version = min(self._deltas.keys())
            del self._deltas[oldest_version]
    
    def get_deltas_since(self, version: int) -> Dict[Tuple[str, int], Member]:
        """
        Get all members that have changed since a specific version.
        
        Args:
            version: The version to get changes since.
            
        Returns:
            A dictionary of changed members.
        """
        if version <= 0 or version < self._version - len(self._deltas):
            # Version is too old, return full state
            return dict(self._members)
        
        # Collect all addresses that have changed since the given version
        changed_addrs = set()
        for v in range(version + 1, self._version + 1):
            changed_addrs.update(self._deltas.get(v, set()))
        
        # Return only the changed members
        return {addr: member for addr, member in self._members.items() if addr in changed_addrs}
    
    def serialize_digest(self, full: bool = True, since_version: int = 0) -> Dict[str, Any]:
        """
        Serialize member list digest with METADATA included.
        
        Args:
            full: Whether to include the full state or just deltas.
            since_version: The version to get changes since if not full.
            
        Returns:
            A serialized digest.
        """
        members_to_include = self._members if full else self.get_deltas_since(since_version)
        
        entries = [
            {
                "addr": f"{member.addr[0]}:{member.addr[1]}",
                "state": member.state.name,
                "incarnation": member.incarnation,
                "last_heartbeat": member.last_heartbeat,
                "metadata": member.metadata  # Include metadata in digest
            }
            for member in members_to_include.values()
        ]
        
        return {
            "version": self._version,
            "entries": entries,
            "is_full": full,
            "timestamp": time.time(),
            "source": f"{self.self_addr[0]}:{self.self_addr[1]}"
        }
    
    async def merge_digest(self, digest: Dict[str, Any]) -> int:
        """
        Merge a received digest into the local member list.
        
        This method handles conflict resolution based on incarnation numbers.
        NOW INCLUDES METADATA PROCESSING!
        
        Args:
            digest: A serialized digest.
            
        Returns:
            Number of members that were updated.
        """
        async with self._lock:
            entries = digest.get("entries", [])
            remote_version = digest.get("version", 0)
            updates_count = 0
            
            for entry in entries:
                try:
                    # Parse address
                    host, port_str = entry["addr"].split(":")
                    addr = (host, int(port_str))
                    
                    # Parse state
                    state = MemberState[entry["state"]]
                    incarnation = entry["incarnation"]
                    last_heartbeat = entry.get("last_heartbeat", time.time())
                    metadata = entry.get("metadata", {})  # Extract metadata
                    
                    # Get existing member or create new one
                    member = self.get_member(addr)
                    if not member:
                        self.add_member(addr, join_method="gossip")
                        member = self.get_member(addr)
                        member.state = state
                        member.incarnation = incarnation
                        member.last_heartbeat = last_heartbeat
                        member.metadata = metadata  # Set metadata
                        member.last_state_change = time.time()
                        updates_count += 1
                        
                        # Log metadata updates at INFO level
                        if metadata and 'agent_capabilities' in metadata:
                            logger.info(f"GOSSIP METADATA: New member {addr[0]}:{addr[1]} capabilities: {metadata['agent_capabilities']}")
                        continue
                    
                    # Handle conflict resolution based on incarnation numbers
                    if incarnation > member.incarnation:
                        # Higher incarnation wins - RESURRECTION LOGIC: Allow DEAD -> ALIVE with higher incarnation
                        old_state = member.state
                        member.state = state
                        member.incarnation = incarnation
                        member.last_heartbeat = max(member.last_heartbeat, last_heartbeat)
                        member.metadata = metadata  # Update metadata
                        member.last_state_change = time.time()
                        self._record_delta(addr)
                        updates_count += 1
                        
                        # Log metadata updates at INFO level
                        if metadata and 'agent_capabilities' in metadata:
                            logger.info(f"GOSSIP METADATA: Updated member {addr[0]}:{addr[1]} capabilities: {metadata['agent_capabilities']}")
                        
                        # Log resurrection if it occurred
                        if old_state == MemberState.DEAD and state == MemberState.ALIVE:
                            logger.info(f"RESURRECTION: Member {addr[0]}:{addr[1]} resurrected from DEAD to ALIVE (inc={incarnation})")
                            # Emit resurrection event
                            if self.event_dispatcher:
                                from swim.events.types import MemberAliveEvent
                                event = MemberAliveEvent(
                                    source_node=f"{self.self_addr[0]}:{self.self_addr[1]}",
                                    target_member=f"{addr[0]}:{addr[1]}",
                                    incarnation=incarnation,
                                    metadata={"resurrection": True, "previous_state": "DEAD"}
                                )
                                self._emit_event(event)
                        else:
                            logger.debug(f"Updated member {addr[0]}:{addr[1]} from {old_state.name} to {state.name} (inc={incarnation})")
                    elif incarnation == member.incarnation:
                        # Same incarnation, DEAD > SUSPECT > ALIVE
                        state_priority = {MemberState.ALIVE: 0, MemberState.SUSPECT: 1, MemberState.DEAD: 2}
                        if state_priority[state] > state_priority[member.state]:
                            old_state = member.state
                            member.state = state
                            member.last_heartbeat = max(member.last_heartbeat, last_heartbeat)
                            member.last_state_change = time.time()
                            self._record_delta(addr)
                            updates_count += 1
                            logger.debug(f"Updated member {addr[0]}:{addr[1]} from {old_state.name} to {state.name} (inc={incarnation})")
                        
                        # Always merge metadata even if state doesn't change
                        if metadata:
                            member.metadata.update(metadata)
                            
                            # Log metadata updates at INFO level
                            if 'agent_capabilities' in metadata:
                                logger.info(f"GOSSIP METADATA: Merged capabilities for {addr[0]}:{addr[1]}: {metadata['agent_capabilities']}")
                    # If incarnation is lower, ignore the update
                    
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error processing digest entry: {e}")
                    continue
            
            logger.debug(f"Merged digest with {updates_count} updates from version {remote_version}")
            return updates_count
    
    def cleanup_dead_members(self, max_age: float = 3600.0) -> int:
        """
        Remove dead members that have been dead for too long.
        
        Args:
            max_age: Maximum age in seconds for dead members.
            
        Returns:
            Number of members removed.
        """
        current_time = time.time()
        to_remove = []
        
        for addr, member in self._members.items():
            if (member.is_dead and 
                addr != self.self_addr and  # Never remove self
                current_time - member.last_state_change > max_age):
                to_remove.append(addr)
        
        removed_count = 0
        for addr in to_remove:
            if self.remove_member(addr, leave_reason="cleanup_expired"):
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} expired dead members")
        
        return removed_count    

    def can_resurrect_member(self, addr: Tuple[str, int], new_incarnation: int) -> bool:
        """
        Check if a member can be resurrected from DEAD state.
        
        Args:
            addr: Member address
            new_incarnation: New incarnation number
            
        Returns:
            True if resurrection is allowed
        """
        member = self._members.get(addr)
        if not member or not member.is_dead:
            return False
        
        # Conservative resurrection: only on higher incarnation
        can_resurrect = new_incarnation > member.incarnation
        
        if can_resurrect:
            logger.info(f"RESURRECTION_CHECK: Member {addr[0]}:{addr[1]} can be resurrected (current_inc={member.incarnation}, new_inc={new_incarnation})")
        
        return can_resurrect

    def force_resurrect_member(self, addr: Tuple[str, int], new_incarnation: int) -> bool:
        """
        Force resurrection of a member with higher incarnation number.
        
        Args:
            addr: Member address to resurrect
            new_incarnation: New incarnation number (must be higher)
            
        Returns:
            True if resurrection was successful
        """
        if not self.can_resurrect_member(addr, new_incarnation):
            return False
        
        member = self._members.get(addr)
        if member:
            old_state = member.state
            member.state = MemberState.ALIVE
            member.incarnation = new_incarnation
            member.last_heartbeat = time.time()
            member.last_state_change = time.time()
            self._record_delta(addr)
            
            logger.info(f"FORCED_RESURRECTION: Member {addr[0]}:{addr[1]} force-resurrected from {old_state.name} to ALIVE (inc={new_incarnation})")
            
            # Emit resurrection event
            if self.event_dispatcher:
                from swim.events.types import MemberAliveEvent
                event = MemberAliveEvent(
                    source_node=f"{self.self_addr[0]}:{self.self_addr[1]}",
                    target_member=f"{addr[0]}:{addr[1]}",
                    incarnation=new_incarnation,
                    metadata={"forced_resurrection": True, "previous_state": old_state.name}
                )
                self._emit_event(event)
            
            return True
        
        return False     