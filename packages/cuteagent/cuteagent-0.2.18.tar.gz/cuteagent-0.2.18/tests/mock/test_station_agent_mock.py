#!/usr/bin/env python3
"""
Mock test suite for StationAgent class that doesn't require real API access.

This test validates the logic and behavior without making actual HTTP requests.
Run with: python test_station_agent_mock.py
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
import json

# Add the cuteagent module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cuteagent'))

from cuteagent import StationAgent

class TestStationAgentMock(unittest.TestCase):
    """Mock test suite for StationAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_token = "test-token-123"
        self.test_station_id = "test-station-456"
        self.test_graph_id = "test-graph-789"
        
        # Mock the initial state push during initialization
        with patch('requests.Session.request') as mock_request:
            # Mock the initial state push response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_request.return_value = mock_response
            
            # Create agent with initial state
            initial_state = {
                "testVar": "testValue",
                "workflowStep": "initialized"
            }
            self.agent = StationAgent(
                station_thread_id=self.test_station_id,
                graph_thread_id=self.test_graph_id,
                token=self.test_token,
                initial_state=initial_state
            )
            
            # Note: agent.initial_state will include server and serverThread automatically
    
    @patch('requests.Session.request')
    def test_initialization(self, mock_request):
        """Test StationAgent initialization."""
        # Mock the initial state push response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response
        
        # Test basic initialization without initial state
        agent = StationAgent("station-1", "graph-1", "token-1")
        self.assertEqual(agent.station_thread_id, "station-1")
        self.assertEqual(agent.graph_thread_id, "graph-1")
        self.assertEqual(agent.token, "token-1")
        
        # Test that initial state is None when not provided
        self.assertIsNone(agent.initial_state)
        
        # Test with initial state
        mock_request.reset_mock()
        initial_state = {
            "workflowId": "workflow-123",
            "currentStep": "start",
            "userData": {"name": "test"}
        }
        agent_with_state = StationAgent("station-1", "graph-1", "token-1", initial_state=initial_state)
        
        # Check that server variables were automatically added to initial_state
        expected_state = initial_state.copy()
        expected_state["server"] = "idle"
        expected_state["serverThread"] = "idle"
        self.assertEqual(agent_with_state.initial_state, expected_state)
        
        # Verify the push request was made during initialization
        mock_request.assert_called()
        
        # Test default URL is used
        from cuteagent.cuteagent import SHARED_STATE_URL
        self.assertEqual(agent.base_url, SHARED_STATE_URL)
        
        # Test reserved variables
        self.assertEqual(StationAgent.RESERVED_VARIABLES, {"server", "serverThread"})
        
        # Test session setup
        self.assertIsNotNone(agent.session)
        self.assertEqual(agent.session.headers["Authorization"], f"Bearer token-1")
        self.assertEqual(agent.session.headers["Content-Type"], "application/json")
    
    @patch('requests.Session.request')
    def test_initialization_empty_state(self, mock_request):
        """Test StationAgent initialization with empty initial state."""
        # Mock successful push response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response
        
        # Test with empty initial state dict
        agent = StationAgent("station-1", "graph-1", "token-1", initial_state={})
        
        # Test that initial state has server variables added to empty dict
        expected_state = {"server": "idle", "serverThread": "idle"}
        self.assertEqual(agent.initial_state, expected_state)
        self.assertIsInstance(agent.initial_state, dict)
        
        # Verify push was called during initialization (even for empty dict)
        # The API should still be called to push the empty state + server defaults
        mock_request.assert_called()
        
        # Check that the last call was a POST to bulk-upsert with server defaults
        last_call = mock_request.call_args
        self.assertEqual(last_call[1]['method'], 'POST')
        self.assertIn('/shared-state/bulk-upsert', last_call[1]['url'])
        
        # Check that server defaults were added to empty dict
        request_data = last_call[1]['json']
        self.assertIn('variables', request_data)
        variables = request_data['variables']
        self.assertEqual(variables['server'], 'idle')
        self.assertEqual(variables['serverThread'], 'idle')
    
    @patch('requests.Session.request')
    def test_initialization_api_failure(self, mock_request):
        """Test StationAgent initialization handles API failure gracefully."""
        # Mock API failure response for push
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"success": False}
        mock_request.return_value = mock_response
        
        initial_state = {"testVar": "testValue"}
        agent = StationAgent("station-1", "graph-1", "token-1", initial_state=initial_state)
        
        # Should handle failure gracefully, keeping the initial state with server variables added
        expected_state = initial_state.copy()
        expected_state["server"] = "idle"
        expected_state["serverThread"] = "idle"
        self.assertEqual(agent.initial_state, expected_state)
        self.assertIsNotNone(agent.state)
        self.assertIsNotNone(agent.server)
    
    @patch('requests.Session.request')
    def test_state_get_success(self, mock_request):
        """Test successful state.get operation."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "attributeValue": "test_value"
            }
        }
        mock_request.return_value = mock_response
        
        result = self.agent.state.get("test_var")
        
        self.assertEqual(result, "test_value")
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_state_get_not_found(self, mock_request):
        """Test state.get with non-existent variable."""
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response
        
        result = self.agent.state.get("nonexistent_var")
        
        self.assertIsNone(result)
    
    @patch('requests.Session.request')
    def test_state_set_success(self, mock_request):
        """Test successful state.set operation."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response
        
        result = self.agent.state.set("test_var", "test_value")
        
        self.assertTrue(result)
        
        # Verify request was made with correct data
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['json']['stationThread'], self.test_station_id)
        self.assertEqual(kwargs['json']['attributeName'], "test_var")
        self.assertEqual(kwargs['json']['attributeValue'], "test_value")
    
    def test_state_set_reserved_variable(self):
        """Test that setting reserved variables raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.agent.state.set("server", "busy")
        
        self.assertIn("reserved variable", str(context.exception))
        self.assertIn("server", str(context.exception))
    
    @patch('requests.Session.request')
    def test_state_push_success(self, mock_request):
        """Test successful state.push operation."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response
        
        test_data = {"var1": "value1", "var2": "value2"}
        result = self.agent.state.push(test_data)
        
        self.assertTrue(result)
        
        # Verify server defaults were added
        args, kwargs = mock_request.call_args
        variables = kwargs['json']['variables']
        self.assertEqual(variables['server'], "idle")
        self.assertEqual(variables['serverThread'], "idle")
        self.assertEqual(variables['var1'], "value1")
        self.assertEqual(variables['var2'], "value2")
    
    def test_state_push_reserved_variables(self):
        """Test that pushing reserved variables raises ValueError."""
        test_data = {"server": "busy", "normal_var": "value"}
        
        with self.assertRaises(ValueError) as context:
            self.agent.state.push(test_data)
        
        self.assertIn("reserved variables", str(context.exception))
    
    @patch('requests.Session.request')
    def test_state_pull_success(self, mock_request):
        """Test successful state.pull operation."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "attributes": {
                "var1": "value1",
                "var2": "value2",
                "server": "idle"
            }
        }
        mock_request.return_value = mock_response
        
        result = self.agent.state.pull()
        
        expected = {"var1": "value1", "var2": "value2", "server": "idle"}
        self.assertEqual(result, expected)
    
    @patch('requests.Session.request')
    def test_state_delete_success(self, mock_request):
        """Test successful state.delete operation."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response
        
        result = self.agent.state.delete("test_var")
        
        self.assertTrue(result)
    
    def test_state_delete_reserved_variable(self):
        """Test that deleting reserved variables raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.agent.state.delete("serverThread")
        
        self.assertIn("reserved variable", str(context.exception))
    
    @patch('requests.Session.request')
    def test_state_exists(self, mock_request):
        """Test state.exists method."""
        # Mock response for existing variable
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"attributeValue": "some_value"}
        }
        mock_request.return_value = mock_response
        
        result = self.agent.state.exists("existing_var")
        self.assertTrue(result)
        
        # Mock response for non-existing variable
        mock_response.status_code = 404
        result = self.agent.state.exists("nonexistent_var")
        self.assertFalse(result)
    
    @patch('requests.Session.request')
    def test_state_list_variables(self, mock_request):
        """Test state.list_variables method."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "attributes": {
                "var1": "value1",
                "var2": "value2",
                "server": "idle"
            }
        }
        mock_request.return_value = mock_response
        
        result = self.agent.state.list_variables()
        
        expected = ["var1", "var2", "server"]
        self.assertEqual(sorted(result), sorted(expected))
    
    @patch.object(StationAgent, '_make_request')
    @patch.object(StationAgent.State, 'get')
    def test_server_load_success(self, mock_get, mock_make_request):
        """Test successful server.load operation."""
        # Mock server is idle
        mock_get.return_value = "idle"
        # Mock successful API responses for direct calls
        mock_make_request.return_value = {"success": True}
        
        result = self.agent.server.load("test_task")
        
        expected = {"status": "loaded", "serverThread": "test_task"}
        self.assertEqual(result, expected)
        
        # Verify correct calls were made
        mock_get.assert_called_with("server")
        self.assertEqual(mock_make_request.call_count, 2)  # Called for server and serverThread
    
    @patch.object(StationAgent.State, 'get')
    def test_server_load_busy(self, mock_get):
        """Test server.load when server is busy."""
        # Mock server is busy
        mock_get.return_value = "busy"
        
        result = self.agent.server.load("test_task")
        
        expected = {"status": "busy", "error": "Server is busy"}
        self.assertEqual(result, expected)
    
    @patch.object(StationAgent, '_make_request')
    @patch.object(StationAgent.State, 'get')
    def test_server_unload_success(self, mock_get, mock_make_request):
        """Test successful server.unload operation."""
        # Mock server is busy
        mock_get.return_value = "busy"
        # Mock successful API responses for direct calls
        mock_make_request.return_value = {"success": True}
        
        result = self.agent.server.unload()
        
        expected = {"status": "unloaded"}
        self.assertEqual(result, expected)
    
    @patch.object(StationAgent.State, 'get')
    def test_server_unload_already_idle(self, mock_get):
        """Test server.unload when server is already idle."""
        # Mock server is idle
        mock_get.return_value = "idle"
        
        result = self.agent.server.unload()
        
        self.assertEqual(result["status"], "idle")
        self.assertIn("already idle", result["error"])
    
    @patch.object(StationAgent.State, 'get')
    def test_server_avail(self, mock_get):
        """Test server.avail method."""
        # Mock return values for server status calls
        mock_get.side_effect = ["busy", "data_processing"]
        
        result = self.agent.server.avail()
        
        expected = {"server": "busy", "serverThread": "data_processing"}
        self.assertEqual(result, expected)
    
    @patch.object(StationAgent.State, 'get')
    @patch.object(StationAgent.State, 'set')
    def test_pause_success(self, mock_set, mock_get):
        """Test successful pause operation."""
        # Mock pause tag not in use
        mock_get.return_value = None
        mock_set.return_value = True
        
        result = self.agent.pause("test_pause_tag")
        
        # Should return success status
        self.assertIn("success", result)
        
    @patch.object(StationAgent.State, 'get')
    def test_unpause_success(self, mock_get):
        """Test successful unpause operation."""
        # Mock pause tag is paused
        mock_get.return_value = "paused"
        
        result = self.agent.unpause("test_pause_tag")
        
        # Should return success status 
        self.assertIn("success", result)
    
    @patch('requests.Session.request')
    def test_network_error_retry(self, mock_request):
        """Test network error retry logic."""
        # Mock network timeout
        from requests.exceptions import Timeout
        mock_request.side_effect = [Timeout(), Timeout(), Mock()]
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = {"success": True}
        
        # This should retry and eventually succeed
        result = self.agent._make_request("GET", "/test")
        
        # Should have made 3 attempts
        self.assertEqual(mock_request.call_count, 3)
    
    @patch('requests.Session.request')
    def test_authentication_error(self, mock_request):
        """Test 401 authentication error handling."""
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
        mock_request.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            self.agent._make_request("GET", "/test")
        
        self.assertIn("Authentication failed", str(context.exception))

class TestStationAgentIntegration(unittest.TestCase):
    """Integration tests that simulate real workflow scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the initial state push during initialization
        with patch('requests.Session.request') as mock_request:
            # Mock the initial state push response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_request.return_value = mock_response
            
            # Create agent with initial workflow state
            initial_state = {
                "currentStep": "ready",
                "workflowId": "workflow-123"
            }
            self.agent = StationAgent("workflow-1", "graph-1", "token", initial_state=initial_state)
            
            # Note: agent.initial_state will include server and serverThread automatically
    
    @patch.object(StationAgent, '_make_request')
    @patch.object(StationAgent.State, 'get')
    @patch.object(StationAgent.State, 'pull')
    def test_workflow_server_coordination(self, mock_pull, mock_get, mock_make_request):
        """Test a complete workflow server coordination scenario."""
        # Setup mocks - need to be more specific about call order
        get_call_count = 0
        def mock_get_side_effect(var_name):
            nonlocal get_call_count
            get_call_count += 1
            if get_call_count == 1:  # First check for server.avail() - server status
                return "idle"
            elif get_call_count == 2:  # Second check for server.avail() - serverThread status  
                return "idle"
            elif get_call_count == 3:  # Check for first load operation
                return "idle"  # Server is idle, so load should succeed
            elif get_call_count == 4:  # Check for second load operation
                return "busy"  # Server is now busy, so second load should fail
            else:  # Subsequent calls for unload
                return "busy"
        
        mock_get.side_effect = mock_get_side_effect
        mock_make_request.return_value = {"success": True}  # API calls succeed
        mock_pull.return_value = {"server": "idle", "currentStep": "ready"}
        
        # Simulate workflow
        # 1. Check server availability
        avail = self.agent.server.avail()
        
        # 2. Load server for task (should succeed since server is idle)
        load_result = self.agent.server.load("data_processing")
        self.assertEqual(load_result["status"], "loaded")
        
        # 3. Try to load again (should be busy)
        load_result2 = self.agent.server.load("another_task")
        self.assertEqual(load_result2["status"], "busy")
        
        # 4. Unload server (server is busy, so unload should work)
        unload_result = self.agent.server.unload()
        self.assertEqual(unload_result["status"], "unloaded")
    
    @patch.object(StationAgent.State, 'set')
    @patch.object(StationAgent.State, 'push')
    @patch.object(StationAgent.State, 'pull')
    def test_workflow_state_management(self, mock_pull, mock_push, mock_set):
        """Test a complete workflow state management scenario."""
        # Setup mocks
        mock_set.return_value = True
        mock_push.return_value = True
        mock_pull.return_value = {
            "currentStep": "processing",
            "userInput": "test data",
            "server": "idle",
            "serverThread": "idle"
        }
        
        # Simulate LangGraph node workflow
        # 1. Update shared state
        shared_data = self.agent.state.pull()
        self.assertIn("currentStep", shared_data)
        
        # 2. Set individual variable (non-reserved)
        self.agent.state.set("nodeStatus", "active")
        
        # 3. Bulk update multiple variables (non-reserved)
        bulk_data = {
            "processedData": {"result": "success"},
            "nextStep": "validation"
        }
        self.agent.state.push(bulk_data)
        
        # Verify all operations succeeded
        mock_pull.assert_called_once()
        mock_set.assert_called_once()
        mock_push.assert_called_once()

def run_mock_tests():
    """Run all mock tests."""
    print("🧪 Running StationAgent Mock Test Suite")
    print("=" * 60)
    print("ℹ️  These tests use mocked responses and don't require API access")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStationAgentMock))
    suite.addTests(loader.loadTestsFromTestCase(TestStationAgentIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 MOCK TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_mock_tests()
    sys.exit(0 if success else 1) 