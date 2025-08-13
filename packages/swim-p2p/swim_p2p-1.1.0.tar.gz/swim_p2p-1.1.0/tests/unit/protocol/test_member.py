"""
Unit tests for the membership model.
"""

import pytest
import asyncio
import time
from swim.protocol.member import Member, MemberState, MemberList


def test_member_state_enum():
    """Test that MemberState enum has the expected values."""
    assert hasattr(MemberState, "ALIVE")
    assert hasattr(MemberState, "SUSPECT")
    assert hasattr(MemberState, "DEAD")


def test_member_creation():
    """Test creating a Member with default values."""
    addr = ("127.0.0.1", 8000)
    member = Member(addr=addr)
    
    assert member.addr == addr
    assert member.state == MemberState.ALIVE
    assert member.incarnation == 1
    assert member.last_heartbeat > 0
    assert member.last_state_change > 0
    assert isinstance(member.rtt_history, list)
    assert len(member.rtt_history) == 0


def test_member_rtt_tracking():
    """Test RTT tracking functionality in Member."""
    addr = ("127.0.0.1", 8000)
    member = Member(addr=addr)
    
    # Add some RTT samples
    member.add_rtt_sample(0.1)
    member.add_rtt_sample(0.2)
    member.add_rtt_sample(0.3)
    
    # Check RTT history
    assert len(member.rtt_history) == 3
    assert member.rtt_history == [0.1, 0.2, 0.3]
    
    # Check average RTT - use pytest.approx for floating point comparison
    assert member.get_average_rtt() == pytest.approx(0.2)
    
    # Check percentile RTT
    assert member.get_percentile_rtt(0.5) == pytest.approx(0.2)  # Median
    assert member.get_percentile_rtt(1.0) == pytest.approx(0.3)  # Max
    
    # Check max samples limit
    for i in range(10):
        member.add_rtt_sample(0.1)
    
    assert len(member.rtt_history) == 10  # Default max_samples is 10


def test_member_state_transition():
    """Test transitioning a member through different states."""
    addr = ("127.0.0.1", 8000)
    member = Member(addr=addr)
    
    # Initial state
    assert member.state == MemberState.ALIVE
    
    # Transition to SUSPECT
    old_state_change = member.last_state_change
    time.sleep(0.001)  # Ensure time difference
    member.state = MemberState.SUSPECT
    assert member.state == MemberState.SUSPECT
    assert member.last_state_change == old_state_change  # Not updated by direct assignment
    
    # Transition to DEAD
    member.state = MemberState.DEAD
    assert member.state == MemberState.DEAD
    
    # Transition back to ALIVE
    old_heartbeat = member.last_heartbeat
    time.sleep(0.001)  # Ensure time difference
    member.state = MemberState.ALIVE
    assert member.state == MemberState.ALIVE
    assert member.last_heartbeat == old_heartbeat  # Heartbeat not updated by direct state change


@pytest.mark.asyncio
async def test_memberlist_operations():
    """Test basic MemberList operations."""
    self_addr = ("127.0.0.1", 8000)
    member_list = MemberList(self_addr)
    
    # Self should be in the list
    assert member_list.self_addr == self_addr
    assert member_list.get_member(self_addr) is not None
    
    # Add a new member
    other_addr = ("127.0.0.1", 8001)
    member_list.add_member(other_addr)
    
    # Check it was added
    assert member_list.get_member(other_addr) is not None
    assert member_list.get_member(other_addr).state == MemberState.ALIVE
    
    # Update heartbeat
    old_heartbeat = member_list.get_member(other_addr).last_heartbeat
    time.sleep(0.001)  # Ensure time difference
    await member_list.update_heartbeat(other_addr)
    assert member_list.get_member(other_addr).last_heartbeat > old_heartbeat
    
    # Mark as suspect
    await member_list.mark_suspect(other_addr)
    assert member_list.get_member(other_addr).state == MemberState.SUSPECT
    
    # Mark as dead
    await member_list.mark_dead(other_addr)
    assert member_list.get_member(other_addr).state == MemberState.DEAD
    
    # Remove member
    member_list.remove_member(other_addr)
    assert member_list.get_member(other_addr) is None


def test_memberlist_get_random_members():
    """Test getting random members from the list."""
    self_addr = ("127.0.0.1", 8000)
    member_list = MemberList(self_addr)
    
    # Add several members
    for port in range(8001, 8011):
        member_list.add_member(("127.0.0.1", port))
    
    # Get 3 random members
    random_members = member_list.get_random_members(3)
    assert len(random_members) == 3
    
    # All should be unique
    addrs = [m.addr for m in random_members]
    assert len(set(addrs)) == 3
    
    # Get more than available (should return all except self)
    all_members = member_list.get_random_members(20)
    assert len(all_members) == 10  # 11 total - 1 self
    
    # Get with exclusion
    exclude_addr = ("127.0.0.1", 8001)
    filtered_members = member_list.get_random_members(5, exclude=[exclude_addr])
    assert len(filtered_members) == 5
    assert all(m.addr != exclude_addr for m in filtered_members)


@pytest.mark.asyncio
async def test_memberlist_delta_tracking():
    """Test delta tracking for efficient state synchronization."""
    list1 = MemberList(("127.0.0.1", 8000))
    
    # Initial version should be 1 (after adding self)
    initial_version = list1._version
    assert initial_version == 1
    
    # Add a member and check version increment
    list1.add_member(("127.0.0.1", 8001))
    assert list1._version == initial_version + 1
    
    # Mark as suspect and check version increment
    await list1.mark_suspect(("127.0.0.1", 8001))
    assert list1._version == initial_version + 2
    
    # Get deltas since initial version
    deltas = list1.get_deltas_since(initial_version)
    assert len(deltas) == 1
    assert ("127.0.0.1", 8001) in deltas
    
    # Get deltas since current version (should be empty)
    deltas = list1.get_deltas_since(list1._version)
    assert len(deltas) == 0


@pytest.mark.asyncio
async def test_memberlist_digest_serialization():
    """Test serializing and merging member list digests."""
    list1 = MemberList(("127.0.0.1", 8000))
    list1.add_member(("127.0.0.1", 8001))
    list1.add_member(("127.0.0.1", 8002))
    
    # Serialize digest (full)
    digest = list1.serialize_digest(full=True)
    
    # Verify digest structure
    assert "version" in digest
    assert "entries" in digest
    assert "is_full" in digest
    assert digest["is_full"] is True
    assert len(digest["entries"]) == 3  # Self + 2 members
    
    for entry in digest["entries"]:
        assert "addr" in entry
        assert "state" in entry
        assert "incarnation" in entry
    
    # Create a new list and merge the digest
    list2 = MemberList(("127.0.0.1", 9000))
    await list2.merge_digest(digest)
    
    # Verify members were added
    assert list2.get_member(("127.0.0.1", 8000)) is not None
    assert list2.get_member(("127.0.0.1", 8001)) is not None
    assert list2.get_member(("127.0.0.1", 8002)) is not None
    
    # Test incremental digest
    await list1.mark_suspect(("127.0.0.1", 8001))
    incremental_digest = list1.serialize_digest(full=False, since_version=digest["version"])
    
    # Verify incremental digest only contains the changed member
    assert len(incremental_digest["entries"]) == 1
    assert incremental_digest["entries"][0]["addr"] == "127.0.0.1:8001"
    assert incremental_digest["entries"][0]["state"] == "SUSPECT"


@pytest.mark.asyncio
async def test_memberlist_conflict_resolution():
    """Test conflict resolution when merging digests."""
    # Create two lists with the same member but different states
    list1 = MemberList(("127.0.0.1", 8000))
    member_addr = ("127.0.0.1", 8001)
    list1.add_member(member_addr)
    
    list2 = MemberList(("127.0.0.1", 9000))
    list2.add_member(member_addr)
    
    # Mark as suspect in list1 with higher incarnation
    await list1.mark_suspect(member_addr)
    member1 = list1.get_member(member_addr)
    member1.incarnation = 5
    
    # Serialize digest from list1
    digest1 = list1.serialize_digest()
    
    # Merge into list2
    await list2.merge_digest(digest1)
    
    # Verify list2 now has the member as suspect
    member2 = list2.get_member(member_addr)
    assert member2.state == MemberState.SUSPECT
    assert member2.incarnation == 5
    
    # Now mark as alive in list2 with higher incarnation
    await list2.mark_alive(member_addr)
    member2 = list2.get_member(member_addr)
    member2.incarnation = 6
    
    # Serialize digest from list2
    digest2 = list2.serialize_digest()
    
    # Merge back into list1
    await list1.merge_digest(digest2)
    
    # Verify list1 now has the member as alive
    member1 = list1.get_member(member_addr)
    assert member1.state == MemberState.ALIVE
    assert member1.incarnation == 6