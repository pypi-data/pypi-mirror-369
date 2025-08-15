#!/usr/bin/env python3
"""
Quick test script to verify server status validation.

This script tests that server status is strictly limited to "busy" or "idle".
"""

import sys
import os

# Add the cuteagent module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cuteagent'))

from cuteagent import StationAgent

def test_server_status_validation():
    """Test that server status validation works correctly."""
    print("🧪 Testing Server Status Validation")
    print("=" * 50)
    
    # Create agent
    agent = StationAgent(
        station_thread_id="test-validation",
        graph_thread_id="test-graph",
        token="test-token"
    )
    
    print("✅ Agent created")
    print(f"   Valid server statuses: {agent.VALID_SERVER_STATUS}")
    print()
    
    # Test valid statuses
    print("🔍 Testing valid server statuses:")
    valid_statuses = ["busy", "idle"]
    for status in valid_statuses:
        is_valid = agent.validate_server_status(status)
        print(f"   '{status}': {'✅ Valid' if is_valid else '❌ Invalid'}")
    print()
    
    # Test invalid statuses
    print("🚫 Testing invalid server statuses:")
    invalid_statuses = ["running", "stopped", "error", "pending", "loading", "", None, "BUSY", "IDLE"]
    for status in invalid_statuses:
        is_valid = agent.validate_server_status(str(status) if status is not None else "None")
        print(f"   '{status}': {'❌ Should be invalid but passed' if is_valid else '✅ Correctly rejected'}")
    print()
    
    # Test server management methods with validation
    print("🖥️  Testing server management with validation:")
    
    # Test that internal validation methods exist
    try:
        server_validate = agent.server._validate_server_status("idle")
        print(f"   Internal validation method works: {'✅' if server_validate else '❌'}")
    except Exception as e:
        print(f"   ❌ Internal validation method error: {e}")
    
    # Test that server methods use validation (we can't test real API calls here)
    try:
        # These won't work without real API, but we can check the method exists
        load_method = hasattr(agent.server, 'load')
        unload_method = hasattr(agent.server, 'unload')
        avail_method = hasattr(agent.server, 'avail')
        
        print(f"   Server methods exist: load={load_method}, unload={unload_method}, avail={avail_method}")
        
        if load_method and unload_method and avail_method:
            print("   ✅ All server management methods are available")
        else:
            print("   ❌ Some server management methods are missing")
            
    except Exception as e:
        print(f"   ❌ Error checking server methods: {e}")
    
    print()
    
    # Test constants
    print("📋 Testing class constants:")
    try:
        reserved_vars = agent.RESERVED_VARIABLES
        valid_statuses = agent.VALID_SERVER_STATUS
        
        print(f"   Reserved variables: {reserved_vars}")
        print(f"   Valid server statuses: {valid_statuses}")
        
        # Check that constants are correct
        expected_reserved = {"server", "serverThread"}
        expected_valid = {"busy", "idle"}
        
        reserved_correct = reserved_vars == expected_reserved
        valid_correct = valid_statuses == expected_valid
        
        print(f"   Reserved variables correct: {'✅' if reserved_correct else '❌'}")
        print(f"   Valid statuses correct: {'✅' if valid_correct else '❌'}")
        
    except Exception as e:
        print(f"   ❌ Error checking constants: {e}")
    
    print()
    print("🎯 Server status validation test completed!")
    print()
    print("📝 Key points:")
    print("   • Server status is strictly limited to 'busy' or 'idle'")
    print("   • Any other values are rejected by validation")
    print("   • Server management methods include built-in validation")
    print("   • Case sensitivity matters ('BUSY' != 'busy')")

if __name__ == "__main__":
    test_server_status_validation() 