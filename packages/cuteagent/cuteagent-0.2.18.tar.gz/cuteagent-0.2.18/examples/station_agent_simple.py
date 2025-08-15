#!/usr/bin/env python3
"""
Simple StationAgent Example

This example demonstrates basic StationAgent usage for shared state management
in LangGraph workflows without the complexity of computer use or human review.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END, START

from cuteagent import StationAgent


@dataclass
class SimpleState:
    """Simple state class with StationAgent integration."""
    current_node: float = 0
    user_input: str = ""
    status: str = "Starting"
    counter: int = 0
    
    # Required for StationAgent integration
    stationThreadId: str = ""
    sharedState: Optional[Dict[str, Any]] = field(default_factory=dict)


async def initialization_node(state: SimpleState, config: RunnableConfig) -> SimpleState:
    """Initialize the workflow with StationAgent."""
    print("🔧 Initializing workflow with StationAgent...")
    
    configuration = config["configurable"]
    
    # Initialize StationAgent with initial state
    initial_workflow_state = {
        "workflowType": "simple_example",
        "startTime": "2024-01-01T12:00:00Z",
        "initialized": True,
        "nodeSequence": []
    }
    
    agent = StationAgent(
        station_thread_id=state.stationThreadId or "simple-workflow",
        graph_thread_id=configuration.get("thread_id"),
        token=configuration.get("shared_state_token", "dev-token-123"),
        initial_state=initial_workflow_state
    )
    
    # Check what initial state was pushed (automatically includes server and serverThread)
    if agent.initial_state:
        print(f"Pushed {len(agent.initial_state)} initial variables: {list(agent.initial_state.keys())}")
        print(f"Server status: {agent.initial_state.get('server')}, Server thread: {agent.initial_state.get('serverThread')}")
    
    # Sync shared state to local state
    state = agent.state.sync_all(state)
    
    state.status = "Initialized"
    state.current_node = 1
    return state


async def processing_node(state: SimpleState, config: RunnableConfig) -> SimpleState:
    """Process data and update shared state."""
    print("⚙️ Processing data...")
    
    configuration = config["configurable"]
    
    # Initialize StationAgent
    agent = StationAgent(
        station_thread_id=state.stationThreadId or "simple-workflow",
        graph_thread_id=configuration.get("thread_id"),
        token=configuration.get("shared_state_token", "dev-token-123")
    )
    
    # Get current counter from shared state or start at 0
    current_counter = agent.state.get("globalCounter") or 0
    
    # Increment counter
    new_counter = current_counter + 1
    state.counter = new_counter
    
    # Update shared state with new counter value
    agent.state.set("globalCounter", new_counter)
    agent.state.set("lastProcessingNode", state.current_node)
    agent.state.set("processingTime", "2024-01-01T12:01:00Z")
    
    print(f"📊 Updated global counter to: {new_counter}")
    
    state.status = "Processing"
    state.current_node = 2
    return state


async def coordination_node(state: SimpleState, config: RunnableConfig) -> SimpleState:
    """Demonstrate coordination between multiple workflow instances."""
    print("🤝 Coordinating with other workflow instances...")
    
    configuration = config["configurable"]
    
    # Initialize StationAgent
    agent = StationAgent(
        station_thread_id=state.stationThreadId or "simple-workflow",
        graph_thread_id=configuration.get("thread_id"),
        token=configuration.get("shared_state_token", "dev-token-123")
    )
    
    # Check server availability
    server_status = agent.server.avail()
    print(f"🖥️ Server status: {server_status}")
    
    # Try to load server for exclusive operation
    load_result = agent.server.load("coordination_task")
    
    if load_result["status"] == "loaded":
        print("✅ Server loaded successfully, performing exclusive operation...")
        
        # Do some exclusive work (simulated)
        await asyncio.sleep(1)
        
        # Update shared state with results
        agent.state.push({
            "exclusiveTaskCompleted": True,
            "completedBy": configuration.get("thread_id"),
            "completionTime": "2024-01-01T12:02:00Z"
        })
        
        # Unload server
        agent.server.unload()
        print("🔓 Server unloaded")
        
    else:
        print("⏳ Server is busy, skipping exclusive operation")
    
    # Sync all shared state
    state = agent.state.sync_all(state)
    
    state.status = "Coordinated"
    state.current_node = 3
    return state


async def completion_node(state: SimpleState, config: RunnableConfig) -> SimpleState:
    """Complete the workflow and clean up."""
    print("🏁 Completing workflow...")
    
    configuration = config["configurable"]
    
    # Initialize StationAgent
    agent = StationAgent(
        station_thread_id=state.stationThreadId or "simple-workflow",
        graph_thread_id=configuration.get("thread_id"),
        token=configuration.get("shared_state_token", "dev-token-123")
    )
    
    # Get final state from shared variables
    all_variables = agent.state.pull()
    print("📋 Final shared state variables:")
    for key, value in all_variables.items():
        print(f"  {key}: {value}")
    
    # Mark workflow as completed
    agent.state.set("workflowCompleted", True)
    agent.state.set("completionTime", "2024-01-01T12:03:00Z")
    agent.state.set("finalStatus", "Success")
    
    state.status = "Completed"
    state.current_node = 4
    return state


def create_simple_workflow() -> StateGraph:
    """Create a simple workflow demonstrating StationAgent features."""
    
    workflow = StateGraph(SimpleState)
    
    # Add nodes
    workflow.add_node("initialize", initialization_node)
    workflow.add_node("process", processing_node)
    workflow.add_node("coordinate", coordination_node)
    workflow.add_node("complete", completion_node)
    
    # Define edges
    workflow.add_edge(START, "initialize")
    workflow.add_edge("initialize", "process")
    workflow.add_edge("process", "coordinate")
    workflow.add_edge("coordinate", "complete")
    workflow.add_edge("complete", END)
    
    return workflow.compile()


async def demonstrate_station_agent_features():
    """Demonstrate various StationAgent features."""
    
    print("🧪 Demonstrating StationAgent features...")
    
    # Create agent for demonstrations with initial demo state
    demo_initial_state = {
        "demo_initialized": True,
        "demo_version": "1.0",
        "demo_features": ["state_management", "server_coordination", "variable_protection"]
    }
    
    agent = StationAgent(
        station_thread_id="demo-station",
        graph_thread_id="demo-graph",
        token="dev-token-123",
        initial_state=demo_initial_state
    )
    
    print(f"Demo initialized with state: {list(agent.initial_state.keys())}")
    print(f"Initial server status: {agent.initial_state.get('server')}, thread: {agent.initial_state.get('serverThread')}")
    
    # 1. Basic variable operations
    print("\n1️⃣ Basic Variable Operations:")
    agent.state.set("demo_var", "Hello World")
    print(f"Set demo_var: {agent.state.get('demo_var')}")
    
    # 2. Bulk operations
    print("\n2️⃣ Bulk Operations:")
    agent.state.push({
        "var1": "value1",
        "var2": 42,
        "var3": {"nested": "data"}
    })
    all_vars = agent.state.pull()
    print(f"All variables: {list(all_vars.keys())}")
    
    # 3. Variable existence checks
    print("\n3️⃣ Variable Existence:")
    print(f"demo_var exists: {agent.state.exists('demo_var')}")
    print(f"nonexistent_var exists: {agent.state.exists('nonexistent_var')}")
    
    # 4. Server management
    print("\n4️⃣ Server Management:")
    server_status = agent.server.avail()
    print(f"Server status: {server_status}")
    
    load_result = agent.server.load("demo_task")
    print(f"Load result: {load_result}")
    
    unload_result = agent.server.unload()
    print(f"Unload result: {unload_result}")
    
    # 5. Protected variables demonstration
    print("\n5️⃣ Protected Variables:")
    try:
        agent.state.set("server", "custom_value")
        print("❌ This should not happen - reserved variable protection failed")
    except ValueError as e:
        print(f"✅ Protected variable correctly blocked: {e}")
    
    # 6. Clean up demo variables
    print("\n6️⃣ Cleanup:")
    variables_to_delete = ["demo_var", "var1", "var2", "var3"]
    for var in variables_to_delete:
        if agent.state.exists(var):
            agent.state.delete(var)
            print(f"Deleted {var}")


async def main():
    """Run the simple StationAgent example."""
    
    # First, demonstrate individual features
    await demonstrate_station_agent_features()
    
    print("\n" + "="*50)
    print("🚀 Running Simple Workflow Example")
    print("="*50)
    
    # Create and run the simple workflow
    workflow = create_simple_workflow()
    
    initial_state = SimpleState(
        user_input="Simple workflow test",
        stationThreadId="simple-example-123"
    )
    
    config = RunnableConfig({
        "configurable": {
            "thread_id": "simple-thread-456",
            "shared_state_token": "dev-token-123"
        }
    })
    
    try:
        final_state = await workflow.ainvoke(initial_state, config)
        
        print(f"\n✅ Simple workflow completed!")
        print(f"Final status: {final_state.status}")
        print(f"Counter value: {final_state.counter}")
        print(f"Current node: {final_state.current_node}")
        
    except Exception as e:
        print(f"❌ Workflow error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 