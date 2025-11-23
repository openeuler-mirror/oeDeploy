#!/usr/bin/env python3
"""
PyAutoGen demo script
Tests basic AutoGen functionality
"""

print("Testing PyAutoGen installation...")

try:
    # Import AutoGen modules
    import autogen
    from autogen import AssistantAgent, UserProxyAgent
    
    print("✓ Successfully imported autogen modules")
    
    # Test basic configuration
    config_list = [
        {
            "model": "gpt-4",
            "api_key": "test_key"
        }
    ]
    
    print("✓ Created configuration successfully")
    
    # Test agent creation (without actual API call)
    llm_config = {
        "config_list": config_list,
        "seed": 42,
    }
    
    print("✓ LLM configuration created successfully")
    
    print("\n=== PyAutoGen Installation Verification ===")
    print("Status: SUCCESS")
    print("AutoGen modules are installed and importable!")
    print("==========================================\n")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please check if pyautogen package is installed correctly.")
    exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    exit(1)


