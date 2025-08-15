import os
import unittest
from dotenv import load_dotenv

from cuteagent.cuteagent import VisionAgent


class TestClaudeVision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()

    def test_claude_coordinate_grounding(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.assertTrue(api_key is not None and len(api_key) > 0, "ANTHROPIC_API_KEY must be set in environment or .env")

        agent = VisionAgent(screen_size=(1366, 768))

        original_image_url = "https://datacollectionfintor.s3.amazonaws.com/screenshot_20250517_180131.png"
        element_description = {
            "name": "Reports",
            "description": "Reports tab on the top navigation bar",
            "element_type": "tab"
        }

        result = agent.claude(original_image_url, element_description)
        print(f"Claude result: {result}")

        # Require a coordinate string in format (x,y)
        self.assertIsInstance(result, str)
        self.assertRegex(result, r"^\(\d+,\d+\)$", msg=f"Expected coordinate string, got: {result}")


if __name__ == "__main__":
    unittest.main() 