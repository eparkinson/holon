
import sys
import os

# Add src to path so we can import holon
sys.path.insert(0, os.path.abspath("src"))

try:
    from tests.test_xchat import test_parse_xchat_definition, test_x_search_tool_implementation
    
    print("Running test_parse_xchat_definition...")
    test_parse_xchat_definition()
    print("test_parse_xchat_definition PASSED")
    
    print("Running test_x_search_tool_implementation...")
    test_x_search_tool_implementation()
    print("test_x_search_tool_implementation PASSED")
    
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
