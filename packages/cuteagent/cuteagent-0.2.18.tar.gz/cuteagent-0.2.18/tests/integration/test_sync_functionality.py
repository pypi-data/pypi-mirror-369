#!/usr/bin/env python3
"""
Test script for StationAgent sync functionality with LangGraph integration.

This script tests the sync methods without requiring real API access.
"""

import sys
import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch

# Add the cuteagent module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cuteagent'))

from cuteagent import StationAgent

@dataclass
class MockLangGraphState:
    """Mock LangGraph state for testing."""
    current_node: float = 0
    user_input: str = ""
    stationThreadId: str = "test-station"
    sharedState: Optional[Dict[str, Any]] = field(default_factory=dict)

def test_sync_functionality():
    """Test all sync methods with mock data."""
    print("🧪 Testing StationAgent Sync Functionality")
    print("=" * 60)
    
    # Create agent and mock state
    agent = StationAgent("test-station", "test-graph", "test-token")
    mock_state = MockLangGraphState()
    
    print("✅ Created StationAgent and mock LangGraph state")
    print(f"   Initial sharedState: {mock_state.sharedState}")
    print()
    
    # Test 1: sync() method with individual variable - NEW PATTERN
    print("🔍 Test 1: sync() method with individual variable (NEW PATTERN)")
    with patch.object(agent.state, 'get') as mock_get:
        mock_get.return_value = "processing"
        
        # NEW PATTERN: state = agent.state.sync("variable", state)
        mock_state = agent.state.sync("currentStep", mock_state)
        
        print(f"   Returned state type: {type(mock_state)}")
        print(f"   LangGraph sharedState: {mock_state.sharedState}")
        
        # Verify
        expected = {"currentStep": "processing"}
        success = mock_state.sharedState == expected
        print(f"   ✅ SUCCESS: {success}")
        
        # Test sync without LangGraph state (backward compatibility)
        result2 = agent.state.sync("currentStep")
        print(f"   Backward compatibility (no state): {result2}")
        print()
    
    # Test 2: sync_multiple() method - NEW PATTERN
    print("🔍 Test 2: sync_multiple() method (NEW PATTERN)")
    with patch.object(agent.state, 'get') as mock_get:
        # Mock multiple get calls
        def mock_get_side_effect(var_name):
            mock_data = {
                "userPreferences": {"theme": "dark", "language": "en"},
                "progress": 0.75,
                "isProcessing": True
            }
            return mock_data.get(var_name)
        
        mock_get.side_effect = mock_get_side_effect
        
        # Reset state for clean test
        mock_state.sharedState = {}
        
        variables_to_sync = ["userPreferences", "progress", "isProcessing"]
        # NEW PATTERN: state = agent.state.sync_multiple(["var1", "var2"], state)
        mock_state = agent.state.sync_multiple(variables_to_sync, mock_state)
        
        print(f"   Returned state type: {type(mock_state)}")
        print(f"   LangGraph sharedState: {mock_state.sharedState}")
        
        # Verify
        expected = {
            "userPreferences": {"theme": "dark", "language": "en"},
            "progress": 0.75,
            "isProcessing": True
        }
        success = mock_state.sharedState == expected
        print(f"   ✅ SUCCESS: {success}")
        print()
    
    # Test 3: sync_all() method - NEW PATTERN
    print("🔍 Test 3: sync_all() method (NEW PATTERN)")
    with patch.object(agent.state, 'pull') as mock_pull:
        all_vars = {
            "server": "idle",
            "serverThread": "idle", 
            "currentStep": "completed",
            "workflowId": "wf-12345",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        mock_pull.return_value = all_vars
        
        # Reset state for clean test
        mock_state.sharedState = {}
        
        # NEW PATTERN: state = agent.state.sync_all(state)
        mock_state = agent.state.sync_all(mock_state)
        
        print(f"   Returned state type: {type(mock_state)}")
        print(f"   Synced {len(mock_state.sharedState)} variables")
        print(f"   LangGraph sharedState: {mock_state.sharedState}")
        
        # Verify
        success = mock_state.sharedState == all_vars
        print(f"   ✅ SUCCESS: {success}")
        print()
    
    # Test 4: Creating sharedState when it doesn't exist
    print("🔍 Test 4: Creating sharedState when it doesn't exist")
    
    # Create state without sharedState attribute
    class StateWithoutSharedState:
        def __init__(self):
            self.current_node = 1
            # No sharedState attribute
    
    state_no_shared = StateWithoutSharedState()
    
    with patch.object(agent.state, 'get') as mock_get:
        mock_get.return_value = "test_value"
        
        # This should create the sharedState attribute
        result = agent.state.sync("testVar", state_no_shared)
        
        has_shared_state = hasattr(state_no_shared, 'sharedState')
        correct_value = getattr(state_no_shared, 'sharedState', {}).get('testVar') == "test_value"
        
        print(f"   Created sharedState attribute: {has_shared_state}")
        print(f"   Correct value set: {correct_value}")
        print(f"   ✅ SUCCESS: {has_shared_state and correct_value}")
        print()
    
    # Test 5: Handling None sharedState
    print("🔍 Test 5: Handling None sharedState")
    
    class StateWithNoneSharedState:
        def __init__(self):
            self.current_node = 1
            self.sharedState = None  # Explicitly None
    
    state_none_shared = StateWithNoneSharedState()
    
    with patch.object(agent.state, 'get') as mock_get:
        mock_get.return_value = "test_value2"
        
        # This should replace None with a dictionary
        result = agent.state.sync("testVar2", state_none_shared)
        
        is_dict = isinstance(state_none_shared.sharedState, dict)
        correct_value = state_none_shared.sharedState.get('testVar2') == "test_value2"
        
        print(f"   Replaced None with dict: {is_dict}")
        print(f"   Correct value set: {correct_value}")
        print(f"   ✅ SUCCESS: {is_dict and correct_value}")
        print()
    
    print("🎯 All sync functionality tests completed!")
    print()
    print("📝 Summary of NEW sync method patterns:")
    print("   • state = agent.state.sync('variableName', state)")
    print("   • state = agent.state.sync_multiple(['var1', 'var2'], state)")
    print("   • state = agent.state.sync_all(state)")
    print()
    print("✅ Key benefits:")
    print("   • Methods return updated state object for assignment")
    print("   • All methods create state.sharedState if it doesn't exist")
    print("   • All methods handle None sharedState gracefully")
    print("   • Maintains backward compatibility (works without state parameter)")
    print("   • Perfect for LangGraph node pattern: return updated state")

def test_integration_example():
    """Test the integration example pattern."""
    print("\n" + "=" * 60)
    print("🔄 Testing LangGraph Integration Pattern")
    print("=" * 60)
    
    # Simulate a LangGraph node using StationAgent
    @dataclass
    class LangGraphState:
        current_node: float = 0
        stationThreadId: str = "workflow-123"
        sharedState: Dict[str, Any] = field(default_factory=dict)
    
    def mock_langgraph_node(state: LangGraphState, config: Dict):
        """Mock LangGraph node using StationAgent pattern."""
        
        # Initialize StationAgent (like in your real nodes)
        station_agent = StationAgent(
            station_thread_id=state.stationThreadId,
            graph_thread_id=config.get("thread_id", "thread-456"),
            token=config.get("shared_state_token", "dev-token-123")
        )
        
        # Sync shared state at node start
        with patch.object(station_agent.state, 'pull') as mock_pull:
            mock_pull.return_value = {
                "currentStep": "processing",
                "server": "idle",
                "serverThread": "idle"
            }
            
            station_agent.state.sync_all(state)
        
        # Simulate node work
        state.current_node = 5
        
        # Update shared state
        with patch.object(station_agent.state, 'set') as mock_set:
            mock_set.return_value = True
            
            # These would be real API calls in production
            station_agent.state.set("currentNode", "node5")
            station_agent.state.set("lastUpdated", "2024-01-01T12:00:00Z")
        
        return state
    
    # Test the mock node
    state = LangGraphState()
    config = {"thread_id": "thread-456", "shared_state_token": "dev-token-123"}
    
    print("🔧 Running mock LangGraph node...")
    result_state = mock_langgraph_node(state, config)
    
    print(f"   ✅ Node completed: current_node = {result_state.current_node}")
    print(f"   ✅ Shared state synced: {result_state.sharedState}")
    print(f"   ✅ Station thread ID: {result_state.stationThreadId}")
    
    expected_shared = {
        "currentStep": "processing", 
        "server": "idle", 
        "serverThread": "idle"
    }
    success = result_state.sharedState == expected_shared
    print(f"   ✅ Integration SUCCESS: {success}")

if __name__ == "__main__":
    test_sync_functionality()
    test_integration_example() 