#!/usr/bin/env python3
"""
OpenAI demo script
Tests basic OpenAI SDK functionality
"""

print("Testing OpenAI installation...")

try:
    # Import OpenAI modules
    from openai import OpenAI
    import openai
    
    print("✓ Successfully imported openai module")
    
    # Get version info
    if hasattr(openai, '__version__'):
        print(f"✓ OpenAI version: {openai.__version__}")
    
    # Test client structure (without actual API key)
    print("✓ OpenAI client class is available")
    
    print("\n=== OpenAI Installation Verification ===")
    print("Status: SUCCESS")
    print("OpenAI SDK is installed correctly!")
    print("=====================================\n")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please check if openai package is installed correctly.")
    exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    exit(1)


