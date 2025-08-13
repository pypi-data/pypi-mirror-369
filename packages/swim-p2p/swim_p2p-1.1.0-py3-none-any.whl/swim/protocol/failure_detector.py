"""
Failure detection for SWIM P2P with Lifeguard enhancements.

This module implements the direct ping/ack failure detection mechanism
and indirect probing for the SWIM protocol, with adaptive timeouts
and Lifeguard enhancements for improved reliability.
"""

import asyncio
import logging
import uuid
import time
import statistics
from typing import Dict, List, Optional, Tuple, Any, Set

from swim.transport.base import Transport
from swim.protocol.member import MemberList, MemberState
from swim.utils.serialization import serialize_message, deserialize_message

# Import Lifeguard components (conditionally used if provided)
try:
    from swim.lifeguard.awareness import AwarenessService
    from swim.lifeguard.timing import TimingService
    from swim.lifeguard.probe_rate import ProbeRateService
    LIFEGUARD_AVAILABLE = True
except ImportError:
    LIFEGUARD_AVAILABLE = False

logger = logging.getLogger(__name__)


class FailureDetector:
    """
    Implements the SWIM failure detection mechanism with Lifeguard enhancements.
    
    This class handles direct ping/ack failure detection and indirect
    probing through other members, with adaptive timeouts based on
    network conditions and Lifeguard awareness to reduce false positives.
    """
    
    def __init__(
        self,
        transport: Transport,
        members: MemberList,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new failure detector with Lifeguard enhancements.
        
        Args:
            transport: The transport to use for sending/receiving messages.
            members: The member list to update based on detection results.
            config: Optional configuration parameters.
        """
        self.transport = transport
        self.members = members
        self.config = config or {}
        
        # Default configuration
        self.config.setdefault("PING_TIMEOUT_BASE", 1.0)
        self.config.setdefault("PING_TIMEOUT_MAX", 3.0)
        self.config.setdefault("PING_TIMEOUT_MIN", 0.5)
        self.config.setdefault("PING_RETRIES", 2)
        self.config.setdefault("INDIRECT_PROBE_COUNT", 3)
        self.config.setdefault("ADAPTIVE_TIMEOUT_FACTOR", 2.0)
        self.config.setdefault("RTT_SMOOTHING_FACTOR", 0.1)
        self.config.setdefault("LIFEGUARD_ENABLED", True)  # Enable Lifeguard by default
        
        # Keep track of active ping operations
        self._ping_in_progress: Set[str] = set()
        
        # RTT tracking for adaptive timeouts
        self._global_rtts: List[float] = []
        self._last_rtt_cleanup = time.time()
        
        # Lifeguard service references (to be set by Node)
        self.awareness_service = None
        self.timing_service = None
        self.probe_rate_service = None
        
        # Set ping timeout property for dynamic adjustment
        self.ping_timeout = self.config["PING_TIMEOUT_BASE"]
        
        logger.info("Failure detector initialized with Lifeguard enhancements")
    
    def _calculate_timeout(self, target: Tuple[str, int]) -> float:
        """
        Calculate an adaptive timeout for a target based on RTT history.
        
        Args:
            target: The target address.
            
        Returns:
            The calculated timeout in seconds.
        """
        # Use Lifeguard timing service if available
        if self.timing_service and self.config.get("LIFEGUARD_ENABLED", True) and LIFEGUARD_AVAILABLE:
            peer_id = f"{target[0]}:{target[1]}"
            timeout = self.timing_service.get_ping_timeout(peer_id)
            logger.info(f"LIFEGUARD: Using adaptive timeout for {peer_id}: {timeout:.2f}s")
            return timeout
        
        # Otherwise use the traditional method
        member = self.members.get_member(target)
        
        if member and member.rtt_history:
            # Use member-specific RTT history if available
            try:
                # Use 95th percentile RTT with a safety factor
                timeout = member.get_percentile_rtt(0.95) * self.config["ADAPTIVE_TIMEOUT_FACTOR"]
                # Clamp to min/max
                timeout = max(
                    self.config["PING_TIMEOUT_MIN"],
                    min(self.config["PING_TIMEOUT_MAX"], timeout)
                )
                logger.debug(f"Using member-specific timeout for {target[0]}:{target[1]}: {timeout:.2f}s")
                return timeout
            except Exception as e:
                logger.warning(f"Error calculating adaptive timeout: {e}")
        
        # Fall back to global RTT statistics if available
        if self._global_rtts:
            try:
                # Use 95th percentile of global RTTs with a safety factor
                global_rtts = sorted(self._global_rtts)
                index = int(len(global_rtts) * 0.95)
                timeout = global_rtts[min(index, len(global_rtts) - 1)] * self.config["ADAPTIVE_TIMEOUT_FACTOR"]
                # Clamp to min/max
                timeout = max(
                    self.config["PING_TIMEOUT_MIN"],
                    min(self.config["PING_TIMEOUT_MAX"], timeout)
                )
                logger.debug(f"Using global timeout for {target[0]}:{target[1]}: {timeout:.2f}s")
                return timeout
            except Exception as e:
                logger.warning(f"Error calculating global adaptive timeout: {e}")
        
        # Fall back to base timeout
        logger.debug(f"Using base timeout for {target[0]}:{target[1]}: {self.ping_timeout:.2f}s")
        return self.ping_timeout
    
    def _get_indirect_probe_count(self, target: Tuple[str, int]) -> int:
        """
        Get the number of nodes to use for indirect probing.
        
        Args:
            target: The target address.
            
        Returns:
            The number of nodes to use for indirect probing.
        """
        # Use Lifeguard probe rate service if available
        if self.probe_rate_service and self.config.get("LIFEGUARD_ENABLED", True) and LIFEGUARD_AVAILABLE:
            peer_id = f"{target[0]}:{target[1]}"
            return self.probe_rate_service.get_probe_count(peer_id)
        
        # Otherwise use the traditional static count
        return self.config["INDIRECT_PROBE_COUNT"]
    
    def _update_rtt(self, target: Tuple[str, int], rtt: float) -> None:
        """
        Update RTT statistics for a target.
        
        Args:
            target: The target address.
            rtt: The measured round-trip time.
        """
        # Update member-specific RTT history
        member = self.members.get_member(target)
        if member:
            member.add_rtt_sample(rtt)
        
        # Update global RTT statistics
        self._global_rtts.append(rtt)
        
        # Periodically clean up old global RTT samples
        current_time = time.time()
        if current_time - self._last_rtt_cleanup > 60:  # Clean up every minute
            self._last_rtt_cleanup = current_time
            # Keep the most recent 1000 samples
            if len(self._global_rtts) > 1000:
                self._global_rtts = self._global_rtts[-1000:]
    
    async def ping(self, target: Tuple[str, int]) -> bool:
        """
        Send a direct ping to a target and wait for a response.
        
        Args:
            target: The address to ping.
        
        Returns:
            True if the ping was successful, False otherwise.
        """
        # Generate a unique ID for this ping operation
        ping_id = str(uuid.uuid4())[:8]
        
        # Check if we're already pinging this target
        target_key = f"{target[0]}:{target[1]}"
        if target_key in self._ping_in_progress:
            logger.debug(f"[{ping_id}] Ping already in progress for {target[0]}:{target[1]}")
            return True  # Assume success to avoid duplicate pings
        
        # Check if target is blacklisted in Lifeguard
        if self.probe_rate_service and self.config.get("LIFEGUARD_ENABLED", True) and LIFEGUARD_AVAILABLE:
            if self.probe_rate_service.is_blacklisted(target_key):
                logger.debug(f"[{ping_id}] Target {target_key} is blacklisted, skipping ping")
                return False
        
        self._ping_in_progress.add(target_key)
        
        try:
            # Prepare ping message
            local_addr = self.transport.local_address
            if not local_addr:
                raise RuntimeError("Transport not bound to an address")
            
            ping_msg = {
                "type": "PING",
                "from": f"{local_addr[0]}:{local_addr[1]}",
                "id": ping_id,
                "timestamp": time.time()  # For RTT calculation
            }
            
            # Calculate adaptive timeout using Lifeguard timing service if available
            timeout = self._calculate_timeout(target)
            
            logger.info(f"[{ping_id}] SENDING PING to {target[0]}:{target[1]} (timeout: {timeout:.2f}s)")
            
            # Calculate the number of retries, potentially based on awareness
            max_retries = self.config["PING_RETRIES"]
            
            # If Lifeguard awareness is available, adjust retries based on awareness
            if self.awareness_service and self.config.get("LIFEGUARD_ENABLED", True) and LIFEGUARD_AVAILABLE:
                awareness = self.awareness_service.get_awareness(target_key)
                # Low awareness members get more retries
                if awareness < 3:  # Low awareness
                    max_retries += 1
            
            # Try up to max_retries times
            for attempt in range(max_retries):
                try:
                    # Send ping
                    send_time = time.time()
                    await self.transport.send(serialize_message(ping_msg), target)
                    logger.debug(f"[{ping_id}] PING sent to {target[0]}:{target[1]} (attempt {attempt+1}/{max_retries})")
                    
                    # Wait for response, specifically a PONG message
                    try:
                        # Adjust timeout for subsequent attempts
                        current_timeout = timeout * (1.0 if attempt == 0 else 0.8)
                        
                        logger.debug(f"[{ping_id}] Waiting for PONG with timeout {current_timeout:.2f}s")
                        
                        # Wait for a PONG message specifically
                        data, addr = await self.transport.receive(timeout=current_timeout, msg_type="PONG")
                        
                        # Calculate RTT
                        receive_time = time.time()
                        rtt = receive_time - send_time
                        
                        # Parse response
                        response = deserialize_message(data)
                        response_id = response.get("id", "unknown")
                        
                        # Check if this is a PONG response from our target
                        if (addr[0] == target[0] and addr[1] == target[1] and
                            response.get("type") == "PONG"):
                            
                            logger.info(f"[{ping_id}] RECEIVED PONG from {target[0]}:{target[1]} (response_id: {response_id}, RTT: {rtt:.4f}s)")
                            
                            # Update RTT statistics
                            self._update_rtt(target, rtt)
                            
                            # Record successful ping in Lifeguard awareness if available
                            if self.awareness_service and self.config.get("LIFEGUARD_ENABLED", True) and LIFEGUARD_AVAILABLE:
                                self.awareness_service.record_success(target_key)
                            
                            # Record successful probe in Lifeguard probe rate service if available
                            if self.probe_rate_service and self.config.get("LIFEGUARD_ENABLED", True) and LIFEGUARD_AVAILABLE:
                                self.probe_rate_service.record_probe_result(target_key, True)
                                
                                # Adapt probe rate based on response time
                                self.probe_rate_service.adapt_rate(target_key, True, rtt)
                            
                            # Success! Check if we need to resurrect a DEAD member or just update heartbeat
                            member = self.members.get_member(target)
                            if member and member.is_dead:
                                # RESURRECTION: DEAD node is responding - mark as ALIVE with higher incarnation
                                new_incarnation = member.incarnation + 1
                                logger.info(f"[{ping_id}] RESURRECTION: DEAD member {target[0]}:{target[1]} responded to ping - resurrecting to ALIVE (inc: {member.incarnation} -> {new_incarnation})")
                                await self.members.mark_alive(target, incarnation=new_incarnation, recovery_method="ping_response")
                                logger.info(f"[{ping_id}] Successfully resurrected {target[0]}:{target[1]} from DEAD to ALIVE")
                            else:
                                # Normal case: Update heartbeat for ALIVE/SUSPECT members
                                logger.info(f"[{ping_id}] UPDATING heartbeat for {target[0]}:{target[1]}")
                                await self.members.update_heartbeat(target, rtt=rtt)
                                
                                # If member was SUSPECT, mark as ALIVE
                                if member and member.is_suspect:
                                    logger.info(f"[{ping_id}] RECOVERY: SUSPECT member {target[0]}:{target[1]} responded - marking as ALIVE")
                                    await self.members.mark_alive(target, recovery_method="ping_response")
                            
                            logger.info(f"[{ping_id}] Ping successful to {target[0]}:{target[1]}")
                            return True
                        else:
                            logger.debug(f"[{ping_id}] Received response is not a valid PONG from {target[0]}:{target[1]}, got from {addr[0]}:{addr[1]} of type {response.get('type', 'unknown')}")
                        
                    except asyncio.TimeoutError:
                        logger.warning(f"[{ping_id}] TIMEOUT waiting for PONG from {target[0]}:{target[1]} (attempt {attempt+1}/{max_retries})")
                        continue
                    
                except Exception as e:
                    logger.error(f"[{ping_id}] Error pinging {target[0]}:{target[1]}: {e}")
                    continue
            
            # All retries failed, mark as suspect
            logger.warning(f"[{ping_id}] All ping attempts failed to {target[0]}:{target[1]}, marking as SUSPECT")
            
            # Record failure in Lifeguard awareness if available
            if self.awareness_service and self.config.get("LIFEGUARD_ENABLED", True) and LIFEGUARD_AVAILABLE:
                self.awareness_service.record_failure(target_key)
            
            # Record failed probe in Lifeguard probe rate service if available
            if self.probe_rate_service and self.config.get("LIFEGUARD_ENABLED", True) and LIFEGUARD_AVAILABLE:
                self.probe_rate_service.record_probe_result(target_key, False)
            
            await self.members.mark_suspect(target)
            return False
            
        finally:
            # Remove from in-progress set
            self._ping_in_progress.discard(target_key)
    
    async def indirect_probe(self, target: Tuple[str, int]) -> bool:
        """
        Probe a target indirectly through other members.
        
        This is used when direct ping fails, to avoid false positives
        due to network issues between this node and the target.
        
        Args:
            target: The address to probe indirectly.
        
        Returns:
            True if any helper successfully reached the target, False otherwise.
        """
        # Determine how many helpers to use, possibly using Lifeguard
        probe_count = self._get_indirect_probe_count(target)
        
        # Get random members to help with the probe
        helpers = self.members.get_random_members(
            probe_count,
            exclude=[target]
        )
        
        if not helpers:
            logger.warning(f"No helpers available for indirect probe of {target[0]}:{target[1]}")
            return False
        
        # Prepare ping-req message
        local_addr = self.transport.local_address
        if not local_addr:
            raise RuntimeError("Transport not bound to an address")
        
        # Generate a unique ID for this operation
        probe_id = str(uuid.uuid4())[:8]
        
        ping_req_msg = {
            "type": "PING-REQ",
            "from": f"{local_addr[0]}:{local_addr[1]}",
            "target": f"{target[0]}:{target[1]}",
            "id": probe_id,
            "timestamp": time.time()  # For RTT calculation
        }
        
        target_key = f"{target[0]}:{target[1]}"
        logger.debug(f"[{probe_id}] Sending indirect probe for {target[0]}:{target[1]} via {len(helpers)} helpers")
        
        # Send ping-req to all helpers
        for helper in helpers:
            try:
                await self.transport.send(serialize_message(ping_req_msg), helper.addr)
                logger.debug(f"[{probe_id}] Sent PING-REQ to helper {helper.addr[0]}:{helper.addr[1]}")
            except Exception as e:
                logger.error(f"[{probe_id}] Error sending PING-REQ to helper {helper.addr[0]}:{helper.addr[1]}: {e}")
                continue
        
        # Wait for responses from helpers with appropriate timeout
        timeout = self._calculate_timeout(target) * 2  # Longer timeout for indirect probes
        
        try:
            # Use asyncio.wait_for to implement the timeout
            start_time = asyncio.get_event_loop().time()
            end_time = start_time + timeout
            
            while asyncio.get_event_loop().time() < end_time:
                try:
                    remaining = end_time - asyncio.get_event_loop().time()
                    
                    # Wait specifically for ACK responses
                    data, addr = await self.transport.receive(
                        timeout=remaining,
                        msg_type="PING-REQ-ACK"
                    )
                    
                    # Parse response
                    response = deserialize_message(data)
                    
                    # Check if this is a PING-REQ-ACK response
                    if response.get("type") == "PING-REQ-ACK":
                        # Check if it's about our target
                        resp_target = response.get("target")
                        if resp_target == f"{target[0]}:{target[1]}":
                            # Check the status
                            if response.get("status") == "alive":
                                # Target is alive according to this helper
                                logger.info(f"[{probe_id}] Indirect probe successful for {target[0]}:{target[1]} via {addr[0]}:{addr[1]}")
                                
                                # Record successful indirect probe in Lifeguard if available
                                if self.awareness_service and self.config.get("LIFEGUARD_ENABLED", True) and LIFEGUARD_AVAILABLE:
                                    self.awareness_service.record_success(target_key)
                                
                                if self.probe_rate_service and self.config.get("LIFEGUARD_ENABLED", True) and LIFEGUARD_AVAILABLE:
                                    self.probe_rate_service.record_probe_result(target_key, True)
                                
                                await self.members.mark_alive(target)
                                return True
                            
                            logger.debug(f"[{probe_id}] Helper {addr[0]}:{addr[1]} reported target as {response.get('status')}")
                
                except asyncio.TimeoutError:
                    # Timeout waiting for a response, continue until overall timeout
                    continue
                
        except Exception as e:
            logger.error(f"[{probe_id}] Error in indirect probe for {target[0]}:{target[1]}: {e}")
        
        logger.info(f"[{probe_id}] Indirect probe failed for {target[0]}:{target[1]}")
        
        # Record failed indirect probe in Lifeguard if available
        if self.awareness_service and self.config.get("LIFEGUARD_ENABLED", True) and LIFEGUARD_AVAILABLE:
            self.awareness_service.record_failure(target_key)
        
        if self.probe_rate_service and self.config.get("LIFEGUARD_ENABLED", True) and LIFEGUARD_AVAILABLE:
            self.probe_rate_service.record_probe_result(target_key, False)
        
        return False
    
    async def handle_ping(self, from_addr: Tuple[str, int], msg: Dict[str, Any]) -> None:
        """
        Handle a received PING message.
        
        Args:
            from_addr: The address that sent the ping.
            msg: The parsed ping message.
        """
        # Prepare PONG response
        local_addr = self.transport.local_address
        if not local_addr:
            raise RuntimeError("Transport not bound to an address")
        
        # Get the message ID if available
        msg_id = msg.get("id", "unknown")
        
        # Get the original timestamp if available
        orig_timestamp = msg.get("timestamp", time.time())
        
        pong_msg = {
            "type": "PONG",
            "from": f"{local_addr[0]}:{local_addr[1]}",
            "id": msg_id,  # Echo back the same ID
            "in_response_to": "PING",  # Explicitly mark what we're responding to
            "orig_timestamp": orig_timestamp,  # Echo back the original timestamp
            "timestamp": time.time()  # Add our own timestamp
        }
        
        logger.info(f"[{msg_id}] RECEIVED PING from {from_addr[0]}:{from_addr[1]}")
        
        # Record successful ping receipt in Lifeguard awareness if available
        if self.awareness_service and self.config.get("LIFEGUARD_ENABLED", True) and LIFEGUARD_AVAILABLE:
            peer_id = f"{from_addr[0]}:{from_addr[1]}"
            self.awareness_service.record_success(peer_id)
        
        # Send PONG back to the sender - do this immediately with minimal processing
        try:
            await self.transport.send(serialize_message(pong_msg), from_addr)
            logger.info(f"[{msg_id}] SENT PONG to {from_addr[0]}:{from_addr[1]}")
        except Exception as e:
            logger.error(f"[{msg_id}] Error sending PONG to {from_addr[0]}:{from_addr[1]}: {e}")
    
    async def handle_ping_req(self, from_addr: Tuple[str, int], msg: Dict[str, Any]) -> None:
        """
        Handle a received PING-REQ message.
        
        Args:
            from_addr: The address that sent the ping-req.
            msg: The parsed ping-req message.
        """
        # Extract target address
        target_str = msg.get("target")
        if not target_str:
            logger.warning(f"Received PING-REQ without target from {from_addr[0]}:{from_addr[1]}")
            return
        
        # Get the message ID if available
        msg_id = msg.get("id", "unknown")
        
        try:
            target_host, target_port_str = target_str.split(":")
            target_addr = (target_host, int(target_port_str))
        except (ValueError, TypeError):
            logger.warning(f"[{msg_id}] Invalid target address in PING-REQ: {target_str}")
            return
        
        # Check if target is blacklisted in Lifeguard
        target_key = f"{target_addr[0]}:{target_addr[1]}"
        if self.probe_rate_service and self.config.get("LIFEGUARD_ENABLED", True) and LIFEGUARD_AVAILABLE:
            if self.probe_rate_service.is_blacklisted(target_key):
                logger.debug(f"[{msg_id}] Target {target_key} is blacklisted, skipping indirect ping")
                
                # Send negative ACK immediately
                ack_msg = {
                    "type": "PING-REQ-ACK",
                    "from": f"{self.transport.local_address[0]}:{self.transport.local_address[1]}",
                    "target": target_str,
                    "status": "blacklisted",
                    "id": msg_id
                }
                
                try:
                    await self.transport.send(serialize_message(ack_msg), from_addr)
                except Exception as e:
                    logger.error(f"[{msg_id}] Error sending blacklist ACK to {from_addr[0]}:{from_addr[1]}: {e}")
                
                return
        
        # Prepare ping message to the target
        local_addr = self.transport.local_address
        if not local_addr:
            raise RuntimeError("Transport not bound to an address")
        
        ping_msg = {
            "type": "PING",
            "from": f"{local_addr[0]}:{local_addr[1]}",
            "ping_req_from": msg.get("from"),
            "id": msg_id,
            "timestamp": time.time()  # For RTT calculation
        }
        
        logger.debug(f"[{msg_id}] Received PING-REQ from {from_addr[0]}:{from_addr[1]} for {target_addr[0]}:{target_addr[1]}")
        
        # Calculate adaptive timeout for the target
        timeout = self._calculate_timeout(target_addr)
        
        # Try to ping the target
        try:
            # Send ping to target
            send_time = time.time()
            await self.transport.send(serialize_message(ping_msg), target_addr)
            logger.debug(f"[{msg_id}] Sent PING to target {target_addr[0]}:{target_addr[1]} (timeout: {timeout:.2f}s)")
            
            try:
                # Wait for response with timeout
                data, addr = await self.transport.receive(
                    timeout=timeout,
                    msg_type="PONG"
                )
                
                # Calculate RTT
                receive_time = time.time()
                rtt = receive_time - send_time
                
                # Parse response
                response = deserialize_message(data)
                
                # Check if this is a PONG response from the target
                if (addr[0] == target_addr[0] and addr[1] == target_addr[1] and
                    response.get("type") == "PONG"):
                    
                    logger.debug(f"[{msg_id}] Received valid PONG from target {target_addr[0]}:{target_addr[1]} (RTT: {rtt:.4f}s)")
                    
                    # Update RTT statistics
                    self._update_rtt(target_addr, rtt)
                    
                    # Record successful indirect ping in Lifeguard if available
                    if self.awareness_service and self.config.get("LIFEGUARD_ENABLED", True) and LIFEGUARD_AVAILABLE:
                        self.awareness_service.record_success(target_key)
                    
                    # Target is alive, send ACK back to the requester
                    ack_msg = {
                        "type": "PING-REQ-ACK",
                        "from": f"{local_addr[0]}:{local_addr[1]}",
                        "target": target_str,
                        "status": "alive",
                        "id": msg_id,
                        "rtt": rtt
                    }
                    
                    logger.debug(f"[{msg_id}] Target {target_addr[0]}:{target_addr[1]} is alive, sending ACK to {from_addr[0]}:{from_addr[1]}")
                    await self.transport.send(serialize_message(ack_msg), from_addr)
                    return
                else:
                    logger.debug(f"[{msg_id}] Received response is not a valid PONG from target")
                
            except asyncio.TimeoutError:
                logger.debug(f"[{msg_id}] Timeout waiting for PONG from {target_addr[0]}:{target_addr[1]}")
            
        except Exception as e:
            logger.error(f"[{msg_id}] Error in PING-REQ handling for {target_addr[0]}:{target_addr[1]}: {e}")
        
        # Target is unreachable, send negative ACK
        ack_msg = {
            "type": "PING-REQ-ACK",
            "from": f"{local_addr[0]}:{local_addr[1]}",
            "target": target_str,
            "status": "unreachable",
            "id": msg_id
        }
        
        logger.debug(f"[{msg_id}] Target {target_addr[0]}:{target_addr[1]} is unreachable, sending negative ACK to {from_addr[0]}:{from_addr[1]}")
        
        try:
            await self.transport.send(serialize_message(ack_msg), from_addr)
        except Exception as e:
            logger.error(f"[{msg_id}] Error sending negative ACK to {from_addr[0]}:{from_addr[1]}: {e}")