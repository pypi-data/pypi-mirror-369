#!/usr/bin/env python3
"""
StationAgent Usage Example

This example demonstrates the correct usage of StationAgent,
especially how reserved variable protection works.
"""

import sys
import os

# Add the cuteagent module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cuteagent'))

from cuteagent import StationAgent

def demonstrate_correct_usage():
    """Demonstrate correct StationAgent usage patterns."""
    print("🚀 StationAgent Usage Example")
    print("=" * 50)
    
    # Initialize agent
    agent = StationAgent(
        station_thread_id="example-workflow-123",
        graph_thread_id="langgraph-node-456", 
        token="dev-token-123"  # Use your real token
    )
    
    print("✅ Agent created successfully")
    print(f"   Station Thread: {agent.station_thread_id}")
    print(f"   Graph Thread: {agent.graph_thread_id}")
    print(f"   API URL: {agent.base_url}")
    print()
    
    # 1. Test connection (optional)
    print("🔗 Testing API connection...")
    connection = agent.validate_connection()
    if connection.get("connected"):
        print(f"✅ Connected! Found {connection.get('variable_count', 0)} existing variables")
    else:
        print(f"❌ Connection failed: {connection.get('error')}")
        print("   Continuing with demo anyway...")
    print()
    
    # 2. Working with user variables (ALLOWED)
    print("📊 Working with user variables...")
    
    # Set individual variables
    print("   Setting individual variables:")
    try:
        agent.state.set("currentStep", "processing")
        agent.state.set("userInput", "Hello World")
        agent.state.set("progress", 0.5)
        print("   ✅ Individual variables set successfully")
    except Exception as e:
        print(f"   ❌ Error setting variables: {e}")
    
    # Bulk set variables
    print("   Bulk setting variables:")
    try:
        bulk_data = {
            "workflowId": "wf-123",
            "context": {"session": "session-456"},
            "metadata": {"version": "1.0", "debug": True}
        }
        agent.state.push(bulk_data)
        print("   ✅ Bulk variables set successfully")
    except Exception as e:
        print(f"   ❌ Error bulk setting: {e}")
    
    # Get variables
    print("   Reading variables:")
    try:
        current_step = agent.state.get("currentStep")
        all_vars = agent.state.pull()
        print(f"   ✅ Current step: {current_step}")
        print(f"   ✅ Total variables: {len(all_vars)}")
    except Exception as e:
        print(f"   ❌ Error reading variables: {e}")
    print()
    
    # 3. Trying to set reserved variables (BLOCKED)
    print("🚫 Attempting to set reserved variables (should fail)...")
    
    try:
        agent.state.set("server", "busy")
        print("   ❌ ERROR: Should not have been able to set 'server'!")
    except ValueError as e:
        print(f"   ✅ Correctly blocked: {e}")
    
    try:
        agent.state.push({"serverThread": "my_task", "normalVar": "value"})
        print("   ❌ ERROR: Should not have been able to push 'serverThread'!")
    except ValueError as e:
        print(f"   ✅ Correctly blocked: {e}")
    print()
    
    # 4. Server management (CORRECT WAY)
    print("🖥️  Server management (correct way)...")
    
    # Check server availability
    try:
        server_status = agent.server.avail()
        print(f"   Current server status: {server_status}")
    except Exception as e:
        print(f"   ❌ Error checking server: {e}")
    
    # Load server
    try:
        load_result = agent.server.load("data_processing")
        print(f"   Server load result: {load_result}")
        
        if load_result.get("status") == "loaded":
            print("   ✅ Server loaded successfully")
        elif load_result.get("status") == "busy":
            print("   ⚠️  Server was already busy")
        else:
            print("   ❌ Server load failed")
            
    except Exception as e:
        print(f"   ❌ Error loading server: {e}")
    
    # Check server status after load
    try:
        server_status = agent.server.avail()
        print(f"   Server status after load: {server_status}")
    except Exception as e:
        print(f"   ❌ Error checking server after load: {e}")
    
    # Unload server
    try:
        unload_result = agent.server.unload()
        print(f"   Server unload result: {unload_result}")
        
        if unload_result.get("status") == "unloaded":
            print("   ✅ Server unloaded successfully")
        elif unload_result.get("status") == "idle":
            print("   ⚠️  Server was already idle")
        else:
            print("   ❌ Server unload failed")
            
    except Exception as e:
        print(f"   ❌ Error unloading server: {e}")
    print()
    
    # 5. Task management
    print("📋 Task management...")
    
    # Test pause/unpause functionality (replaces uninterrupt)
    try:
        # Test pause functionality
        pause_result = agent.pause("example_pause_tag")
        print(f"   Pause result: {pause_result}")
        
        # Test unpause functionality  
        unpause_result = agent.unpause("example_pause_tag")
        print(f"   Unpause result: {unpause_result}")
        
    except Exception as e:
        print(f"   ❌ Error in pause/unpause operations: {e}")
    print()
    
    # 6. Advanced operations
    print("🔧 Advanced operations...")
    
    try:
        # List all variables
        var_list = agent.state.list_variables()
        print(f"   All variables: {var_list}")
        
        # Check if variable exists
        exists = agent.state.exists("currentStep")
        print(f"   'currentStep' exists: {exists}")
        
        # Sync (same as get)
        synced_value = agent.state.sync("userInput")
        print(f"   Synced userInput: {synced_value}")
        
    except Exception as e:
        print(f"   ❌ Error in advanced operations: {e}")
    print()
    
    # 7. Cleanup (optional)
    print("🧹 Cleanup...")
    try:
        # Delete some variables (but not reserved ones)
        agent.state.delete("currentStep")
        agent.state.delete("userInput")
        print("   ✅ Cleaned up test variables")
        
        # Try to delete reserved variable (should fail)
        try:
            agent.state.delete("server")
            print("   ❌ ERROR: Should not have been able to delete 'server'!")
        except ValueError as e:
            print(f"   ✅ Correctly blocked deletion: {e}")
            
    except Exception as e:
        print(f"   ❌ Error in cleanup: {e}")
    
    print("\n🎯 Demo completed!")
    print("\n📝 Key takeaways:")
    print("   • Use state.set() and state.push() for user variables")
    print("   • Use server.load() and server.unload() for server management")  
    print("   • Reserved variables (server, serverThread) are protected")
    print("   • Always handle exceptions in production code")

def demonstrate_langgraph_integration():
    """Show how to use StationAgent in a LangGraph workflow."""
    print("\n" + "=" * 50)
    print("🔄 LangGraph Integration Example")
    print("=" * 50)
    
    def example_langgraph_node(state):
        """Example LangGraph node using StationAgent."""
        
        # Initialize agent in the node
        agent = StationAgent(
            station_thread_id=state.get("station_id", "default-station"),
            graph_thread_id=state.get("thread_id", "default-thread"),
            token=state.get("api_token", "dev-token-123")
        )
        
        # Pull shared state
        shared_state = agent.state.pull()
        state["sharedState"] = shared_state
        
        # Check server availability
        server_status = agent.server.avail()
        if server_status.get("server") == "busy":
            return {"error": "Server is busy, please retry later"}
        
        # Load server for this task
        load_result = agent.server.load("data_processing")
        if load_result.get("status") != "loaded":
            return {"error": "Failed to load server"}
        
        # Update workflow state
        agent.state.set("currentNode", "processing") 
        agent.state.set("startTime", "2024-01-01T12:00:00Z")
        
        # Process data here...
        result = {"processed": "data", "status": "complete"}
        
        # Update completion state
        agent.state.set("result", result)
        agent.state.set("currentNode", "completed")
        
        # Unload server
        agent.server.unload()
        
        return state
    
    # Simulate calling the node
    print("Simulating LangGraph node execution...")
    mock_state = {
        "station_id": "workflow-123",
        "thread_id": "thread-456", 
        "api_token": "dev-token-123",
        "input_data": "test data"
    }
    
    try:
        result_state = example_langgraph_node(mock_state)
        print(f"✅ Node executed successfully")
        print(f"   Shared state keys: {list(result_state.get('sharedState', {}).keys())}")
    except Exception as e:
        print(f"❌ Node execution failed: {e}")

if __name__ == "__main__":
    demonstrate_correct_usage()
    demonstrate_langgraph_integration() 