# hello world edit test
# Copyright 2025 Test Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Integration test module for complete diff functionality.
"""

import unittest
import sys
import io
from contextlib import redirect_stdout


class TestCompleteDiff(unittest.TestCase):
    """Integration tests for complete diff functionality."""
    
    def test_hello_integration(self):
        """Test hello integration functionality."""
        # Capture stdout to verify print output
        captured_output = io.StringIO()
        
        with redirect_stdout(captured_output):
            print("hello")
        
        # Verify the output
        output = captured_output.getvalue().strip()
        self.assertEqual(output, "hello")
        
    def test_hello_integration_with_message(self):
        """Test hello integration with custom message."""
        test_message = "hello integration test"
        captured_output = io.StringIO()
        
        with redirect_stdout(captured_output):
            print(test_message)
        
        # Verify the output contains expected message
        output = captured_output.getvalue().strip()
        self.assertEqual(output, test_message)
        self.assertIn("hello", output)
        self.assertIn("integration", output)
        
    def test_hello_integration_multiple_prints(self):
        """Test multiple hello print statements."""
        captured_output = io.StringIO()
        
        with redirect_stdout(captured_output):
            print("hello")
            print("integration")
            print("test")
        
        # Verify all outputs
        output_lines = captured_output.getvalue().strip().split('\n')
        expected_lines = ["hello", "integration", "test"]
        
        self.assertEqual(len(output_lines), 3)
        for i, expected in enumerate(expected_lines):
            self.assertEqual(output_lines[i], expected)


def run_hello_integration():
    """Standalone function to run hello integration."""
    print("hello")
    return "hello"


if __name__ == "__main__":
    # Run the integration test directly
    print("Running hello integration test...")
    
    # Direct test execution
    result = run_hello_integration()
    assert result == "hello", f"Expected 'hello', got '{result}'"
    
    print("✓ Hello integration test passed!")
    
    # Run unittest suite
    unittest.main(verbosity=2)