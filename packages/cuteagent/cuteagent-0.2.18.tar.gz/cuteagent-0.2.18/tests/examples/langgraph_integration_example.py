#!/usr/bin/env python3
"""
LangGraph Integration Example for StationAgent

This example shows how to use StationAgent's sync methods 
to integrate SharedState API with LangGraph workflows.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, TypedDict, Tuple, Optional, List, Union
import asyncio
import logging
import os
from cuteagent import StationAgent, WindowsAgent

# Your existing State class - we just need to add sharedState field
@dataclass
class State:
    """Your existing LangGraph State class with added sharedState field."""
    user_input: Union[str, Dict[str, Any], None] = None
    current_node: float = 0
    screenshot_url: str | None = None
    messages: List = field(default_factory=list)
    borrower_names: List[str] = field(default_factory=list)
    webhook_status: str | None = None
    table_csv: str | None = None
    pending_review_info: Optional[Dict[str, Any]] = None
    human_review_decision: str | None = None
    final_api_status: str | None = None
    status: str = "Ongoing"
    reason_code: str | None = None
    stationThreadId: str | None = None
    
    # Add this field for SharedState integration
    sharedState: Optional[Dict[str, Any]] = field(default_factory=dict)

class Configuration(TypedDict):
    """Your existing Configuration with StationAgent settings."""
    config_url: str
    os_url: Optional[str]
    # ... your existing config fields ...
    
    # Add these for StationAgent
    shared_state_token: Optional[str]
    shared_state_url: Optional[str]

# Example: Modified node1 with StationAgent integration
async def node1_with_station_agent(state: State, config) -> State:
    """
    Example of your node1 modified to use StationAgent for shared state management.
    """
    configuration = config["configurable"]
    
    # Your existing coordinate and OS setup
    coords = configuration.get("node1_coords", (85, 60))
    x, y = coords
    os_url = configuration.get("os_url", "https://fintor-ec2-test-2.ngrok.app")
    
    # Initialize StationAgent
    station_agent = StationAgent(
        station_thread_id=state.stationThreadId or "default-station", 
        graph_thread_id=configuration.get("thread_id", "default-thread"),
        token=configuration.get("shared_state_token", "dev-token-123"),
        shared_state_url=configuration.get("shared_state_url")
    )
    
    # Your existing WindowsAgent operations
    agent = WindowsAgent(os_url=os_url)
    try:
        await asyncio.to_thread(agent.click_element, x, y)
    except Exception as e:
        print(f"Error in node 1: {e}")
        pass
    
    # Extract stationThreadId (your existing logic)
    if state.user_input:
        # ... your existing stationThreadId extraction logic ...
        pass
    
    # NEW: Sync shared state at the beginning of the workflow
    try:
        # Option 1: Sync all shared state variables to LangGraph state
        station_agent.state.sync_all(state)
        
        # Option 2: Sync specific variables you need
        # station_agent.state.sync_multiple(['currentStep', 'userPreferences'], state)
        
        # Option 3: Sync individual variables
        # current_step = station_agent.state.sync('currentStep', state)
        
        print(f"📊 Shared state synced to LangGraph: {state.sharedState}")
        
    except Exception as e:
        logging.error(f"Error syncing shared state: {e}")
        # Continue workflow even if sync fails
    
    # Update shared state with current workflow information
    try:
        station_agent.state.set("currentNode", "node1")
        station_agent.state.set("workflowStatus", "processing")
        station_agent.state.set("lastUpdated", "2024-01-01T12:00:00Z")
        
        # Check server availability before proceeding
        server_status = station_agent.server.avail()
        print(f"🖥️  Server status: {server_status}")
        
    except Exception as e:
        logging.error(f"Error updating shared state: {e}")
    
    state.current_node = 1
    return state

# Example: Node that uses shared state for coordination
async def coordination_node(state: State, config) -> State:
    """
    Example node that coordinates with other workflows using shared state.
    """
    configuration = config["configurable"]
    
    # Initialize StationAgent
    station_agent = StationAgent(
        station_thread_id=state.stationThreadId or "default-station",
        graph_thread_id=configuration.get("thread_id", "default-thread"),
        token=configuration.get("shared_state_token", "dev-token-123")
    )
    
    try:
        # Check if another workflow is processing
        other_workflow_status = station_agent.state.get("otherWorkflowStatus")
        
        if other_workflow_status == "processing":
            print("⏳ Another workflow is processing, waiting...")
            
            # Load server to signal we're active
            load_result = station_agent.server.load("current_workflow")
            
            if load_result.get("status") == "busy":
                print("🚫 Server is busy, will retry later")
                # You could implement retry logic here
                return state
        
        # Sync the latest shared state
        station_agent.state.sync_all(state)
        
        # Update coordination variables
        station_agent.state.set("currentWorkflow", "main_workflow")
        station_agent.state.set("coordinationTimestamp", "2024-01-01T12:00:00Z")
        
        # Share data between workflows
        if state.borrower_names:
            station_agent.state.set("sharedBorrowerNames", state.borrower_names)
        
        print(f"🔄 Coordination completed, shared state: {state.sharedState}")
        
    except Exception as e:
        logging.error(f"Error in coordination: {e}")
    
    state.current_node = 5.5  # Example intermediate node
    return state

# Example: Node that handles workflow completion
async def completion_node_with_shared_state(state: State, config) -> State:
    """
    Example completion node that updates shared state with final results.
    """
    configuration = config["configurable"]
    
    # Initialize StationAgent
    station_agent = StationAgent(
        station_thread_id=state.stationThreadId or "default-station",
        graph_thread_id=configuration.get("thread_id", "default-thread"),
        token=configuration.get("shared_state_token", "dev-token-123")
    )
    
    try:
        # Update shared state with final workflow results
        completion_data = {
            "workflowStatus": "completed",
            "finalStatus": state.status,
            "reasonCode": state.reason_code,
            "borrowerNames": state.borrower_names,
            "humanReviewDecision": state.human_review_decision,
            "completionTimestamp": "2024-01-01T12:00:00Z"
        }
        
        # Bulk update shared state
        station_agent.state.push(completion_data)
        
        # Unload server to make it available for other workflows
        unload_result = station_agent.server.unload()
        print(f"🖥️  Server unload result: {unload_result}")
        
        # Sync final state back to LangGraph
        station_agent.state.sync_all(state)
        
        print(f"✅ Workflow completion data saved to shared state")
        print(f"📊 Final shared state: {state.sharedState}")
        
    except Exception as e:
        logging.error(f"Error updating completion state: {e}")
    
    state.current_node = 12
    return state

# Example: How to check for interruptions and resume
async def resume_check_node(state: State, config) -> State:
    """
    Example node that checks if this workflow was interrupted and can be resumed.
    """
    configuration = config["configurable"]
    
    # Initialize StationAgent
    station_agent = StationAgent(
        station_thread_id=state.stationThreadId or "default-station",
        graph_thread_id=configuration.get("thread_id", "default-thread"),
        token=configuration.get("shared_state_token", "dev-token-123")
    )
    
    try:
        # Check workflow state for coordination (replaces uninterrupt functionality)
        print("🆕 Checking workflow coordination state")
        
        # Sync shared state to get the latest data
        station_agent.state.sync_all(state)
        
        # Check if there's existing workflow state
        existing_workflow = state.sharedState.get("main_workflow_status")
        if existing_workflow == "paused":
            print("🔄 Found paused workflow, can use unpause() to resume")
            # You could use agent.unpause(pause_tag) here
        else:
            print("🆕 Starting new workflow")
            # Set workflow status for coordination
            station_agent.state.set("main_workflow_status", "active")
            station_agent.state.set("main_workflow_thread_id", configuration.get("thread_id"))
        
    except Exception as e:
        logging.error(f"Error checking workflow state: {e}")
    
    return state

def main():
    """Example showing how the integration would work."""
    print("🔄 LangGraph + StationAgent Integration Example")
    print("=" * 60)
    print()
    print("📋 Key Integration Points:")
    print("   1. Add 'sharedState' field to your LangGraph State class")
    print("   2. Initialize StationAgent in each node that needs shared state")
    print("   3. Use agent.state.sync_all(state) to pull all shared variables")
    print("   4. Use agent.state.sync('variable', state) for specific variables") 
    print("   5. Use agent.state.set() to update shared state")
    print("   6. Use agent.server.load/unload() for workflow coordination")
    print("   7. Use agent.pause()/unpause() to handle workflow coordination")
    print()
    print("🔧 Configuration needed:")
    print("   - shared_state_token: API token for SharedState")
    print("   - shared_state_url: Optional custom API URL")
    print("   - Ensure stationThreadId is available in state")
    print()
    print("✅ Your existing LangGraph workflow will now have:")
    print("   - Shared state across multiple workflow instances")
    print("   - Server coordination to prevent conflicts")
    print("   - Ability to resume interrupted workflows")
    print("   - Cross-workflow data sharing")

if __name__ == "__main__":
    main() 