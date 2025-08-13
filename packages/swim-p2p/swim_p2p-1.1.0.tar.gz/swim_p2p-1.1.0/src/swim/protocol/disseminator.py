"""
Gossip dissemination for SWIM P2P.
This module implements the gossip-based dissemination mechanism
for the SWIM protocol, piggybacking membership updates on heartbeats,
with push-pull synchronization for efficient state convergence.
"""

import asyncio
import logging
import random
import uuid
import time
from typing import Dict, List, Optional, Tuple, Any, Set

from swim.transport.base import Transport
from swim.protocol.member import MemberList, MemberState
from swim.utils.serialization import serialize_message, deserialize_message

logger = logging.getLogger(__name__)


class GossipService:
    """
    Implements the SWIM gossip dissemination mechanism with push-pull sync.
    
    This class handles sending heartbeats with piggybacked membership
    updates and processing incoming gossip messages. It also implements
    push-pull synchronization for efficient state convergence.
    """
    
    def __init__(
        self,
        transport: Transport,
        members: MemberList,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new gossip service.
        
        Args:
            transport: The transport to use for sending/receiving messages.
            members: The member list to disseminate and update.
            config: Optional configuration parameters.
        """
        self.transport = transport
        self.members = members
        self.config = config or {}
        
        # Default configuration
        self.config.setdefault("GOSSIP_FANOUT", 3)
        self.config.setdefault("GOSSIP_FANOUT_FACTOR", 0.5)  # Adjust fanout based on cluster size
        self.config.setdefault("FULL_SYNC_INTERVAL", 30.0)  # Seconds between full syncs
        self.config.setdefault("PUSH_PULL_SYNC_ENABLED", True)
        self.config.setdefault("PUSH_PULL_SYNC_PROBABILITY", 0.2)  # Probability of initiating push-pull
        
        # Track gossip statistics
        self._gossip_sent = 0
        self._gossip_received = 0
        self._last_full_sync = time.time()
        
        # Track known versions of other nodes
        self._known_versions: Dict[Tuple[str, int], int] = {}
        
        logger.info("Gossip service initialized with push-pull synchronization")
    
    def _calculate_fanout(self) -> int:
        """
        Calculate the gossip fanout based on cluster size.
        
        Returns:
            The number of nodes to gossip to.
        """
        cluster_size = len(self.members.get_all_members())
        
        # Base fanout
        fanout = self.config["GOSSIP_FANOUT"]
        
        # Adjust based on cluster size
        if cluster_size > 10:
            # Logarithmic scaling with cluster size
            import math
            fanout = max(
                fanout,
                min(
                    int(math.log2(cluster_size) * self.config["GOSSIP_FANOUT_FACTOR"]),
                    cluster_size // 4  # Cap at 25% of cluster size
                )
            )
        
        return max(1, fanout)  # Ensure at least 1
    
    async def send_heartbeat(self) -> None:
        """
        Send heartbeat messages to random members with piggybacked digest.
        
        This method selects random members and sends them a heartbeat message
        containing the local membership digest. It also initiates push-pull
        synchronization periodically.
        """
        # Generate a unique ID for this gossip operation
        gossip_id = str(uuid.uuid4())[:8]
        
        # Calculate fanout
        fanout = self._calculate_fanout()
        
        # Get random members to gossip to
        targets = self.members.get_random_members(fanout)
        if not targets:
            logger.debug(f"[{gossip_id}] No targets available for gossip")
            return
        
        # Prepare heartbeat message with digest
        local_addr = self.transport.local_address
        if not local_addr:
            raise RuntimeError("Transport not bound to an address")
        
        # Determine if we should do a full sync
        current_time = time.time()
        do_full_sync = (current_time - self._last_full_sync) > self.config["FULL_SYNC_INTERVAL"]
        
        if do_full_sync:
            self._last_full_sync = current_time
            logger.debug(f"[{gossip_id}] Performing full sync")
        
        # Create digest of member states
        digest = self.members.serialize_digest(full=do_full_sync)
        
        heartbeat_msg = {
            "type": "HEARTBEAT",
            "from": f"{local_addr[0]}:{local_addr[1]}",
            "digest": digest,
            "id": gossip_id,
            "timestamp": time.time()
        }
        
        # Serialize once for efficiency
        serialized_msg = serialize_message(heartbeat_msg)
        
        logger.info(f"[{gossip_id}] SENDING heartbeats to {len(targets)} members with {len(digest['entries'])} membership entries")
        
        # Log metadata being sent in heartbeats
        for entry in digest["entries"]:
            if entry.get("metadata", {}).get("agent_capabilities"):
                caps = entry["metadata"]["agent_capabilities"]
                logger.info(f"[{gossip_id}] SENDING capabilities:")
                logger.info(f"   - agent_id: {caps.get('agent_id')}")
                logger.info(f"   - supported_action_types: {caps.get('supported_action_types')}")
                logger.info(f"   - workload: {caps.get('current_workload', 0)}, healthy: {caps.get('healthy', True)}")
        
        # Log digest details at debug level
        if logger.isEnabledFor(logging.DEBUG):
            for entry in digest["entries"]:
                logger.debug(f"[{gossip_id}] Digest entry: {entry['addr']} - {entry['state']} (inc={entry['incarnation']})")
        
        # Send to all targets
        for target in targets:
            try:
                await self.transport.send(serialized_msg, target.addr)
                self._gossip_sent += 1
                logger.debug(f"[{gossip_id}] Heartbeat sent to {target.addr[0]}:{target.addr[1]} "
                           f"(total sent: {self._gossip_sent})")
                
                # Randomly initiate push-pull sync
                if (self.config["PUSH_PULL_SYNC_ENABLED"] and 
                    random.random() < self.config["PUSH_PULL_SYNC_PROBABILITY"]):
                    await self._initiate_push_pull_sync(target.addr, gossip_id)
                
            except Exception as e:
                logger.error(f"[{gossip_id}] Error sending heartbeat to {target.addr[0]}:{target.addr[1]}: {e}")
                continue
    
    async def _initiate_push_pull_sync(self, target: Tuple[str, int], sync_id: str) -> None:
        """
        Initiate push-pull synchronization with a target.
        
        Args:
            target: The address to sync with.
            sync_id: The ID for this sync operation.
        """
        local_addr = self.transport.local_address
        if not local_addr:
            raise RuntimeError("Transport not bound to an address")
        
        # Get the target's known version
        target_key = f"{target[0]}:{target[1]}"
        known_version = self._known_versions.get(target, 0)
        
        # Create sync request message
        sync_req_msg = {
            "type": "SYNC-REQ",
            "from": f"{local_addr[0]}:{local_addr[1]}",
            "id": sync_id,
            "known_version": known_version,
            "timestamp": time.time()
        }
        
        logger.debug(f"[{sync_id}] Initiating push-pull sync with {target[0]}:{target[1]} (known version: {known_version})")
        
        try:
            await self.transport.send(serialize_message(sync_req_msg), target)
        except Exception as e:
            logger.error(f"[{sync_id}] Error sending sync request to {target[0]}:{target[1]}: {e}")
    
    async def handle_message(self, from_addr: Tuple[str, int], raw_msg: bytes) -> None:
        """
        Handle a received gossip message.
        
        Args:
            from_addr: The address that sent the message.
            raw_msg: The raw message bytes.
        """
        try:
            msg = deserialize_message(raw_msg)
        except Exception as e:
            logger.warning(f"Error deserializing message from {from_addr[0]}:{from_addr[1]}: {e}")
            return
        
        msg_type = msg.get("type")
        msg_id = msg.get("id", "unknown")
        
        if msg_type == "HEARTBEAT":
            await self._handle_heartbeat(from_addr, msg)
        elif msg_type == "SYNC-REQ":
            await self._handle_sync_req(from_addr, msg)
        elif msg_type == "SYNC-RESP":
            await self._handle_sync_resp(from_addr, msg)
        else:
            logger.debug(f"[{msg_id}] Ignoring unknown message type: {msg_type}")
    
    async def _handle_heartbeat(self, from_addr: Tuple[str, int], msg: Dict[str, Any]) -> None:
        """
        Handle a received HEARTBEAT message.
        
        Args:
            from_addr: The address that sent the heartbeat.
            msg: The parsed heartbeat message.
        """
        # Get message ID
        msg_id = msg.get("id", "unknown")
        
        # Update sender's heartbeat
        logger.info(f"[{msg_id}] RECEIVED heartbeat from {from_addr[0]}:{from_addr[1]}")
        await self.members.update_heartbeat(from_addr)
        
        # Process digest
        digest = msg.get("digest")
        if digest:
            # Update known version for this node
            version = digest.get("version", 0)
            self._known_versions[from_addr] = version
            
            entries = digest.get("entries", [])
            logger.info(f"[{msg_id}] Processing member digest with {len(entries)} entries from {from_addr[0]}:{from_addr[1]} (version: {version})")
            
            # Log metadata being received in heartbeats
            for entry in entries:
                if entry.get("metadata", {}).get("agent_capabilities"):
                    caps = entry["metadata"]["agent_capabilities"]
                    logger.info(f"[{msg_id}] RECEIVED heartbeat from {from_addr[0]}:{from_addr[1]}")
                    logger.info(f"GOSSIP METADATA: Merged capabilities for {entry['addr']}: {{")
                    logger.info(f"  'agent_id': '{caps.get('agent_id')}',")
                    logger.info(f"  'supported_action_types': {caps.get('supported_action_types')},")
                    logger.info(f"  'current_workload': {caps.get('current_workload', 0)},")
                    logger.info(f"  'healthy': {caps.get('healthy', True)}")
                    logger.info(f"}}")
            
            # Log digest details at debug level
            if logger.isEnabledFor(logging.DEBUG):
                for entry in entries:
                    logger.debug(f"[{msg_id}] Digest entry: {entry['addr']} - {entry['state']} (inc={entry['incarnation']})")
            
            # Track statistics
            self._gossip_received += 1
            
            # Merge the digest into our membership list
            before_states = {member.addr: member.state for member in self.members.get_all_members()}
            await self.members.merge_digest(digest)
            after_states = {member.addr: member.state for member in self.members.get_all_members()}
            
            # Log state changes resulting from the digest
            for addr, after_state in after_states.items():
                if addr in before_states:
                    if before_states[addr] != after_state:
                        # State changed due to the digest
                        logger.info(f"[{msg_id}] Member {addr[0]}:{addr[1]} state changed from "
                                  f"{before_states[addr].name} to {after_state.name} due to digest")
                else:
                    # New member from the digest
                    logger.info(f"[{msg_id}] New member {addr[0]}:{addr[1]} in state {after_state.name} added from digest")
                    
            # Check for members in our list not in the digest (potential removals)
            for addr in before_states:
                if addr not in after_states:
                    logger.info(f"[{msg_id}] Member {addr[0]}:{addr[1]} in our list but not in the digest")
                    
        else:
            logger.warning(f"[{msg_id}] Received HEARTBEAT without digest from {from_addr[0]}:{from_addr[1]}")
    
    async def _handle_sync_req(self, from_addr: Tuple[str, int], msg: Dict[str, Any]) -> None:
        """
        Handle a received SYNC-REQ message.
        
        Args:
            from_addr: The address that sent the sync request.
            msg: The parsed sync request message.
        """
        # Get message ID
        msg_id = msg.get("id", "unknown")
        
        # Get the requester's known version
        known_version = msg.get("known_version", 0)
        
        logger.debug(f"[{msg_id}] Received SYNC-REQ from {from_addr[0]}:{from_addr[1]} (known version: {known_version})")
        
        # Prepare sync response with deltas since the known version
        local_addr = self.transport.local_address
        if not local_addr:
            raise RuntimeError("Transport not bound to an address")
        
        # Create digest with deltas
        digest = self.members.serialize_digest(full=False, since_version=known_version)
        
        sync_resp_msg = {
            "type": "SYNC-RESP",
            "from": f"{local_addr[0]}:{local_addr[1]}",
            "id": msg_id,
            "digest": digest,
            "timestamp": time.time()
        }
        
        logger.debug(f"[{msg_id}] Sending SYNC-RESP to {from_addr[0]}:{from_addr[1]} with {len(digest['entries'])} entries")
        
        try:
            await self.transport.send(serialize_message(sync_resp_msg), from_addr)
        except Exception as e:
            logger.error(f"[{msg_id}] Error sending sync response to {from_addr[0]}:{from_addr[1]}: {e}")
    
    async def _handle_sync_resp(self, from_addr: Tuple[str, int], msg: Dict[str, Any]) -> None:
        """
        Handle a received SYNC-RESP message.
        
        Args:
            from_addr: The address that sent the sync response.
            msg: The parsed sync response message.
        """
        # Get message ID
        msg_id = msg.get("id", "unknown")
        
        # Process digest
        digest = msg.get("digest")
        if digest:
            # Update known version for this node
            version = digest.get("version", 0)
            self._known_versions[from_addr] = version
            
            entries = digest.get("entries", [])
            logger.info(f"[{msg_id}] Processing sync response with {len(entries)} entries from {from_addr[0]}:{from_addr[1]} (version: {version})")
            
            # Merge the digest into our membership list
            await self.members.merge_digest(digest)
            
            logger.debug(f"[{msg_id}] Completed push-pull sync with {from_addr[0]}:{from_addr[1]}")
        else:
            logger.warning(f"[{msg_id}] Received SYNC-RESP without digest from {from_addr[0]}:{from_addr[1]}")


    def debug_gossip_knowledge(self) -> None:
        """
        Debug method to show what this node knows about other agents via gossip.
        Call this to verify gossip is working.
        """
        logger.info("=== GOSSIP KNOWLEDGE DUMP ===")
        local_addr = self.transport.local_address
        logger.info(f"Local node: {local_addr[0]}:{local_addr[1]}")
        
        all_members = self.members.get_all_members()
        logger.info(f"Total known members: {len(all_members)}")
        
        for member in all_members:
            logger.info(f"Member: {member.addr[0]}:{member.addr[1]} (state: {member.state.name})")
            
            if hasattr(member, 'metadata') and member.metadata:
                logger.info(f"  Raw metadata: {member.metadata}")
                
                if 'agent_capabilities' in member.metadata:
                    caps = member.metadata['agent_capabilities']
                    agent_id = caps.get('agent_id', 'unknown')
                    action_types = caps.get('supported_action_types', [])
                    logger.info(f"Agent: {agent_id}, Actions: {action_types}")
                else:
                    logger.info("No agent_capabilities in metadata")
            else:
                logger.info("No metadata at all")
        
        logger.info("=== END GOSSIP DUMP ===")
    
    def find_agent_for_action_type_debug(self, action_type: str) -> Optional[str]:
        """
        Debug version of agent discovery that logs the search process.
        """
        logger.info(f"SEARCHING for agent that handles action_type: {action_type}")
        
        for member in self.members.get_all_members():
            logger.debug(f"Checking member {member.addr[0]}:{member.addr[1]}")
            
            if hasattr(member, 'metadata') and member.metadata:
                if 'agent_capabilities' in member.metadata:
                    caps = member.metadata['agent_capabilities']
                    supported_types = caps.get('supported_action_types', [])
                    
                    logger.debug(f"  Agent {caps.get('agent_id')} supports: {supported_types}")
                    
                    if action_type in supported_types:
                        agent_id = caps.get('agent_id', f"{member.addr[0]}:{member.addr[1]}")
                        logger.info(f"FOUND: Agent {agent_id} handles {action_type}")
                        return agent_id
        
        logger.info(f"NOT FOUND: No agent handles {action_type}")
        return None
