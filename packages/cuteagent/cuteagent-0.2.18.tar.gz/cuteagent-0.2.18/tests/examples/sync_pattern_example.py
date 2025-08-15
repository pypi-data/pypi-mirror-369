#!/usr/bin/env python3
"""
Simple example showing the exact sync pattern you requested:

    state = agent.state.sync("VariableName", state)

This pattern updates the LangGraph state and returns it for reassignment.
"""

import sys
import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

# Add the cuteagent module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cuteagent'))

from cuteagent import StationAgent

@dataclass 
class State:
    """Your LangGraph State class."""
    current_node: float = 0
    user_input: str = ""
    stationThreadId: str = "workflow-123"
    sharedState: Optional[Dict[str, Any]] = field(default_factory=dict)

def example_langgraph_node(state: State, config: Dict) -> State:
    """
    Example LangGraph node showing the exact sync patterns you want.
    """
    print("🔧 LangGraph Node: Starting execution")
    print(f"   Initial state.sharedState: {state.sharedState}")
    
    # Initialize StationAgent
    agent = StationAgent(
        station_thread_id=state.stationThreadId,
        graph_thread_id=config.get("thread_id", "thread-456"),
        token=config.get("shared_state_token", "dev-token-123")
    )
    
    # PATTERN 1: Sync single variable
    print("\n📊 Pattern 1: Sync single variable")
    print("   Code: state = agent.state.sync('currentStep', state)")
    
    # Mock the API call for demo
    with MockAPI(agent, "currentStep", "processing"):
        state = agent.state.sync("currentStep", state)
    
    print(f"   ✅ Updated state.sharedState: {state.sharedState}")
    
    # PATTERN 2: Sync multiple variables
    print("\n📊 Pattern 2: Sync multiple variables")
    print("   Code: state = agent.state.sync_multiple(['userPrefs', 'progress'], state)")
    
    with MockAPI(agent, multiple={
        "userPrefs": {"theme": "dark"},
        "progress": 0.8
    }):
        state = agent.state.sync_multiple(["userPrefs", "progress"], state)
    
    print(f"   ✅ Updated state.sharedState: {state.sharedState}")
    
    # PATTERN 3: Sync all variables
    print("\n📊 Pattern 3: Sync all variables")
    print("   Code: state = agent.state.sync_all(state)")
    
    with MockAPI(agent, all_vars={
        "server": "idle",
        "serverThread": "idle",
        "currentStep": "processing",
        "userPrefs": {"theme": "dark"},
        "progress": 0.8,
        "timestamp": "2024-01-01T12:00:00Z"
    }):
        state = agent.state.sync_all(state)
    
    print(f"   ✅ Updated state.sharedState: {state.sharedState}")
    
    # Your node logic here...
    state.current_node = 5
    
    print(f"\n🎯 Node completed. Final state.sharedState: {state.sharedState}")
    return state

class MockAPI:
    """Helper class to mock API responses for the demo."""
    
    def __init__(self, agent, single_var=None, single_value=None, multiple=None, all_vars=None):
        self.agent = agent
        self.single_var = single_var
        self.single_value = single_value
        self.multiple = multiple or {}
        self.all_vars = all_vars or {}
        
    def __enter__(self):
        # Mock the appropriate methods
        if self.single_var:
            original_get = self.agent.state.get
            def mock_get(var_name):
                if var_name == self.single_var:
                    return self.single_value
                return original_get(var_name)
            self.agent.state.get = mock_get
            
        elif self.multiple:
            original_get = self.agent.state.get
            def mock_get(var_name):
                return self.multiple.get(var_name)
            self.agent.state.get = mock_get
            
        elif self.all_vars:
            original_pull = self.agent.state.pull
            def mock_pull():
                return self.all_vars
            self.agent.state.pull = mock_pull
            
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original methods (not needed for this demo)
        pass

def main():
    """Run the example."""
    print("🚀 StationAgent Sync Pattern Example")
    print("=" * 60)
    print()
    print("This example shows exactly what you requested:")
    print("   state = agent.state.sync('VariableName', state)")
    print()
    
    # Create initial state
    state = State()
    config = {
        "thread_id": "example-thread-123",
        "shared_state_token": "dev-token-123"
    }
    
    # Run the example node
    final_state = example_langgraph_node(state, config)
    
    print("\n" + "=" * 60)
    print("✅ SUMMARY")
    print("=" * 60)
    print("🎯 All three sync patterns work exactly as requested:")
    print()
    print("1️⃣  state = agent.state.sync('variableName', state)")
    print("   → Syncs one variable, returns updated state")
    print()
    print("2️⃣  state = agent.state.sync_multiple(['var1', 'var2'], state)")
    print("   → Syncs multiple variables, returns updated state")
    print()
    print("3️⃣  state = agent.state.sync_all(state)")
    print("   → Syncs all SharedState variables, returns updated state")
    print()
    print("🔧 Integration in your LangGraph nodes:")
    print("   • Add sharedState field to your State class")
    print("   • Use these patterns in any node that needs shared state")
    print("   • State object is updated and returned for reassignment")
    print("   • Works seamlessly with your existing LangGraph workflow")

if __name__ == "__main__":
    main() 