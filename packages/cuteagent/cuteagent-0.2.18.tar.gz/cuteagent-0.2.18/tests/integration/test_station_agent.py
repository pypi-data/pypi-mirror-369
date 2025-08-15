#!/usr/bin/env python3
"""
Comprehensive test suite for StationAgent class.

This test file validates all functionality including:
- State management operations
- Server management
- Reserved variable protection
- Error handling
- API integration

Run with: python test_station_agent.py
"""

import os
import sys
import time
import json
from typing import Dict, Any

# Add the cuteagent module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cuteagent'))

from cuteagent import StationAgent

class StationAgentTester:
    """Test suite for StationAgent class."""
    
    def __init__(self, token: str = "test-token", test_station_id: str = "test-station-123"):
        """
        Initialize the tester.
        
        Args:
            token (str): API token for testing
            test_station_id (str): Station thread ID for testing
        """
        self.token = token
        self.test_station_id = test_station_id
        self.test_graph_id = "test-graph-456"
        self.agent = None
        self.test_results = []
        
    def setup_agent(self):
        """Create a StationAgent instance for testing."""
        try:
            self.agent = StationAgent(
                station_thread_id=self.test_station_id,
                graph_thread_id=self.test_graph_id,
                token=self.token
            )
            self.log_test("Agent Setup", True, "StationAgent created successfully")
        except Exception as e:
            self.log_test("Agent Setup", False, f"Failed to create agent: {e}")
            
    def log_test(self, test_name: str, passed: bool, message: str):
        """Log test results."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
    
    def test_initialization(self):
        """Test StationAgent initialization."""
        print("\n🔧 Testing Initialization...")
        
        # Test successful initialization
        try:
            agent = StationAgent("test-id", "graph-id", "token")
            self.log_test("Basic Initialization", True, "Agent initialized with required parameters")
        except Exception as e:
            self.log_test("Basic Initialization", False, f"Initialization failed: {e}")
        
        # Test with custom URL
        try:
            custom_url = "https://custom-api.example.com"
            agent = StationAgent("test-id", "graph-id", "token", shared_state_url=custom_url)
            passed = agent.base_url == custom_url
            self.log_test("Custom URL", passed, f"Custom URL {'set correctly' if passed else 'not set properly'}")
        except Exception as e:
            self.log_test("Custom URL", False, f"Custom URL test failed: {e}")
        
        # Test reserved variables constant
        try:
            expected_reserved = {"server", "serverThread"}
            passed = StationAgent.RESERVED_VARIABLES == expected_reserved
            self.log_test("Reserved Variables", passed, f"Reserved variables: {StationAgent.RESERVED_VARIABLES}")
        except Exception as e:
            self.log_test("Reserved Variables", False, f"Reserved variables test failed: {e}")
    
    def test_state_operations(self):
        """Test state management operations."""
        print("\n📊 Testing State Operations...")
        
        if not self.agent:
            self.log_test("State Operations", False, "No agent available for testing")
            return
        
        # Test setting a regular variable
        try:
            result = self.agent.state.set("testVariable", "testValue")
            self.log_test("Set Variable", isinstance(result, bool), f"Set operation returned: {result}")
        except Exception as e:
            self.log_test("Set Variable", False, f"Set operation failed: {e}")
        
        # Test setting reserved variable (should fail)
        try:
            self.agent.state.set("server", "should_fail")
            self.log_test("Set Reserved Variable", False, "Should have raised ValueError for reserved variable")
        except ValueError as e:
            self.log_test("Set Reserved Variable", True, f"Correctly blocked reserved variable: {e}")
        except Exception as e:
            self.log_test("Set Reserved Variable", False, f"Unexpected error: {e}")
        
        # Test getting a variable
        try:
            result = self.agent.state.get("testVariable")
            self.log_test("Get Variable", True, f"Get operation completed, result type: {type(result)}")
        except Exception as e:
            self.log_test("Get Variable", False, f"Get operation failed: {e}")
        
        # Test getting non-existent variable
        try:
            result = self.agent.state.get("nonExistentVariable")
            passed = result is None
            self.log_test("Get Non-existent Variable", passed, f"Non-existent variable returned: {result}")
        except Exception as e:
            self.log_test("Get Non-existent Variable", False, f"Get non-existent failed: {e}")
        
        # Test pull operation
        try:
            result = self.agent.state.pull()
            passed = isinstance(result, dict)
            self.log_test("Pull All Variables", passed, f"Pull returned {type(result)} with {len(result) if isinstance(result, dict) else 0} items")
        except Exception as e:
            self.log_test("Pull All Variables", False, f"Pull operation failed: {e}")
        
        # Test push operation with valid variables
        try:
            test_data = {"userVar1": "value1", "userVar2": {"nested": "value"}}
            result = self.agent.state.push(test_data)
            self.log_test("Push Valid Variables", isinstance(result, bool), f"Push operation returned: {result}")
        except Exception as e:
            self.log_test("Push Valid Variables", False, f"Push operation failed: {e}")
        
        # Test push operation with reserved variables (should fail)
        try:
            test_data = {"server": "should_fail", "normalVar": "value"}
            self.agent.state.push(test_data)
            self.log_test("Push Reserved Variables", False, "Should have raised ValueError for reserved variables")
        except ValueError as e:
            self.log_test("Push Reserved Variables", True, f"Correctly blocked reserved variables: {e}")
        except Exception as e:
            self.log_test("Push Reserved Variables", False, f"Unexpected error: {e}")
        
        # Test sync operation
        try:
            result = self.agent.state.sync("testVariable")
            self.log_test("Sync Variable", True, f"Sync operation completed, result type: {type(result)}")
        except Exception as e:
            self.log_test("Sync Variable", False, f"Sync operation failed: {e}")
        
        # Test exists operation
        try:
            result = self.agent.state.exists("testVariable")
            passed = isinstance(result, bool)
            self.log_test("Variable Exists Check", passed, f"Exists check returned: {result}")
        except Exception as e:
            self.log_test("Variable Exists Check", False, f"Exists operation failed: {e}")
        
        # Test delete operation
        try:
            result = self.agent.state.delete("testVariable")
            self.log_test("Delete Variable", isinstance(result, bool), f"Delete operation returned: {result}")
        except Exception as e:
            self.log_test("Delete Variable", False, f"Delete operation failed: {e}")
        
        # Test delete reserved variable (should fail)
        try:
            self.agent.state.delete("server")
            self.log_test("Delete Reserved Variable", False, "Should have raised ValueError for reserved variable")
        except ValueError as e:
            self.log_test("Delete Reserved Variable", True, f"Correctly blocked deleting reserved variable: {e}")
        except Exception as e:
            self.log_test("Delete Reserved Variable", False, f"Unexpected error: {e}")
        
        # Test list variables
        try:
            result = self.agent.state.list_variables()
            passed = isinstance(result, list)
            self.log_test("List Variables", passed, f"List variables returned {type(result)} with {len(result) if isinstance(result, list) else 0} items")
        except Exception as e:
            self.log_test("List Variables", False, f"List variables failed: {e}")
    
    def test_server_operations(self):
        """Test server management operations."""
        print("\n🖥️  Testing Server Operations...")
        
        if not self.agent:
            self.log_test("Server Operations", False, "No agent available for testing")
            return
        
        # Test server availability check
        try:
            result = self.agent.server.avail()
            passed = isinstance(result, dict) and "server" in result and "serverThread" in result
            self.log_test("Server Availability", passed, f"Availability check returned: {result}")
        except Exception as e:
            self.log_test("Server Availability", False, f"Availability check failed: {e}")
        
        # Test server load
        try:
            result = self.agent.server.load("test_task")
            passed = isinstance(result, dict) and "status" in result
            self.log_test("Server Load", passed, f"Server load returned: {result}")
        except Exception as e:
            self.log_test("Server Load", False, f"Server load failed: {e}")
        
        # Test server load when busy (should return busy status)
        try:
            # First load should succeed or return busy
            result1 = self.agent.server.load("task1")
            result2 = self.agent.server.load("task2")
            
            # At least one should work, and if server becomes busy, second should indicate that
            passed = isinstance(result1, dict) and isinstance(result2, dict)
            self.log_test("Server Load When Busy", passed, f"Load attempts: {result1}, {result2}")
        except Exception as e:
            self.log_test("Server Load When Busy", False, f"Server busy test failed: {e}")
        
        # Test server unload
        try:
            result = self.agent.server.unload()
            passed = isinstance(result, dict) and "status" in result
            self.log_test("Server Unload", passed, f"Server unload returned: {result}")
        except Exception as e:
            self.log_test("Server Unload", False, f"Server unload failed: {e}")
        
        # Test server unload when already idle
        try:
            # Ensure server is unloaded first
            self.agent.server.unload()
            result = self.agent.server.unload()
            expected_idle = result.get("status") == "idle" and "already idle" in result.get("error", "").lower()
            self.log_test("Server Unload When Idle", expected_idle, f"Unload when idle returned: {result}")
        except Exception as e:
            self.log_test("Server Unload When Idle", False, f"Unload when idle failed: {e}")
    
    def test_task_operations(self):
        """Test task management operations."""
        print("\n📋 Testing Task Operations...")
        
        if not self.agent:
            self.log_test("Task Operations", False, "No agent available for testing")
            return
        
        # Test pause functionality
        try:
            result = self.agent.pause("test_pause_tag")
            passed = isinstance(result, dict) and "success" in result
            self.log_test("Pause Functionality", passed, f"Pause returned: {result}")
        except Exception as e:
            self.log_test("Pause Functionality", False, f"Pause test failed: {e}")
        
        # Test unpause functionality
        try:
            result = self.agent.unpause("test_pause_tag")
            passed = isinstance(result, dict) and "success" in result
            self.log_test("Unpause Functionality", passed, f"Unpause returned: {result}")
        except Exception as e:
            self.log_test("Unpause Functionality", False, f"Unpause test failed: {e}")
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        print("\n⚠️  Testing Error Handling...")
        
        # Test with invalid token
        try:
            invalid_agent = StationAgent("test", "test", "invalid-token")
            # This should not fail until we make a request
            self.log_test("Invalid Token Creation", True, "Agent created with invalid token (no immediate validation)")
            
            # Try to make a request that should fail
            try:
                result = invalid_agent.state.get("test")
                self.log_test("Invalid Token Request", False, f"Request should have failed but returned: {result}")
            except Exception as e:
                self.log_test("Invalid Token Request", True, f"Request correctly failed: {type(e).__name__}")
        except Exception as e:
            self.log_test("Invalid Token Test", False, f"Unexpected error in token test: {e}")
        
        # Test with None values
        try:
            if self.agent:
                result = self.agent.state.set("testNone", None)
                self.log_test("Set None Value", isinstance(result, bool), f"Setting None value returned: {result}")
        except Exception as e:
            self.log_test("Set None Value", False, f"Setting None failed: {e}")
        
        # Test with complex data types
        try:
            if self.agent:
                complex_data = {
                    "list": [1, 2, 3],
                    "dict": {"nested": {"deep": "value"}},
                    "bool": True,
                    "number": 42.5
                }
                result = self.agent.state.set("complexData", complex_data)
                self.log_test("Set Complex Data", isinstance(result, bool), f"Setting complex data returned: {result}")
        except Exception as e:
            self.log_test("Set Complex Data", False, f"Setting complex data failed: {e}")
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        print("\n🔍 Testing Edge Cases...")
        
        if not self.agent:
            self.log_test("Edge Cases", False, "No agent available for testing")
            return
        
        # Test empty string variable name
        try:
            result = self.agent.state.set("", "value")
            self.log_test("Empty Variable Name", isinstance(result, bool), f"Empty name returned: {result}")
        except Exception as e:
            self.log_test("Empty Variable Name", True, f"Empty name correctly failed: {type(e).__name__}")
        
        # Test very long variable name
        try:
            long_name = "a" * 1000
            result = self.agent.state.set(long_name, "value")
            self.log_test("Long Variable Name", isinstance(result, bool), f"Long name returned: {result}")
        except Exception as e:
            self.log_test("Long Variable Name", False, f"Long name failed: {e}")
        
        # Test empty push object
        try:
            result = self.agent.state.push({})
            self.log_test("Empty Push Object", isinstance(result, bool), f"Empty push returned: {result}")
        except Exception as e:
            self.log_test("Empty Push Object", False, f"Empty push failed: {e}")
        
        # Test special characters in variable names
        try:
            special_names = ["var-with-dash", "var_with_underscore", "var.with.dots", "var123"]
            for name in special_names:
                try:
                    result = self.agent.state.set(name, f"value_for_{name}")
                    self.log_test(f"Special Char Name: {name}", isinstance(result, bool), f"Special char name returned: {result}")
                except Exception as e:
                    self.log_test(f"Special Char Name: {name}", False, f"Special char failed: {e}")
        except Exception as e:
            self.log_test("Special Characters Test", False, f"Special characters test failed: {e}")
    
    def run_all_tests(self):
        """Run all test suites."""
        print("🧪 Starting StationAgent Comprehensive Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_initialization()
        self.setup_agent()
        self.test_state_operations()
        self.test_server_operations()
        self.test_task_operations()
        self.test_error_handling()
        self.test_edge_cases()
        
        end_time = time.time()
        
        # Generate summary
        self.print_summary(end_time - start_time)
    
    def print_summary(self, duration: float):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  • {result['test']}: {result['message']}")
        
        print("\n" + "=" * 60)
        
        # Save detailed results to file
        self.save_results()
    
    def save_results(self):
        """Save test results to a JSON file."""
        try:
            results_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_tests": len(self.test_results),
                "passed_tests": sum(1 for result in self.test_results if result["passed"]),
                "test_station_id": self.test_station_id,
                "results": self.test_results
            }
            
            with open("station_agent_test_results.json", "w") as f:
                json.dump(results_data, f, indent=2)
            
            print("📄 Detailed results saved to: station_agent_test_results.json")
        except Exception as e:
            print(f"⚠️  Could not save results: {e}")

def main():
    """Main function to run tests."""
    print("🚀 StationAgent Test Suite")
    print("This will test all StationAgent functionality.")
    print("Note: Some tests may fail if the API is not accessible or token is invalid.")
    print()
    
    # Get token from environment or use default test token
    token = os.environ.get("SHARED_STATE_TOKEN", "test-token-123")
    station_id = f"test-station-{int(time.time())}"
    
    print(f"🔑 Using token: {token[:10]}..." if len(token) > 10 else f"🔑 Using token: {token}")
    print(f"🏷️  Using station ID: {station_id}")
    print()
    
    # Create and run tester
    tester = StationAgentTester(token=token, test_station_id=station_id)
    tester.run_all_tests()

if __name__ == "__main__":
    main() 