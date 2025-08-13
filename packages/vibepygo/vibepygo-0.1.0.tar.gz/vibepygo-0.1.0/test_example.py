"""
Test script to demonstrate vibe_python usage
"""
import sys
import os

# Add src to path so we can import vibe_python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import vibe_python

# Configure API settings
vibe_python.set_api_key("api_key")
vibe_python.set_model("gpt-5-nano-2025-08-07")
vibe_python.set_temperature(1.0)
print("Testing vibe_python with provided settings...")
print("=" * 50)

# Test with example.py file
try:
    print("Running example.py through OpenAI API...")
    result = vibe_python.run_vibe("example.py")
    print("Result:")
    print(result)
    print("=" * 50)
except Exception as e:
    print(f"Error running through API: {e}")
    print("=" * 50)

# Test with direct code string
test_code = """
print("Hello from vibe_python!")
import math
print(f"Square root of 16 is {math.sqrt(16)}")
for i in range(3):
    print(f"Count: {i}")
"""

try:
    print("Running test code through OpenAI API...")
    result = vibe_python.run_vibe(test_code)
    print("Result:")
    print(result)
    print("=" * 50)
except Exception as e:
    print(f"Error running test code: {e}")
    print("=" * 50)

# Test local execution for comparison
try:
    print("Running example.py locally for comparison...")
    local_result = vibe_python.run_vibe("example.py", use_local=True)
    print("Local Result:")
    print(local_result)
    print("=" * 50)
except Exception as e:
    print(f"Error running locally: {e}")
    print("=" * 50)

print("Test completed!")