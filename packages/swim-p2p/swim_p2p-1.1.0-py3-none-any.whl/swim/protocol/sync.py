"""
Push-Pull synchronization for SWIM P2P.
This module implements the push-pull synchronization mechanism
for efficient state convergence in the SWIM protocol.
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


class SyncService:
    """
    Implements push-pull synchronization for efficient state convergence.
    
    This class handles periodic full-state exchanges between random peers
    and supports delta updates for incremental changes.
    """
    
    def __init__(
        self,
        transport: Transport,
        members: MemberList,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new sync service.
        
        Args:
            transport: The transport to use for sending/receiving messages.
            members: The member list to synchronize.
            config: Optional configuration parameters.
        """
        self.transport = transport
        self.members = members
        self.config = config or {}
        
        # Default configuration
        self.config.setdefault("FULL_SYNC_INTERVAL", 30.0)  # Seconds between full syncs
        self.config.setdefault("SYNC_FANOUT", 2)  # Number of nodes to sync with
        self.config.setdefault("SYNC_TIMEOUT", 5.0)  # Timeout for sync operations
        
        # Sync state
        self._running = False
        self._sync_task = None
        self._known_versions: Dict[Tuple[str, int], int] = {}
        self._last_full_sync = time.time()
        
        # Sync statistics
        self._sync_operations = 0
        self._sync_successes = 0
        self._sync_failures = 0
        
        logger.info("Sync service initialized")
    
    async def start(self) -> None:
        """
        Start the sync service.
        
        This method starts the periodic sync task.
        """
        if self._running:
            return
        
        self._running = True
        self._sync_task = asyncio.create_task(self._sync_loop())
        
        logger.info("Sync service started")
    
    async def stop(self) -> None:
        """
        Stop the sync service.
        
        This method stops the periodic sync task.
        """
        if not self._running:
            return
        
        self._running = False
        
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
            self._sync_task = None
        
        logger.info("Sync service stopped")
    
    async def _sync_loop(self) -> None:
        """
        Main sync loop.
        
        This method runs the push-pull synchronization periodically.
        """
        try:
            while self._running:
                try:
                    # Determine if we should do a full sync
                    current_time = time.time()
                    do_full_sync = (current_time - self._last_full_sync) > self.config["FULL_SYNC_INTERVAL"]
                    
                    if do_full_sync:
                        self._last_full_sync = current_time
                        await self._perform_full_sync()
                    else:
                        await self._perform_incremental_sync()
                    
                    # Sleep until next sync
                    await asyncio.sleep(self.config["FULL_SYNC_INTERVAL"] / 10)  # More frequent incremental syncs
                    
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.error(f"Error in sync loop: {e}")
                    await asyncio.sleep(1.0)  # Avoid tight loop on errors
        
        except asyncio.CancelledError:
            logger.debug("Sync loop cancelled")
    
    async def _perform_full_sync(self) -> None:
        """
        Perform a full state synchronization with random peers.
        
        This method selects random peers and initiates a full state exchange.
        """
        # Generate a unique ID for this sync operation
        sync_id = str(uuid.uuid4())[:8]
        
        # Get random members to sync with
        targets = self.members.get_random_members(self.config["SYNC_FANOUT"])
        if not targets:
            logger.debug(f"[{sync_id}] No targets available for full sync")
            return
        
        logger.info(f"[{sync_id}] Performing full sync with {len(targets)} members")
        
        # Prepare sync request message
        local_addr = self.transport.local_address
        if not local_addr:
            raise RuntimeError("Transport not bound to an address")
        
        for target in targets:
            try:
                # Create sync request message
                sync_req_msg = {
                    "type": "SYNC-REQ",
                    "from": f"{local_addr[0]}:{local_addr[1]}",
                    "id": sync_id,
                    "known_version": 0,  # 0 indicates full sync
                    "timestamp": time.time()
                }
                
                logger.debug(f"[{sync_id}] Sending full sync request to {target.addr[0]}:{target.addr[1]}")
                
                # Send sync request
                await self.transport.send(serialize_message(sync_req_msg), target.addr)
                self._sync_operations += 1
                
            except Exception as e:
                logger.error(f"[{sync_id}] Error sending full sync request to {target.addr[0]}:{target.addr[1]}: {e}")
                self._sync_failures += 1
    
    async def _perform_incremental_sync(self) -> None:
        """
        Perform an incremental state synchronization with random peers.
        
        This method selects random peers and initiates an incremental state exchange.
        """
        # Generate a unique ID for this sync operation
        sync_id = str(uuid.uuid4())[:8]
        
        # Get random members to sync with
        targets = self.members.get_random_members(1)  # Just one target for incremental sync
        if not targets:
            return
        
        target = targets[0]
        
        # Prepare sync request message
        local_addr = self.transport.local_address
        if not local_addr:
            raise RuntimeError("Transport not bound to an address")
        
        try:
            # Get the target's known version
            known_version = self._known_versions.get(target.addr, 0)
            
            # Create sync request message
            sync_req_msg = {
                "type": "SYNC-REQ",
                "from": f"{local_addr[0]}:{local_addr[1]}",
                "id": sync_id,
                "known_version": known_version,
                "timestamp": time.time()
            }
            
            logger.debug(f"[{sync_id}] Sending incremental sync request to {target.addr[0]}:{target.addr[1]} (known version: {known_version})")
            
            # Send sync request
            await self.transport.send(serialize_message(sync_req_msg), target.addr)
            self._sync_operations += 1
            
        except Exception as e:
            logger.error(f"[{sync_id}] Error sending incremental sync request to {target.addr[0]}:{target.addr[1]}: {e}")
            self._sync_failures += 1
    
    async def handle_message(self, from_addr: Tuple[str, int], raw_msg: bytes) -> None:
        """
        Handle a received sync message.
        
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
        
        if msg_type == "SYNC-REQ":
            await self._handle_sync_req(from_addr, msg)
        elif msg_type == "SYNC-RESP":
            await self._handle_sync_resp(from_addr, msg)
        else:
            logger.debug(f"[{msg_id}] Ignoring unknown message type: {msg_type}")
    
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
        
        # Prepare sync response with appropriate state
        local_addr = self.transport.local_address
        if not local_addr:
            raise RuntimeError("Transport not bound to an address")
        
        # Create digest based on known version
        if known_version == 0:
            # Full sync requested
            digest = self.members.serialize_digest(full=True)
            logger.debug(f"[{msg_id}] Sending full state to {from_addr[0]}:{from_addr[1]} ({len(digest['entries'])} entries)")
        else:
            # Incremental sync requested
            digest = self.members.serialize_digest(full=False, since_version=known_version)
            logger.debug(f"[{msg_id}] Sending delta state to {from_addr[0]}:{from_addr[1]} ({len(digest['entries'])} entries)")
        
        # Create sync response message
        sync_resp_msg = {
            "type": "SYNC-RESP",
            "from": f"{local_addr[0]}:{local_addr[1]}",
            "id": msg_id,
            "digest": digest,
            "timestamp": time.time()
        }
        
        try:
            # Send sync response
            await self.transport.send(serialize_message(sync_resp_msg), from_addr)
            logger.debug(f"[{msg_id}] Sent SYNC-RESP to {from_addr[0]}:{from_addr[1]}")
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
            is_full = digest.get("is_full", False)
            
            if is_full:
                logger.info(f"[{msg_id}] Processing full sync response with {len(entries)} entries from {from_addr[0]}:{from_addr[1]} (version: {version})")
            else:
                logger.info(f"[{msg_id}] Processing incremental sync response with {len(entries)} entries from {from_addr[0]}:{from_addr[1]} (version: {version})")
            
            # Merge the digest into our membership list
            before_states = {member.addr: member.state for member in self.members.get_all_members()}
            await self.members.merge_digest(digest)
            after_states = {member.addr: member.state for member in self.members.get_all_members()}
            
            # Log state changes resulting from the sync
            changes = 0
            for addr, after_state in after_states.items():
                if addr in before_states:
                    if before_states[addr] != after_state:
                        # State changed due to the sync
                        logger.info(f"[{msg_id}] Member {addr[0]}:{addr[1]} state changed from "
                                  f"{before_states[addr].name} to {after_state.name} due to sync")
                        changes += 1
                else:
                    # New member from the sync
                    logger.info(f"[{msg_id}] New member {addr[0]}:{addr[1]} in state {after_state.name} added from sync")
                    changes += 1
            
            # Check for members in our list not in the sync (potential removals)
            for addr in before_states:
                if addr not in after_states:
                    logger.info(f"[{msg_id}] Member {addr[0]}:{addr[1]} in our list but not in the sync")
                    changes += 1
            
            logger.debug(f"[{msg_id}] Completed sync with {from_addr[0]}:{from_addr[1]} ({changes} changes)")
            
            # Update statistics
            self._sync_successes += 1
            
        else:
            logger.warning(f"[{msg_id}] Received SYNC-RESP without digest from {from_addr[0]}:{from_addr[1]}")
            self._sync_failures += 1