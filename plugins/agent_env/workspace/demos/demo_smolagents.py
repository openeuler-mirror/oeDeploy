#!/usr/bin/env python3
"""
Smolagents demo script
Tests basic Smolagents functionality
"""

print("Testing Smolagents installation...")

try:
    # Import Smolagents modules
    import smolagents
    
    print("✓ Successfully imported smolagents module")
    
    # Get version info
    if hasattr(smolagents, '__version__'):
        print(f"✓ Smolagents version: {smolagents.__version__}")
    else:
        print("✓ Smolagents module loaded successfully")
    
    # Check for main components
    if hasattr(smolagents, 'Agent'):
        print("✓ Agent class is available")
    
    print("\n=== Smolagents Installation Verification ===")
    print("Status: SUCCESS")
    print("Smolagents is installed and ready to use!")
    print("==========================================\n")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please check if smolagents package is installed correctly.")
    exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    exit(1)


