#!/usr/bin/env python

"""Tests for `cuteagent` package."""


import unittest
from io import StringIO
import sys
import logging
from cuteagent import WindowsAgent, VisionAgent, HumanAgent
from gradio_client import Client
import os
import time
# Set up logging to file
logging.basicConfig(filename='test_debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(message)s', filemode='w')

def screenshot1(url):
    try:
        client = Client(url) 
        result = client.predict(
            api_name="/get_screenshot_url"
        )
        print(result)
        print("Done")
        return result
    except Exception as e:
        print(f"Error in act operation: {e}")
        return result
        
class TestWindowsAgent(unittest.TestCase):
    """Tests for `cuteagent` package."""

    def setUp(self):
        """Capture stdout before each test."""
        self.held_stdout = sys.stdout
        sys.stdout = self.captured_output = StringIO()

    def tearDown(self):
        """Restore stdout after each test."""
        sys.stdout = self.held_stdout

    def test_hello_old_friend_default_config(self):
        """Test hello_old_friend with default variable_name."""
        agent = WindowsAgent()
        agent.hello_old_friend()
        self.assertEqual(self.captured_output.getvalue().strip(), "Hello, my old friend!")

    def test_hello_old_friend_custom_config(self):
        """Test hello_old_friend with a custom variable_name."""
        custom_name = "companion"
        agent = WindowsAgent(variable_name=custom_name)
        agent.hello_old_friend()
        self.assertEqual(self.captured_output.getvalue().strip(), f"Hello, my old {custom_name}!")

    def test_hello_world(self):
        """Test the hello_world method."""
        agent = WindowsAgent()
        agent.hello_world()
        self.assertEqual(self.captured_output.getvalue().strip(), "Hello World from WindowsAgent!")

    def test_act_method(self):
        """Test the act method."""
        agent = WindowsAgent()
        result = agent.act({"action": "CLICK","coordinate": [50,100], "value": "value", "model_selected": "claude"})
        
        # Temporarily restore original stdout to print debug output
        sys.stdout = self.held_stdout
        print("DEBUG - ACT RESULT:", result)
        # Also log to file for backup
        logging.debug(f"ACT RESULT: {result}")
        # Reset back to captured output
        sys.stdout = self.captured_output

    def test_screenshot_method(self):
        """Test the screenshot method."""
        agent = WindowsAgent()
        result = agent.screenshot()
        
        # Temporarily restore original stdout to print debug output
        sys.stdout = self.held_stdout
        print("DEBUG - SCREENSHOT RESULT:", result)
        # Also log to file for backup
        logging.debug(f"SCREENSHOT RESULT: {result}")
        # Reset back to captured output
        sys.stdout = self.captured_output

    def test_add_method(self):
        """Test the add method."""
        agent = WindowsAgent()
        result = agent.add(5, 3)
        self.assertEqual(result, 8)
        result_negative = agent.add(-5, 3)
        self.assertEqual(result_negative, -2)


if __name__ == '__main__':
    # Create a TestLoader instance
    loader = unittest.TestLoader()
    # Load tests from the current module
    # Correctly get the current module: sys.modules[__name__] if run as script
    # or for more robustness if imported: unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
    # Given the __name__ == '__main__' context, sys.modules[__name__] is fine.
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    # Create a TestRunner to run the tests
    runner = unittest.TextTestRunner(verbosity=2) # verbosity=2 for more detailed output
    # OS_URL = "https://fintor-ec2-test-2.ngrok.app" #"https://fintor-cute-test-1.ngrok.app"
    OS_URL = "https://fintor-ec2-united.ngrok.app"

    try:
        # test for windows agent
        agent = WindowsAgent(os_url=OS_URL)
        # result = agent.click_element(150,200)
        # result = agent.act({"action": "INPUT","coordinate": [0,0], "value": "Masoud MJ", "model_selected": "claude"})
        result = agent.screenshot()
        time.sleep(1)
        result2 = agent.click_element(200,200)
        time.sleep(1)
        # agent.pause(1)
        result3 = agent.click_element(250,200)

        # test for vision agent
        # agent = VisionAgent(model_selected="FINTOR_GUI")
        # result = agent.find_element(screenshot_url="https://datacollectionfintor.s3.amazonaws.com/screenshot_20250517_180131.png", element_name="click on Reports tab on navigation bar")
        # result = agent.find_element(screenshot_url="https://datacollectionfintor.s3.amazonaws.com/screenshot_20250517_180131.png", element_name="loan number 000067029 in the table")

        # test for hitl agent
        # HITL_TOKEN=os.getenv("HITL_TOKEN")
        # print("HITL_TOKEN", HITL_TOKEN)
        # agent = HumanAgent(HITL_token=HITL_TOKEN)
        # result = agent.task(
        #     image_urls=["https://datacollectionfintor.s3.amazonaws.com/screenshot_20250517_180131.png"], 
        #     thread_id="1234567890", 
        #     task_type="test1",
        #     questions=[{"Question": "Confirm list of borrowers with Document name are correct?", "Choices": ["TRUE", "FALSE"]}]
        # )

        # test for reporting
        # HITL_TOKEN=os.getenv("HITL_TOKEN")
        # agent = HumanAgent(HITL_token=HITL_TOKEN)
        # result = agent.reporting(thread_id="1234567890", thread_state={"status": "completed"})

        print("result", result)
        print("Come on man")
    except Exception as e:
        print(f"Error running test suite: {e}")
        sys.exit(1)

    # result = runner.run(suite)

    # if result.wasSuccessful():
    #     print("\nAll Python unit tests passed successfully!")
    # else:
    #     print("\nSome Python unit tests failed.")
    #     # Exit with a non-zero status code to indicate failure
    #     sys.exit(1)
